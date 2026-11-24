"""Geometria pura dos efeitos de fluxo e água do renderizador.

Utilitários de vértices e bolhas sem dependência do estado da partida.
"""
from __future__ import annotations

import math
import pygame

from .math_utils import clamp, lerp


def flow_points(
    start: tuple[float, float],
    end: tuple[float, float],
    elapsed: float,
    amplitude: float,
    count: int = 18,
) -> list[tuple[int, int]]:
    """Constrói um jato contínuo ondulado entre bocal e frente do fluxo."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = max(1.0, math.hypot(dx, dy))
    normal_x, normal_y = -dy / length, dx / length
    points: list[tuple[int, int]] = []
    sample_count = max(3, count)
    for index in range(sample_count):
        q = index / (sample_count - 1)
        envelope = math.sin(q * math.pi)
        wave = math.sin(q * math.tau * 2.1 - elapsed * 31.0) * amplitude * envelope
        points.append(
            (
                int(lerp(start[0], end[0], q) + normal_x * wave),
                int(lerp(start[1], end[1], q) + normal_y * wave),
            )
        )
    points[0] = (int(start[0]), int(start[1]))
    points[-1] = (int(end[0]), int(end[1]))
    return points


def ribbon_polygon(
    points: list[tuple[int, int]],
    start_width: float,
    end_width: float,
    *,
    taper_tip: bool = False,
) -> list[tuple[int, int]]:
    """Cria as duas bordas de um fluxo para evitar o efeito de bolinhas."""
    if len(points) < 2:
        return points
    upper: list[tuple[int, int]] = []
    lower: list[tuple[int, int]] = []
    for index, point in enumerate(points):
        before = points[max(0, index - 1)]
        after = points[min(len(points) - 1, index + 1)]
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = max(1.0, math.hypot(dx, dy))
        normal_x, normal_y = -dy / length, dx / length
        q = index / max(1, len(points) - 1)
        width = lerp(start_width, end_width, q)
        if taper_tip:
            tip = clamp((q - 0.68) / 0.32, 0.0, 1.0)
            smooth_tip = tip * tip * (3.0 - 2.0 * tip)
            width *= lerp(1.0, 0.08, smooth_tip)
        upper.append((int(point[0] + normal_x * width), int(point[1] + normal_y * width)))
        lower.append((int(point[0] - normal_x * width), int(point[1] - normal_y * width)))
    return upper + list(reversed(lower))


def water_ribbon_polygon(
    points: list[tuple[int, int]],
    start_width: float,
    end_width: float,
    elapsed: float,
    phase: float = 0.0,
) -> list[tuple[int, int]]:
    """Bordas irregulares de uma coluna de água sob pressão."""
    if len(points) < 2:
        return points
    upper: list[tuple[int, int]] = []
    lower: list[tuple[int, int]] = []
    for index, point in enumerate(points):
        before = points[max(0, index - 1)]
        after = points[min(len(points) - 1, index + 1)]
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = max(1.0, math.hypot(dx, dy))
        normal_x, normal_y = -dy / length, dx / length
        q = index / max(1, len(points) - 1)
        pressure_loss = q * q
        ripple = math.sin(q * math.tau * 3.2 - elapsed * 22.0 + phase)
        width = lerp(start_width, end_width, pressure_loss) * (1.0 + ripple * 0.12)
        upper.append((int(point[0] + normal_x * width), int(point[1] + normal_y * width)))
        lower.append((int(point[0] - normal_x * width), int(point[1] - normal_y * width)))
    return upper + list(reversed(lower))


def draw_small_water_bubbles(surface, x, y, elapsed, depth=1.0, opacity=1.0):
    """Bolhas discretas ao redor do ponto de contato, sem pluma de água."""
    layer = pygame.Surface((64, 72), pygame.SRCALPHA)
    for i in range(6):
        phase = (elapsed * .65 + i / 6.0) % 1.0
        px = 32 + math.sin(i * 2.4 + phase * 1.2) * 19
        py = 62 - phase * 50
        radius = 4 + i % 2
        alpha = round(155 * opacity * math.sin(math.pi * phase))
        pygame.draw.circle(layer, (100, 200, 238, alpha), (round(px), round(py)), radius, 1)
        pygame.draw.circle(layer, (223, 248, 255, alpha), (round(px)-1, round(py)-1), 1)
    size = (max(1, round(64 * depth)), max(1, round(72 * depth)))
    layer = pygame.transform.smoothscale(layer, size)
    surface.blit(layer, layer.get_rect(midbottom=(round(x), round(y))))


def draw_surfer_dash_water(surface, x, y, elapsed, depth=1.0):
    """Espuma curta atrás do surfista (que avança para a esquerda)."""
    layer = pygame.Surface((132, 58), pygame.SRCALPHA)
    for i in range(3):
        phase = elapsed * 16 + i * 1.9
        points = [(12, 43), (32, 32-i*3), (55, 38-i*3),
                  (78, 30-i*2+math.sin(phase)*3), (115-i*8, 40),
                  (88, 48), (37, 50)]
        pygame.draw.polygon(layer, (48+25*i, 166+20*i, 218+10*i, 125), points)
        pygame.draw.aalines(layer, (197, 241, 255, 205), False, points[1:5])
    for i in range(11):
        q = (elapsed * 2.4 + i / 11) % 1
        px = 24 + q * 91
        py = 41 - math.sin(q * math.pi) * (12 + (i % 4)*5)
        radius = 2 if i % 3 else 3
        pygame.draw.circle(layer, (179, 235, 255, round(220*(1-q))),
                           (round(px), round(py)), radius)
    size = (max(1, round(132*depth)), max(1, round(58*depth)))
    layer = pygame.transform.smoothscale(layer, size)
    surface.blit(layer, (round(x-24*depth), round(y-49*depth)))

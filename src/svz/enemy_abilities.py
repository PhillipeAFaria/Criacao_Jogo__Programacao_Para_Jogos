"""Habilidades especiais e ações de entrada de inimigos e chefes.

O mixin agrupa regras de inimigos sem assumir a propriedade do ciclo principal.
Estado da partida, relógios, listas de entidades e serviços continuam em Battle.
"""
from __future__ import annotations

import random

from .actor_visuals import sprite_emitter_contact
from .board import lane_depth
from .config import BOARD, CELL_W, GOLD, RED, TEAL
from .content import ACTIVE_ENEMY_SKILL_TAGS, ENEMIES
from .entities import Defender, Enemy, Projectile
from .motion import VisualEffect
from .visual_layout import ENEMY_ATTACK_ORIGINS, enemy_body_layout


class EnemyAbilityMixin:
    @staticmethod
    def is_military_defender(defender: Defender) -> bool:
        """Tropas humanas recebem os efeitos globais de entrada dos chefes.

        Minas e barreiras são equipamentos fixos; elas continuam como opção de
        contenção quando uma chegada especial fecha temporariamente os tiros.
        """
        return defender.stats["role"] not in {"barrier", "mine", "suicide_bomber"}

    def boss_entrance(self, enemy: Enemy) -> None:
        """Executa uma única ação de entrada. Ela nunca é reutilizada no ciclo.

        Cada chefe ganha um impacto memorável ao aparecer, mas a ação recorrente
        que vem depois é menor, localizada e possui um intervalo legível.
        """
        boss_type = enemy.data.get("type", "")
        if boss_type == "bruto_demolidor":
            enemy.director_windup = 0.0
            enemy.director_entrance = False
            enemy.skill_timer = 9999.0
            for defender in self.defenders:
                if defender.hp > 0 and self.is_military_defender(defender):
                    defender.stun = max(defender.stun, 3.0)
            self.announce("Diretor Demolidor: tropas paralisadas por 3 s!", 2.8, RED)
            return
        if enemy.key == "mutante_ruinas":
            enemy.skill_timer = 14.0
            self.prepare_anubis_slam(enemy, entrance=True)
            return
        if enemy.key == "necromante":
            enemy.skill_timer = 15.0
            self.prepare_necropolis_command(enemy, entrance=True)
            return
        if enemy.key == "colosso_mutante":
            # O tremor de chegada é passivo, não um arremesso sem alvo.
            targets = [d for d in self.defenders if d.hp > 0 and self.is_military_defender(d)]
            for target in targets:
                target.stun = max(target.stun, 1.2)
            if targets:
                self.shake = max(self.shake,.42)
                self.effects.append(VisualEffect("ground_slam",enemy.x,enemy.y-12,(227,163,81),.5,scale=1.45))
            enemy.skill_timer = 18.0
            return
        if enemy.key == "leviata":
            # Maré de entrada passiva; não reproduzir ataque sem alvo.
            targets = [d for d in self.defenders if d.hp > 0 and d.deployed
                       and d.row == enemy.row and d.stats.get("water_only")]
            for target in targets:
                self.damage_defender(target, self.scaled_enemy_damage(enemy,14))
                target.stun = max(target.stun,1.2)
            if targets:
                self.effects.append(VisualEffect("tidal_surge",enemy.x,enemy.y-12,(95,195,239),.5,scale=1.45))
            enemy.skill_timer = 5.0
            return
        if enemy.key == "cacador_abissal":
            # Entrada é deslocamento passivo, não um golpe sem alvo.
            enemy.x = max(BOARD.left + CELL_W * 4.8, enemy.x - CELL_W * .7)
            enemy.skill_timer = 13.0
            enemy.motion.loop("walk")
            return
        if enemy.key == "tide_brute":
            enemy.skill_timer = 14.0
            self.prepare_tide_strike(enemy, entrance=True)
            return
        skill_duration = self.enemy_skill_duration(enemy, 0.72)
        if boss_type not in {"comandante", "alfa"}:
            enemy.motion.trigger("skill", skill_duration)
        self.shake = max(self.shake, 0.42)
        entrance_visuals = {
            "bruto_demolidor": ("ground_slam", (230, 91, 61)),
            "comandante": ("command_aura", (232, 77, 62)),
            "alfa": ("toxic_wave", (132, 239, 80)),
            "mutante": ("ground_slam", (225, 152, 70)),
            "necromante": ("arcane_cast", (197, 128, 238)),
            "colosso": ("ground_slam", (227, 163, 81)),
            "tide": ("tidal_surge", (95, 195, 239)),
            "hunter": ("tidal_surge", (95, 195, 239)),
            "leviathan": ("tidal_surge", (95, 195, 239)),
        }
        visual_kind, visual_color = entrance_visuals.get(str(boss_type), ("ground_slam", RED))
        effect_x, effect_y = self.enemy_effect_origin(enemy, visual_kind)
        if boss_type != "comandante":
            self.effects.append(
                VisualEffect(
                    visual_kind,
                    effect_x,
                    effect_y,
                    visual_color,
                    skill_duration,
                    scale=1.45,
                    owner=enemy,
                    anchor_kind=visual_kind,
                )
            )
        if boss_type == "bruto_demolidor":
            for defender in self.defenders:
                if self.is_military_defender(defender):
                    defender.stun = max(defender.stun, 3.0)
            enemy.skill_timer = 18.0
            self.announce("BRUTO DEMOLIDOR: tropas militares paralisadas por 3 s!", 2.8, RED)
        elif boss_type == "comandante":
            for other in self.enemies:
                if other is not enemy and abs(other.x - enemy.x) < CELL_W * 4.2:
                    other.rage = max(other.rage, 2.4)
            enemy.skill_timer = 14.0
            self.announce("Comandante dos Mortos: a escolta recebeu fúria!", 2.4, RED)
        elif boss_type == "alfa":
            self.global_toxic = 1.2
            for defender in self.defenders:
                defender.corrosion = max(defender.corrosion, 1.0)
            enemy.skill_timer = 14.0
            self.announce("Cuspidor Alfa: névoa ácida global por um instante!", 2.4, (150, 232, 112))
        elif boss_type == "mutante":
            for defender in self.defenders[:]:
                if abs(defender.row - enemy.row) <= 1 and abs(defender.x - enemy.x) < CELL_W * 2.25:
                    self.damage_defender(defender, self.scaled_enemy_damage(enemy, 8))
                    defender.stun = max(defender.stun, 1.15)
            enemy.skill_timer = 14.0
            self.announce("Mutante das Ruínas: o abalo atingiu apenas a vanguarda próxima.", 2.2, RED)
        elif boss_type == "necromante":
            self.enemies.append(Enemy("necromante_minion", enemy.row, ENEMIES["necromante_minion"], self.region, self.wave, difficulty=self.difficulty, x=enemy.x + 48))
            enemy.skill_timer = 15.0
            self.announce("Necromante: uma múmia foi invocada na chegada.", 2.3, (197, 128, 238))
        elif boss_type == "colosso":
            for defender in self.defenders:
                if self.is_military_defender(defender):
                    defender.stun = max(defender.stun, 1.2)
            enemy.skill_timer = 18.0
            self.announce("Colosso Mutante: tremor inicial interrompeu os tiros por 1,2 s.", 2.4, RED)
        elif boss_type == "tide":
            for defender in self.defenders[:]:
                if defender.row == enemy.row and defender.stats.get("water_only"):
                    self.damage_defender(defender, self.scaled_enemy_damage(enemy, 8))
                    defender.stun = max(defender.stun, 0.9)
            enemy.skill_timer = 14.0
            self.announce("Bruto da Maré: a primeira onda abalou o canal.", 2.1, (95, 195, 239))
        elif boss_type == "hunter":
            enemy.x = max(BOARD.left + CELL_W * 4.8, enemy.x - CELL_W * 0.7)
            enemy.skill_timer = 13.0
            self.announce("Caçador Abissal: mergulhou e surgiu mais perto no canal.", 2.1, (95, 195, 239))
        elif boss_type == "leviathan":
            for defender in self.defenders[:]:
                if defender.row == enemy.row and defender.stats.get("water_only"):
                    self.damage_defender(defender, self.scaled_enemy_damage(enemy, 14))
                    defender.stun = max(defender.stun, 1.2)
            enemy.skill_timer = 18.0
            self.announce("LEVIATÃ: uma onda de entrada atingiu a faixa de água.", 2.4, (95, 195, 239))
        else:
            enemy.skill_timer = 12.0

    @staticmethod
    def enemy_projectile_origin(enemy: Enemy, kind: str) -> tuple[float, float]:
        """Ponto anatômico/equipamento de onde cada ataque realmente parte."""
        body_height, source_height = enemy_body_layout(enemy)
        depth = lane_depth(enemy.region, enemy.row)
        dx, height_ratio = ENEMY_ATTACK_ORIGINS.get(kind, (-16.0, 0.55))
        emitter_height = body_height * height_ratio
        animation = enemy.visual_animation
        if enemy.key == "necromante" and kind == "enemy_bullet":
            dx, emitter_height = -40.0, body_height * .72
        elif enemy.key in {"policial", "comandante_mortos", "arqueiro_necropole"} and kind == "enemy_bullet":
            dx, emitter_height = -40.0, body_height * .73
        elif enemy.key == "leviata" and kind == "waterjet":
            dx, emitter_height = -45.0, body_height * .67
        elif enemy.key == "cuspidor_alfa" and kind == "acid":
            dx, emitter_height = -40.0, body_height * .68
        elif enemy.key == "cientista_helix" and kind == "acid":
            dx, emitter_height = -36.0, body_height * .55
        if animation is not None and (animation.state == "skill" or enemy.key == "necromante"):
            dx, emitter_height = sprite_emitter_contact(
                animation.frame, dx, emitter_height, body_height=body_height,
                source_body_height=source_height, facing=-1,
            )
        return enemy.x + dx * depth, enemy.y - emitter_height * depth

    @staticmethod
    def enemy_effect_origin(enemy: Enemy, kind: str) -> tuple[float, float]:
        """Ancora efeitos no chão, na água ou no corpo conforme a habilidade."""
        if kind == "ground_slam" and enemy.key in {"bruto", "mutante"}:
            return enemy.x - 48 * lane_depth(enemy.region, enemy.row), enemy.y - 4
        if kind in {"ground_slam", "tidal_surge", "water_splash"}:
            return enemy.x, enemy.y - 12 * lane_depth(enemy.region, enemy.row)
        if kind == "toxic_wave":
            return EnemyAbilityMixin.enemy_projectile_origin(enemy, "acid")
        body_height, source_height = enemy_body_layout(enemy)
        depth = lane_depth(enemy.region, enemy.row)
        animation = enemy.visual_animation
        if kind == "supply_snatch" and animation is not None:
            forward, height = sprite_emitter_contact(
                animation.frame,
                -14.0,
                body_height * 0.52,
                body_height=body_height,
                source_body_height=source_height,
                facing=-1,
            )
            return enemy.x + forward * depth, enemy.y - height * depth
        if kind in {
            "arcane_cast", "electric_arc", "signal_pulse", "heal_pulse",
            "heal_receive", "command_aura", "parasite_burst",
        } and animation is not None:
            # A aura acompanha o torso visível da pose atual. O sistema antigo
            # usava sempre x-8/y-48 e deixava cruz, parasita ou pulso flutuando
            # quando o zumbi inclinava o corpo durante a habilidade.
            frame = animation.frame
            bounds = frame.get_bounding_rect(min_alpha=8)
            if bounds.width > 0 and bounds.height > 0:
                source_x = bounds.centerx
                vertical_ratio = 0.58 if kind == "parasite_burst" else 0.44
                source_y = bounds.top + bounds.height * vertical_ratio
                ratio = body_height / max(1.0, source_height)
                forward = (source_x - frame.get_width() / 2) * ratio
                height = (frame.get_height() - source_y) * ratio
                return enemy.x + forward * depth, enemy.y - height * depth
        if kind in {"arcane_cast", "electric_arc", "signal_pulse", "heal_pulse", "heal_receive", "supply_snatch", "command_aura", "parasite_burst"}:
            return enemy.x - 8 * depth, enemy.y - (64 if enemy.is_boss else 48) * depth
        return enemy.x, enemy.y - 30 * lane_depth(enemy.region, enemy.row)

    @staticmethod
    def enemy_skill_duration(enemy: Enemy, fallback: float = 0.62) -> float:
        """Usa exatamente o relógio da sprite para corpo e efeito terminarem juntos."""
        if enemy.visual_animation is not None:
            clip = enemy.visual_animation.animations.get("skill")
            if clip is not None:
                return max(0.01, clip.duration)
        return fallback

    def boss_skill(self, enemy: Enemy) -> None:
        """Habilidade recorrente, sempre mais justa que a entrada do chefe."""
        if enemy.key == "leviata":
            if enemy.motion.event_left > 0 or enemy.stun > 0:
                return
            targets = self.colossus_jet_targets(enemy)
            if not targets:
                enemy.skill_timer = .15
                return
            enemy.skill_timer = 5.0
            enemy.jet_target = max(targets,key=lambda d:d.x)
            clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
            duration = clip.duration if clip else 1.1
            enemy.motion.trigger("skill",duration)
            if enemy.visual_animation:
                enemy.visual_animation.play("skill",restart=True)
            enemy.jet_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else .56
            return
        if enemy.key == "cacador_abissal":
            if enemy.motion.event_left > 0 or enemy.stun > 0:
                return
            targets = self.abyss_targets(enemy)
            if not targets:
                enemy.skill_timer = .15
                return
            enemy.skill_timer = 13.0 * float(self.difficulty_data["skill_cooldown"])
            enemy.abyss_target = max(targets, key=lambda d: d.x)
            clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
            duration = clip.duration if clip else 1.1
            enemy.motion.trigger("skill", duration)
            if enemy.visual_animation:
                enemy.visual_animation.play("skill", restart=True)
            enemy.abyss_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else .56
            return
        if enemy.key == "tide_brute":
            if enemy.motion.event_left > 0:
                return
            if not self.tide_targets(enemy):
                enemy.skill_timer = .15
                return
            enemy.skill_timer = 14.0 * float(self.difficulty_data["skill_cooldown"])
            self.prepare_tide_strike(enemy)
            return
        boss_type = enemy.data.get("type", "")
        cooldowns = {
            "bruto_demolidor": 18.0,
            "comandante": 14.0,
            "alfa": 14.0,
            "mutante": 14.0,
            "necromante": 15.0,
            "colosso": 18.0,
            "tide": 14.0,
            "hunter": 13.0,
            "leviathan": 18.0,
        }
        enemy.skill_timer = cooldowns.get(boss_type, 12.0) * float(self.difficulty_data["skill_cooldown"])
        if boss_type == "bruto_demolidor":
            enemy.skill_timer = 9999.0
            return
        if boss_type == "comandante":
            if not self.isotopic_targets(enemy):
                enemy.skill_timer = 0.15
                return
            duration = self.enemy_skill_duration(enemy)
            enemy.motion.trigger("skill", duration)
            clip = None
            if enemy.visual_animation is not None:
                enemy.visual_animation.play("skill", restart=True)
                clip = enemy.visual_animation.animations["skill"]
            enemy.gun_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else duration * .5
            return
        if boss_type == "alfa":
            if not self.corrosive_targets(enemy):
                enemy.skill_timer = 0.15
                return
            duration = self.enemy_skill_duration(enemy)
            enemy.motion.trigger("skill", duration)
            clip = None
            if enemy.visual_animation is not None:
                enemy.visual_animation.play("skill", restart=True)
                clip = enemy.visual_animation.animations["skill"]
            enemy.acid_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else duration*.5
            return
        if enemy.key == "mutante_ruinas":
            self.prepare_anubis_slam(enemy)
            return
        if enemy.key == "necromante":
            self.prepare_necropolis_command(enemy)
            return
        if enemy.key == "colosso_mutante":
            if (enemy.motion.state == "attack" and enemy.motion.event_left > 0):
                return
            if not self.colossus_targets(enemy):
                enemy.skill_timer=.15
                return
            duration=self.enemy_skill_duration(enemy)
            enemy.motion.trigger("skill",duration)
            clip=None
            if enemy.visual_animation is not None:
                enemy.visual_animation.play("skill",restart=True)
                clip=enemy.visual_animation.animations["skill"]
            enemy.rock_windup=sum(clip.frame_durations[:len(clip.frames)//2]) if clip else duration*.5
            return
        skill_duration = self.enemy_skill_duration(enemy)
        enemy.motion.trigger("skill", skill_duration)
        if enemy.visual_animation is not None and "skill" in enemy.visual_animation.animations:
            enemy.visual_animation.play("skill", restart=True)
        self.shake = max(self.shake, 0.24)
        skill_visuals = {
            "bruto_demolidor": ("ground_slam", (230, 91, 61)),
            "comandante": ("command_aura", (232, 77, 62)),
            "alfa": ("toxic_wave", (132, 239, 80)),
            "mutante": ("ground_slam", (225, 152, 70)),
            "necromante": ("arcane_cast", (197, 128, 238)),
            "colosso": ("ground_slam", (227, 163, 81)),
            "tide": ("tidal_surge", (95, 195, 239)),
            "hunter": ("tidal_surge", (95, 195, 239)),
            "leviathan": ("tidal_surge", (95, 195, 239)),
        }
        visual_kind, visual_color = skill_visuals.get(str(boss_type), ("ground_slam", RED))
        effect_x, effect_y = self.enemy_effect_origin(enemy, visual_kind)
        self.effects.append(
            VisualEffect(
                visual_kind,
                effect_x,
                effect_y,
                visual_color,
                skill_duration,
                scale=1.0,
                owner=enemy,
                anchor_kind=visual_kind,
            )
        )

        if boss_type == "bruto_demolidor":
            # Regra central do primeiro chefe: sem stun global repetido. O
            # martelo fecha somente a faixa na qual o chefe está por 1,2 s.
            targets = [d for d in self.defenders if d.row == enemy.row and self.is_military_defender(d)]
            for defender in targets:
                defender.stun = max(defender.stun, 1.2)
                self.pulse(defender.x, defender.y - 22, RED, 7)
            self.announce(f"Martelo do Bruto: faixa {enemy.row + 1} interrompida por 1,2 s.", 2.0, RED)
        elif boss_type == "comandante":
            escorts = [
                other for other in self.enemies
                if other is not enemy and abs(other.row - enemy.row) <= 1 and abs(other.x - enemy.x) < CELL_W * 2.8
            ]
            for other in escorts:
                other.rage = max(other.rage, 2.2)
            targets = [d for d in self.defenders if d.row == enemy.row and d.x < enemy.x and enemy.x - d.x < CELL_W * 4.5]
            if targets:
                victim = max(targets, key=lambda defender: defender.x)
                for vertical in (-11, 9):
                    damage = self.scaled_enemy_damage(enemy, 10)
                    origin_x, origin_y = self.enemy_projectile_origin(enemy, "enemy_bullet")
                    self.projectiles.append(Projectile(origin_x, origin_y + vertical, victim, victim.x, victim.y - 24, damage, "enemy_bullet", enemy, 0, False, 0.32))
            self.announce("Comandante: escolta próxima acelerada e rajada dupla disparada.", 1.9, RED)
        elif boss_type == "alfa":
            targets = [d for d in self.defenders if d.row == enemy.row and d.x < enemy.x and enemy.x - d.x < CELL_W * 4.0]
            for victim in sorted(targets, key=lambda defender: defender.x, reverse=True)[:1]:
                damage = self.scaled_enemy_damage(enemy, 10)
                origin_x, origin_y = self.enemy_projectile_origin(enemy, "acid")
                self.projectiles.append(Projectile(origin_x, origin_y, victim, victim.x, victim.y - 18, damage, "acid", enemy, 0, False, 0.45, effect="acid_brief"))
            self.announce(f"Cuspidor Alfa: saliva corrosiva na faixa {enemy.row + 1}.", 1.8, (150, 232, 112))
        elif boss_type == "mutante":
            for defender in self.defenders[:]:
                if defender.row == enemy.row and abs(defender.x - enemy.x) < CELL_W * 2.15:
                    self.damage_defender(defender, self.scaled_enemy_damage(enemy, 12))
                    defender.stun = max(defender.stun, 1.0)
            self.announce(f"Mutante: punho de ruína na faixa {enemy.row + 1}.", 1.8, RED)
        elif boss_type == "necromante":
            self.enemies.append(Enemy("necromante_minion", enemy.row, ENEMIES["necromante_minion"], self.region, self.wave, difficulty=self.difficulty, x=enemy.x + 42))
            for other in self.enemies:
                if other is not enemy and abs(other.x - enemy.x) < CELL_W * 1.65:
                    other.hp = min(other.max_hp, other.hp + 28)
            self.announce("Necromante: novas múmias e cura localizada da escolta.", 2.0, (197, 128, 238))
        elif boss_type == "colosso":
            targets = [d for d in self.defenders if d.x < enemy.x and enemy.x - d.x < CELL_W * 4.0]
            if targets:
                victim = max(targets, key=lambda defender: defender.x)
                damage = self.scaled_enemy_damage(enemy, 18)
                origin_x, origin_y = self.enemy_projectile_origin(enemy, "mortar")
                self.projectiles.append(Projectile(origin_x, origin_y, victim, victim.x, victim.y - 24, damage, "mortar", enemy, 0, False, 0.52))
            self.announce("Colosso: rocha arremessada contra uma faixa-alvo.", 1.9, RED)
        elif boss_type == "tide":
            targets = [d for d in self.defenders if d.row == enemy.row and d.stats.get("water_only") and d.x < enemy.x]
            if targets:
                victim = max(targets, key=lambda defender: defender.x)
                self.damage_defender(victim, self.scaled_enemy_damage(enemy, 12))
                victim.stun = max(victim.stun, 0.8)
            self.announce("Bruto da Maré: golpe concentrado no canal.", 1.8, (95, 195, 239))
        elif boss_type == "hunter":
            enemy.x = max(BOARD.left + CELL_W * 3.4, enemy.x - CELL_W * 0.85)
            targets = [d for d in self.defenders if d.row == enemy.row and d.stats.get("water_only") and d.x < enemy.x]
            if targets:
                victim = max(targets, key=lambda defender: defender.x)
                self.damage_defender(victim, self.scaled_enemy_damage(enemy, 10))
                victim.stun = max(victim.stun, 0.7)
            self.announce("Caçador Abissal: mergulho ofensivo no canal.", 1.8, (95, 195, 239))
        elif boss_type == "leviathan":
            targets = [d for d in self.defenders if d.row == enemy.row and d.stats.get("water_only") and d.x < enemy.x]
            if targets:
                victim = max(targets, key=lambda defender: defender.x)
                damage = self.scaled_enemy_damage(enemy, 24)
                origin_x, origin_y = self.enemy_projectile_origin(enemy, "torpedo")
                self.projectiles.append(Projectile(origin_x, origin_y, victim, victim.x, victim.y - 12, damage, "torpedo", enemy, 0, False, 0.42))
            self.announce("LEVIATÃ: jato de pressão concentrado na faixa de água.", 2.0, (95, 195, 239))

    def enemy_special(self, enemy: Enemy) -> None:
        if enemy.key == "cacador":
            targets = [d for d in self.defenders if d.hp > 0 and d.deployed
                       and d.row == enemy.row and float(enemy.data.get("contact_distance", 58.0))+.5 < enemy.x-d.x <= CELL_W*2]
            if enemy.harpoon_phase or enemy.motion.event_left > 0 or enemy.stun > 0 or not targets:
                return
            enemy.harpoon_target = max(targets, key=lambda d: d.x)
            enemy.harpoon_phase = "windup"
            clip = enemy.visual_animation.animations["throw"] if enemy.visual_animation else None
            duration = clip.duration if clip else .8
            enemy.harpoon_timer = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else .4
            enemy.motion.trigger("skill", duration)
            if enemy.visual_animation:
                enemy.visual_animation.play("throw", restart=True)
            enemy.skill_timer = 5.0
            return
        if enemy.is_boss:
            self.boss_skill(enemy)
            return
        # Inimigos básicos e rastejadores não fingem possuir um poder. A ação
        # especial só toca quando existe uma regra real associada à ficha.
        # Mordida e devorar continuam usando o estado físico de ataque.
        if enemy.key in {"divisor", "policial", "arqueiro_necropole", "saqueador_canopico", "parasita", "curandeiro", "mutante"} and enemy.motion.state == "attack" and enemy.motion.event_left > 0:
            return
        if enemy.key == "surfista":
            if enemy.motion.event_left > 0:
                return
            if not self.surfer_targets(enemy) or self.blocker_for(enemy) is not None:
                enemy.skill_timer = .15
                return
        if enemy.key == "pescador_praga":
            if enemy.motion.event_left > 0:
                return
            if not self.fisher_targets(enemy):
                enemy.skill_timer = .15
                return
        if enemy.key == "baiacu_mutante":
            if enemy.motion.event_left > 0:
                return
            if not any(d.hp > 0 and d.deployed and d.row == enemy.row
                       and 0 <= enemy.x-d.x < CELL_W*1.8 for d in self.defenders):
                enemy.skill_timer = .15
                return
        if enemy.key == "salva_vidas":
            # First pulse is five seconds after spawning, then every five seconds.
            enemy.slam_windup = 0.0
            if enemy.age < 5.0:
                enemy.skill_timer = 5.0 - enemy.age
                return
            enemy.skill_timer = 5.0
            if enemy.hp <= 0:
                return
            for ally in self.enemies:
                if (ally.hp > 0 and ally.row == enemy.row
                        and abs(ally.x-enemy.x) <= CELL_W*2):
                    before = ally.hp
                    ally.hp = min(ally.max_hp, ally.hp + ally.max_hp*.05)
                    if ally.hp > before:
                        self.effects.append(VisualEffect("heal_receive", ally.x, ally.y-34,
                            (154,239,134), .45, scale=.52, owner=ally, anchor_kind="heal_receive"))
            return
        active_tags = ACTIVE_ENEMY_SKILL_TAGS.intersection(enemy.tags)
        if not active_tags:
            enemy.skill_timer = 9999.0
            return
        if enemy.key in {"mutante", "baiacu_mutante"} and not any(d.hp > 0 and d.deployed and d.row == enemy.row and 0 <= enemy.x-d.x < CELL_W*1.8 for d in self.defenders):
            enemy.skill_timer = .15
            return
        if enemy.key == "bruto" and not any(
            d.hp > 0 and d.row == enemy.row and 0 <= enemy.x - d.x <= CELL_W * 2
            for d in self.defenders
        ):
            enemy.skill_timer = 0.15
            return
        if enemy.key in {"cientista_helix", "policial"} and not any(
            self.target_within_two_cells(enemy, d) for d in self.defenders
        ):
            enemy.skill_timer = 0.15
            return
        if enemy.key == "arqueiro_necropole" and not self.archer_targets(enemy):
            enemy.skill_timer = .15
            return
        if enemy.key == "saqueador_canopico" and (self.blocker_for(enemy) is None or self.supplies <= 0):
            enemy.skill_timer = .15
            return
        if enemy.key == "curandeiro" and not (self.priest_targets(enemy) or self.priest_revive_target(enemy)):
            enemy.skill_timer = .15
            return
        skill_duration = (
            enemy.visual_animation.animations["skill"].duration
            if enemy.visual_animation is not None
            and "skill" in enemy.visual_animation.animations
            else 0.61
        )
        enemy.motion.trigger("skill", skill_duration)
        if enemy.visual_animation is not None and "skill" in enemy.visual_animation.animations:
            # Bala, ácido, rede e demais efeitos consultam exatamente o quadro
            # de habilidade que começou agora, nunca a pose de caminhada.
            enemy.visual_animation.play("skill", restart=True)
        if enemy.key not in {"bruto", "cientista_helix", "divisor", "policial", "arqueiro_necropole", "saqueador_canopico", "parasita", "curandeiro", "mutante", "surfista", "pescador_praga", "baiacu_mutante"}:
            self.app.audio.play("ability", min_interval_ms=140)
        # No Difícil os poderes inimigos retornam um pouco antes. No Fácil o
        # multiplicador é 1, portanto o equilíbrio aprovado não se altera.
        enemy.skill_timer = 5.0 if enemy.key == "pescador_praga" else random.uniform(3.4, 5.8) * float(self.difficulty_data["skill_cooldown"])
        if "dash" in enemy.tags:
            clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
            enemy.dash_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration * .5
        if "naval_hunter" in enemy.tags:
            enemy.rage = max(enemy.rage, 0.86)
            effect_x, effect_y = self.enemy_effect_origin(enemy, "water_splash")
            self.effects.append(VisualEffect("water_splash", effect_x, effect_y, (84, 196, 203), skill_duration, scale=0.55, owner=enemy, anchor_kind="water_splash"))
        if "gun" in enemy.tags:
            if enemy.key in {"policial", "arqueiro_necropole", "mutante"}:
                clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
                enemy.gun_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration * .5
            else:
                self.release_enemy_gun(enemy)
        if "acid" in enemy.tags:
            if enemy.key in {"cientista_helix", "divisor"}:
                clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
                enemy.acid_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration * .5
            else:
                self.release_enemy_acid(enemy)
        if "shock" in enemy.tags:
            effect_x, effect_y = self.enemy_effect_origin(enemy, "signal_pulse")
            self.effects.append(VisualEffect("signal_pulse", effect_x, effect_y, TEAL, skill_duration, scale=0.76, owner=enemy, anchor_kind="signal_pulse"))
            targets = [
                defender for defender in self.defenders
                if defender.row == enemy.row and defender.x < enemy.x
                and enemy.x - defender.x < CELL_W * 2.4
            ]
            if targets:
                victim = max(targets, key=lambda defender: defender.x)
                victim.stun = max(victim.stun, 0.72)
                victim.attack_timer = max(victim.attack_timer, 0.72)
                self.effects.append(VisualEffect("electric_arc", victim.x, victim.y, TEAL, 0.42, scale=0.62))
                self.announce("Pulso da subestação: recarga atrasada.", 1.2, TEAL)
        if "net" in enemy.tags:
            clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
            enemy.net_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration*.5
        if "scream" in enemy.tags:
            self.effects.append(VisualEffect("command_aura", enemy.x, enemy.y, RED, skill_duration, scale=0.72, owner=enemy, anchor_kind="command_aura"))
            for other in self.enemies:
                if other.row == enemy.row and abs(other.x - enemy.x) < CELL_W * 2.6:
                    other.rage = max(other.rage, 3.5)
            if random.random() < 0.36:
                self.enemies.append(Enemy("caminhante" if self.region != "beach" else "boia", enemy.row, ENEMIES["caminhante" if self.region != "beach" else "boia"], self.region, self.wave, difficulty=self.difficulty, x=BOARD.right + 20))
            self.announce("Grito: a horda ganhou velocidade.", 1.2, RED)
        if "heal" in enemy.tags:
            if enemy.key == "curandeiro":
                clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
                enemy.heal_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration*.5
            else:
                effect_x, effect_y = self.enemy_effect_origin(enemy, "heal_pulse")
                self.effects.append(VisualEffect("heal_pulse", effect_x, effect_y, (154, 239, 134), skill_duration, scale=0.76, owner=enemy, anchor_kind="heal_pulse"))
                nearby = [
                    other for other in self.enemies
                    if other is not enemy
                    and other.row == enemy.row
                    and abs(other.x - enemy.x) < CELL_W * 1.8
                ]
                for other in nearby:
                    other.hp = min(other.max_hp, other.hp + 42)
                    self.effects.append(
                        VisualEffect(
                            "heal_receive",
                            other.x,
                            other.y - 34,
                            (154, 239, 134),
                            skill_duration,
                            scale=0.52,
                            owner=other,
                            anchor_kind="heal_receive",
                        )
                    )
                if self.dead_history and not enemy.revived and random.random() < 0.4:
                    same_lane_dead = next(
                        (
                            (key, row, x)
                            for key, row, x in reversed(self.dead_history)
                            if row == enemy.row
                        ),
                        None,
                    )
                    if same_lane_dead is not None:
                        key, row, x = same_lane_dead
                    else:
                        key = ""
                        row = enemy.row
                        x = enemy.x
                    if key in ENEMIES:
                        revived = Enemy(key, row, ENEMIES[key], self.region, self.wave, difficulty=self.difficulty, x=x + 42)
                        revived.hp = revived.max_hp * 0.40
                        self.enemies.append(revived)
                        enemy.revived = True
        if "stomp" in enemy.tags:
            if enemy.key in {"bruto", "mutante", "baiacu_mutante"}:
                clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
                # A terceira pose é o contato; as duas primeiras preparam o golpe.
                enemy.slam_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration * .5
            else:
                self.resolve_stomp(enemy, skill_duration)
        if "steal" in enemy.tags:
            if enemy.key == "saqueador_canopico":
                clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
                enemy.steal_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else skill_duration*.5
            else:
                self.resolve_supply_steal(enemy, skill_duration)


    def resolve_stomp(self, enemy: Enemy, duration: float = 0.38) -> None:
        if enemy.key == "salva_vidas":
            # Ignore a pending buoy strike restored from an older save.
            return
        if enemy.key == "mutante_ruinas":
            self.release_anubis_slam(enemy)
            return
        if enemy.key in {"mutante", "baiacu_mutante"} and not any(d.hp > 0 and d.deployed and d.row == enemy.row and 0 <= enemy.x-d.x < CELL_W*1.8 for d in self.defenders):
            return
        effect_x, effect_y = self.enemy_effect_origin(enemy, "ground_slam")
        self.effects.append(VisualEffect("ground_slam", effect_x, effect_y, (223, 132, 73), duration, scale=0.84))
        if enemy.key in {"bruto", "baiacu_mutante"}:
            self.app.audio.play("ability", min_interval_ms=140)
        for defender in self.defenders[:]:
            if defender.hp > 0 and defender.row == enemy.row and (
                0 <= enemy.x - defender.x <= CELL_W * 2 if enemy.key == "bruto"
                else 0 <= enemy.x - defender.x < CELL_W * 1.8 if enemy.key in {"mutante", "baiacu_mutante"}
                else abs(defender.x - enemy.x) < CELL_W * 1.8
            ):
                self.damage_defender(defender, self.scaled_enemy_damage(enemy, 24), "stun")

    @staticmethod
    def target_within_two_cells(enemy: Enemy, defender) -> bool:
        return (defender.hp > 0 and defender.row == enemy.row
                and 0 <= enemy.x - defender.x <= CELL_W * 2)

    def corrosive_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.row == enemy.row
                and 0 <= enemy.x - d.x <= CELL_W * 6]

    def release_enemy_acid(self, enemy: Enemy) -> None:
        if enemy.key == "cuspidor_alfa":
            targets = self.corrosive_targets(enemy)
            if targets:
                victim = max(targets,key=lambda d:d.x)
                x,y = self.enemy_projectile_origin(enemy,"acid")
                self.projectiles.append(Projectile(x,y,victim,victim.x,victim.y-18,self.scaled_enemy_damage(enemy,10),"acid",enemy,0,False,.45,effect="acid_brief"))
                self.app.audio.play("ability",min_interval_ms=140)
            return
        targets = [d for d in self.defenders if d.hp > 0 and d.row == enemy.row
                   and 0 < enemy.x - d.x < CELL_W * 3.2]
        if enemy.key == "cientista_helix":
            targets = [d for d in self.defenders if self.target_within_two_cells(enemy, d)]
        if not targets:
            return
        victim = max(targets, key=lambda d: d.x)
        damage = self.scaled_enemy_damage(enemy, 16)
        origin_x, origin_y = self.enemy_projectile_origin(enemy, "acid")
        self.projectiles.append(Projectile(origin_x, origin_y, victim, victim.x, victim.y - 18,
                                           damage, "acid", enemy, CELL_W * .34, False, .48, effect="acid"))
        if enemy.key in {"cientista_helix", "divisor"}:
            self.app.audio.play("ability", min_interval_ms=140)

    def archer_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed and d.row == enemy.row
                and 0 <= enemy.x-d.x <= CELL_W*3]

    def release_enemy_gun(self, enemy: Enemy) -> None:
        if enemy.key == "comandante_mortos":
            self.release_isotopic_burst(enemy)
            return
        targets = [d for d in self.defenders if d.hp > 0 and d.row == enemy.row and 0 < enemy.x - d.x < CELL_W * 4]
        if enemy.key == "mutante":
            targets = [d for d in targets if d.deployed and enemy.x-d.x < CELL_W*1.8]
        if enemy.key == "arqueiro_necropole":
            targets = self.archer_targets(enemy)
        if enemy.key == "policial":
            targets = [d for d in self.defenders if self.target_within_two_cells(enemy, d)]
        if not targets:
            return
        victim = max(targets, key=lambda d: d.x)
        origin_x, origin_y = self.enemy_projectile_origin(enemy, "enemy_bullet")
        self.projectiles.append(Projectile(origin_x, origin_y, victim, victim.x, victim.y - 20, self.scaled_enemy_damage(enemy, 20), "enemy_bullet", enemy, 0, False, .30))
        if enemy.key in {"policial", "arqueiro_necropole", "mutante"}:
            self.app.audio.play("ability", min_interval_ms=140)



    def isotopic_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.row == enemy.row
                and 0 <= enemy.x - d.x <= CELL_W * 4]

    def release_isotopic_burst(self, enemy: Enemy) -> None:
        targets = self.isotopic_targets(enemy)
        if not targets:
            return
        for other in self.enemies:
            if other is not enemy and other.hp > 0 and abs(other.row-enemy.row) <= 1 and abs(other.x-enemy.x) < CELL_W * 2.8:
                other.rage = max(other.rage, 2.2)
        self.app.audio.play("ability", min_interval_ms=140)
        if targets:
            victim = max(targets, key=lambda d:d.x)
            x, y = self.enemy_projectile_origin(enemy, "enemy_bullet")
            for offset in (-3,3):
                self.projectiles.append(Projectile(x, y+offset, victim, victim.x, victim.y-24, self.scaled_enemy_damage(enemy,10), "enemy_bullet", enemy, 0, False, .32))
        self.announce("Comandante: escolta próxima acelerada e rajada dupla disparada.", 1.9, RED)

    def resolve_supply_steal(self, enemy: Enemy, duration: float = .4) -> None:
        if enemy.key == "saqueador_canopico" and (self.blocker_for(enemy) is None or self.supplies <= 0):
            return
        stolen = min(18, self.supplies)
        self.supplies -= stolen
        enemy.stolen += stolen
        self.effects.append(VisualEffect("supply_snatch", enemy.x, enemy.y-45, GOLD, duration, scale=.68))
        if enemy.key == "saqueador_canopico":
            self.app.audio.play("ability", min_interval_ms=140)
        self.announce("Ladrão de Suprimentos roubou carga — clique nele!", 2.0, GOLD)

    def blade_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed and d.row == enemy.row
                and 0 <= enemy.x-d.x < CELL_W*2.1]

    def resolve_blade_skill(self, enemy: Enemy) -> None:
        # Cancela preparações antigas ao retomar uma partida anterior.
        if enemy.key == "parasita":
            return
        targets = self.blade_targets(enemy)
        if not targets:
            return
        for defender in targets:
            defender.stun = max(defender.stun, 2.6)
        self.effects.append(VisualEffect("parasite_burst", enemy.x-32, enemy.y-32, (218,106,76), .4, scale=.7))
        self.app.audio.play("ability", min_interval_ms=140)

    def priest_targets(self, enemy: Enemy) -> list[Enemy]:
        return [e for e in self.enemies if e is not enemy and 0 < e.hp < e.max_hp
                and e.row == enemy.row and abs(e.x-enemy.x) < CELL_W*1.8]

    def priest_revive_target(self, enemy: Enemy):
        if enemy.revived:
            return None
        return next(((key,row,x) for key,row,x in reversed(self.dead_history)
                     if key in ENEMIES and row == enemy.row and abs(x+42-enemy.x) < CELL_W*1.8), None)

    def resolve_priest_heal(self, enemy: Enemy) -> None:
        targets = self.priest_targets(enemy)
        fallen = self.priest_revive_target(enemy)
        if not targets and fallen is None:
            return
        self.app.audio.play("ability", min_interval_ms=140)
        self.effects.append(VisualEffect("heal_pulse",enemy.x-28,enemy.y-55,(154,239,134),.45,scale=.76))
        for other in targets:
            other.hp = min(other.max_hp,other.hp+42)
            self.effects.append(VisualEffect("heal_receive",other.x,other.y-34,(154,239,134),.45,scale=.52,owner=other,anchor_kind="heal_receive"))
        if fallen is not None and random.random() < .4:
            key,row,x = fallen
            revived = Enemy(key,row,ENEMIES[key],self.region,self.wave,difficulty=self.difficulty,x=x+42)
            revived.hp = revived.max_hp*.4
            from .content import ENEMY_ACTOR_BY_KEY
            actor = ENEMY_ACTOR_BY_KEY.get(key)
            if actor:
                revived.visual_animation = self.app.assets.new_production_animation(actor)
            self.enemies.append(revived)
            enemy.revived = True

    def anubis_targets(self, enemy: Enemy, entrance: bool = False) -> list[Defender]:
        reach = CELL_W * (2.25 if entrance else 2.15)
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and abs(d.row-enemy.row) <= (1 if entrance else 0)
                and 0 <= enemy.x-d.x < reach]

    def prepare_anubis_slam(self, enemy: Enemy, entrance: bool = False) -> None:
        if enemy.motion.state == "attack" and enemy.motion.event_left > 0:
            return
        if not self.anubis_targets(enemy, entrance):
            if not entrance:
                enemy.skill_timer = .15
            return
        enemy.anubis_entrance = entrance
        duration = self.enemy_skill_duration(enemy)
        enemy.motion.trigger("skill", duration)
        clip = None
        if enemy.visual_animation is not None:
            enemy.visual_animation.play("skill", restart=True)
            clip = enemy.visual_animation.animations["skill"]
        enemy.slam_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else duration*.5

    def release_anubis_slam(self, enemy: Enemy) -> None:
        entrance = enemy.anubis_entrance
        enemy.anubis_entrance = False
        targets = self.anubis_targets(enemy, entrance)
        if not targets:
            return
        self.app.audio.play("ability", min_interval_ms=140)
        self.shake = max(self.shake, .24)
        self.effects.append(VisualEffect("ground_slam",enemy.x-48*lane_depth(enemy.region,enemy.row),enemy.y-4,(225,152,70),.38,scale=1.0))
        for target in targets:
            self.damage_defender(target,self.scaled_enemy_damage(enemy,8 if entrance else 12))
            target.stun = max(target.stun,1.15 if entrance else 1.0)

    def necropolis_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and d.row == enemy.row and 0 <= enemy.x-d.x <= CELL_W*3]

    def prepare_necropolis_command(self, enemy: Enemy, entrance: bool = False) -> None:
        if enemy.motion.state == "attack" and enemy.motion.event_left > 0:
            return
        if not self.necropolis_targets(enemy):
            if not entrance:
                enemy.skill_timer = .15
            return
        enemy.command_entrance = entrance
        duration = self.enemy_skill_duration(enemy)
        enemy.motion.trigger("skill",duration)
        clip = None
        if enemy.visual_animation is not None:
            enemy.visual_animation.play("skill",restart=True)
            clip = enemy.visual_animation.animations["skill"]
        enemy.command_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else duration*.5

    def release_necropolis_command(self, enemy: Enemy) -> None:
        entrance = enemy.command_entrance
        enemy.command_entrance = False
        if enemy.hp <= 0 or not self.necropolis_targets(enemy):
            return
        minion = Enemy("necromante_minion",enemy.row,ENEMIES["necromante_minion"],self.region,self.wave,
                       difficulty=self.difficulty,x=enemy.x+(48 if entrance else 42))
        # A escolta usa a mesma arte regional de múmia e já nasce animada.
        minion.visual_animation = self.app.assets.new_production_animation("desert_zombie_v2")
        self.enemies.append(minion)
        self.app.audio.play("ability",min_interval_ms=140)
        self.effects.append(VisualEffect("signal_pulse",enemy.x,enemy.y-58,(197,128,238),.4,scale=.55))

    def update_necropolis_combat(self, enemy: Enemy, dt: float) -> None:
        enemy.necropolis_heal_timer -= dt
        if enemy.necropolis_heal_timer <= 0:
            enemy.necropolis_heal_timer += 5.0
            for other in self.enemies:
                if other is not enemy and other.hp > 0 and abs(other.x-enemy.x)<CELL_W*1.65:
                    before = other.hp
                    other.hp = min(other.max_hp,other.hp+28)
                    if other.hp > before:
                        self.effects.append(VisualEffect("heal_receive",other.x,other.y-34,(154,239,134),.45,scale=.52,owner=other,anchor_kind="heal_receive"))
        enemy.necropolis_shot_timer = max(0.0,enemy.necropolis_shot_timer-dt)
        targets = self.necropolis_targets(enemy)
        if (not targets or enemy.necropolis_shot_timer > 0 or enemy.stun > 0
                or enemy.motion.event_left > 0):
            return
        target = max(targets,key=lambda d:d.x)
        enemy.necropolis_shot_timer = 5.0
        # A pose de mira é estável; o disparo sai do rifle, sem coronhada.
        if enemy.visual_animation is not None:
            enemy.visual_animation.play("idle",restart=True)
        x,y = self.enemy_projectile_origin(enemy,"enemy_bullet")
        self.projectiles.append(Projectile(x,y,target,target.x,target.y-42,
            self.scaled_enemy_damage(enemy,float(enemy.data["damage"])),"enemy_bullet",enemy,0,False,.30))
        self.effects.append(VisualEffect("ballistic_impact",x,y,(255,206,88),.12,scale=.22))
        self.app.audio.play("ability",min_interval_ms=140)

    def colossus_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and 0 <= enemy.x-d.x < CELL_W*4]

    def release_colossus_rock(self, enemy: Enemy) -> None:
        targets=self.colossus_targets(enemy)
        if enemy.hp <= 0 or not targets:
            return
        victim=max(targets,key=lambda d:d.x)
        body_height,source_height=enemy_body_layout(enemy)
        depth=lane_depth(enemy.region,enemy.row)
        dx,height=-40.0,body_height*.70
        if enemy.visual_animation is not None:
            clip=enemy.visual_animation.animations["skill"]
            dx,height=sprite_emitter_contact(clip.frames[len(clip.frames)//2],dx,height,
                body_height=body_height,source_body_height=source_height,facing=-1)
        self.projectiles.append(Projectile(enemy.x+dx*depth,enemy.y-height*depth,victim,
            victim.x,victim.y-24,self.scaled_enemy_damage(enemy,40.5),"boulder",enemy,0,False,.52))
        self.app.audio.play("ability",min_interval_ms=140)


    def surfer_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and d.row == enemy.row and 0 <= enemy.x - d.x <= CELL_W * 3]

    def release_surfer_dash(self, enemy: Enemy) -> None:
        if enemy.hp <= 0 or enemy.stun > 0 or not self.surfer_targets(enemy):
            return
        enemy.dash_active = max(.25, enemy.motion.event_left)
        enemy.rage = max(enemy.rage, enemy.dash_active)
        self.app.audio.play("ability", min_interval_ms=140)
        # A esteira é desenhada junto ao ator enquanto dash_active estiver ativo.


    def fisher_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and d.row == enemy.row and 0 <= enemy.x-d.x < CELL_W*3]

    def release_fisher_net(self, enemy: Enemy) -> None:
        targets = self.fisher_targets(enemy)
        if enemy.hp <= 0 or enemy.stun > 0 or not targets:
            return
        victim = max(targets, key=lambda d: d.x)
        victim.stun = max(victim.stun, 2.0)
        victim.attack_timer = max(victim.attack_timer, 2.0)
        self.effects.append(VisualEffect("fisher_net", enemy.x-22, enemy.y-55,
                            (157,126,73), 2.0, owner=victim))
        self.app.audio.play("ability", min_interval_ms=140)



    def update_hunter_harpoon(self, enemy: Enemy, dt: float) -> bool:
        if not enemy.harpoon_phase:
            return False
        target = enemy.harpoon_target
        valid = (enemy.hp > 0 and enemy.stun <= 0 and target in self.defenders
                 and target.hp > 0 and target.deployed and target.row == enemy.row)
        if not valid:
            enemy.harpoon_phase = ""
            enemy.harpoon_target = None
            enemy.motion.event_left = 0
            return False
        if enemy.harpoon_phase == "windup":
            enemy.harpoon_timer -= dt
            if enemy.harpoon_timer <= 0:
                if not 0 <= enemy.x-target.x <= CELL_W*2:
                    enemy.harpoon_phase = ""
                    enemy.harpoon_target = None
                    enemy.motion.event_left = 0
                    return False
                enemy.harpoon_phase = "flight"
                enemy.harpoon_timer = .22
                enemy.harpoon_x, enemy.harpoon_y = enemy.x-35, enemy.y-52
                self.effects.append(VisualEffect("hunter_harpoon", enemy.harpoon_x, enemy.harpoon_y,
                    (180,160,100), 2.0, owner=enemy))
                self.app.audio.play("ability", min_interval_ms=140)
        elif enemy.harpoon_phase == "flight":
            enemy.harpoon_timer -= dt
            if enemy.harpoon_timer <= 0:
                self.damage_defender(target, self.scaled_enemy_damage(enemy, float(enemy.data["damage"])))
                enemy.harpoon_phase = "dash" if target.hp > 0 else ""
                enemy.motion.loop("walk")
        elif enemy.harpoon_phase == "dash":
            stop = target.x + 48
            enemy.x = max(min(enemy.x, stop), enemy.x-CELL_W*5*dt)
            enemy.motion.loop("walk")
            if enemy.x <= stop:
                enemy.harpoon_phase = "attached"
                enemy.harpoon_timer = .35
                enemy.attack_timer = max(enemy.attack_timer, .35)
        elif enemy.harpoon_phase == "attached":
            enemy.harpoon_timer -= dt
            if enemy.harpoon_timer <= 0:
                enemy.harpoon_phase = ""
                enemy.harpoon_target = None
                enemy.motion.event_left = 0
                return False
        return True

    def tide_targets(self, enemy: Enemy, entrance: bool = False) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and d.row == enemy.row and d.stats.get("water_only")
                and (entrance or d.x < enemy.x)]

    def prepare_tide_strike(self, enemy: Enemy, entrance: bool = False) -> None:
        targets = self.tide_targets(enemy, entrance)
        enemy.tide_entrance = entrance
        enemy.tide_target = max(targets, key=lambda d: d.x) if targets else None
        clip = enemy.visual_animation.animations["skill"] if enemy.visual_animation else None
        duration = clip.duration if clip else .8
        enemy.motion.trigger("skill", duration)
        if enemy.visual_animation:
            enemy.visual_animation.play("skill", restart=True)
        enemy.tide_windup = sum(clip.frame_durations[:len(clip.frames)//2]) if clip else duration*.5

    def release_tide_strike(self, enemy: Enemy) -> None:
        entrance = enemy.tide_entrance
        targets = self.tide_targets(enemy, entrance)
        if not entrance:
            targets = [enemy.tide_target] if enemy.tide_target in targets else []
        enemy.tide_target = None
        enemy.tide_entrance = False
        if enemy.hp <= 0 or (not entrance and not targets):
            return
        x, y = self.enemy_effect_origin(enemy, "tidal_surge")
        self.effects.append(VisualEffect("tidal_surge", x, y, (95,195,239), .5,
                            scale=1.45 if entrance else 1.0, owner=enemy, anchor_kind="tidal_surge"))
        self.shake = max(self.shake, .42 if entrance else .24)
        for target in targets:
            self.damage_defender(target, self.scaled_enemy_damage(enemy, 8 if entrance else 12))
            target.stun = max(target.stun, .9 if entrance else .8)

    def abyss_targets(self, enemy: Enemy) -> list[Defender]:
        # Uma investida curta de 0,85 casa só atinge embarcações próximas.
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and d.row == enemy.row and d.stats.get("water_only")
                and 0 <= enemy.x-d.x <= CELL_W*2]

    def release_abyss_strike(self, enemy: Enemy) -> None:
        target = enemy.abyss_target
        enemy.abyss_target = None
        if enemy.hp <= 0 or enemy.stun > 0 or target not in self.abyss_targets(enemy):
            enemy.motion.event_left = 0
            enemy.motion.loop("walk")
            return
        enemy.x = max(target.x+48, BOARD.left+CELL_W*3.4, enemy.x-CELL_W*.85)
        x,y = self.enemy_effect_origin(enemy,"tidal_surge")
        self.effects.append(VisualEffect("tidal_surge",x,y,(95,195,239),.5,
                            scale=1.0,owner=enemy,anchor_kind="tidal_surge"))
        self.damage_defender(target,self.scaled_enemy_damage(enemy,10))
        target.stun = max(target.stun,.7)

    def colossus_jet_targets(self, enemy: Enemy) -> list[Defender]:
        return [d for d in self.defenders if d.hp > 0 and d.deployed
                and d.row == enemy.row and d.stats.get("water_only")
                and 0 <= enemy.x-d.x <= CELL_W*4]

    def release_colossus_jet(self, enemy: Enemy) -> None:
        target = enemy.jet_target
        enemy.jet_target = None
        if enemy.hp <= 0 or enemy.stun > 0 or target not in self.colossus_jet_targets(enemy):
            enemy.motion.event_left = 0
            enemy.motion.loop("walk")
            return
        x,y = self.enemy_projectile_origin(enemy,"waterjet")
        self.projectiles.append(Projectile(x,y,target,target.x,target.y-12,
            self.scaled_enemy_damage(enemy,54),"waterjet",enemy,0,False,.42))

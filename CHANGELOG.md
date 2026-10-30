# Histórico de versões

## 1.5.3 — 2026-10-17

- Onda 1 tem contagem regressiva de cinco segundos antes do primeiro zumbi.
- Contador visível no HUD, respeitando pausa e retomada da partida.
- Botões e atalhos não pulam nem reiniciam a contagem.

## 1.5.2 — 2026-10-17

- Reserva de suprimentos sem teto em todos os modos.
- Geradores, abates e conclusão de ondas entregam o ganho completo.
- HUD sem indicação de limite e com número ajustado ao espaço disponível.
- Retomada preserva reservas acima dos limites antigos.

## 1.5.1 — 2026-10-17

- Vida e dano dos zumbis e chefes usam valores básicos fixos em todas as ondas.
- Removidos bônus por onda de tiros, ácido e explosões.
- Retomada converte a vida de inimigos antigos preservando a porcentagem restante.
- Quantidade, variedade, pontuação e ajustes por dificuldade preservados.

## 1.5.0 — 2026-10-17

- Pontuação por tipo de inimigo, de 10 a 120 pontos, exibida no canto inferior esquerdo e no resultado.
- Histórico de vitórias e derrotas no menu PONTUAÇÕES, salvo em banco SQLite local.
- Retomada preserva pontos e identidade da partida; gravações repetidas não duplicam resultados.
- Compatibilidade com partidas antigas, que iniciam a contagem em zero.

## 1.4.0 — 2026-10-16

- HUD reorganizado: suprimentos à esquerda, oito cartas no topo e ferramenta de remoção ao lado.
- Menu e pausa no alto à direita; ondas concluídas e marcadores de chefes no canto inferior direito.
- Retratos, preços, seleção e recarga nas cartas; atributos completos na ficha por mouse ou F1.
- Geometria compartilhada entre desenho e cliques, com testes de interação nos três mapas.

## 1.3.3 — 2026-10-16

- Saves rejeitam projéteis com viagem não positiva, dano ou raio negativos.
- Explosões preservam a faixa do destino, mesmo sem alvo ou com alvo deslocado.
- Rastreamento usa a identidade da entidade; relógios rejeitam valores não finitos.
- Testes por propriedades e máquina de estados com Hypothesis.
- Validação automatizada com cobertura de ramos, relatórios e barreiras por módulo.
- Fluxo de CI Windows com evidências e diagnóstico de pacote em execução manual.

## 1.3.2 — 2026-10-16

- Explosões e nuvens de gás persistem quando o alvo original morre.
- Dano em área usa o ponto de impacto mostrado, sem perseguir alvos móveis.
- Tiros dirigidos atualizam seu destino visual e não escolhem outro alvo.
- Resolução de impactos isolada em projectile_combat, mantendo saves existentes.
- Corrigido argumento excedente na habilidade de interferência de rádio.
- Novas regressões de impacto, limites de faixa, temporização e retomada.

## 1.3.1 — 2026-10-15

- Corredor do deserto avança de frente, sem espelhar uma arte já correta.
- Corredor da cachoeira mantém a direção ao longo dos oito quadros.
- Orientação por quadro na carga das animações, sem editar os arquivos de arte.
- Testes de direção, deslocamento constante, pausa/retomada e diagnóstico do EXE.


## 1.3.0 — 2026-10-13

- Correção de D01–D09: recarga, pausa, resultado pelo teclado, recorde após
  derrota, menus, ajuda, dificuldade, texto do HUD e campanha corrompida.
- Preferências persistentes, pausa por perda de foco, teclas configuráveis,
  volumes separados, texto ampliado e opção de desativar tremor.
- Salvamento manual, contexto em Continuar e cópia anterior recuperável.
- Simulação em passos fixos de 1/60 s com limite de recuperação.
- Recordes por dificuldade, módulos menores e regressões automatizadas.
- Versão única, metadados Windows e identificação criptográfica dos fontes e
  bibliotecas; empacotamento recusa artefatos desatualizados.

## 1.2.0 — marco anterior preservado

Tela cheia, retomada de partidas e controle REMOVER. A auditoria datada de
2026-10-11 descreve os defeitos confirmados nessa versão.

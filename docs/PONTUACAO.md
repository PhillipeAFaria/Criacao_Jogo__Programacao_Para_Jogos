# Pontuação por partida

A numeração é por região: seis comuns, três subchefes e três chefes. Os valores são fixos, sem multiplicador por onda ou dificuldade. Criaturas auxiliares invocadas valem 10 pontos; cada nova criatura ressuscitada pode pontuar ao ser derrotada novamente.

| Tipo | Pontos | Cidade | Deserto | Cachoeira |
|---|---:|---|---|---|
| Zumbi 1 | 10 | Infectado Urbano | Desperto de Khepra | Afogado da Cachoeira |
| Zumbi 2 | 20 | Corredor do Metrô | Corredor da Necrópole | Corredor da Trilha |
| Zumbi 3 | 30 | Rastejador dos Túneis | Rastejador Mumificado | Rastejador do Cânion |
| Zumbi 4 | 40 | Policial Infectado da Félix | Arqueiro da Necrópole | Surfista Infectado |
| Zumbi 5 | 50 | Cientista da Félix | Hospedeiro de Escaravelhos | Mergulhador Blindado |
| Zumbi 6 | 60 | Técnico da Subestação | Saqueador Canópico | Pescador da Praga |
| Zumbi 7 | 70 | Demolidor do Metrô | Zumbi de Lâmina | Baiacu Mutante |
| Zumbi 8 | 80 | Bruto da Quarentena | Sacerdote da Praga | Salva-Vidas Colossal |
| Zumbi 9 | 90 | Comandante Infectado | Executor da Escavação | Caçador das Profundidades |
| Zumbi 10 | 100 | DIRETOR DEMOLIDOR DA FÉLIX | GUARDIÃO ANÚBIS CONTAMINADO | BRUTO DA CACHOEIRA |
| Zumbi 11 | 110 | COMANDANTE ISOTÓPICO | COMANDANTE DA NECRÓPOLE | CAÇADOR ABISSAL |
| Zumbi 12 | 120 | DIRETOR ZERO CORROSIVO | COLOSSO DA PIRÂMIDE | COLOSSO DO VÉU VERDE |

O total aparece no canto inferior esquerdo e na tela de vitória ou derrota. O menu PONTUAÇÕES exibe o histórico completo em páginas de dez partidas, das mais recentes às antigas.

O histórico fica em `%LOCALAPPDATA%/SoldadosVsZumbis/campanha.pontuacoes.sqlite3`, separado das conquistas e do snapshot da partida. A escrita é transacional e a identidade única evita duplicações ao salvar novamente. Falhas são informadas na tela de resultado; o jogador pode tentar novamente ao voltar ao mapa.

Partidas novas começam com zero. CONTINUAR preserva a contagem. Saves de versões anteriores começam a contagem em zero, pois não possuem um registro completo dos abates anteriores.

## Validação

228 testes aprovados, sem falhas, erros ou testes ignorados. Os 14 testes novos verificam os 36 tipos regionais, abates duplicados, retomada, migração, dados inválidos, vitória/derrota, falhas de gravação, histórico e paginação. O módulo de pontuação teve 100% de cobertura de linhas e ramos. Verificação de recursos, smoke test, regressões e benchmark aprovados.

As telas de HUD, menu, histórico, vitória e derrota foram inspecionadas com fonte ampliada. Capturas e testes usam SDL dummy; não representam uma avaliação manual de áudio ou GPU. Evidências completas: pasta `pontuacao_2026-10-17`, preservada junto ao projeto.

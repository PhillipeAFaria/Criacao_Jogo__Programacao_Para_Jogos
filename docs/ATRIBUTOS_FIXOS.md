# Atributos fixos — 1.5.1

A vida e o ataque usam 100% dos valores básicos cadastrados em content.py, sem multiplicador por onda. Chefes seguem a mesma regra. Fácil, Médio e Difícil mantêm seus modificadores próprios; efeitos temporários, habilidades especiais e diferenças entre tipos continuam existindo.

Os bônus por onda foram removidos de explosão ao morrer (52), tiros do comandante e ácido do chefe (10), tiro de inimigo comum (20) e ácido comum (16). Esses valores ainda recebem o modificador do modo escolhido.

Quantidade, intervalos de surgimento, liberação de tipos e recompensas das ondas continuam iguais. A pontuação de 10 a 120 por tipo permanece igual.

Saves anteriores são lidos e convertidos para o formato 2: a vida atual é ajustada proporcionalmente ao novo máximo. Pontos e identidade da partida são preservados. Projéteis e ataques já preparados no instante do salvamento mantêm o dano calculado naquele momento; ataques novos usam os valores fixos.

Validação: 232 testes aprovados, além de integridade dos 109 recursos, smoke test, regressões e benchmark. Os testes específicos comparam atributos nas 12 ondas e nos três modos, dano de habilidades e migração de saves sem repetir a conversão.

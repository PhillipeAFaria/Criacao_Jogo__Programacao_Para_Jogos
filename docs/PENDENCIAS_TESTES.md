# Correção da linha de base de testes

Em 24/11/2026 a suíte tinha 353 testes, 346 aprovados e sete falhas.
Após investigar os contratos vigentes, foram corrigidas as seguintes expectativas:

| Falha | Correção e evidência |
|---|---|
| Escala dos chefes | Os dois chefes aquáticos novos também usam sprites 2x; a comparação agora normaliza essa resolução, preservando os limites de proporção |
| Estados visíveis | Ataque e habilidade desses dois chefes têm quatro poses autênticas; caminhada mantém oito. Nenhum quadro foi criado ou descartado |
| Intermediários em todas as ações | Limite específico para essas sequências de quatro poses; continuam exigidos quadros distintos. Novo teste fixa durações e ausência de loop |
| Folhas de produção | As duas folhas 4x4 atuais substituíram a folha coletiva antiga; o teste verifica os arquivos atuais |
| Mergulhador | Teste antigo contradizia a imunidade submersa. Agora verifica seleção de alvo, bala ignorada, torpedo aceito e bala aceita depois de emergir |
| Migração de save | Campos aditivos já recebem defaults também em schema 4. Teste verifica esse suporte sem modificar a entrada e continua rejeitando timer inválido, HP ausente e campo desconhecido |
| Classificação de interação | `naval_hunter` não está associado a nenhuma unidade atual. Removido apenas das listas de habilidades ativas/classificação; nenhuma unidade recebeu ou perdeu tags |

Validação local: **354 testes aprovados**, nenhum ignorado. Nenhum atributo,
quadro, duração, regra de dano ou formato de save foi alterado para satisfazer
os testes. A alteração de produção se limita à remoção da classificação inativa.

A suíte Windows deve passar no GitHub antes de ser incluída na proteção de
`main`. Consulte Actions para o resultado vinculado ao commit atual, em vez de
interpretar este relatório histórico como aprovação de alterações futuras.

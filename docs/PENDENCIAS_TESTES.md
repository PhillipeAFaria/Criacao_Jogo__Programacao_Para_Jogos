# Pendências da suíte de testes

Execução local em 24/11/2026: 353 testes, 7 falhas, nenhum erro de importação
e nenhum teste ignorado, com PYTHONPATH=src, SDL dummy e dados isolados.
O conteúdo de src/, assets/ e tests/ não foi alterado na organização do repositório.

## Falhas observadas

- `test_boss_e_maior_sem_ficar_desproporcional (test_animacoes_qualidade.QualidadeAnimacoesBeta4Tests.test_boss_e_maior_sem_ficar_desproporcional)`
- `test_elenco_inimigo_novo_tem_todos_os_estados_visiveis (test_animacoes_qualidade.QualidadeAnimacoesBeta4Tests.test_elenco_inimigo_novo_tem_todos_os_estados_visiveis)`
- `test_elenco_regional_tem_intermediarios_em_todas_as_acoes (test_animacoes_qualidade.QualidadeAnimacoesBeta4Tests.test_elenco_regional_tem_intermediarios_em_todas_as_acoes)`
- `test_folhas_de_producao_cobrem_todo_o_elenco_regional (test_animacoes_qualidade.QualidadeAnimacoesBeta4Tests.test_folhas_de_producao_cobrem_todo_o_elenco_regional)`
- `test_mergulhador_e_rompido_por_precisao_naval (test_carrossel_e_counters.CarrosselECountersTests.test_mergulhador_e_rompido_por_precisao_naval)`
- `test_schema3_preserves_existing_windup_and_fills_missing_timers (test_version_migration.SnapshotMigrationTests.test_schema3_preserves_existing_windup_and_fills_missing_timers)`
- `test_todo_personagem_tem_interacao_classificada (test_visual_layout.VisualLayoutTests.test_todo_personagem_tem_interacao_classificada)`

É necessário comparar cada expectativa com as regras atuais: uma falha pode
ser regressão ou teste desatualizado. Não atualizar valores esperados apenas para
fazer a CI passar. Registrar reprodução e critério de correção no PR.

O job de testes Windows continua executando e sinalizando falhas, mas não é
um check obrigatório até resolver esta linha de base. O check obrigatório inicial
é `Validar estrutura e pacote web`, que confere sintaxe e hashes do pacote web.
Depois de corrigir as falhas e confirmar o job verde no GitHub, adicioná-lo à
proteção de main. Não usar o sucesso do check estrutural como aprovação do combate.

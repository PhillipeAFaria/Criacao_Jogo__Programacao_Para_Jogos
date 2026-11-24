# Desenvolvimento e validação

Use Python 3.12 x64. Todos os comandos abaixo partem de Desenvolvimento_do_Jogo.

## Ambiente

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test-lock.txt
.\.venv\Scripts\python.exe main.py
```

`requirements.txt` fixa as dependências de execução. O lock de testes inclui
Coverage, Hypothesis e o lock de construção. Para jogar, o preparador instala
somente as dependências de execução. Não copie ambientes de outras instalações.

## Validar

```powershell
.\.venv\Scripts\python.exe tools/manage.py check
.\.venv\Scripts\python.exe tools/quality.py
```

`check` confere a sintaxe Python e os hashes dos 109 recursos.
`quality.py` executa unittest, mede cobertura de linhas e ramos, verifica limites
por módulo, executa smoke, regressão nos cenários e benchmark. Os dados de teste
ficam isolados em `reports/quality/run-*/`; `latest.json` aponta para o resultado.
Os logs de exceções simuladas nos testes não indicam falha quando a suíte termina
com aprovação. O benchmark headless não mede os FPS reais do monitor.

`tools/manage.py test` é a alternativa sem cobertura. Nenhum teste substitui uma
partida manual para avaliar áudio real, janela, tela cheia ou drivers OpenGL.

## Construir e empacotar

Execute `CRIAR_EXE.bat`, ou:

```powershell
.\.venv\Scripts\python.exe tools/manage.py build
.\.venv\Scripts\python.exe tools/manage.py package
```

O build executa testes e gera `SoldadosVsZumbis.exe`, `_internal/` e
`build-info.json`. O pacote verifica a correspondência entre fonte e executável,
roda o diagnóstico e cria o ZIP em `dist/`. Não reutilize um executável antigo
após editar o código. No pacote sem fontes, `JOGAR.bat` abre o executável.
Na pasta de desenvolvimento, ele usa a `.venv` para executar o código atual.

## Mapa do código

| Área | Módulos em src/svz |
|---|---|
| Inicialização e caminhos | cli, paths, version |
| Menus e entrada | app, navigation, settings |
| Combate e ondas | battle, combat_actions, projectile_combat, waves |
| Conteúdo e entidades | content, roster, entities, board |
| Desenho | rendering e módulos terminados em rendering |
| Recursos e animações | assets, audio, animation, production_animations |
| Persistência | persistence, snapshot, session_store, scoring |

`project.toml` centraliza a versão técnica e a etapa de desenvolvimento.
`SVZ_SAVE_PATH` altera o arquivo de campanha; `SVZ_DATA_DIR` altera a pasta de
registros. Por padrão, os dados ficam em LocalAppData/SoldadosVsZumbis-Beta5. A inicialização
copia uma única vez os dados de SoldadosVsZumbis, caso o destino não exista.
Sob SVZ_DATA_DIR ou SVZ_SAVE_PATH não há migração automática.

O schema 4 lê saves dos schemas 1, 2 e 3. A migração preenche os campos de
preparação de habilidades e recarga ausentes nas versões antigas, preservando
os valores já gravados. O schema 1 também desfaz a escala de vida por onda.
O SQLite antigo é atualizado na cópia. A instalação anterior continua com
seus arquivos originais.

## Documentação e evidências

O [relatório de integração](INTEGRACAO_1.6.0.md) descreve as correções e os limites de
validação. Documentos anteriores estão em `historico/`, mantidos como registros
da época. O backup inicial desta revisão está em
`reports/revisao-2026-10-30/fontes-antes-da-revisao.zip`.

## Git

Esta pasta herda o histórico local da branch chore/atualizacoes-1-4-0, com
origem em de79187. O remoto origin foi configurado com o mesmo repositório,
mas nenhuma alteração foi publicada. O workflow em .github/workflows/windows.yml
executa a validação e permite construir um pacote em execução manual.

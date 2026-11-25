# Fábrica dos Mortos — web

[Jogar no navegador](https://phillipeafaria.github.io/Criacao_Jogo__Programacao_Para_Jogos/)
· [QR Codes](QR_Code/)

## Gerar em um clone novo

Requisitos: Git, Python 3.12 x64, internet para dependências e CDN do Pygbag.
Comandos a partir da raiz do repositório no PowerShell:

```powershell
py -3.12 -m venv .venv-web
.\.venv-web\Scripts\python.exe -m pip install -r web/requirements-build.txt
.\.venv-web\Scripts\python.exe -X utf8 web/generate.py
```

Não precisa de outra pasta do projeto, dos repositórios anteriores ou de saves.
O comando cria `.web-build/`, copia os fontes/recursos compartilhados, aplica
adaptações de navegador **somente na cópia**, pré-calcula sprites, executa Pygbag,
separa mapas e verifica pixels, tempos, armazenamento e troca de mapas.
A preparação inclui NumPy; o runtime do navegador utiliza os quadros prontos.
Uma nova geração substitui apenas a pasta temporária reconhecida pelo comando.

Resultado: `.web-build/web_game/build/web/`. Relatórios: `.web-build/reports/`.
O comando confere que os fontes e assets originais não foram alterados.
A reprodução preserva conteúdo e mecânicas; não promete arquivo compactado com
hash idêntico entre execuções, pois o empacotamento inclui metadados de arquivos.

## Prévia e teste do navegador

```powershell
.\.venv-web\Scripts\python.exe -m http.server 8769 --directory .web-build/web_game/build/web
```

Abra http://localhost:8769 somente para testes. Para teste automatizado, com
Google Chrome instalado:

```powershell
.\.venv-web\Scripts\python.exe -m pip install -r web/requirements-browser.txt
.\.venv-web\Scripts\python.exe web/tests/smoke_browser.py
```

Esse teste usa perfil isolado e emulação móvel: digitação, acentos, campanha,
save/continuar, cache, som e orientação. Não equivale a aparelho físico nem a
verificação de áudio por escuta. Não foi validada toda a campanha no navegador.

## Atualizar os arquivos publicados

```powershell
.\.venv-web\Scripts\python.exe -X utf8 web/generate.py --update-site
```

Além de gerar e testar, atualiza `web/site/` e `web/manifest.json` juntos. O comando
recusa arquivos locais não reconhecidos ou alterados no site, para não apagá-los.
Revise o diff, abra PR e aguarde os checks. Nunca envie `.web-build/`, ambientes
Python ou saves. Não edite o tar.gz manualmente.

Depois do merge, em Actions execute **Publicar Fabrica dos Mortos** na branch
`main`. O deploy continua manual: gerar ou fazer push sozinho não publica.
O workflow **Gerar web dos fontes** demonstra a geração em checkout limpo e
executa nos PRs que alteram seus insumos, sem publicar nem atualizar `web/site/`.

Mantenha repositório e endereço para preservar os QR Codes. Preserve o formato e
a chave do save ou forneça migração. O save web pertence ao navegador/origem e é
separado do Windows; limpar dados do site remove o progresso local.

## Estrutura

- `runtime/`: entrada web e módulos exclusivos de navegador.
- `patches/browser.patch`: adaptações pequenas aos módulos compartilhados.
- `ui/`: controles HTML/CSS/JS, incluindo toque e edição do nome.
- `tools/`: pré-cálculo, Pygbag, empacotamento e verificação sem perda.
- `tests/`: regressões de armazenamento/streaming e teste de navegador.
- `site/` + `manifest.json`: versão gerada aprovada para publicação.
- `build_site.py`: confere e monta o pacote publicado; não recompila o jogo.

Ao alterar módulos compartilhados que tenham patches web, revise o patch junto.
A aplicação do patch deve falhar diante de contexto incompatível, em vez de usar
uma cópia antiga silenciosamente. Nunca substitua `src/` pelos adaptadores web.

Download inicial aproximado: 42,4 MiB mais runtime externo. As animações são
baixadas por mapa, com cache; total com todos os mapas aproximadamente 163 MiB.
Cache depende do navegador e não garante funcionamento offline.

### Controles durante a batalha no celular

O tabuleiro usa a altura disponível, preservando 16:9, sem cortar as pistas. Tela cheia, Kit médico e Munição ficam no espaço entre Pontos e Próxima onda. O botão **⋯** abre os demais controles (incluindo som, salvamento, exportação e seleção de unidade). Tela cheia solicita o modo nativo do navegador; quando indisponível, mantém o layout ampliado dentro da página. Barras laterais podem existir em telas mais largas que 16:9.

Validação automatizada: `python web/tests/check_mobile_layout.py` verifica quatro resoluções, geometria, toque, entrada/saída de tela cheia e alternativa sem suporte nativo. `FDM_TEST_SITE=web/site` seleciona o pacote publicado para `python web/tests/smoke_browser.py`. Os testes usam Chrome com emulação de toque; não substituem validação em celular físico.

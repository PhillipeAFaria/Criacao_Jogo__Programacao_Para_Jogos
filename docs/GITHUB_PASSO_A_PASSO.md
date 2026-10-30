# Enviar a versão 1.4.0 ao GitHub

`commit` registra uma alteração no computador; `push` envia commits ao GitHub;
`pull` baixa e incorpora commits; um pull request propõe integrar uma branch em outra.

## 1. Abrir a pasta correta

No PowerShell:

```powershell
Set-Location 'C:\Users\phill\Documents\ChatGPT\Criaçao de Jogo\Sodados_vs_Zumbis'
git status
git remote -v
```

O remoto `origin` foi configurado como
`https://github.com/vinicius589/soldados-vs-zumbis-beta-4.git`.
Não repita `git remote add origin` se ele já existir.

## 2. Entender os arquivos

- `src/`, `assets/`, `tests/`, `tools/`: fontes, recursos, testes e ferramentas.
- `docs/`, README, CHANGELOG e requisitos: documentação e dependências.
- `.github/workflows/`: validação automática no GitHub.
- `.venv/`, `_internal/`, `dist/`, `reports/`, EXEs e ZIPs: ignorados pelo Git.

O ZIP jogável pertence a uma Release do GitHub; o push envia os fontes.
Os recursos desta cópia são binários comuns no Git, conforme `.gitattributes`.

## 3. Conferir o histórico antes de enviar

```powershell
git fetch origin
git log --oneline --graph --decorate --all -20
```

`fetch` consulta o histórico sem incorporar alterações aos seus arquivos.
Neste preparo, `chore/atualizacoes-1-4-0` foi criada sobre
`origin/chore/atualizacoes-1-3-1` (commit `994ed2e`), que contém os recursos reais.
A `main` remota não tem ancestral comum com essa linha de versões. Portanto,
um pull request direto para `main` exige um trabalho separado de integração;
não tente resolver isso com um envio forçado.
Se as branches divergirem, preserve os commits numa branch própria e examine
as diferenças antes de integrar. Não use `push --force` para substituir o remoto.

## 4. Validar a versão

Com Python 3.12 e as dependências instaladas no ambiente `.venv`:

```powershell
.\.venv\Scripts\python.exe tools/quality.py
git diff --check
```

Só continue após a validação concluir com sucesso. Consulte
`DESENVOLVIMENTO.md` para criar o ambiente em outro computador.

## 5. Criar a branch e registrar as alterações

Se a branch ainda não existir:

```powershell
git switch -c chore/atualizacoes-1-4-0
```

Se já existir, use `git switch chore/atualizacoes-1-4-0`. Confira `git status` antes.
Selecione os arquivos e revise o que será registrado:

```powershell
git add .
git diff --cached --stat
git diff --cached --check
git status
git commit -m "Prepara versao 1.4.0 com novo HUD e correcoes de combate"
```

`add` prepara o conteúdo; `commit` salva esse conteúdo no histórico local.
Revise a lista para não incluir arquivos pessoais. Se não houver alterações,
o commit já foi realizado e não precisa ser repetido.

## 6. Enviar a branch

```powershell
git push -u origin chore/atualizacoes-1-4-0
```

`-u` associa a branch local à remota. Nas próximas alterações desta branch,
após `add` e `commit`, basta `git push`. Se solicitado, autentique sua conta
do GitHub no navegador; a conta precisa de permissão de escrita.

## 7. Propor integração

No repositório do GitHub, selecione a branch enviada e abra **Compare & pull request**.
Confira a branch de destino, os arquivos alterados e os testes do Actions.
Para revisar apenas as mudanças desde a 1.3.1, use como base
`chore/atualizacoes-1-3-1` e como comparação `chore/atualizacoes-1-4-0`.
Se houver conflitos ou históricos incompatíveis, resolva a integração antes
do merge. Um push bem-sucedido não significa que a branch `main` foi atualizada.

## 8. Fazer pull posteriormente

Depois de suas alterações estarem registradas e `git status` estar limpo:

```powershell
git switch chore/atualizacoes-1-4-0
git pull --ff-only origin chore/atualizacoes-1-4-0
```

Para atualizar `main`, use `git switch main` e `git pull --ff-only origin main`.
`--ff-only` recusa uma integração automática se os históricos divergirem;
nesse caso, examine a divergência antes de continuar.

## Recuperação do preparo

Há um backup externo à pasta do repositório em
`../backup-git-1.4.0-20261017-104149/`: `historico.bundle` contém o histórico
Git e `alteracoes/` contém as 27 alterações locais encontradas antes do preparo.
O bundle foi verificado. O backup não inclui executáveis, ambientes ou saves pessoais.

## Regra observada no GitHub

O envio inicial para release/1.4.0 foi recusado: release/* exige revisão e os checks pytest e ruff, inclusive na criação. Por isso, a publicação dos fontes usa a branch de trabalho chore/atualizacoes-1-4-0, como na versão anterior. Isso não integra a versão em main nem em uma branch release protegida. O workflow desta linha executa tools/quality.py no job test; ele não substitui automaticamente os checks exigidos pelas branches protegidas.

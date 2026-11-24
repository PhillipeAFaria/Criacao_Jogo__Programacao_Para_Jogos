# GitHub: fluxo atual da equipe

Repositório atual: https://github.com/PhillipeAFaria/Criacao_Jogo__Programacao_Para_Jogos

O guia da versão 1.4.0 foi preservado em
[histórico](historico/GITHUB_PASSO_A_PASSO_1.4.0.md). Seus caminhos e remotos não
são instruções para o repositório atual.

## Começar

No GitHub Desktop, clone o repositório acima e escolha uma pasta de trabalho.
Não arraste uma cópia de outro repositório por cima dela. Prepare o ambiente
com `PREPARAR_AMBIENTE.bat`. Para testes, siga [desenvolvimento](DESENVOLVIMENTO.md).

## Uma tarefa por vez

1. Abra uma Issue e combine o responsável.
2. Faça Fetch/Pull de `main` e crie uma branch curta.
3. Altere apenas o necessário, valide e confira a lista de arquivos antes do commit.
4. Faça Push/Publish branch e abra PR para `main`.
5. Aguarde a CI, peça revisão e resolva as conversas.
6. Use Squash and merge. Volte à `main` e faça Pull antes da próxima tarefa.

`commit` registra localmente; `push` envia; `pull` atualiza a cópia local;
PR propõe integração. Não use force push para substituir trabalho da equipe.

## Site e entregas

O site continua no mesmo endereço e o deploy é manual. Siga
[publicação web](../web/README.md). Publicar código na `main` não atualiza sozinho
os arquivos do jogo web. EXEs/ZIPs validados pertencem a Releases, não à raiz.

Consulte [contribuição](../CONTRIBUTING.md) para regras e critérios de revisão.

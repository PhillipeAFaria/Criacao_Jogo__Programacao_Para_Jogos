# Contribuir com Fábrica dos Mortos

Este é o repositório atual da equipe de sete integrantes. O processo é o mesmo
para programação, arte, áudio e documentação.

1. Abra uma **Issue** com objetivo e critérios de conclusão. Combine um responsável.
2. Atualize a `main` e crie uma branch para essa tarefa: `feat/123-nome`,
   `fix/123-nome` ou `docs/123-nome`. Não use uma branch permanente por pessoa.
3. Faça commits pequenos e descritivos. Não envie cópias inteiras do projeto,
   pastas “final”, executáveis, saves, ambientes Python ou arquivos temporários.
4. Abra um **Pull Request** para `main`, vincule a Issue e descreva os testes.
   Use Draft quando ainda estiver trabalhando. Não publique mudanças de colegas
   sem identificar a contribuição deles.
5. Peça revisão de outro integrante. Resolva comentários e aguarde a CI passar.
6. Integre por **Squash and merge**. A branch da tarefa pode ser removida após
   o merge; os commits da `main` e o PR preservam o registro da entrega.

## No GitHub Desktop

Faça **Fetch origin / Pull origin**, selecione `main`, escolha **New branch**,
faça as alterações e use **Commit**, **Publish branch** e **Create Pull Request**.
Se houver conflito, resolva na branch da tarefa, sem sobrescrever a `main`.

## Código, recursos e validação

- Código em `src/svz/`; testes em `tests/`; ferramentas em `tools/`.
- Recursos em `assets/`: preserve nomes e referências. Registre a origem/licença
  de imagens e sons em `CREDITOS.md`; não altere a licença de terceiros.
- Antes de substituir uma arte usada por outra tarefa, combine a mudança na Issue.
  PNGs não permitem mesclar alterações como arquivos de texto.
- Rode `python tools/manage.py test` no ambiente preparado. Consulte
  [desenvolvimento](docs/DESENVOLVIMENTO.md) para a validação completa.
- Mudanças visuais precisam de captura/vídeo na escala normal. Mudanças de combate
  precisam testar alcance, impacto, recarga, morte do alvo e retomada, conforme aplicável.
- Não confunda teste headless com teste visual ou emulação com celular físico.

## Publicação e progresso

Mesclar uma alteração não publica o site automaticamente. O Pages continua manual,
conforme [web/README.md](web/README.md). O pacote web deve ser atualizado junto com
seu manifesto; não edite o arquivo compactado manualmente. Não altere saves pessoais
nem apague progresso para testar. Use pastas de dados isoladas.

Consulte [organização da equipe](docs/ORGANIZACAO_EQUIPE.md) e
[histórico dos repositórios](docs/HISTORICO_REPOSITORIOS.md).

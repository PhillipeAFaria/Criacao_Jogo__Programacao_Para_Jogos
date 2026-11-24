# Organização da equipe

## Um repositório atual

Trabalhar em `PhillipeAFaria/Criacao_Jogo__Programacao_Para_Jogos`.
`main` é a versão integrada; cada tarefa usa uma branch curta e um PR.
Não é necessário manter uma branch `develop` ou criar outro repositório.

## Responsabilidades

Há sete integrantes, conforme informado pelo responsável do projeto. Apenas
`@PhillipeAFaria` foi encontrado como colaborador deste repositório na auditoria
de 24/11/2026. Os nomes de usuário dos outros seis e suas responsabilidades ainda
precisam ser confirmados. O proprietário do repositório anterior é `@vinicius589`;
isso, por si só, não determina sua função ou seus direitos no repositório atual.

Após a confirmação, o proprietário deve convidar os integrantes por
**Settings → Collaborators**. Em repositório pessoal, colaborador normalmente recebe
acesso de escrita; não compartilhem conta ou senha. Não foram enviados convites.
Para permissões mais detalhadas e equipes, uma organização pode ser considerada
depois; transferir agora não é necessário e requer planejar o endereço do Pages.

Distribuam tarefas por área (combate, interface, arte/animação, áudio, testes,
documentação e integração), sem transformar isso em exclusividade rígida.
Registrem responsáveis nas Issues. Quem implementa solicita revisão de outra pessoa.
Não foi criado CODEOWNERS com nomes ou responsabilidades presumidos.

## Regras da main

- Exigir PR e verificações automáticas aprovadas.
- Bloquear force push e exclusão da `main`.
- Resolver conversas antes de integrar e usar squash para manter o histórico legível.
- Durante a configuração inicial, não exigir aprovação formal de outro usuário:
  só o proprietário está cadastrado. Assim que houver outro colaborador, configurar
  **1 aprovação**, descartando aprovações antigas após novos commits.
- Revisão humana continua sendo o processo esperado; CI não avalia qualidade visual.

Não tornar um teste obrigatório antes de ele existir e passar no GitHub.
Não usar a exigência de revisão como substituto para cadastrar os integrantes.

## Trabalho semanal

Cada Issue deve ter objetivo, responsável, área, prioridade e critério de pronto.
Usem a lista de Issues e PRs abertos como acompanhamento inicial. Se precisarem
de um quadro, usem somente cinco estados: Backlog, Pronto, Em andamento, Em revisão,
Concluído. Evitem manter planilhas e quadros duplicados.

Uma tarefa está concluída quando o PR foi revisado, os testes pertinentes passaram,
a documentação foi atualizada e não há arquivos pessoais. Publicação é uma etapa
separada, registrada pelo workflow do Pages. Build Windows deve ser anexado a uma
Release quando validado; não adicionar EXE/ZIP ao histórico Git.

## Limitação atual da versão web

`web/site/` contém o pacote publicado e `web/build_site.py` verifica seus hashes e
monta o site. Ainda não recompila Python/Pygame para web a partir de `src/`.
Os adaptadores e o processo completo de geração estão na cópia local
`Fabrica_dos_Mortos_Web`. Uma tarefa prioritária é versionar essa cadeia de geração
com instruções reproduzíveis, preservando a versão Windows. Até isso ser feito,
alterar `src/` não atualiza automaticamente o jogo publicado.

## Créditos e licença

Confirmar nomes, usuários e contribuições dos sete integrantes antes de completar
créditos de autoria. O histórico dos repositórios anteriores ajuda, mas contagem de
commits não mede todo o trabalho. A licença MIT existente e seu aviso de copyright
foram preservados. Não atribuir autoria, reescrever commits ou trocar a licença
sem acordo entre os autores.

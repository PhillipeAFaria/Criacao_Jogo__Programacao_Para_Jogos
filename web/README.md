# Fábrica dos Mortos — versão web

[Jogar no navegador](https://phillipeafaria.github.io/Criacao_Jogo__Programacao_Para_Jogos/)

Publicada em 24/11/2026 pelo workflow `fabrica-pages.yml`.
Os [QR Codes](QR_Code/) são estáticos, apontam diretamente para essa página e incluem PNG e SVG, com e sem identificação.

## Atualização

1. Na cópia de desenvolvimento web, execute `ATUALIZAR_WEB.bat` e os testes.
2. Copie os arquivos de `github-pages/web/site/` e `web/manifest.json` preparados para esta pasta. Remova somente os recursos antigos que deixaram de fazer parte do manifesto.
3. Preserve os bytes dos arquivos de `web/site/` conforme `.gitattributes`. Execute `python web/build_site.py` para conferir os hashes.
4. Envie o commit. Em Actions, abra **Publicar Fabrica dos Mortos**, selecione **Run workflow** na branch `main`.
5. Aguarde build e deploy concluírem e teste o endereço acima.

O workflow é manual. Um push sozinho não atualiza o site. Mantenha o repositório e o endereço para continuar usando os mesmos QR Codes.
Não altere a chave/formato do save web sem migração. Os saves pertencem ao navegador e são separados dos saves Windows; limpar os dados do site remove o progresso local.

## Testes e limites

106 testes Python aprovados na preparação; pixels e durações de 2941 quadros conferidos. Chrome desktop local testado; na página pública, Chrome com emulação móvel testou digitação, campanha, salvar/recarregar/continuar, cache, controle de som e orientação. A pausa foi testada por evento de visibilidade simulado. Não houve teste em celular físico nem verificação de áudio por escuta.

Download inicial aproximado: 42,41 MiB, além do runtime externo Pygbag. Os mapas carregam animações sob demanda; total com todos os mapas aproximadamente 163 MiB. Cache depende do espaço e das políticas do navegador. Sem garantia offline. O código e os saves Windows não foram substituídos.

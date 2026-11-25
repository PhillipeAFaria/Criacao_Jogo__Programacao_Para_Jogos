# Fábrica dos Mortos

Jogo de estratégia 2D em Python e Pygame-CE. Posicione tropas em quatro faixas para defender sua base contra 12 ondas de zumbis. A campanha tem três regiões, com oito cartas por região.

**[Jogar no navegador](https://phillipeafaria.github.io/Criacao_Jogo__Programacao_Para_Jogos/)** · [QR Code](web/QR_Code/Fabrica_dos_Mortos_QR_identificado.png)

## Executar no Windows

1. Baixe ou clone este repositório e instale o **Python 3.12 x64** com o Python Launcher (`py`).
2. Na pasta do repositório, execute [PREPARAR_AMBIENTE.bat](PREPARAR_AMBIENTE.bat) uma vez para instalar as dependências. Essa etapa requer internet.
3. Execute [JOGAR.bat](JOGAR.bat).

Use o mouse para escolher cartas e posicionar tropas. Pressione **P** para pausar, **F5** para salvar e **F11** para alternar a tela cheia. Os saves do navegador e do Windows são independentes.

## Encontrar o código

| Onde | O que contém |
| --- | --- |
| [`main.py`](main.py) | Ponto de entrada do jogo |
| [`src/svz/`](src/svz/) | Código do jogo, incluindo menus, campanha e combate |
| [`assets/`](assets/) | Imagens e sons |
| [`tests/`](tests/) e [`tools/`](tools/) | Testes, validação e empacotamento |
| [`docs/`](docs/) e [`web/`](web/) | Documentação e arquivos da versão web |

## Desenvolvimento

- [Guia de desenvolvimento, testes e build](docs/DESENVOLVIMENTO.md)
- [Como contribuir](CONTRIBUTING.md) e [organização da equipe](docs/ORGANIZACAO_EQUIPE.md)
- [Histórico de versões](CHANGELOG.md) e [integração da versão 1.6.0](docs/INTEGRACAO_1.6.0.md)
- [Créditos](CREDITOS.md) e [licença](LICENSE)

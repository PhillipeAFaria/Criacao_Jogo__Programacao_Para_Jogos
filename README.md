# Fábrica dos Mortos

Um **tower defense 2D em tempo real**. Distribua suas tropas em quatro faixas, administre os suprimentos e defenda a base contra ondas de zumbis.

**[Jogar no navegador](https://phillipeafaria.github.io/Criacao_Jogo__Programacao_Para_Jogos/)** · [Executar no Windows](#executar-no-windows) · [Explorar o código](#explorar-o-código)

**Versão 1.6.0 · Alfa da Beta 5** · [Histórico de versões](CHANGELOG.md)

## Executar no Windows

1. Baixe ou clone o repositório e instale o **Python 3.12 x64**.
2. Execute [PREPARAR_AMBIENTE.bat](PREPARAR_AMBIENTE.bat) na raiz do projeto. O script cria o ambiente virtual e instala as dependências pela internet.
3. Execute [JOGAR.bat](JOGAR.bat) para iniciar o jogo.

<details>
<summary>Executar pelo PowerShell</summary>

Abra o PowerShell na raiz do repositório e use o Python Launcher (<code>py</code>):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

</details>

## Como jogar

- **Monte a defesa.** Escolha uma carta, gaste suprimentos para posicionar a tropa e aguarde a recarga antes de usar a carta novamente.
- **Avance pela campanha.** Cada região tem 12 ondas com chefes e subchefes. A campanha passa por Nova York, pelo Egito e pela Cachoeira Contaminada, em Minas Gerais.
- **Continue de onde parou.** O jogo tem salvamento de partidas, perfil local, ranking e loja de consumíveis. Cada versão, web e Windows, mantém seu próprio progresso.

Use o **mouse** para selecionar e posicionar tropas, **P** para pausar, **F5** para salvar e **F11** para alternar a tela cheia na versão Windows. Para abrir a versão web pelo celular, use o [QR Code](web/QR_Code/Fabrica_dos_Mortos_QR_identificado.png).

<img src="assets/interface/menu.png" alt="Arte do menu de Fábrica dos Mortos com três soldados e uma horda de zumbis" width="720">

## Explorar o código

| O que você procura | Onde está |
| --- | --- |
| Inicialização e menus | [main.py](main.py) e [src/svz/app.py](src/svz/app.py) |
| Regras de combate e progressão | [Batalha](src/svz/battle.py), [ondas](src/svz/waves.py) e [regiões e unidades](src/svz/content.py) |
| Imagens e sons | [assets/](assets/) |
| Testes e ferramentas de build | [tests/](tests/) e [tools/](tools/) |
| Versão para navegador | [Código de geração e guia de publicação](web/README.md) |

O código principal fica em [src/svz/](src/svz/) e usa Python com Pygame-CE. A versão Windows usa renderização por software por padrão e oferece OpenGL como opção. As dependências estão em [requirements.txt](requirements.txt).

## Documentação

- [Desenvolvimento, testes e empacotamento](docs/DESENVOLVIMENTO.md)
- [Como contribuir](CONTRIBUTING.md) e [organização da equipe](docs/ORGANIZACAO_EQUIPE.md)
- [Histórico dos repositórios](docs/HISTORICO_REPOSITORIOS.md), [créditos](CREDITOS.md) e [licença MIT](LICENSE)

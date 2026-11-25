# Fábrica dos Mortos

Tower defense 2D em tempo real, desenvolvido em Python com Pygame-CE. Posicione tropas em quatro faixas e defenda sua base contra hordas de zumbis.

**[Jogar no navegador](https://phillipeafaria.github.io/Criacao_Jogo__Programacao_Para_Jogos/)** · [QR Code](web/QR_Code/Fabrica_dos_Mortos_QR_identificado.png) · [Histórico de versões](CHANGELOG.md)

**Versão 1.6.0 · Alfa da Beta 5**

## Início rápido

### Windows

1. Baixe ou clone o repositório e instale o **Python 3.12 x64**.
2. Na raiz do projeto, execute [PREPARAR_AMBIENTE.bat](PREPARAR_AMBIENTE.bat) para criar o ambiente virtual e instalar as dependências. Essa etapa requer internet.
3. Execute [JOGAR.bat](JOGAR.bat).

<details>
<summary>Executar pelo PowerShell</summary>

Na raiz do repositório, com o comando <code>py</code> disponível:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

</details>

## Como funciona

- **Defesa tática.** Escolha cartas de tropas, gaste suprimentos para posicioná-las e gerencie o tempo de recarga.
- **Campanha.** Enfrente 12 ondas com chefes e subchefes em Nova York, no Egito e em Minas Gerais.
- **Progresso.** Retome partidas salvas e use o perfil local para acessar o ranking e a loja de consumíveis. A versão web e a versão Windows guardam o progresso separadamente.

Use o **mouse** para jogar, **P** para pausar, **F5** para salvar e **F11** para alternar a tela cheia.

## Onde encontrar o código

| Caminho | Conteúdo |
| --- | --- |
| [main.py](main.py) | Ponto de entrada |
| [src/svz/](src/svz/) | Código do jogo, incluindo [estado da batalha](src/svz/battle.py), [ondas](src/svz/waves.py) e [conteúdo das regiões](src/svz/content.py) |
| [assets/](assets/) | Imagens e sons |
| [tests/](tests/) e [tools/](tools/) | Testes, validação e empacotamento |
| [web/](web/) | Geração da versão para navegador e publicação no GitHub Pages |

O Pygame-CE cuida da janela, dos controles e do áudio. No Windows, a renderização por software é padrão e o OpenGL é opcional. As dependências estão em [requirements.txt](requirements.txt).

## Documentação

- [Desenvolvimento, testes e build](docs/DESENVOLVIMENTO.md)
- [Como contribuir](CONTRIBUTING.md) e [organização da equipe](docs/ORGANIZACAO_EQUIPE.md)
- [Histórico dos repositórios](docs/HISTORICO_REPOSITORIOS.md), [créditos](CREDITOS.md) e [licença MIT](LICENSE)

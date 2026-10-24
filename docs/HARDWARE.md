# Perfil para GPUs de 2005–2019

RoseShell usa Qt Widgets com pintura raster e Openbox, sem iniciar compositor,
desfoque, transparência de janelas ou animações obrigatórias. O perfil
Econômico é padrão: wallpaper pré-renderizado em cache por monitor, leitura
com tamanho de destino, escalonamento rápido e consultas de status a cada
10 segundos. Equilibrado usa escalonamento suave e consultas de 5 segundos.
Nada força renderização por software de jogos ou altera os drivers do host.

Isso reduz o trabalho do shell; não garante aceleração 3D, vídeo ou suporte
de driver em todas as placas de um período. Não instalar automaticamente
drivers proprietários antigos nem misturar repositórios de outras versões.

## Testes físicos pendentes

| Família de teste | Exemplos informados | Verificar |
| --- | --- | --- |
| ATI pré-GCN | X1600 XT; Radeon 8500 (anterior a 2005) | radeon, firmware, saída e resolução, 2D |
| NVIDIA antiga | 6800 Ultra (anterior a 2005), 9600 GT, GTX 275 | nouveau, modos de vídeo, estabilidade |
| NVIDIA Fermi | GTS 450, GTX 550 Ti | driver disponível no Debian usado, 2D e 3D separadamente |
| NVIDIA Kepler/variantes | GT 730, depende da identificação PCI | confirmar chip exato e suporte |
| NVIDIA Maxwell/Pascal | 750 Ti, GTX 970, 1050 Ti | driver compatível, dois monitores e jogos |
| Intel | integrada do i3, modelo pendente | identificar geração e driver |

Registrar `lspci -nnk`, `xrandr`, RAM em repouso, movimentação de janelas,
wallpaper, arraste de ícones, captura, troca de resolução e teste separado
do SuperTux. Não foi feita validação física dessas GPUs nesta VM.

## Fontes técnicas

- [Renderização Qt Widgets](https://doc.qt.io/qt-6/topics-graphics.html)
- [Vídeo no Debian](https://wiki.debian.org/GraphicsCard)
- [NVIDIA no Debian](https://wiki.debian.org/NvidiaGraphicsDrivers)
- [SuperTux do Debian 13](https://packages.debian.org/trixie/supertux)

SuperTux integra `shell/packages-default.txt`. O jogo tem requisitos próprios;
fluidez do shell não prova desempenho do jogo.

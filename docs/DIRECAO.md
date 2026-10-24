# RoseShell — direção do projeto

## Estado atual

Atalhos opcionais móveis implementados com tamanho 24–96 px, posições
normalizadas por monitor, visibilidade, organização e remoção sem apagar app.
Testes de arraste/persistência/cache passaram. SuperTux instalado na VM e
incluído no manifesto de pacotes padrão e no instalador de base/sessão.
Coleção com 21 arquivos: sete desenhos em 5:4, 16:9 e 4:3. Estúdio FM
corrigido para sala menor, personagem sentada diretamente diante da mesa.
Perfil Econômico padrão reduz redesenho/cache e frequência de sondagem.
Validação de layout repetida com atalhos em 640×480 (100/125%), 5:4, Full HD
e 4K, sem elementos fora da tela. Fechar preferências preserva o shell ativo.

Controles: indicadores Linux reais de volume, enlace de rede, USB, discos e
idioma; data e hora. Preferências funcionais (tema/lado/monitor/escala), menu
de contexto, colagem de arquivos/imagens sem sobrescrever e clipboard em
memória. Ferramenta de captura por monitor e atalho Print verificados no X11.
Bônus 07-estudio-fm-1979 com cartucheiras, mesa analógica, rolo e transmissores.
Sete wallpapers no total, formatos PNG/JPG/WebP validados. Layouts testados
em 640×480 a 100% e 125%, 1280×1024, Full HD e 4K sem ultrapassar limites.
Escala exige nova sessão. Rede/áudio dependem dos serviços disponíveis; USB
e discos precisam estar visíveis ao Debian. Não há validação física de Wi-Fi
nem de hotplug de USB; diagnóstico de dispositivos não instala drivers.

Atualização visual: ícones ilustrados originais com pigmentos rosa, sálvia,
ocre e papel creme; seis wallpapers originais raster em assets/wallpapers.
Biblioteca de aplicativos com busca, descoberta XDG e abertura via gio.
Galeria com miniaturas e rotação opcional de 1–60 minutos. Testes no Debian:
36 aplicativos descobertos, busca e abertura de FeatherPad verificadas;
catálogo/precedência XDG, ícones, seleção e rotação validados por verify.py.
Somente os ícones do painel e os de arquivos/editor no lançador foram
substituídos; a identidade de ícones dos demais aplicativos é trabalho futuro.

Sessão X11 registrada no Debian da VM. Painel e desktop próprios executados
em Xephyr com Openbox e tema RoseShell. Inicialização e alternância de tema
e lado verificadas em teste offscreen; desktop e abertura de terminal
verificados visualmente. Login direto na sessão e teste com dois monitores
ainda pendentes. O tema claro de decorações e aplicativos está pendente.

## Identidade

- Preto e grafite; tema claro opcional.
- Cantos retos, contraste legível, sem desfoque ou animações obrigatórias.
- Painel à esquerda ou à direita.
- Ícones próprios com contornos expressivos: clipe para arquivos;
  folha com lápis para editor.
- Referências visuais: animação japonesa de 1980–2000 e Cartoon Network
  dos anos 1990. Wallpapers distribuídos devem ter licença compatível
  ou ser originais; anexos do usuário são referências, não assets incluídos.
- Preservar proporção dos wallpapers; permitir ajuste por monitor.

## Alvos de teste

Debian amd64, VirtualBox no Windows 11. Máquinas físicas com 4–16 GB.
Ryzen 5 5500, Core 2 Quad Q8300 (4 GB DDR2-800), Athlon II X2 250,
Core 2 Duo E7500, i7 940, i7 4770 e Xeon informado como 1220 v2.
Monitores 5:4 e 16:9, inclusive combinações com dois monitores.
GPUs ATI/AMD, Intel e NVIDIA antigas e recentes: identificação não implica
aceleração funcional. Validar por modelo e driver em hardware real.

## Etapas

1. Painel próprio: lançadores, relógio, temas e posicionamento (protótipo).
2. Validar na VM e implementar integração X11, reserva de espaço e lista
   de janelas. Medir consumo em repouso.
3. Menu de aplicativos, área de trabalho e wallpapers próprios.
4. Sessão própria com gerenciador de janelas existente; manter sessão de
   desenvolvimento disponível para recuperação.
5. Configurações, ícones e aplicativos próprios.
6. Empacotamento Debian e ISO reproduzível.
7. Avaliar desenvolvimento de gerenciador de janelas próprio.

Não impor instruções de CPU específicas do Ryzen aos componentes.

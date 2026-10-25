# Pacotes e instalação AllyOS 0.3.3

## Perfis

`shell/packages-minimal.txt` define os utilitários da sessão essencial.
`allyos-desktop` depende deles, Qt/Python, X11, Openbox, rede, áudio e login.
Thunar cuida de arquivos; XFCE Task Manager é a alternativa leve para processos.
SuperTux está em ambos os perfis.

`allyos-apps` acrescenta o pacote recomendado: Firefox ESR, Wine de 64 e 32 bits,
TuxManager, Fastfetch, Neofetch original, Hardinfo2, NVTOP, lm-sensors,
GSmartControl, ferramentas SMART/NVMe/PCI/USB e teste de controles.
Firefox ESR recebe a versão disponível nos repositórios Debian/security durante
a construção. Atualizações posteriores dependem de atualizar os pacotes do sistema.
Wine não garante compatibilidade com todos os programas Windows; suporte a
a integração multiarch de 32 bits está incluída na nova receita e em teste.

O perfil mínimo remove uma lista explícita de aplicativos do sistema copiado.
Simula a remoção de dependências não usadas e recusa planos que removam sessão, kernel, firmware ou bootloader; somente então aplica a limpeza. Ainda é
necessário medir a diferença de espaço após instalar cada perfil.

## Instalador

Calamares e configurações oficiais Debian 13.0.13, com overlay AllyOS.
O arquivo original está em `iso/vendor`, com licença dentro do arquivo e
SHA256 verificado por `iso/installer.py`. Não é um particionador escrito do zero.

O fluxo oferece idioma, teclado, disco, usuário, pacote completo/essencial,
resumo e confirmação. Particionamento automático usa ext4 e swap pequeno,
com partição EFI quando necessária; modo manual permanece habilitado.
Nenhum disco é escolhido ou apagado automaticamente ao abrir o instalador.
A cópia do sistema, GRUB, initramfs e fontes Debian seguem as tarefas Debian.

**Estado:** configuração preparada; os dois perfis e o novo instalador ainda
precisam de instalação real. Os testes da primeira ISO não validam este fluxo.

## Áudio, controles e vídeo

ALSA + PipeWire + WirePlumber; Pavucontrol fornece mixer, perfis e áudio por app.
RoseShell oferece escolha de saída e entrada, volume/mudo e relatório ALSA/USB.
O relatório mostra IDs e drivers efetivamente carregados.

Armer Agent ONE/G2, Focusrite, Behringer, SSL2+, M-Audio e Teyun precisam de
identificação USB e testes por revisão. A presença da marca numa lista não
significa suporte confirmado. Interfaces compatíveis com a classe USB Audio
podem funcionar com snd_usb_audio; recursos proprietários dependem do modelo.

Controles usam drivers do kernel e joystick/jstest-gtk. Validar USB, Bluetooth,
botões, eixos e vibração separadamente. Drivers externos de controles não são
instalados automaticamente.

As GPUs seguem os drivers disponíveis no Debian 13. Não instalar blobs NVIDIA
antigos sem compatibilidade com o kernel. A GTX 970 física ainda não foi testada:
a VM atual identifica VMware SVGA II / vmwgfx, sem exposição da GTX 970.

O som original de entrada tem 72.808 bytes, com controle nas preferências.
É reproduzido após iniciar a sessão de usuário, quando o servidor de áudio
responder; não é áudio do firmware ou do carregador de boot.

A compilação local pode incluir o som enviado em iso/local-assets; ele fica fora do Git e das fontes públicas. Sem esse arquivo, usa o som original RoseShell. O instalador usa apenas o logotipo do AllyOS, sem retrato na recepção.

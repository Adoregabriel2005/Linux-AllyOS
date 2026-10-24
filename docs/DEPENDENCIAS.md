# Dependências e limites da validação

RoseShell usa Python 3 e **PySide6-Essentials (Qt Widgets)** para painel,
desktop, configurações, biblioteca e captura; **X11 e Openbox** gerenciam
as janelas. Não há compositor obrigatório nem uso obrigatório de OpenGL
pela interface. A lista de pacotes é `shell/packages-default.txt`.

| Componente | Uso |
| --- | --- |
| wmctrl | Lista, ativação, maximização e fechamento de janelas via EWMH |
| Thunar | Gerenciador de arquivos padrão |
| TuxManager | Gerenciador padrão de processos e recursos; Ctrl+Shift+Esc |
| xfce4-taskmanager | Alternativa caso TuxManager esteja ausente |
| mate-polkit + serviço polkit do Debian | Janela de autenticação para ações que usam polkit |
| network-manager-gnome | Editor de conexões de rede |
| pulseaudio-utils | Controle de volume por pactl; wpctl também é reconhecido se disponível |
| pciutils, iproute2, lsblk/util-linux | Diagnóstico de dispositivos e rede |
| libglib2.0-bin | Lançamento dos arquivos .desktop por gio |
| libxcb-cursor0, bibliotecas Qt/X11 transitivas | Backend gráfico xcb |
| setxkbmap/x11-xkb-utils | Troca de teclado BR/US |
| SuperTux | Jogo incluído por padrão |

Fastfetch, Hardinfo2, sensores, GPU e diagnósticos de discos são aplicativos
padrão adicionais, descritos em `docs/DIAGNOSTICOS.md`. Não são requisitos
para desenhar a interface. TuxManager usa seu próprio Qt6 do Debian;
RoseShell usa Qt/PySide6 no ambiente Python. Os componentes de terceiros
mantêm suas licenças. O código da RoseShell é GPL-3.0-or-later, autoria gorigamia.

Xephyr e libXtst são usados nos testes, não são parte obrigatória da sessão.
LXQt continua instalado como recuperação durante a validação.

## Autenticação

A sessão inicia o agente MATE Polkit. As senhas ficam a cargo do agente
e do serviço polkit; o código da RoseShell não recebe essas senhas.
A prévia com `ROSESHELL_NESTED=1` não registra outro agente sobre o LXQt.
Aplicativos que usam `sudo` em um terminal continuam pedindo senha naquele
terminal; não se deve interceptar isso com uma caixa genérica da interface.
Ainda é necessário validar o diálogo do agente em um login RoseShell real.

## GPU e aplicativos de terceiros

Em 23/10/2026, `lspci -nnk` da VM identificou **VMware SVGA II [15ad:0405]**,
driver **vmwgfx**, correspondente ao adaptador VMSVGA configurado no VirtualBox.
A GTX 970 do host não está sendo exposta diretamente ao Debian dessa VM.

O perfil econômico reduz o trabalho do shell (desenho raster, imagem em
cache e consultas assíncronas). Não força variáveis de software rendering
em todos os aplicativos e não instala drivers NVIDIA por suposição.
Steam/Proton e aceleração 3D precisam de testes separados em hardware
real; a execução do shell na VM não comprova desempenho desses aplicativos.

## Estabilidade

Fechar a última janela comum não encerra mais a aplicação Qt do shell.
Em falha inesperada da UI, o supervisor faz até duas novas tentativas;
uma saída normal encerra a sessão. Falhas persistentes retornam ao login.
Isso não substitui diagnóstico nem garante ausência de bugs.

`verify_tasks.py`, com Openbox em display isolado, verifica lista de janelas,
ativação, Alt+Tab e fechamento sem encerrar o desktop. Os testes de resolução
também verificam limites e sobreposição dos atalhos. Testes físicos de GPUs,
autenticação em login real e uso prolongado permanecem necessários antes
de remover o ambiente de recuperação.

Referências: [Openbox Actions](https://openbox.org/help/Actions),
[Thunar no Debian](https://packages.debian.org/trixie/thunar),
[MATE Polkit no Debian](https://packages.debian.org/trixie/mate-polkit).

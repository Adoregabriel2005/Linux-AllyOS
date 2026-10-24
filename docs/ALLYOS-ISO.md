# AllyOS 0.01 — desenvolvimento

**AllyOS** é a distribuição; **RoseShell** é sua interface. A base continua
sendo **Debian GNU/Linux 13 (trixie)**, com kernel, pacotes e repositórios
Debian. Não é uma imagem oficial do projeto Debian.

A versão está em `iso/release.json`. O builder a usa nos pacotes, na
identidade do sistema, no login e no nome da ISO. Mudar esse arquivo é o
início de uma nova versão; exige reconstrução e novos testes.

## Identidade do sistema

O pacote `allyos-branding` instala:

```ini
NAME="AllyOS"
PRETTY_NAME="AllyOS 0.01 (Debian 13)"
ID=allyos
ID_LIKE=debian
VERSION_ID="0.01"
VERSION_CODENAME=trixie
DEBIAN_VERSION_ID=13
```

O arquivo original `/usr/lib/os-release` é preservado por `dpkg-divert`;
atualizações do pacote Debian `base-files` não devem apagar a identidade
AllyOS. A remoção do branding restaura a identidade Debian. O arquivo
`/etc/debian_version` permanece sob responsabilidade do Debian.

Fastfetch e Neofetch leem essa identidade e também exibem uma linha
**Base: Debian GNU/Linux 13 (trixie)**. O Fastfetch vem do Debian.
Como Neofetch não está no repositório trixie, o builder empacota o script
original upstream 7.1.0, com checksum fixado e licença MIT preservada.
Não é um comando falso redirecionado ao Fastfetch.

## Login e sessão

O tema SDDM AllyOS usa o wallpaper original, painel grafite, cantos retos,
detalhes rosa, seleção de sessão, usuário/senha, reinício e desligamento.
O processamento de senha é feito pelo SDDM/PAM. Não há armazenamento de senha
em código, configuração ou logs da RoseShell. O greeter usa desenho por
software para reduzir exigência gráfica.

As prévias visuais usam `PreviewMode=true`, mostram um aviso e desativam
usuário, senha e entrada. Elas não autenticam contas. A imagem instalada
usa `PreviewMode=false` e o SDDM real. Não confundir a prévia em uma janela
com a tela de login da VM.

Em uma imagem nova, RoseShell é a sessão escolhida inicialmente. Não são
instalados os desktops completos LXQt/GNOME/KDE. Openbox continua necessário
como gerenciador de janelas da RoseShell. O protótipo já instalado na VM
permanece separado desta receita; não é copiado para a ISO.

## Construção em Debian 13 amd64

Requer uma máquina Linux ou VM Debian, conexão de rede e espaço livre;
reserve aproximadamente 20 GB para trabalho, além da ISO e dos fontes.
O build usa root dentro do ambiente Linux para criar o chroot, não o Windows.

```sh
sudo apt-get install live-build python3 xorriso squashfs-tools
sh iso/build.sh
```

O resultado esperado é:

```text
~/allyos-build/AllyOS-0.01-dev-amd64.iso
~/allyos-build/AllyOS-0.01-dev-amd64.iso.sha256
```

`ALLYOS_BUILD_DIR` permite escolher outra pasta de trabalho dedicada.
Não usar uma pasta com dados pessoais. Não executar `lb clean --purge`
fora da pasta de build. Para reconstruir depois de alterar a configuração,
limpe o build conforme o manual live-build e repita o processo.

O fluxo é versionado e repetível. Ainda não é uma promessa de ISO idêntica
byte a byte: os repositórios trixie recebem atualizações. O live-build gera
manifestos, e um inventário é gravado em
`/usr/share/allyos/package-versions.txt`. Uma release reproduzível requer
também fixar snapshot APT, versões e timestamps do build.

## Conteúdo e instalação

A receita gera ISO híbrida com boot BIOS/UEFI, sessão Live e instalador
Debian Live. A instalação deve copiar a imagem com RoseShell e solicitar
normalmente disco, usuário e senha. Não há particionamento destrutivo
automático nem credenciais do desenvolvedor embutidas.

Inclui SuperTux, Fastfetch, TuxManager e o conjunto de diagnóstico da
RoseShell. Fontes e licenças próprios e os fontes correspondentes do
TuxManager/Neofetch acompanham a mídia em `sources/`.

Antes de publicação, cumprir também as obrigações de código-fonte e avisos
dos pacotes Debian efetivamente redistribuídos. O live-build suporta
imagens de fontes separadas; uma ISO binária de teste não é o pacote completo
de distribuição pública. Não são adicionados drivers NVIDIA proprietários
por suposição, chaves pessoais, histórico, senhas, contas ou discos da VM.

## Validação necessária

1. Preparar os pacotes locais e verificar seu conteúdo e dependências.
2. Renderizar o greeter em modo de teste, nos dois idiomas e em resolução baixa.
3. Construir a ISO e conferir seu SHA256 e seus manifestos.
4. Iniciar uma VM vazia por BIOS e por UEFI; testar o modo Live.
5. Instalar em um disco virtual descartável; remover a ISO e reiniciar.
6. Confirmar login, RoseShell padrão, autoria, versão em fetches, rede,
   áudio, arquivos, Alt+Tab, captura e aplicativos.
7. Testar separadamente máquinas físicas e GPUs antigas.

Preparar arquivos não confirma que a ISO foi construída nem que o
instalador funciona. Esses resultados devem ser registrados após testes.
Não remover o desktop de recuperação da VM de desenvolvimento nessa etapa.

Fontes: [Debian Live Manual](https://live-team.pages.debian.net/live-manual/html/live-manual.en.html),
[os-release](https://www.freedesktop.org/software/systemd/man/os-release.html),
[SDDM theming](https://github.com/sddm/sddm/blob/v0.21.0/docs/THEMING.md),
[Neofetch original](https://github.com/dylanaraps/neofetch/tree/7.1.0).

# AllyOS 0.01 — registro de validação

## Construção em 23/10/2026

A primeira construção parou no hook final: o live-build materializou
`/etc/os-release` como arquivo Debian, diferente do arquivo AllyOS em
`/usr/lib/os-release`. A checagem interrompeu a geração corretamente.
O hook agora verifica o identificador canônico e restaura o vínculo relativo
`/etc/os-release -> ../usr/lib/os-release`, mantendo a base Debian explícita.

A VM foi desligada antes de concluir a limpeza do build. A retomada mostrou
marcadores incompatíveis com o chroot restaurado. A recuperação usa
`lb clean --all` somente na pasta absoluta de build verificada, preservando
configuração, fontes e cache de downloads, e reconstrói as etapas.

A preparação estática e `iso/verify.py` passaram depois da correção.
Isso verifica o conteúdo preparado; não confirma boot nem instalação.

## Retomada em 24/10/2026

O hook final e o inventário de pacotes passaram na construção anterior.
O desligamento ocorreu durante a preparação do instalador Debian.
O live-build preserva a raiz Live em `chroot/chroot` enquanto trabalha
numa raiz temporária em `chroot`; isso foi conferido antes da recuperação.
`iso/continue-installer.sh` continua pelas etapas nativas `installer`,
`binary` e `source`, sem restaurar o bootstrap sobre o sistema pronto.
O script verifica a identidade da raiz preservada, recusa outro construtor
ativo e preserva caches de download que colidem após uma interrupção.

A seleção de `x-session-manager` também é fixada em RoseShell, pois o
tema Breeze recomendado por SDDM trouxe Plasma como sessão adicional.
O modo Live recebe `LIVE_SESSION="roseshell.desktop"` explicitamente.
Esses ajustes ainda precisam ser confirmados no boot da ISO.

## Primeira ISO construída e boot Live

Arquivo: `iso/output/AllyOS-0.01-dev-amd64.iso`, 3.670.622.208 bytes.
SHA256 conferido entre builder Debian e cópia Windows:
`6bd334c99a3380ec694460273be629437959cbf85c48ad70a0e974a6db0e6a7c`.
O live-build concluiu as etapas de instalador e imagem binária. O helper de
recuperação, editado durante sua execução, apresentou erro de sintaxe após
exportar a ISO; a sintaxe do arquivo atual passou em `sh -n`. Não editar
scripts em execução em retomadas futuras. Hash e testes funcionais são
avaliados independentemente desse helper.

Boot BIOS executado na VM separada AllyOS-ISO-Test. A sessão iniciou via
SDDM com RoseShell e Openbox. A primeira imagem gráfica ficou preta até
alternar VT3/VT2; isso permanece pendente de diagnóstico e correção.
O roteiro `iso/check-live.sh` passou: identidade, PySide6, aplicativos,
21 variantes de wallpapers, processos, rede/DNS, Fastfetch e Neofetch.
Nenhum serviço falho foi listado; uso observado de RAM: cerca de 642 MiB
numa VM de 4 GB. Isso não representa medição em hardware físico.

A mídia monta em `/run/live/medium`, não `/lib/live/mount/medium`.
Os fontes próprios e de terceiros foram encontrados em `sources/`.
A conferência integral `dpkg --verify` ainda não concluiu; a VM de
construção foi desligada durante a auditoria. Não declarar integridade
completa nem estabilidade geral com base apenas nos testes Live.

### Falha encontrada na instalação a partir do Live

O `debian-installer-launcher` recusa iniciar: kernel Live
`6.12.113+deb13-amd64` diferente do instalador
`6.12.107+deb13-amd64`. A instalação pelo menu de boot foi iniciada
separadamente com o kernel próprio do instalador. O fluxo iniciado do
desktop precisa de correção; não ocultar nem ignorar essa verificação.
O disco de teste foi conferido vazio: VBOX HARDDISK de 24 GB, `/dev/sda`.

### Instalação BIOS em disco vazio

O instalador gráfico pelo boot parou durante a inicialização do
particionador e deixou de responder às tentativas de console. Foi reiniciado
antes de confirmar qualquer gravação. A mesma ISO em modo texto passou
pelo particionador, formatou somente o disco de testes e copiou a imagem.
Esquema: ext4 em `/dev/sda1` e swap em `/dev/sda5`.

A instalação em modo texto informou **Instalação completada**. O espelho
`deb.debian.org` foi configurado e o GRUB instalado em `/dev/sda`.
Conta descartável: `tester`; hostname `allyos-test`; fuso São Paulo.
Nenhuma conta nem senha dessa instalação integra a ISO.
A mídia foi removida para validar o primeiro boot a partir do disco.
Essa conclusão do instalador ainda não confirma o login do sistema instalado.

Pendências observadas até aqui: primeiro quadro gráfico preto no Live,
launcher Live incompatível com o kernel do instalador, parada do instalador
gráfico no particionador, identificação do menu da mídia ainda genérica
Debian e aparência dos aplicativos Qt externos ainda parcialmente clara.

## Testes ainda necessários

- Construção concluída e hash SHA256 conferido após exportação.
- Boot BIOS e UEFI na VM AllyOS-ISO-Test.
- Desktop Live e verificações de `iso/check-live.sh`.
- Instalação no disco vazio de testes, reinício sem ISO e login real.
- Rede, áudio, autenticação administrativa, aplicativos e atalhos.
- Hardware físico e placas de vídeo antigas.

O desktop LXQt da VM de desenvolvimento permanece como recuperação.

## Continuação em 24/10/2026 — revisão 0.2.1

O boot em disco BIOS da primeira ISO e o login real na RoseShell foram
confirmados. A auditoria integral da instalação descartável encontrou somente
`/var/lib/openbox` ausente; após criar esse diretório vazio, a repetição de
`dpkg --verify` passou, permitindo apenas o overlay Main.qml já conferido com
os fontes. Evidência: `iso/output/installed-integrity/image-integrity.json`.
A ISO 0.01 original não foi alterada por esse reparo na VM.

A correção `InputMethod=` removeu o teclado virtual do SDDM em teste real.
O login também foi confirmado visualmente em português após definir Language.
Capturas: `login-without-osk.png` e `login-ptbr.png`, em `iso/output/`.

Os testes da revisão nova passaram para catálogo PT/EN, ciclo de vida,
seleção de saída/entrada sem alterações durante consulta, transparência do
ícone ilustrado Wine, oito wallpapers em três proporções e limites X11:
640x480, 640x480 com 125% (512x384 lógicos), 1280x1024, 1920x1080 e 3840x2160.
A última rodada inclui som, rede, dispositivos, Sobre e diagnósticos.
Evidência: `new-x11-resolution-suite.json` e `painted-wine-check.json`.

O Calamares real carregou branding e todos os módulos configurados, incluindo
packagechooser e contextualprocess@allyos-profile, sem iniciar instalação.
Foram corrigidos slideshow obrigatório e identificação completa da instância.
Evidência: `installer-native-probe.json` e `installer-probe-final/calamares-probe.log`.
Isso ainda não comprova cópia do sistema, GRUB ou aplicação do perfil mínimo.

A construção 0.2.1 foi iniciada em fonte congelado e disco virtual separado
80 GB na VM AllyOS-ISO-Test. Log: `iso/output/build-0.2.1.log`.
Os pacotes incluem Firefox ESR do repositório de segurança e Wine 64 bits.
O SDDM usa o tema próprio como provider; não foi solicitado Plasma.

Duas VMs vazias estão preparadas, ainda sem a nova ISO: AllyOS-Install-Full
(BIOS) e AllyOS-Install-Minimal (UEFI64), ambas 4 GB RAM e disco 32 GB.
Ainda é necessário construir/exportar/conferir hash, bootar a nova ISO,
instalar os dois perfis, reiniciar sem mídia e validar aplicativos,
áudio, processos, autenticação e fechamento de janelas. Os drivers físicos,
interfaces USB de áudio, controles e GPUs antigas continuam pendentes.
A VM Debian-Interface-Dev e seu LXQt foram preservados.

# Correção do teste de instalação — 0.3.4

A ISO 0.3.3 foi construída e iniciou a RoseShell pelo modo Live. A instalação
BIOS no disco virtual vazio copiou o sistema e instalou o GRUB, mas falhou
na limpeza dos pacotes Live: APT não encontrou `live-task-localisation` e
`live-task-recommended`. Essa imagem não foi publicada em Releases.

A configuração do Calamares agora remove somente os componentes Live e do
instalador efetivamente incluídos. A auditoria do sistema de arquivos da ISO
confere cada nome dessa lista contra o estado instalado do dpkg.

No VirtualBox com VMSVGA, o Xorg modesetting usa explicitamente renderização
sem aceleração e cursor por software. A regra depende da identificação do
VirtualBox e do dispositivo PCI virtual; não altera GPUs físicas.

A nova construção usa uma pasta limpa e aproveita somente downloads de
pacotes Debian. O teste da instalação e a reinicialização da 0.3.4 devem
ser concluídos antes da publicação da ISO.

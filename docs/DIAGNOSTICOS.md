# Diagnóstico incluído por padrão

Abra **Configurações → Sistema → Diagnóstico de hardware**, ou a mesma
opção no menu da RoseShell.

| Ferramenta | Finalidade |
| --- | --- |
| Fastfetch | Resumo do sistema no terminal |
| TuxManager | Processos, CPU, RAM, GPU e serviços; padrão de Ctrl+Shift+Esc |
| Hardinfo2 | Informações de CPU, GPU, placa-mãe, memória e sistema; alternativa nativa para consultar dados do tipo CPU-Z/GPU-Z |
| lm-sensors | Temperaturas, tensões e ventoinhas expostas pelo kernel |
| NVTOP | Uso de GPU quando suportado pelo hardware/driver |
| GSmartControl e smartmontools | Consulta de saúde SMART de armazenamento; pode solicitar autorização pelo sistema |
| nvme-cli | Diagnóstico de unidades NVMe |
| inxi, lshw, dmidecode | Inventário de hardware e firmware |
| mesa-utils e vulkan-tools | Informações de OpenGL/Vulkan |
| pciutils, usbutils, util-linux | Dispositivos PCI/USB e discos |

Não há testes destrutivos, estresse, atualização de firmware nem execução
automática de `sensors-detect`. Em uma VM, sensores, SMART e a GPU física
podem não estar expostos. A interface informa ausência de sensores;
não inventa valores nem apresenta zero como temperatura válida.

O TuxManager instalado é o pacote oficial **1.0.8-1~deb13 amd64**, com
SHA256 verificado. Arquivo, procedência e fonte estão em `shell/vendor/`.
Atualizações desse pacote externo são explícitas, sem repositório extra.
O xfce4-taskmanager permanece como alternativa se o TuxManager estiver ausente.

## Idiomas e autoria

Selecione **Português (Brasil)** ou **English** em Configurações → Sistema
ou no indicador de idioma. A escolha da interface é independente do teclado
BR/US e entra em vigor ao iniciar novamente a sessão. O catálogo usa os nomes
traduzidos dos arquivos `.desktop` quando existem. A configuração de idioma
da RoseShell não reconfigura os locales do Debian inteiro.

**Sobre a RoseShell** informa a autoria **gorigamia**, as dependências,
o crédito de terceiros e a licença completa GPLv3, consultável offline.
Veja `COPYRIGHT.md` e `LICENSE` para o escopo da licença.

Fontes: [TuxManager](https://github.com/benapetr/TuxManager),
[Hardinfo2 no Debian](https://packages.debian.org/trixie/hardinfo2),
[Fastfetch no Debian](https://sources.debian.org/src/fastfetch/).

## Validação de 23/10/2026

Instalação dos pacotes confirmada na VM Debian 13 amd64. TuxManager
abriu na sessão de teste; Fastfetch executou pelo lançador e permaneceu
visível até Enter. Testes de idioma PT-BR/English, catálogo XDG, créditos,
licença offline e dez combinações de idioma/resolução passaram, incluindo
640×480 a 125% e 4K. A janela dos relatórios foi centralizada e limitada
a 85% × 75% do monitor, com geometria real conferida na prévia.
Sensores físicos, SMART real e métricas da GTX 970 seguem dependentes
de testes fora da VM; autenticação em login RoseShell completo continua pendente.

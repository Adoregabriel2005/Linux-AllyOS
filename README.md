# AllyOS / RoseShell

**AllyOS 0.3.3 (em validação)** é a distribuição derivada do Debian 13;
**RoseShell** é a interface. A receita da ISO, o tema de login SDDM e a
identidade com versão estão em `iso/`. Consulte `docs/ALLYOS-ISO.md`.
A primeira ISO 0.01 foi instalada em disco BIOS e iniciou a RoseShell.
A revisão 0.3.3 acrescenta Calamares e perfis de aplicativos; sua instalação
precisa de validação própria. Veja `docs/VALIDACAO-ISO.md`,
`docs/APPS-E-INSTALADOR.md` e `docs/VERSOES.md`.

Ambiente gráfico próprio sobre Debian, em desenvolvimento. Python e Qt 6
Widgets, sem navegador incorporado. Openbox fornece o gerenciamento de
janelas nesta primeira versão; RoseShell fornece painel e desktop.

## Funcionalidades

- Painel angular grafite ou claro, à esquerda ou direita; ícones originais.
- Desktop por monitor; PNG, JPG, WebP e BMP, inteiros, centralizados,
  preenchendo ou esticados. Importação de fotos próprias com validação.
- Reserva EWMH de espaço na borda externa para janelas maximizadas.
- Sessão RoseShell própria no login, sem iniciar o painel/desktop LXQt.
- Tema Openbox próprio, bordas finas, sem compositor obrigatório.
- Biblioteca de aplicativos instalados com busca (primeiro botão do painel).
- Oito wallpapers originais (incluindo estúdio FM e guitarra âmbar) com miniaturas; imagem fixa ou rotação em
  intervalos de 1, 5, 15, 30 ou 60 minutos, nas preferências do painel.
- Ícones ilustrados próprios para painel, arquivos e editor. Demais apps
  conservam seus ícones de origem quando disponíveis.
- Indicadores reais de rede, USB e discos; volume/mudo via wpctl ou pactl,
  gerenciador de dispositivos com USB, discos e PCI/drivers.
- Idioma do sistema, troca de teclado BR/US, relógio e data.
- Captura por monitor com Print, botão no painel, salvar arquivo e copiar.
- Menu de botão direito com personalização, configurações, copiar caminho
  e colar arquivos/imagens na pasta da área de trabalho. Arquivos existentes
  não são sobrescritos. Pastas não são copiadas por esse menu nesta versão.
- Preferências de tema, lado, monitor e escala 100%/125% (requer nova sessão).
- Clipboard de texto, URLs e imagens mantido em memória enquanto a sessão roda.
- Atalhos opcionais de apps no desktop: adicionar pela biblioteca, arrastar,
  mover com setas, salvar posição por monitor, tamanhos de 24 a 96 px,
  ocultar/mostrar, organizar, remover e escolher outro monitor pelo menu.
- Oito wallpapers em três proporções: 24 versões em `shell/assets/wallpapers/variants`.
  Seleção automática pelo monitor ou manual (5:4, 16:9, 4:3).
- Perfil Econômico padrão: pintura raster, cache de wallpaper e polling
  reduzido. Perfil Equilibrado disponível nas preferências.
- SuperTux faz parte dos pacotes padrão e já foi instalado na VM. No perfil
  Econômico o lançador usa seu renderizador SDL.

## Instalar no Debian

Copie `shell/` para `~/interface-dev` e abra um terminal nessa pasta:

```sh
sh install-base.sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
sh install-session.sh
```

Saia da sessão atual e selecione **RoseShell** no seletor do login.
LXQt permanece instalado para recuperação. O instalador registra a sessão
em `/usr/share/xsessions/roseshell.desktop`; não remove outros ambientes.
Não mova a pasta instalada: o lançador aponta para seu caminho absoluto.

Para executar apenas o painel na sessão atual: `.venv/bin/python main.py`.

## Limitações desta versão

Ainda faltam suporte a bandejas de terceiros e bloqueio de tela.
A lista de janelas e Alt+Tab estão implementados; o agente de autenticação
está integrado, mas requer validação em um login completo. Aplicativos externos mantêm seus temas;
o tema claro atual aplica-se ao painel e desktop, não às decorações Openbox.
Wallpaper e modo de ajuste são globais, renderizados em cada monitor;
escolha individual por monitor ainda está planejada. Reserva de espaço em
bordas internas entre monitores não é suportada nesta versão.

Rede mostra enlace/interface e IP. Edição de conexões usa o programa
`nm-connection-editor` quando instalado e NetworkManager disponível.
Indicadores USB/discos veem dispositivos apresentados ao Linux: no VirtualBox,
um dispositivo do Windows precisa ser repassado à VM para aparecer.
O gerenciador de dispositivos é informativo, não instala drivers.
Áudio depende de uma saída disponível no PipeWire/PulseAudio e de wpctl/pactl.
Menus e janelas da RoseShell se ajustam a telas pequenas; apps externos podem
ter dimensões mínimas maiores. Escala é global da RoseShell, não por monitor.

O suporte a GPUs antigas e o consumo no hardware mínimo ainda precisam de
medições físicas. Wallpapers gerados com ImageGen integrado; direção e
prompts em `shell/assets/PROMPTS.md`. Referências anexadas não incluídas.

## Validação na VM

Execute `.venv/bin/python verify.py` no Debian. Verifica descoberta real de
apps, precedência e filtros XDG, renderização de ícones, busca, oito imagens,
troca de wallpaper, rotação, formatos, colagem de imagem e preferências. Os aplicativos gráficos
podem ser abertos pela biblioteca com duplo clique ou Enter.

`resolution_checks.sh` (requer xserver-xephyr) valida limites em 640×480,
640×480 a 125%, 1280×1024, 1920×1080 e 3840×2160. Todos passaram na VM.
`verify_capture.py` e `verify_print.py`, em display isolado, validam captura
real, PNG/clipboard e atalho Print. `verify_clipboard.py` valida persistência
após encerrar a origem. Testes geométricos não substituem avaliação física.

`verify_shortcuts.py` valida arraste, posições persistentes, tamanhos,
visibilidade, remoção sem apagar o app e reutilização do cache de wallpaper.
`verify_variants.py` valida os 24 arquivos e seleção pela proporção.
`verify_lifecycle.py` confirma que fechar configurações não encerra o shell.
`verify_tasks.py` valida janelas abertas, ativação, Alt+Tab e fechamento com
Openbox em display isolado. A barra lista janelas e permite restaurar,
maximizar e fechar pelo menu de contexto. Configurações estão organizadas
em Aparência e Sistema. Dependências e pendências de validação estão em
`docs/DEPENDENCIAS.md`.
O plano de compatibilidade física está em `docs/HARDWARE.md`; a VM não
comprova suporte ou desempenho em todas as GPUs de 2005–2019.

## Código e VM

A RoseShell é criada por **gorigamia**, sob **GPL-3.0-or-later**. Veja
`COPYRIGHT.md` e `LICENSE`. Configurações → Sobre apresenta créditos,
dependências e o texto integral da licença offline.

Português e inglês são selecionáveis em Configurações → Sistema, com
aplicação no próximo login. Diagnóstico de hardware reúne Fastfetch,
TuxManager, Hardinfo2, sensores e ferramentas de GPU/discos; detalhes em
`docs/DIAGNOSTICOS.md`. `install-base.sh` inclui os pacotes e o TuxManager
oficial fixado em `shell/vendor/`. `verify_release.sh` testa os dois idiomas,
resoluções, catálogo e ferramentas instaladas.

- `shell/main.py`: painel e menu de configurações.
- `shell/desktop.py`: desktop e integração X11/EWMH.
- `shell/session.py`: supervisor da sessão.
- `shell/openbox.xml`, `shell/themerc`: configuração e tema de janelas.
- `docs/DIRECAO.md`: identidade e metas.
- `vms/`: máquina virtual, excluída do controle de versão.

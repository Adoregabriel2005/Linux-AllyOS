# Revisão de aplicativos e interface — 0.3.3

Revisão solicitada antes da nova ISO e da publicação em Releases.

- Qt6 Settings/qt6ct e ajustes internos de Openbox/KDE não aparecem no menu
  da RoseShell. qt6ct permanece como backend de tema dos aplicativos Qt.
- No sistema instalado, nenhum atalho para reinstalar o sistema aparece.
  No Live, somente Instalar AllyOS é apresentado, sem a entrada Install Debian.
- NVTOP é consultado pelo modo snapshot, sem abrir terminal ou pedir senha.
  Na VM com vmwgfx não há métricas de GPU: a entrada sai do catálogo e o
  diagnóstico explica a indisponibilidade. A identificação PCI continua disponível.
  O retorno 0 de NVTOP com “No GPU to monitor” não é interpretado como sucesso.
- Aplicativos com executável/TryExec ausente são filtrados. Atalhos antigos
  são verificados antes de abrir. Falhas de inicialização de processos não
  deixam consultas pendentes nem caixas de erro vazias.
- Diagnósticos opcionais ausentes no perfil mínimo ficam desativados, com
  explicação. O gerenciador de dispositivos e o gerenciador de tarefas alternativo
  permanecem disponíveis. Com TuxManager instalado, evita-se a entrada duplicada XFCE.
- Testes e documentação da coleção foram corrigidos para oito wallpapers e
  24 variantes, em vez dos números antigos de sete e 21.

Passaram na VM descartável: catálogo real e precedência XDG; formatos de foto,
clipboard, configurações e indicadores; idiomas PT/EN; diagnósticos mínimos;
falha real de inicialização de processo; oito imagens em três proporções;
fechamento de configurações sem encerrar o desktop; duas janelas com Alt+Tab
e remoção da barra ao fechar; X11 em 640×480, 125%, 1280×1024, 1080p e 4K.

Esses resultados validam a revisão do código. A instalação da ISO 0.3.3 e o
primeiro boot ainda precisam de validação própria. Nenhuma release da ISO foi
publicada nesta etapa. GPUs e interfaces de áudio físicas continuam dependendo
dos testes nos equipamentos reais.

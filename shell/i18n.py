"""Catálogo local PT-BR/English, sem rede; idioma aplicado no próximo login."""
import locale
import os
from PySide6.QtCore import QSettings

_language = None


def language():
    global _language
    if _language is None:
        default = 'pt_BR' if (locale.getlocale()[0] or '').startswith('pt') else 'en'
        value = os.environ.get('ROSESHELL_LANGUAGE') or QSettings('RoseShell', 'Desktop').value('language', default)
        _language = 'en' if value == 'en' else 'pt_BR'
    return _language


EN = {
    '\n\nDISPOSITIVOS PCI / DRIVERS\n': '\n\nPCI DEVICES / DRIVERS\n',
    'Cabo': 'Ethernet', 'Aplicado': 'Applied', '\n\nDISCOS E PARTIÇÕES\n': '\n\nDISKS AND PARTITIONS\n',
    ' aplicativos • duplo clique ou Enter para abrir • Esc para fechar': ' applications • double-click or Enter to open • Esc to close',
    'Aplicativos instalados': 'Installed applications', 'Arquivos': 'Files',
    'Editor de texto': 'Text editor', 'Navegador': 'Web browser',
    'Preferências da RoseShell': 'RoseShell preferences', 'Aplicativo indisponível': 'Application unavailable',
    'Não foi possível abrir o aplicativo.\nVerifique se há um programa compatível instalado.': 'Could not open the application.\nCheck that a compatible program is installed.',
    'Configurações da interface…': 'Interface settings…', 'Gerenciador de dispositivos…': 'Device manager…',
    'Coleção de papéis de parede…': 'Wallpaper collection…', 'Ajuste do papel de parede': 'Wallpaper layout',
    'Mover para ': 'Move to the ', 'direita': 'right', 'esquerda': 'left',
    'Usar tema ': 'Use theme ', 'escuro': 'dark', 'claro': 'light',
    'Inteiro, sem cortar': 'Fit without cropping', 'Centralizado': 'Centered', 'Preencher': 'Fill', 'Esticar': 'Stretch',
    'Sair da sessão': 'Sign out', 'Encerrar painel': 'Close panel',
    'Encerrar a sessão? Salve seus arquivos antes de sair.': 'Sign out? Save your files before leaving.',
    'RoseShell · desenvolvimento': 'RoseShell · development',
    'Copiar caminho da área de trabalho': 'Copy desktop folder path', 'Colar arquivos ou imagem': 'Paste files or image',
    'Ícones da área de trabalho': 'Desktop icons', 'Mostrar ícones': 'Show icons',
    'Organizar ícones': 'Arrange icons', 'Personalizar': 'Personalize', 'Papéis de parede…': 'Wallpapers…',
    'Escala da RoseShell': 'RoseShell scale', 'Capturar tela…': 'Take screenshot…',
    'Abrir pasta da área de trabalho': 'Open desktop folder', ' · próxima sessão': ' · next session',
    'Tamanho ': 'Size ', 'RoseShell — papel de parede': 'RoseShell — wallpaper',
    'Imagens (*.png *.jpg *.jpeg *.webp *.bmp)': 'Images (*.png *.jpg *.jpeg *.webp *.bmp)',
    'Não foi possível ler essa imagem. Verifique o formato e o arquivo.': 'Could not read this image. Check the file and its format.',
    'Falha ao salvar a imagem.': 'Could not save the image.',
    'Arquivo já existente ou não é arquivo comum: ': 'File already exists or is not a regular file: ',
    'RoseShell — Configurações': 'RoseShell — Settings', 'PERSONALIZAR ROSESHELL': 'PERSONALIZE ROSESHELL',
    'Grafite': 'Graphite', 'Claro': 'Light', 'Tema': 'Theme', 'Painel': 'Panel',
    'Esquerda': 'Left', 'Direita': 'Right', 'Monitor do painel': 'Panel monitor',
    'Mostrar atalhos na área de trabalho': 'Show desktop shortcuts', 'Tamanho dos ícones': 'Icon size',
    'Econômico · GPUs antigas': 'Economy · older GPUs', 'Equilibrado': 'Balanced', 'Perfil de desenho': 'Rendering profile',
    'A escala será aplicada ao entrar novamente na sessão.\nAplicativos externos podem ter seus próprios ajustes de escala.': 'Scale will apply when you sign in again.\nExternal applications may have their own scaling settings.',
    'Aparência': 'Appearance', 'Sistema': 'System', 'Fechar': 'Close',
    'Papéis de parede e rotação…': 'Wallpapers and slideshow…', 'Som…': 'Sound…', 'Rede…': 'Network…',
    'Idioma e teclado…': 'Language and keyboard…', 'Captura de tela…': 'Screenshot…',
    'Gerenciador de tarefas · Ctrl+Shift+Esc': 'Task manager · Ctrl+Shift+Esc',
    'Idioma da interface': 'Interface language', 'Sobre a RoseShell': 'About RoseShell',
    'Diagnóstico de hardware…': 'Hardware diagnostics…', 'Idioma e teclado': 'Language and keyboard',
    'Captura de tela · Print Screen': 'Screenshot · Print Screen',
    'Rede: ': 'Network: ', 'Idioma: ': 'Language: ', 'sem enlace ativo': 'no active link',
    'Áudio: nenhuma saída disponível': 'Audio: no output available',
    'Nenhuma saída de áudio disponível': 'No audio output available',
    'Nenhuma interface encontrada': 'No interface found', 'Idioma do sistema: ': 'System language: ',
    'Ativar / desativar mudo': 'Toggle mute', 'Conexões de rede': 'Network connections',
    'Configurar conexões…': 'Configure connections…', 'Editor de conexões do NetworkManager': 'NetworkManager connection editor',
    'Gerenciador de dispositivos': 'Device manager', 'Atualizar dispositivos': 'Refresh devices',
    'Teclado brasileiro': 'Brazilian keyboard', 'Teclado americano': 'US keyboard',
    ' indisponível': ' unavailable', ' dispositivos\n': ' devices\n', 'Discos conectados: ': 'Connected disks: ',
    ' · mudo': ' · muted', 'Nenhum dispositivo USB externo detectado': 'No external USB device detected',
    'Teclado aplicado: ': 'Keyboard applied: ',
    'RoseShell — Captura de tela': 'RoseShell — Screenshot', 'Salvar captura': 'Save screenshot',
    'Nova captura': 'New screenshot', 'Salvar…': 'Save…', 'Copiar': 'Copy',
    'A captura não está disponível nesta sessão gráfica.': 'Screenshots are unavailable in this graphical session.',
    'Não foi possível salvar a captura nesse formato ou caminho.': 'Could not save the screenshot in this format or location.',
    'RoseShell — Aplicativos': 'RoseShell — Applications', 'APLICATIVOS': 'APPLICATIONS',
    'Buscar nos aplicativos instalados…': 'Search installed applications…', 'Buscar aplicativos': 'Search applications',
    'Adicionar selecionado à área de trabalho': 'Add selected application to desktop',
    'Adicionar à área de trabalho': 'Add to desktop',
    'Atalho adicionado. Arraste na área de trabalho para posicionar.': 'Shortcut added. Drag it on the desktop to position it.',
    ' aplicativos · duplo clique ou Enter para abrir · Esc para fechar': ' applications · double-click or Enter to open · Esc to close',
    'Instale libglib2.0-bin para abrir aplicativos.': 'Install libglib2.0-bin to open applications.',
    'RoseShell — falha ao abrir': 'RoseShell — launch failed',
    'RoseShell — Papéis de parede': 'RoseShell — Wallpapers', 'COLEÇÃO ROSESHELL': 'ROSESHELL COLLECTION',
    'Escolha uma ilustração para fixar ou ative a troca automática.': 'Choose a fixed illustration or enable the slideshow.',
    'Trocar automaticamente': 'Change automatically', 'Escolher outra imagem…': 'Choose another image…',
    'Ajustar sem cortar': 'Fit without cropping', 'Preencher a tela': 'Fill screen', 'Centralizar': 'Center',
    'Proporção automática por monitor': 'Automatic aspect ratio per monitor',
    'Versão 5:4': '5:4 version', 'Versão 16:9': '16:9 version', 'Versão 4:3': '4:3 version', 'A cada ': 'Every ',
    '\nArraste para mover · duplo clique para abrir': '\nDrag to move · double-click to open',
    'Abrir': 'Open', 'Mover para monitor': 'Move to monitor', 'Remover atalho': 'Remove shortcut',
    'RoseShell — área de trabalho': 'RoseShell — desktop',
    'Restaurar / ativar': 'Restore / activate', 'Maximizar / restaurar': 'Maximize / restore',
    'Instale wmctrl para mostrar janelas abertas.': 'Install wmctrl to show open windows.',
    'Criada por gorigamia.': 'Created by gorigamia.',
    'Uma interface sóbria, angular e leve sobre Debian.': 'A restrained, angular and lightweight desktop on Debian.',
    'Licença': 'License', 'Dependências da interface': 'Interface dependencies', 'Aplicativos incluídos': 'Included applications',
    'Você pode usar, estudar, modificar e redistribuir a RoseShell, inclusive comercialmente, seguindo a GPLv3 ou posterior. Preserve os créditos e forneça o código-fonte correspondente ao redistribuir binários. Sem garantia.': 'You may use, study, modify and redistribute RoseShell, including commercially, under GPLv3 or later. Preserve attribution and provide corresponding source code when redistributing binaries. No warranty.',
    'Debian, Qt e aplicativos incluídos pertencem aos respectivos autores e mantêm suas próprias licenças. O crédito de gorigamia refere-se à RoseShell.': 'Debian, Qt and included applications belong to their respective authors and retain their own licenses. The gorigamia credit refers to RoseShell.',
    'Diagnóstico de hardware': 'Hardware diagnostics',
    'CPU, GPU, memória, temperaturas e armazenamento. Sensores disponíveis dependem do hardware e do driver; máquinas virtuais podem não expor temperaturas ou SMART.': 'CPU, GPU, memory, temperatures and storage. Available sensors depend on hardware and drivers; virtual machines may not expose temperatures or SMART.',
    'Resumo do sistema · Fastfetch': 'System summary · Fastfetch',
    'Informações de CPU, GPU e RAM · Hardinfo2': 'CPU, GPU and RAM information · Hardinfo2',
    'Gerenciador de tarefas · TuxManager': 'Task manager · TuxManager',
    'Uso da GPU · NVTOP': 'GPU usage · NVTOP', 'Saúde dos discos · GSmartControl': 'Disk health · GSmartControl',
    'Relatório de hardware · inxi': 'Hardware report · inxi', 'Temperaturas detectadas': 'Detected temperatures',
    'Nenhum sensor disponível nesta máquina ou VM.': 'No sensor available on this machine or VM.',
    'Atualizar temperaturas': 'Refresh temperatures',
}


EN.update({
    'Não foi possível iniciar este aplicativo.': 'This application could not be started.',
    'Escolha um programa Windows ou abra a configuração do Wine.': 'Choose a Windows program or open Wine settings.',
    'Wine não está instalado neste perfil.': 'Wine is not installed in this profile.',
    'Não foi possível iniciar o Wine.': 'Could not start Wine.',
    'Abrir programa Windows': 'Open Windows program',
    'Abrir programa Windows…': 'Open Windows program…',
    'Configurar Wine…': 'Configure Wine…',
    'Saída de som': 'Audio output',
    'Entrada / microfone': 'Input / microphone',
    'Mixer, perfis e áudio dos aplicativos…': 'Mixer, profiles and application audio…',
    'Dispositivos de áudio e drivers…': 'Audio devices and drivers…',
    'Dispositivos de áudio e drivers': 'Audio devices and drivers',
    'Interfaces USB compatíveis usam ALSA, PipeWire e WirePlumber. A detecção abaixo informa os dispositivos presentes; não confirma compatibilidade de modelos ausentes.': 'Compatible USB interfaces use ALSA, PipeWire and WirePlumber. Detection below lists connected devices; it does not confirm compatibility of absent models.',
    'Tocar som ao entrar na sessão': 'Play sound when signing in',
    'Testar controle de jogo…': 'Test game controller…',
})

EN.update({
    'NVTOP não está instalado neste perfil.': 'NVTOP is not installed in this profile.',
    'A GPU virtual desta máquina não fornece métricas ao NVTOP. Consulte a GPU em Informações de hardware.': 'This virtual GPU does not provide NVTOP metrics. See GPU identification in Hardware information.',
    'O driver da GPU não forneceu métricas ao NVTOP. Consulte a GPU em Informações de hardware.': 'The GPU driver did not provide NVTOP metrics. See GPU identification in Hardware information.',
    'Não foi possível consultar a GPU neste momento.': 'GPU information could not be queried at this time.',
    'Este aplicativo não está instalado neste perfil.': 'This application is not installed in this profile.',
    'Este aplicativo não está disponível nesta sessão. Atualize ou remova o atalho.': 'This application is not available in this session. Update or remove its shortcut.',
})

_fragments = tuple(sorted(EN, key=len, reverse=True))


def tr(text):
    if language() != 'en':
        return text
    if text in EN:
        return EN[text]
    # Fragmentos de mensagens com números, nomes de dispositivos e arquivos.
    for source in _fragments:
        if text.startswith(source):
            return EN[source] + text[len(source):]
        if text.endswith(source):
            return text[:-len(source)] + EN[source]
    return text

# Publicação do AllyOS

Nome solicitado: Linux-AllyOS. Autoria do código próprio: gorigamia.
Licença: GPL-3.0-or-later; componentes de terceiros conservam suas licenças.

O repositório contém os fontes da RoseShell, a receita da ISO, os recursos
originais e os avisos dos componentes incluídos. Máquinas virtuais, discos,
logs de teste, comandos temporários e imagens ISO ficam fora do Git.

`iso/local-assets/` é somente local e está excluído do Git e do arquivo de
fontes público. O áudio enviado pelo usuário, identificado como Windows
Longhorn startup, não tem licença de redistribuição confirmada. A receita
pública usa o som original RoseShell quando esse recurso local está ausente.
Não publicar a ISO local contendo esse áudio como uma release pública sem
resolver sua licença ou substituí-lo pelo som original.

A ISO de desenvolvimento precisa de teste de instalação e reinicialização.
Sucesso no VirtualBox não confirma compatibilidade de todos os dispositivos
físicos. Registrar os resultados em VALIDACAO-ISO.md antes da publicação.

Para distribuir binários, cumprir as obrigações de código-fonte correspondente
dos componentes distribuídos; o arquivo de fontes próprios não substitui os
fontes de todos os pacotes Debian. Não subir uma ISO grande no histórico Git.

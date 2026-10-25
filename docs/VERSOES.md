# Versão do AllyOS

Formato: `release.revisão.compilação`, sem zeros à esquerda.

- **release**: número da versão pública. `0` identifica desenvolvimento;
  a primeira versão pública será `1`.
- **revisão**: conjunto de alterações do código dentro da release. Não é
  quantidade de linhas ou arquivos, que muda sem representar uma atualização.
- **compilação**: tentativa de gerar a imagem daquela revisão.

A próxima imagem é **0.3.3**. A primeira imagem experimental **0.01** continua
arquivada, com o hash e as evidências dos testes; não é sobrescrita.
Uma nova revisão começa com compilação 1. Uma nova release começa com revisão 0.
O arquivo `iso/release.json` é a fonte para pacotes, ISO, login, Sobre e os-release.
Debian 13 / trixie continua identificado separadamente como a base.

Uma imagem gerada não é uma release aprovada: instalar, iniciar a sessão e
validar os dois perfis são etapas distintas da compilação.

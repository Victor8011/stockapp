## Aplicativo de controle de estoque

### App multiplataforma em python com framework flet para controle de estoque. Integração com API da firebase para controle de Login.

- Funcionalidades:
  - Sistema para alterar imagem de perfil que armazena localmente
  - Sistema de validação de Login com email criado no firebase
  - Adicionar e remover categorias
  - Adicionar e remover produtos
  - Adicionar e remover produtos nas/das categorias
  - adicionar e diminuir quantidade de produtos conforme uso.

- Em processo de desenvolvimento:
  - [x] Integração com SQLite para persistencia de dados local
  - [x] Sistema semi-automático de update
  - Sistema de Backup
  - Criação e Validação de novos usuários
  - [x] Relatórios de produtos
  - Importação de relatórios baseado na data para PDF com FPDF
  - Paginação
  - Versão para WEB refatorado com Views
  - Entre outros.

- Dependências:
  - Python 3.12.1
  - sqlite3
  - datetime
  - pytz
  - Flet 0.26.0
    - `pip install flet`
  - Requests 2.32.3
    - `pip install requests` 

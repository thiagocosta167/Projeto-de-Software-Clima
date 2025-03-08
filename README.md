# Projeto-de-Software-Clima

Projeto criado para as atividades da Matéria de Software Product.

Ele tem como intuito ser um projeto onde após o usuário criar o seu cadastro, e logar, o mesmo pode pesquisar o clima de cidades, onde ficará salvo no histórico as três últimas pesquisas recentes do usuário

## Tecnologias Utilizadas.

    * Python
    * Flask
    * JavaScript
    * MySQL
 

## APIs Utilizadas

    * Google Fonts API: [(https://fonts.google.com/)]
    * API de Clima: [(https://openweathermap.org/)]



 ## Funcionalidades Principais
 
    * Cadastro de usuários: Permite que os usuários criem uma conta no sistema.
    * Login de usuários: Permite que os usuários acessem suas contas.
    * Pesquisa de clima: Permite que os usuários pesquisem o clima de cidades.
    * Histórico de pesquisas: Armazena as três últimas pesquisas de cada usuário.

   ## Como Executar o Projeto

     ## Como Executar o Projeto

    1. Clone este repositório: `git clone <URL_do_repositorio>`
    2.  Crie a pasta "templates" para armazenar o HMTL dentro 
    3.  Crie a pasta "static" para armazenas o CSS e JS dentro 
    2. Navegue até o diretório do projeto: `cd <nome_do_repositorio>`
    3. Crie um ambiente virtual: `python -m venv venv`
    4. Ative o ambiente virtual:
        * macOS/Linux: `source venv/bin/activate`
        * Windows: `venv\Scripts\activate`
    5. Instale as dependências: `pip install -r requirements.txt`
    6. Configure o banco de dados MySQL:
        * Importe o arquivo `banco_de_dados.sql`.
        * Configure as credenciais no arquivo `config.py`.
    7. Configure as variáveis de ambiente.

    8. Execute o aplicativo: `python app.py`
    9. Acesse o aplicativo no navegador: `http://127.0.0.1:5000` para verificar a conexão com o MWSQL
   10. Acesse o aplicativo no navegador: `http://127.0.0.1:5000/clima`

## Documentação da API Soluciona

### 1\. Introdução

A **Soluciona API** é um serviço de backend projetado para uma plataforma de engajamento cívico. Ela permite que os usuários registrem problemas (reports) em locais específicos (places), gerenciem seus perfis e façam upload de imagens.

O serviço utiliza autenticação baseada em JSON Web Tokens (JWT) para proteger rotas, armazena dados em um banco de dados PostgreSQL e integra-se ao Amazon S3 para armazenamento de arquivos de imagem.

### 2\. Configuração e Instalação

Siga estas etapas para configurar e executar a API localmente.

#### 2.1. Dependências

O projeto requer as seguintes bibliotecas Python, conforme listado em `requirements.txt`:

  * Flask
  * psycopg (com `binary`)
  * dotenv (para carregar variáveis de ambiente)
  * flask-jwt-extended (para autenticação JWT)
  * boto3 (para integração com AWS S3)

Instale-as usando:

```bash
pip install -r requirements.txt
```

#### 2.2. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto. A API carrega essas variáveis usando o arquivo `config.py`.

```ini
# Conexão com o banco de dados PostgreSQL
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME

# Chave secreta para assinar os tokens JWT
JWT_SECRET_KEY=sua_chave_secreta_aqui

# Credenciais da AWS S3 para upload de imagens
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
S3_BUCKET_NAME=nome-do-seu-bucket
S3_BUCKET_REGION=regiao-do-bucket
```

#### 2.3. Inicialização do Banco de Dados

O arquivo `seeder.py` contém as declarações DDL (Data Definition Language) para criar todas as tabelas, tipos e restrições (chaves estrangeiras) necessárias no banco de dados.

Execute o seeder para inicializar o esquema:

```bash
python seeder.py
```

Isso criará as tabelas: `places`, `users`, `reports` e `images`, com todas as suas inter-relações.

#### 2.4. Executando a API

Após instalar as dependências e configurar o `.env`, inicie o servidor Flask:

```bash
python app.py
```

O servidor será executado em `http://127.0.0.1:5000` por padrão.

### 3\. Autenticação

A API usa **JWT** para proteger a maioria de suas rotas, conforme definido em `app.py`.

**Fluxo de Autenticação:**

1.  Um usuário se registra (via `POST /register`) e faz login (via `POST /login`).
2.  O endpoint `/login`, implementado em `AuthController`, verifica as credenciais. Se forem válidas, ele retorna um `access_token` JWT.
3.  Para acessar rotas protegidas (marcadas com `@jwt_required()`), o cliente deve enviar este token no cabeçalho `Authorization` como `Bearer <TOKEN>`, conforme mencionado no `README.md`.

### 4\. Endpoints da API

A seguir estão todas as rotas definidas em `app.py` e sua lógica de controle.

-----

#### 4.1. Autenticação e Usuários

**`POST /register`**

  * **Descrição:** Registra um novo usuário no sistema.
  * **Controlador:** `UserRegisterController.register`.
  * **Autenticação:** Nenhuma.
  * **Corpo (JSON):**
      * `username` (string, obrigatório)
      * `email` (string, obrigatório)
      * `password` (string, obrigatório)
      * `phone` (string, opcional)
      * `place_id` (int, opcional)
      * `profile_picture` (int, opcional - ID de uma imagem já existente)
  * **Resposta (Sucesso):** `201 Created` com `{ "message": "User registered successfully.", "user": { ... } }`.

**`POST /login`**

  * **Descrição:** Autentica um usuário e retorna um token de acesso.
  * **Controlador:** `AuthController.login`.
  * **Autenticação:** Nenhuma.
  * **Corpo (JSON):**
      * `identifier` (string, obrigatório - pode ser `username`, `email` ou `phone`).
      * `password` (string, obrigatório).
  * **Resposta (Sucesso):** `200 OK` com `{ "access_token": "...", "username": "...", "place_id": ... }`.

**`GET /user`**

  * **Descrição:** Obtém as informações de perfil do usuário autenticado.
  * **Controlador:** `UserRegisterController.get_user_profile`.
  * **Autenticação:** **JWT Obrigatório**.
  * **Resposta (Sucesso):** `200 OK` com `{ "user": { ... } }`. O campo `profile_picture` conterá a URL completa da imagem do S3, se existir.

-----

#### 4.2. Places (Locais)

**`GET /places`**

  * **Descrição:** Retorna uma lista de todos os "places" (locais, como cidades ou instituições) cadastrados.
  * **Controlador:** `PlacesController.return_all_places`.
  * **Autenticação:** Nenhuma.
  * **Resposta (Sucesso):** `200 OK` com a lista de locais vinda da consulta `SELECT * FROM places`.

-----

#### 4.3. Reports (Relatos de Problemas)

**`POST /reports`**

  * **Descrição:** Registra um novo "report" (problema).
  * **Controlador:** `ReportsController.report_problem`.
  * **Autenticação:** **JWT Obrigatório**.
  * **Corpo (JSON):** (Campos obrigatórios: `name`, `latitude`, `longitude`, `description`, `place_id`)
    ```json
    {
        "name":"Buraco Na Rua",
        "latitude":-23.55052,
        "longitude":-46.633308,
        "description":"Há um buraco grande...",
        "place_id": 1,
        "address": "Rua A, 123"
    }
    ```
  * **Resposta (Sucesso):** `201 Created` com `{ "message": "Report registered successfully.", "report": { ... } }`.

**`GET /reports`**

  * **Descrição:** Lista os reports **ativos** associados ao `place_id` do usuário autenticado.
  * **Controlador:** `ReportsController.list_reports_by_user_place`.
  * **Autenticação:** **JWT Obrigatório**.
  * **Resposta (Sucesso):** `200 OK` com `{ "place": { ... }, "reports": [ ... ] }`. Retorna apenas `id`, `latitude` e `longitude` dos reports.

**`GET /reports/user`**

  * **Descrição:** Lista todos os reports registrados pelo usuário autenticado, ordenados por data.
  * **Controlador:** `ReportsController.list_reports_by_user`.
  * **Autenticação:** **JWT Obrigatório**.
  * **Resposta (Sucesso):** `200 OK` com `{ "user_id": ..., "reports": [ ... ] }`.

**`GET /reports/<int:report_id>`**

  * **Descrição:** Obtém os detalhes completos de um report específico, incluindo a lista de URLs de imagens associadas.
  * **Controlador:** `ReportsController.get_report_full_details`.
  * **Autenticação:** **JWT Obrigatório**.
  * **Resposta (Sucesso):** `200 OK` com o objeto completo do report e um array `images`.

**`DELETE /reports/<int:report_id>`**

  * **Descrição:** Remove um report.
  * **Controlador:** `ReportsController.remove_report`.
  * **Autenticação:** **JWT Obrigatório**.
  * **Lógica de Permissão:** Somente o usuário que criou o report (`registered_by`) pode excluí-lo.
  * **Resposta (Sucesso):** `200 OK` com `{ "message": "Report removed successfully.", "report_id": ... }`.

-----

#### 4.4. Upload de Imagens

**`POST /upload-image`**

  * **Descrição:** Faz upload de uma imagem e a define como a foto de perfil do usuário autenticado.
  * **Controlador:** `ImageController.upload_image` (chamado sem `report_id`).
  * **Autenticação:** **JWT Obrigatório**.
  * **Corpo:** `multipart/form-data` com um campo `image`.
  * **Lógica:** A imagem é enviada ao S3. O ID da nova imagem atualiza a coluna `users.profile_picture` do usuário logado.
  * **Resposta (Sucesso):** `201 Created` com `{ "message": "Image uploaded successfully.", "image": { ... } }`.

**`POST /reports/<int:report_id>/upload-image`**

  * **Descrição:** Faz upload de uma imagem e a associa a um report existente.
  * **Controlador:** `ImageController.upload_image` (chamado com `report_id`).
  * **Autenticação:** **JWT Obrigatório**.
  * **Corpo:** `multipart/form-data` com um campo `image`.
  * **Lógica:** A imagem é enviada ao S3 e o `report_id` é salvo na tabela `images`.
  * **Resposta (Sucesso):** `201 Created` com `{ "message": "Image uploaded successfully.", "image": { ... } }`.

### 5\. Esquema do Banco de Dados

O esquema é definido em `seeder.py`. A classe `Database` em `models/database.py` gerencia a conexão e execução das queries.

  * **`places`**

      * `id` (SERIAL, PK)
      * `name` (VARCHAR, UNIQUE)
      * `type` (VARCHAR)

  * **`users`**

      * `id` (SERIAL, PK)
      * `username` (VARCHAR, UNIQUE)
      * `email` (VARCHAR, UNIQUE)
      * `phone` (VARCHAR)
      * `password` (VARCHAR - armazena o hash SHA-256)
      * `profile_picture` (INT, FK -\> `images.id`)
      * `place_id` (INT, FK -\> `places.id`)
      * `account_status` (VARCHAR, DEFAULT 'active')
      * `created_at` (TIMESTAMP)

  * **`reports`**

      * `id` (SERIAL, PK)
      * `name` (VARCHAR)
      * `latitude` (DOUBLE)
      * `longitude` (DOUBLE)
      * `description` (TEXT)
      * `place_id` (INT, FK -\> `places.id`)
      * `address` (VARCHAR)
      * `status` (VARCHAR, DEFAULT 'active')
      * `registered_by` (INT, FK -\> `users.id`)
      * `registered_date` (TIMESTAMP)

  * **`images`**

      * `id` (SERIAL, PK)
      * `url_storage` (VARCHAR - URL pública do S3)
      * `report_id` (INT, FK -\> `reports.id`)
      * `image_type` (VARCHAR)
      * `image_size` (BIGINT)
      * `registered_date` (TIMESTAMP)
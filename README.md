# Soluciona API — Tutorial de Uso

1 — Clonar repositório
```powershell
git clone https://github.com/schumann7/soluciona-api.git
cd soluciona-api
```

2 — Criar e ativar virtualenv (recomendado)
```powershell
python -m venv .venv
.venv\Scripts\Activate
```

3 — Instalar dependências
Se existir requirements.txt:
```powershell
pip install -r requirements.txt
```

4 — Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz com estas chaves (exemplo):
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
JWT_SECRET_KEY=sua_chave_jwt
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=seu-bucket
S3_BUCKET_REGION=us-east-1
```

6 — Rodar a API
```powershell
python app.py
```
Por padrão: http://127.0.0.1:5000

Rotas

- POST /register  
  Registrar usuário. Body JSON:
  { "username": "...", "email": "...", "password": "...", "phone": (opcional), "place_id": "...", "profile_picture": (opcional id) }  

- POST /login  
  Fazer login. Body JSON:
  { "identifier": "<username|email|phone>", "password": "..." }  
  Retorna: { "access_token": "<JWT>" }  

- POST /places (JWT required)  
  Criar place (local). Body JSON: { "name": "Nome", "type": "tipo" }  
  Header: Authorization: Bearer <TOKEN>

- GET /places  
  Listar todos os places.

- POST /reports (JWT required)  
  Criar report (problema). Body JSON:  
  { "name":"...", "latitude": <num>, "longitude": <num>, "description":"...", "place_id": <int>, "address": (opt) }  

- GET /reports/<place_id> (JWT required)  
  Listar reports ativos daquele lugar (cidade ou instituição).

- DELETE /reports/<report_id> (JWT required)  
  Remover um report.

- Upload de imagens
  - POST /upload-image (JWT required) — enviar foto de perfil (sem report_id). multipart/form-data com campo `image`.
    Resposta inclui `image.id` e `image.url_storage` (link público no S3).
    O campo `users.profile_picture` é atualizado com o id da imagem inserida.
  - POST /reports/<report_id>/upload-image (JWT required) — enviar imagem vinculada a um report:

Como obter a URL da foto de perfil no frontend
- A resposta do upload retorna `url_storage` (use direto no <img src="...">).
- Se quiser buscar depois, faça uma query no backend que junta users.profile_picture com images.url_storage (ex.: SELECT ... JOIN images ON users.profile_picture = images.id).

Dicas rápidas
- Sempre obtenha o JWT via /login e envie no header Authorization: Bearer <TOKEN> para rotas protegidas.
- Para debug: verifique console onde rodou `python app.py` para erros.
import boto3
import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename
from controllers.db_instance import db
from config import Config
from flask_jwt_extended import get_jwt_identity

# Define as extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ImageController:
    
    def __init__(self):
        # Inicializa o cliente S3
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.S3_BUCKET_REGION
        )

    def upload_image(self, report_id=None):
        # report_id optional: if provided -> image of a report; else -> profile picture
        if 'image' not in request.files:
            return jsonify({"error": "Nenhum arquivo de imagem enviado."}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado."}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Tipo de arquivo não permitido."}), 400

        # 2. Obter metadados
        # Precisamos ler o arquivo em memória para o Boto3
        file_bytes = file.read()
        image_size = len(file_bytes) # Tamanho em bytes
        image_type = file.mimetype
        
        # Resetar o ponteiro do arquivo para o Boto3 ler do início
        file.seek(0) 

        # 3. Preparar o upload para o S3
        original_filename = secure_filename(file.filename)
        # Cria um nome único (key) para o objeto no S3
        unique_key = f"images/{uuid.uuid4().hex}-{original_filename}"

        try:
            # 4. Fazer o Upload para o S3
            self.s3.upload_fileobj(
                file, # O objeto do arquivo (stream)
                Config.S3_BUCKET_NAME, # O nome do seu bucket
                unique_key, # O nome/caminho do arquivo no bucket
                ExtraArgs={
                    "ContentType": image_type,
                }
            )
        except Exception as e:
             return jsonify({"error": "Erro ao fazer upload para o S3.", "detail": str(e)}), 500

        # 5. Construir a URL pública
        url_storage = f"https://{Config.S3_BUCKET_NAME}.s3.{Config.S3_BUCKET_REGION}.amazonaws.com/{unique_key}"

        # Insert into images table (report_id may be None)
        try:
            result = db.execute(
                "INSERT INTO images (url_storage, report_id, image_type, image_size, registered_date) VALUES (%s, %s, %s, %s, NOW()) RETURNING id",
                (url_storage, report_id, image_type, image_size),
            )
        except Exception as e:
            # rollback S3 object if DB insert fails
            try:
                self.s3.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=unique_key)
            except Exception:
                pass
            return jsonify({"error": "Erro ao registrar a imagem no banco.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            try:
                self.s3.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=unique_key)
            except Exception:
                pass
            return jsonify({"error": "Erro ao registrar a imagem no banco.", "detail": result["error"]}), 500

        new_image_id = result[0][0] if result and len(result) > 0 else None

        # If no report_id -> treat as profile picture: update users.profile_picture for authenticated user
        if report_id is None:
            identity = get_jwt_identity()
            # identity can be a string id or a dict; normalize to int user_id if possible
            try:
                if isinstance(identity, dict):
                    user_id = int(identity.get("id"))
                else:
                    user_id = int(identity)
            except Exception:
                # can't determine user id
                return jsonify({"error": "Não foi possível identificar o usuário autenticado."}), 400

            try:
                upd = db.execute(
                    "UPDATE users SET profile_picture = %s WHERE id = %s",
                    (new_image_id, user_id)
                )
            except Exception as e:
                # try delete S3 object if user update fails
                try:
                    self.s3.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=unique_key)
                except Exception:
                    pass
                return jsonify({"error": "Erro ao atualizar foto de perfil no banco.", "detail": str(e)}), 500

            if isinstance(upd, dict) and upd.get("error"):
                try:
                    self.s3.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=unique_key)
                except Exception:
                    pass
                return jsonify({"error": "Erro ao atualizar foto de perfil no banco.", "detail": upd["error"]}), 500

        image_info = {
            "id": new_image_id,
            "url_storage": url_storage,
            "report_id": report_id,
            "image_type": image_type,
            "image_size": image_size
        }

        return jsonify({"message": "Imagem enviada com sucesso.", "image": image_info}), 201
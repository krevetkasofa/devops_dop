from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
import secrets
import string
import json

app = Flask(__name__)

# Подключение к MinIO
minio_client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="admin12345678",
    secure=False
)

# Хранилище созданных инстансов
instances = {}

def generate_credentials():
    """Генерирует случайные креды для пользователя"""
    # Генерируем имя bucket: только маленькие буквы и цифры, длина 20 символов
    bucket_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    access_key = 'user' + bucket_suffix
    secret_key = secrets.token_hex(32)
    return access_key, secret_key

@app.route('/create-instance', methods=['POST'])
def create_instance():
    """Создает новое изолированное хранилище для пользователя"""
    try:
        data = request.json or {}
        user_name = data.get('user_name', 'default_user')
        
        # Генерируем уникальные credentials
        access_key, secret_key = generate_credentials()
        bucket_name = access_key
        
        print(f"Creating bucket: {bucket_name} for user: {user_name}")
        
        # Создаем bucket
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} created successfylly")
        
        # Сохраняем информацию об инстансе
        instance_info = {
            "user_name": user_name,
            "access_key": access_key,
            "secret_key": secret_key,
            "endpoint": "localhost:9000",
            "bucket": bucket_name,
            "status": "active"
        }
        instances[bucket_name] = instance_info
        
        return jsonify({
            "message": "Storage created successfylly",
            "instance": instance_info
        }), 201
        
    except S3Error as err:
        print(f"S3 Error: {err}")
        return jsonify({"error": str(err)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete-instance/<bucket_name>', methods=['DELETE'])
def delete_instance(bucket_name):
    """Удаляет хранилище пользователя"""
    try:
        print(f"Delete request for bucket: {bucket_name}")
        
        if not minio_client.bucket_exists(bucket_name):
            return jsonify({"error": "Storage not found"}), 404
        
        # Удаляем все объекты из bucket
        objects = minio_client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
            print(f"Deleted object: {obj.object_name}")
        
        # Удаляем bucket
        minio_client.remove_bucket(bucket_name)
        print(f"Bucket {bucket_name} deleted successfylly")
        
        # Удаляем из списка
        if bucket_name in instances:
            del instances[bucket_name]
        
        return jsonify({
            "message": f"Storage {bucket_name} deleted successfylly"
        }), 200
        
    except S3Error as err:
        print(f"S3 Error: {err}")
        return jsonify({"error": str(err)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/list-instances', methods=['GET'])
def list_instances():
    """Показывает все активные хранилища"""
    try:
        buckets = minio_client.list_buckets()
        result = []
        for bucket in buckets:
            info = instances.get(bucket.name, {})
            result.append({
                "bucket": bucket.name,
                "created": bucket.creation_date.isoformat(),
                "user_name": info.get("user_name", "unknown"),
                "status": info.get("status", "unknown")
            })
        return jsonify({
            "instances": result, 
            "total": len(result)
        }), 200
        
    except S3Error as err:
        print(f"S3 Error: {err}")
        return jsonify({"error": str(err)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/instance-info/<bucket_name>', methods=['GET'])
def instance_info(bucket_name):
    """Показывает информацию о конкретном хранилище"""
    try:
        if minio_client.bucket_exists(bucket_name):
            info = instances.get(bucket_name, {})
            return jsonify({
                "bucket": bucket_name,
                "endpoint": "localhost:9000",
                "user_name": info.get("user_name", "unknown"),
                "status": "active"
            }), 200
        else:
            return jsonify({"error": "Хранилище не найдено"}), 404
            
    except S3Error as err:
        print(f"S3 Error: {err}")
        return jsonify({"error": str(err)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Проверка работоспособности"""
    try:
        minio_client.list_buckets()
        return jsonify({
            "status": "healthy",
            "service": "MinIO SaaS",
            "instances_count": len(instances)
        }), 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    print("MinIO SaaS raunning on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

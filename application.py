from flask import Flask, request, jsonify
import uuid
import os
import boto3
from botocore.exceptions import NoCredentialsError
import sqlite3

application = Flask(__name__)

REPOSITORY_PATH = 'https://appdistribution.s3.amazonaws.com'
DEF_IOS_IMG = "ios.jpg"


@application.route('/')
def hello_world():
    return 'Hello World!'


@application.route('/metadata', methods=['GET'])
def get_metadata():
    bucket_uuid = str(uuid.uuid4())
    app_url = os.path.join(REPOSITORY_PATH, bucket_uuid)
    image_url = os.path.join(REPOSITORY_PATH, DEF_IOS_IMG)

    return jsonify({
        "appId": bucket_uuid,
        "appUrl": app_url,
        "imageUrl": image_url
    })


@application.route('/upload', methods=['POST'])
def upload_file():
    appName = request.form['appName']
    appVersion = request.form['appVersion']
    appFiles = request.files.getlist('appFiles')
    appId = request.form['appId']

    try:
        # Inicializa el cliente de S3
        s3_client = boto3.client('s3')
        bucket_name = "appdistribution"
        object_url = ""

        # Sube el archivo al bucket especificado
        for file in appFiles:
            filename = file.filename
            remote_path = f"{appId}/{file.filename}"
            s3_client.upload_fileobj(file, bucket_name, remote_path)
            object_url = f"https://{bucket_name}.s3.amazonaws.com/{remote_path}"
            print(f"Archivo {filename} subido exitosamente a {object_url}")

        # Guardar en la base de datos (SQLite)
        conn = sqlite3.connect('appdistribution.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO apps (name, version, url) VALUES (?, ?, ?)",
                       (appName, appVersion, object_url))
        conn.commit()
        conn.close()
        print("Se guardo en base de datos!!!")

        return jsonify({"mensaje": object_url})

    except NoCredentialsError:
        response = "No se encontraron credenciales de AWS. Asegúrate de configurarlas correctamente."
        return jsonify({"mensaje": response})

    except Exception as e:
        response = f"Error al subir el archivo a S3: {str(e)}"
        return jsonify({"mensaje": response})


if __name__ == '__main__':
    application.run(debug=True)

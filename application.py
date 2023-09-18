from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import boto3
from botocore.exceptions import NoCredentialsError
import sqlite3

application = Flask(__name__)

# Configuración de CORS
CORS(application)

REPOSITORY_PATH = 'https://appdistribution.s3.amazonaws.com'
DEF_IOS_IMG = "ios.jpg"


@application.route('/')
def get_apps():
    filterName = request.args.get('name', None)
    orderBy = request.args.get('orderBy', None)

    # Conectar a la base de datos
    conn = sqlite3.connect('appdistribution.db')
    cursor = conn.cursor()

    if filterName:
        cursor.execute(
            "SELECT * FROM apps WHERE name LIKE ?", ('%' + filterName + '%',))
    else:
        cursor.execute("SELECT * FROM apps")

    if orderBy == 'version':
        cursor.execute("SELECT * FROM apps ORDER BY version ASC")

    apps = []

    for app in cursor.fetchall():
        apps.append({
            "name": app[1],
            "version": app[2],
            "build": app[3],
            "url": get_download_url(app[4]),
        })

    conn.close()

    return jsonify(apps)


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
        response = ""

        # Sube el archivo al bucket especificado
        for file in appFiles:
            remote_path = f"{appId}/{file.filename}"
            s3_client.upload_fileobj(file, bucket_name, remote_path)
            response = f"https://{bucket_name}.s3.amazonaws.com/{remote_path}"

        # Guardar en la base de datos (SQLite)
        conn = sqlite3.connect('appdistribution.db')
        cursor = conn.cursor()

        # Consulta para contar las aplicaciones con el mismo nombre y versión
        query = "SELECT COUNT(*) FROM apps WHERE name = ? AND version = ?"
        cursor.execute(query, (appName, appVersion))
        build = cursor.fetchone()[0] + 1

        # Consulta para guardar aplicacion
        query = "INSERT INTO apps (name, version, build, uuid) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (appName, appVersion, build, appId))

        conn.commit()
        conn.close()

    except NoCredentialsError:
        response = "No se encontraron credenciales de AWS. Asegúrate de configurarlas correctamente."

    except Exception as e:
        response = f"Error al subir el archivo a S3: {str(e)}"

    return jsonify({"mensaje": response})


def get_download_url(uuid):
    s3_client = boto3.client('s3')

    response = s3_client.list_objects_v2(
        Bucket="appdistribution",
        Prefix=uuid
    )

    if 'Contents' in response:
        for obj in response['Contents']:
            object_key = obj['Key']

            # Obtiene la extensión del archivo
            extension = get_extension(object_key)
            url = os.path.join(REPOSITORY_PATH, object_key)

            # Comprueba si la extensión es .apk
            if extension == 'apk':
                return url
            # Comprueba si la extensión es .ipa o .plist
            elif extension in ('plist'):
                return f"itms-services://?action=download-manifest&url={url}"
    else:
        print("La carpeta está vacía o no existe.")
        return None


def get_extension(filename):
    return filename.split('.')[-1].lower()


if __name__ == '__main__':
    application.run(debug=True)

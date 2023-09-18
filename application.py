from flask import Flask, jsonify
import uuid
import os

application = Flask(__name__)

# Directorio donde se almacenan las aplicaciones
CARPETA_APLICACIONES = 'uploads'
RUTA_API = 'https://127.0.0.1:5000'
IMAGEN_IOS = "ios.jpg"


@application.route('/')
def hello_world():
    return 'Hello World!'


@application.route('/metadata', methods=['GET'])
def get_metadata():
    # Generar un UUID para la carpeta única
    carpeta_uuid = str(uuid.uuid4())
    app_url = os.path.join(RUTA_API, CARPETA_APLICACIONES, carpeta_uuid)
    image_url = os.path.join(RUTA_API, CARPETA_APLICACIONES, IMAGEN_IOS)

    return jsonify({
        "appId": carpeta_uuid,
        "appUrl": app_url,
        "imageUrl": image_url
    })


if __name__ == '__main__':
    application.run(debug=True)

from flask import Flask, jsonify
import uuid
import os

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


if __name__ == '__main__':
    application.run(debug=True)

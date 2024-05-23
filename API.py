from flask import Flask, jsonify, request, send_file
from PIL import Image
import numpy as np
from sklearn.decomposition import PCA
import io
import os

app = Flask(__name__)

@app.route('/API/resize', methods=['POST'])
def resize():
    file = request.files['image']
    print("We got file")
    if file:
        image = Image.open(file.stream)
        image_gray = image.convert('L')
        
        image_arr = np.array(image_gray)
        flattened_image = image_arr.flatten()

        pca = PCA(n_components=0.99)
        pca.fit(flattened_image.reshape(-1, 1))


        transformed_image = pca.transform(flattened_image.reshape(-1, 1))
        reconstructed_image = pca.inverse_transform(transformed_image)

        reconstructed_image = reconstructed_image.reshape(image_arr.shape)
        reconstructed_image = np.clip(reconstructed_image, 0, 255)
        reconstructed_image = reconstructed_image.astype(np.uint8)

        output_image = Image.fromarray(reconstructed_image)
        byte_io = io.BytesIO()
        output_image.save(byte_io, 'JPEG')
        byte_io.seek(0)

        return send_file(byte_io, mimetype='image/jpeg')

UPLOAD_FOLDER = os.path.expanduser("~/Gallery")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith((".jpg", ".png", ".docx")):
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"message": f"File {filename} uploaded successfully!"}), 200

    return jsonify({"error": "Invalid file type"}), 400


@app.route('/')
def index():
    return 'Welcome to Piyush API'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

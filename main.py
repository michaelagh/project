from flask import Flask, render_template, jsonify, request
from PIL import Image
import io
import base64
from ves import generate_image_from_ves  

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render():
    data = request.json
    ves_code = data.get('code')

    with open("ves_code.txt", "w") as f:
        f.write(ves_code)

    obr = generate_image_from_ves(ves_code)

    img_io = io.BytesIO()
    obr.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    return jsonify({"image": img_base64})

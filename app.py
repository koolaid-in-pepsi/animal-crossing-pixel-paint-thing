from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from PIL import Image
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Define the color palette
PALETTE = [
    (255, 0, 0, 255),      # Red
    (255, 165, 0, 255),    # Orange
    (255, 255, 0, 255),    # Yellow
    (57, 255, 20, 255),    # Neon
    (0, 255, 0, 255),      # Green
    (173, 216, 230, 255),  # Light Blue
    (0, 128, 255, 255),    # Cool Blue
    (0, 0, 255, 255),      # Blue
    (128, 0, 128, 255),    # Purple
    (255, 192, 203, 255),  # Pink
    (255, 218, 185, 255),  # Peach
    (165, 42, 42, 255),    # Brown
    (255, 255, 255, 255),  # White
    (128, 128, 128, 255),  # Grey
    (0, 0, 0, 255),        # Black
    (0, 0, 0, 0),          # Transparent
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def closest_color(pixel, palette):
    distances = np.sqrt(np.sum((np.array(palette) - pixel) ** 2, axis=1))
    return palette[np.argmin(distances)]

def quantize_image(image, palette):
    image = image.convert('RGBA')
    pixel_data = np.array(image)
    quantized_data = np.zeros_like(pixel_data)

    for i in range(pixel_data.shape[0]):
        for j in range(pixel_data.shape[1]):
            quantized_data[i, j] = closest_color(pixel_data[i, j], palette)
    
    return Image.fromarray(quantized_data, 'RGBA')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            x = int(request.form.get('x', 0))
            y = int(request.form.get('y', 0))
            width = int(request.form.get('width', 64))
            height = int(request.form.get('height', 64))

            with Image.open(file_path) as img:
                img = img.resize((width, height), Image.ANTIALIAS)
                img = img.crop((x, y, x + 64, y + 64))
                img = quantize_image(img, PALETTE)
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_' + filename)
                img.save(output_path)

            return redirect(url_for('uploaded_file', filename='output_' + filename))

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

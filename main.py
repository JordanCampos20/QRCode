from flask import Flask, flash, request, redirect, url_for, render_template
import os
import qrcode
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

try:
    os.makedirs("static/uploads/")
    os.makedirs("static/Render/QRCode/")
    UPLOAD_FOLDER = 'static/uploads/'
    RENDER_FOLDER = 'static/Render/QRCode/'
except FileExistsError:
    UPLOAD_FOLDER = 'static/uploads/'
    RENDER_FOLDER = 'static/Render/QRCode/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RENDER_FOLDER'] = RENDER_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    url = request.form.get('url')
    name = request.form.get('name')

    if file.filename == '':
        flash('No image selected for create the QR Code')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filenamesave = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filenamesave))
        try:
            os.makedirs("static/uploads/")
            logo = Image.open(f'static/uploads/{filenamesave}')
        except FileExistsError:
            logo = Image.open(f'static/uploads/{filenamesave}')
        basewidth = 75
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        qr_big = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr_big.add_data(url)
        qr_big.make()
        img_qr_big = qr_big.make_image(fill_color='black', back_color='white').convert('RGB')
        pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)
        img_qr_big.paste(logo, pos)
        full_filename = os.path.join(app.config['RENDER_FOLDER'], name)
        try:
            os.makedirs("static/Render/QRCode/")
            filenamefinal = img_qr_big.save(f'static/Render/QRCode/{name}.png')
            flash('QR Code created successfully and shown below. \n right click on the image to save')
            return render_template('index.html', filename=full_filename)
        except FileExistsError:
            filenamefinal = img_qr_big.save(f'static/Render/QRCode/{name}.png')
            flash('QR Code created successfully and shown below. \n right click on the image to save')
            return render_template('index.html', filename=full_filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/<filename>.png')
def display_image(filename):
    return redirect(url_for('static', filename='Render/QRCode/' + filename + '.png'), code=301)


if __name__ == "__main__":
    app.run(debug=True)
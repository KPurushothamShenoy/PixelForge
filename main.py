from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2
import os
import numpy as np  # Import NumPy

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sepia_tone(img):
    # Define sepia transformation matrix
    sepia_matrix = np.array([[0.393, 0.769, 0.189],
                             [0.349, 0.686, 0.168],
                             [0.272, 0.534, 0.131]])
    # Apply sepia transformation
    sepia_img = cv2.transform(img, sepia_matrix)
    return sepia_img

def black_and_white(img):
    # Convert image to grayscale
    bw_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return bw_img

def duotone(img, color1, color2):
    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply duotone effect
    duotone_img = np.zeros_like(img)
    duotone_img[:, :, 0] = gray_img * color1[0] + (1 - gray_img) * color2[0]
    duotone_img[:, :, 1] = gray_img * color1[1] + (1 - gray_img) * color2[1]
    duotone_img[:, :, 2] = gray_img * color1[2] + (1 - gray_img) * color2[2]
    return duotone_img

def monochrome(img, hue):
    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply monochrome effect
    monochrome_img = np.zeros_like(img)
    monochrome_img[:, :, 0] = hue
    monochrome_img[:, :, 1] = gray_img
    monochrome_img[:, :, 2] = gray_img
    return monochrome_img

def cyanotype(img):
    # Apply cyanotype effect
    cyan_img = np.zeros_like(img)
    cyan_img[:, :, 0] = 255  # Set blue channel to maximum
    cyan_img[:, :, 1] = 255 - img[:, :, 0]  # Set green channel to complement of red channel
    cyan_img[:, :, 2] = 255 - img[:, :, 0]  # Set red channel to complement of red channel
    return cyan_img

def process_image(filename, operation):
    new_filename = ''
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if operation == "cgray":
        img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        new_filename = f"static/{filename}"
        cv2.imwrite(new_filename, img_processed)
    elif operation == "cwebp":
        new_filename = f"static/{filename.split('.')[0]}.webp"
        cv2.imwrite(new_filename, img)
    elif operation == "cjpg":
        new_filename = f"static/{filename.split('.')[0]}.jpg"
        cv2.imwrite(new_filename, img)
    elif operation == "cpng":
        new_filename = f"static/{filename.split('.')[0]}.png"
        cv2.imwrite(new_filename, img)
    elif operation == "edge":
        # Perform edge detection
        img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(img_processed, 100, 200)
        new_filename = f"static/{filename.split('.')[0]}_edges.jpg"
        cv2.imwrite(new_filename, edges)
    elif operation == "sepia":
        sepia_img = sepia_tone(img)
        new_filename = f"static/{filename.split('.')[0]}_sepia.jpg"
        cv2.imwrite(new_filename, sepia_img)
    elif operation == "bw":
        bw_img = black_and_white(img)
        new_filename = f"static/{filename.split('.')[0]}_bw.jpg"
        cv2.imwrite(new_filename, bw_img)
    elif operation == "duotone":
        duotone_img = duotone(img, (255, 0, 0), (0, 255, 255))  # Example duotone colors: red and yellow
        new_filename = f"static/{filename.split('.')[0]}_duotone.jpg"
        cv2.imwrite(new_filename, duotone_img)
    elif operation == "monochrome":
        monochrome_img = monochrome(img, 128)  # Example monochrome hue: gray
        new_filename = f"static/{filename.split('.')[0]}_monochrome.jpg"
        cv2.imwrite(new_filename, monochrome_img)
    elif operation == "cyanotype":
        cyanotype_img = cyanotype(img)
        new_filename = f"static/{filename.split('.')[0]}_cyanotype.jpg"
        cv2.imwrite(new_filename, cyanotype_img)
    return new_filename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = process_image(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'> here</a>")
            return render_template("index.html")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

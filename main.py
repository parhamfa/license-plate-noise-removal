import os
import uuid
import cv2
import numpy as np

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# --------------------
# CREATE/CONFIG FOLDERS
# --------------------
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
for folder in (UPLOAD_FOLDER, OUTPUT_FOLDER):
    if not os.path.exists(folder):
        os.makedirs(folder)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# --------------------
# GLOBAL STATE (DEMO ONLY)
# --------------------
image_paths = []    # list of uploaded filenames
current_index = 0   # index of currently displayed image
# For each image:
# {
#   "filterName": "None" or "Pipeline",
#   "tempFilename": "temp_...",
#   "finalImage": <OpenCV np.array or None>
# }
images_data = {}

# --------------------
# HELPER FUNCTIONS
# --------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_image_cv2(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return cv2.imread(path)

def save_image_cv2(image, filename, folder):
    path = os.path.join(folder, filename)
    cv2.imwrite(path, image)

# --------------------
# FILTER FUNCTIONS
# --------------------
def apply_no_filter(image, **kwargs):
    return image.copy()

def apply_gaussian_blur(image, **kwargs):
    return cv2.GaussianBlur(image, (5, 5), 0)

def apply_median_blur(image, **kwargs):
    return cv2.medianBlur(image, 5)

def apply_bilateral_filter(image, **kwargs):
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

# --- MANUAL THRESHOLD ---
def apply_manual_threshold(image, **kwargs):
    """
    threshold param: integer, e.g. 128
    """
    thr_val = int(kwargs.get('threshold', 128))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binarized = cv2.threshold(gray, thr_val, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(binarized, cv2.COLOR_GRAY2BGR)

# --- OTSU THRESHOLD ---
def apply_otsu_threshold(image, **kwargs):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binarized = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return cv2.cvtColor(binarized, cv2.COLOR_GRAY2BGR)

# --- ADAPTIVE THRESHOLD ---
def apply_adaptive_threshold(image, **kwargs):
    """
    blockSize: odd integer, e.g. 11
    C: constant subtracted from mean, e.g. 2
    """
    block_size = int(kwargs.get('blockSize', 11))
    c_val = float(kwargs.get('C', 2))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use Gaussian weighted method and invert
    binarized = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c_val
    )
    return cv2.cvtColor(binarized, cv2.COLOR_GRAY2BGR)

# --- NON-LOCAL MEANS ---
def apply_non_local_means(image, **kwargs):
    h = float(kwargs.get('hStrength', 10.0))
    return cv2.fastNlMeansDenoisingColored(image, None, h, h, 7, 21)

# --- CLAHE ---
def apply_clahe(image, **kwargs):
    clip_limit = float(kwargs.get('clipLimit', 2.0))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8,8))
    result = clahe.apply(gray)
    return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

# --- GAMMA CORRECTION ---
def apply_gamma_correction(image, **kwargs):
    gamma = float(kwargs.get('gamma', 1.5))
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        lookUpTable[0,i] = np.clip((i / 255.0)**(1.0 / gamma)*255.0, 0, 255)
    return cv2.LUT(image, lookUpTable)

# --- UNSHARP MASK ---
def apply_unsharp_mask(image, **kwargs):
    sigma = float(kwargs.get('sigma', 3.0))
    strength = float(kwargs.get('strength', 1.5))
    blur = cv2.GaussianBlur(image, (0, 0), sigma)
    sharpened = cv2.addWeighted(image, 1 + strength, blur, -strength, 0)
    return sharpened

# Example "Auto Enhance" pipeline
def auto_enhance_pipeline(original_image):
    img = apply_gamma_correction(original_image, gamma=1.2)
    img = apply_non_local_means(img, hStrength=10.0)
    img = apply_unsharp_mask(img, sigma=3.0, strength=1.0)
    img = apply_adaptive_threshold(img, blockSize=11, C=2)
    return img

# --------------------
# FILTERS DICT
# --------------------
FILTERS = {
    "None": apply_no_filter,
    "Gaussian Blur": apply_gaussian_blur,
    "Median Blur": apply_median_blur,
    "Bilateral Filter": apply_bilateral_filter,

    "Manual Threshold": apply_manual_threshold,
    "Otsu Threshold": apply_otsu_threshold,
    "Adaptive Threshold": apply_adaptive_threshold,

    "Non-Local Means": apply_non_local_means,
    "CLAHE": apply_clahe,
    "Gamma Correction": apply_gamma_correction,
    "Unsharp Mask": apply_unsharp_mask,
    "Auto Enhance": auto_enhance_pipeline
}

# --------------------
# ROUTES
# --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global image_paths, current_index, images_data

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({"status": "error", "message": "No files uploaded."}), 400

    # Clear old data
    image_paths = []
    current_index = 0
    images_data.clear()

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))

            image_paths.append(unique_name)
            images_data[unique_name] = {
                "filterName": "None",
                "tempFilename": None,
                "finalImage": None
            }

    return jsonify({"status": "success", "message": "Files uploaded successfully."})

@app.route('/current-image', methods=['GET'])
def get_current_image():
    global current_index
    if not image_paths:
        return jsonify({"status": "error", "message": "No images available."}), 400

    filename = image_paths[current_index]
    data_for_image = images_data.get(filename, {})

    return jsonify({
        "status": "success",
        "filename": filename,
        "currentIndex": current_index,
        "totalImages": len(image_paths),
        "filterName": data_for_image.get("filterName", "None")
    })

@app.route('/image/<path:filename>')
def serve_image(filename):
    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # no-cache headers
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/apply-filter', methods=['POST'])
def apply_filter():
    global current_index
    if not image_paths:
        return jsonify({"status": "error", "message": "No images to filter."}), 400

    filter_name = request.form.get('filterName', 'None')
    filename = image_paths[current_index]

    # Collect extra params
    extra_params = {
        "threshold": request.form.get("threshold"),
        "blockSize": request.form.get("blockSize"),
        "C": request.form.get("C"),
        "hStrength": request.form.get("hStrength"),
        "clipLimit": request.form.get("clipLimit"),
        "gamma": request.form.get("gamma"),
        "sigma": request.form.get("sigma"),
        "strength": request.form.get("strength")
    }
    # Convert to float/int if possible
    for k, v in list(extra_params.items()):
        if v is None:
            extra_params.pop(k)
        else:
            try:
                # threshold or blockSize might need int
                if k in ("threshold", "blockSize"):
                    extra_params[k] = int(float(v))  # handle "128" or "128.0"
                else:
                    extra_params[k] = float(v)
            except:
                extra_params.pop(k)

    image = load_image_cv2(filename)
    if image is None:
        return jsonify({"status": "error", "message": "Could not load image."}), 400

    func = FILTERS.get(filter_name, apply_no_filter)
    if filter_name == "Auto Enhance":
        # ignoring extra params for demonstration
        processed = func(image)
    else:
        processed = func(image, **extra_params)

    temp_filename = "temp_" + filename
    save_image_cv2(processed, temp_filename, app.config['UPLOAD_FOLDER'])

    images_data[filename]["filterName"] = filter_name
    images_data[filename]["tempFilename"] = temp_filename

    return jsonify({
        "status": "success",
        "processedFilename": temp_filename
    })

@app.route('/apply-pipeline', methods=['POST'])
def apply_pipeline():
    global current_index
    if not image_paths:
        return jsonify({"status": "error", "message": "No images loaded."}), 400

    data = request.get_json()
    if not data or "steps" not in data:
        return jsonify({"status": "error", "message": "Invalid pipeline data."}), 400

    pipeline_steps = data["steps"]
    filename = image_paths[current_index]
    original_image = load_image_cv2(filename)
    if original_image is None:
        return jsonify({"status": "error", "message": "Could not load image."}), 400

    processed = original_image
    for step in pipeline_steps:
        filter_name = step.get("filterName", "None")
        params = step.get("params", {})
        for k, v in list(params.items()):
            # threshold / blockSize might need int
            if k in ("threshold", "blockSize"):
                params[k] = int(float(v))
            else:
                params[k] = float(v) if v is not None else v

        filter_func = FILTERS.get(filter_name, apply_no_filter)
        processed = filter_func(processed, **params)

    temp_filename = f"temp_{filename}"
    save_image_cv2(processed, temp_filename, app.config['UPLOAD_FOLDER'])

    images_data[filename]["filterName"] = "Pipeline"
    images_data[filename]["tempFilename"] = temp_filename

    return jsonify({
        "status": "success",
        "processedFilename": temp_filename
    })

@app.route('/confirm-filter', methods=['POST'])
def confirm_filter():
    global current_index
    if not image_paths:
        return jsonify({"status": "error", "message": "No images loaded."}), 400

    filename = image_paths[current_index]
    temp_filename = images_data[filename]["tempFilename"]
    if not temp_filename or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)):
        return jsonify({"status": "error", "message": "No preview image to confirm."}), 400

    processed_image = load_image_cv2(temp_filename)
    if processed_image is None:
        return jsonify({"status": "error", "message": "Could not load preview image."}), 400

    images_data[filename]["finalImage"] = processed_image

    return jsonify({
        "status": "success",
        "message": f"Filter (or pipeline) confirmed for image {filename}."
    })

@app.route('/next-image', methods=['POST'])
def next_image():
    global current_index
    if not image_paths:
        return jsonify({"status": "error", "message": "No images loaded."}), 400

    if current_index < len(image_paths) - 1:
        current_index += 1

    return jsonify({"status": "success", "currentIndex": current_index})

@app.route('/prev-image', methods=['POST'])
def prev_image():
    global current_index
    if not image_paths:
        return jsonify({"status": "error", "message": "No images loaded."}), 400

    if current_index > 0:
        current_index -= 1

    return jsonify({"status": "success", "currentIndex": current_index})

@app.route('/export', methods=['GET'])
def export_images():
    confirmed_count = 0
    for filename, data in images_data.items():
        if data["finalImage"] is not None:
            save_image_cv2(data["finalImage"], filename, app.config['OUTPUT_FOLDER'])
            confirmed_count += 1

    if confirmed_count == 0:
        return jsonify({
            "status": "error",
            "message": "No images have been confirmed yet."
        }), 400

    return jsonify({
        "status": "success",
        "message": f"Exported {confirmed_count} images to '{OUTPUT_FOLDER}' folder."
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)

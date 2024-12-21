License Plate Noise Removal & Enhancement
A Flask + OpenCV web application to improve the readability of vehicle license plates under challenging conditions (noise, poor lighting, etc.). Users can apply single filters or build a pipeline of multiple filters (including thresholding, denoising, contrast enhancement, etc.) and then preview and confirm results before exporting.

Table of Contents
Features
Technologies Used
Installation
Usage
Project Structure
Available Filters
Noise Removal
Thresholding
Contrast & Brightness
Edge Enhancement
Auto Enhance
Screenshots
License
Features
Upload Multiple Images: Easily select one or more vehicle images.
Single Filter Mode: Pick a single filter (e.g., Median Blur) and apply it with optional parameters.
Pipeline Mode: Stack multiple filters in sequence (e.g. Gamma Correction → Non-Local Means → Otsu Threshold).
Preview & Confirm: See immediate results in the browser; confirm if the outcome is acceptable.
Export: Save all confirmed final images to a designated output folder.
Thresholding: Includes Manual (fixed value), Otsu (auto), and Adaptive threshold methods.
Technologies Used
Python 3.x
Flask (web framework)
OpenCV (image processing)
NumPy (array/matrix operations)
Bootstrap (optional for styling)
HTML / CSS / JavaScript (front end)
Installation
Clone this repository:

bash
Copy code
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Install dependencies (preferably in a virtual environment):

bash
Copy code
pip install -r requirements.txt
Make sure you have flask, opencv-python, and numpy in your requirements file.

Run the Flask app:

bash
Copy code
python app.py
Open your browser and navigate to:
http://127.0.0.1:5000/
(or whatever host/port you have configured)

Usage
Upload Images:

Click Choose Files and select one or more images (JPG, PNG, BMP, etc.).
Click Upload.
View & Navigate:

The first image appears in the Image Container.
Use Previous / Next to switch between uploaded images.
Single Filter:

Select a filter from the dropdown (e.g., Manual Threshold).
Adjust parameters (if any), like threshold value.
Click Preview Filter to see the result.
If satisfied, click Confirm.
Multi-Filter Pipeline:

Choose a filter from the pipeline dropdown.
Click Configure / Show Params to reveal its parameter panel.
Set your desired values, click Add to Pipeline.
Repeat for more steps if desired.
Click Preview Pipeline to apply them in sequence.
Confirm if the final preview is acceptable.
Export:

Once you have confirmed results for some or all images, click Export to save them into an output/ folder.
Project Structure
php
Copy code
.
├── app.py                # Flask backend
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css     # Basic styling
│   └── js/
│       └── script.js     # Front-end JavaScript (AJAX + UI logic)
├── uploads/              # Temporary folder for uploaded images
├── output/               # Folder for exported (confirmed) images
└── README.md             # This file
app.py contains:

Routes for uploading images, applying filters, pipeline management, etc.
Filter methods (e.g., thresholding, denoising, gamma correction)
Global state (for demonstration) storing images, current index, final results.
templates/index.html:

The main user interface with upload form, filter dropdowns, parameter panels, etc.
static/js/script.js:

Uses AJAX to communicate with Flask routes without reloading the page.
Implements preview, confirm, navigation, and the pipeline logic.
Available Filters
Noise Removal
Gaussian Blur
Median Blur
Bilateral Filter
Non-Local Means
Thresholding
Manual Threshold (user sets a fixed value, 0-255)
Otsu Threshold (automatic global threshold based on image histogram)
Adaptive Threshold (local threshold for uneven lighting, adjustable block size & constant C)
Contrast & Brightness
CLAHE (Contrast-Limited Adaptive Histogram Equalization)
Gamma Correction (tweak brightness curve)
Edge Enhancement
Unsharp Mask (sharpen details by subtracting blurred image from original)
Auto Enhance
A predefined pipeline that applies multiple steps in a row (e.g., gamma correction → denoising → unsharp → threshold).
Screenshots (Optional)
(Add screenshots or GIFs of your web UI showing an image before/after, filter selection, pipeline preview, etc.)

License (Optional)
(Choose a license, e.g., MIT, and place its text here. If this is a private/academic project, you can omit or adjust accordingly.)

Enjoy using the License Plate Noise Removal & Enhancement Web App! Feel free to open an issue or submit pull requests for improvements.

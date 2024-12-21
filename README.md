
# License Plate Noise Removal

A **Flask + OpenCV** web application to improve readability of vehicle license plates in images with noise, poor lighting, or other challenges. Users can apply **single filters** or **build a filter pipeline**, preview results in real time, and then **export** the final processed images.

**Repo:** [github.com/parhamfa/license-plate-noise-removal](https://github.com/parhamfa/license-plate-noise-removal)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Available Filters](#available-filters)
- [Project Structure](#project-structure)
- [Screenshots (Optional)](#screenshots-optional)
- [License (Optional)](#license-optional)

---

## Overview

This application focuses on **noise removal** and **image enhancement** techniques specifically for license plate images. It includes:

1. Denoising filters (Gaussian, Median, Bilateral, Non-Local Means)  
2. Thresholding methods (Manual, Otsu, Adaptive)  
3. Contrast enhancements (CLAHE, Gamma Correction)  
4. An **edge enhancement** step (Unsharp Mask)  
5. An **Auto Enhance** pipeline that combines multiple methods automatically.

---

## Features

1. **Multiple Image Upload**: Select one or more images of license plates.  
2. **Single Filter Mode**: Choose a single filter, preview its effect, and confirm if you like the result.  
3. **Pipeline Mode**: Add several filters in sequence (e.g., `Non-Local Means` → `Gamma Correction` → `Otsu Threshold`), then preview the final outcome.  
4. **Threshold Variants**:  
   - **Manual** (user-specified threshold value)  
   - **Otsu** (auto global threshold)  
   - **Adaptive** (localized threshold)  
5. **Confirm & Export**: Save finalized images to an `output/` folder for further use (e.g., OCR).

---

## Technologies Used

- **Python 3.x**  
- **Flask** (web framework)  
- **OpenCV** (image processing)  
- **NumPy** (matrix/array operations)  
- **Bootstrap 5** (optional styling)  
- **HTML / CSS / JavaScript** (front end)

---

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/parhamfa/license-plate-noise-removal.git
   cd license-plate-noise-removal
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Flask app**:
   ```bash
   python main.py
   ```
4. **Open** [http://127.0.0.1:8000](http://127.0.0.1:8000/) in your browser.

---

## Usage

1. **Upload Images**  
   - Click the **Choose Files** button and select your images.  
   - Click **Upload** to send them to the server.

2. **Navigate Images**  
   - The first image is displayed immediately.  
   - Use **Previous** / **Next** to switch between images.

3. **Single Filter**  
   - From the dropdown, pick a filter (e.g., `Manual Threshold`).  
   - Adjust parameters if needed (e.g., threshold value).  
   - Click **Preview Filter** to see the updated image.  
   - If satisfied, click **Confirm**.

4. **Multi-Filter Pipeline**  
   - Choose a filter from the **pipeline** dropdown.  
   - Click **Configure / Show Params**, fill in parameter values.  
   - Click **Add to Pipeline**.  
   - Repeat for more filters, if desired.  
   - Click **Preview Pipeline** to see the final stacked result.  
   - **Confirm** when it’s good.

5. **Export**  
   - Click **Export** to save all confirmed images into `output/`.

---

## Available Filters

- **Noise Removal**  
  - Gaussian Blur  
  - Median Blur  
  - Bilateral Filter  
  - Non-Local Means  

- **Thresholding**  
  - Manual Threshold (fixed value)  
  - Otsu Threshold (automatic)  
  - Adaptive Threshold (localized)  

- **Contrast & Brightness**  
  - CLAHE (Localized histogram equalization)  
  - Gamma Correction (Adjust brightness curve)

- **Edge Enhancement**  
  - Unsharp Mask (sharpen edges)

- **Auto Enhance**  
  - A built-in pipeline combining multiple filters automatically.

---

## Project Structure

```
license-plate-noise-removal/
├── app.py                # Main Flask backend
├── requirements.txt      # Dependencies
├── templates/
│   └── index.html        # Main UI (HTML)
├── static/
│   ├── css/
│   │   └── style.css     # Basic styling
│   └── js/
│       └── script.js     # Front-end AJAX & UI logic
├── uploads/              # Temporary folder for uploads
├── output/               # Final processed images saved here
└── README.md             # This file
```

---

**Happy filtering!**  
Feel free to open an issue or pull request if you encounter any problems or have ideas for new filters.

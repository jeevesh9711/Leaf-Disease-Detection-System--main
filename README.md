# Leaf Disease Detection System 🌱💻

## Overview

The Leaf Disease Detection System is a Flask-based web application that detects plant leaf diseases using a PyTorch ResNet18 model. It combines image classification, severity analysis, secure session management, simple blockchain logging, and an ERP-style dashboard to track analyses and diagnosis history.

## What This Project Includes

- **Web app interface** for leaf image upload and disease diagnosis.
- **AI prediction engine** using a ResNet18 model with 5 disease classes.
- **Severity analysis** and treatment recommendations for detected diseases.
- **Simple blockchain ledger** to record prediction transactions.
- **ERP dashboard** that displays analysis records and disease distribution.
- **Firebase support** for optional cloud storage of analysis records.
- **API endpoint** for programmatic image prediction requests.

## Supported Diseases

- Anthracnose
- Bacterial Blight
- Cercospora Leaf Spot
- Powdery Mildew
- Shot Hole Disease

## Files and Structure

- `integrated-leaf-disease-project.py` – Main Flask application entrypoint.
- `my_leaf_disease_model.pth` – Trained model weights used for prediction.
- `firebase-key.json` – Firebase service account credentials (or placeholder file).
- `templates/` – HTML templates for the web UI and dashboard.
- `requirements.txt` – Python dependencies.

## Features

- **Image-based disease classification** with confidence scores.
- **Leaf validation** to reject non-leaf image uploads.
- **Severity assessment** with risk level, affected area, and action recommendations.
- **Blockchain recording** of user prediction events.
- **ERP-style analytics** for total records, block count, and disease counts.
- **API access** via `/api/predict` with API key validation.
- **Automatic placeholder generation** for missing `firebase-key.json` and dummy model file.

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python integrated-leaf-disease-project.py
   ```

3. **Open the app**:
   - Visit `http://127.0.0.1:5000` in your browser.

4. **Dashboard**:
   - Visit `http://127.0.0.1:5000/dashboard` to see ERP records and blockchain data.

## API Usage

Endpoint:
- `POST /api/predict`

Headers:
- `X-API-Key: demo_api_key`
- `X-User-ID: your_user_id` (optional)

Body:
- Multipart form with a `file` field containing the leaf image.

Example using `curl`:
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "X-API-Key: demo_api_key" \
  -F "file=@path/to/leaf.jpg"
```

## Notes

- The application will create a placeholder `firebase-key.json` if none exists.
- If `my_leaf_disease_model.pth` is missing, the app creates a dummy model for testing. Use your trained model file for accurate predictions.
- Cloud features are optional; the app will still run locally if Firebase initialization fails.

## Dependencies

Key packages used:
- `Flask`
- `Flask-Session`
- `torch`
- `torchvision`
- `Pillow`
- `firebase-admin`
- `requests`

## Contribution

Contributions are welcome. Feel free to open an issue or submit a pull request with enhancements, bug fixes, or new disease support.

## License

This project is released under the MIT License.

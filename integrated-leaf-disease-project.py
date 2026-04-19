# app.py - Main Flask Application
import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import hashlib
import uuid
import base64
import datetime
import requests
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from flask_session import Session
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ------ CLOUD COMPUTING INTEGRATION ------
# Initialize Firebase (Cloud Database)
# Use a service account or set up with environment variables
try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    cloud_enabled = True
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}. Running without cloud features.")
    cloud_enabled = False

# ------ DEVICE AND MODEL SETUP ------
# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Define the class labels (your 5 leaf diseases)
classes = [
    'Anthracnose', 
    'Bacterial_Blight', 
    'Cercospora_Leaf_Spot', 
    'Powdery_Mildew', 
    'Shot_Hole_Disease'
]

# Disease information dictionary with solutions
disease_info = {
    'Anthracnose': {
        'description': 'A fungal disease that causes dark, sunken lesions on leaves, stems, flowers and fruits.',
        'solutions': [
            'Remove infected leaves and plant debris',
            'Apply fungicide sprays (copper-based or sulfur)',
            'Ensure good air circulation and avoid overhead watering',
            'Maintain proper spacing between plants',
            'Disinfect pruning tools between cuts'
        ]
    },
    'Bacterial_Blight': {
        'description': 'A bacterial infection causing water-soaked lesions that eventually turn brown.',
        'solutions': [
            'Prune and remove infected branches',
            'Apply copper-based bactericide sprays',
            'Avoid wetting foliage when watering',
            'Sterilize pruning equipment',
            'Practice crop rotation and proper sanitation'
        ]
    },
    'Cercospora_Leaf_Spot': {
        'description': 'A fungal disease characterized by circular spots with gray centers and dark borders.',
        'solutions': [
            'Remove and destroy infected leaves',
            'Apply systemic fungicides containing azoxystrobin',
            'Improve air circulation within the canopy',
            'Water at the base of plants to keep leaves dry',
            'Apply preventive fungicide sprays weekly'
        ]
    },
    'Powdery_Mildew': {
        'description': 'A fungal disease that appears as a white or gray powdery coating on leaf surfaces.',
        'solutions': [
            'Apply sulfur or neem oil sprays',
            'Remove heavily infected leaves',
            'Increase air circulation and reduce humidity',
            'Avoid excessive nitrogen fertilizer',
            'Spray with baking soda solution (1 tablespoon per gallon)'
        ]
    },
    'Shot_Hole_Disease': {
        'description': 'A fungal disease where small circular lesions fall out of leaves creating a "shot hole" appearance.',
        'solutions': [
            'Remove infected leaves from the plant and ground',
            'Apply preventive copper fungicide sprays',
            'Improve drainage and reduce leaf wetness',
            'Prune to enhance air flow',
            'Avoid working with wet plants to prevent spore spread'
        ]
    }
}

# Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ------ BLOCKCHAIN INTEGRATION ------
class SimpleBlockchain:
    def __init__(self):
        self.chain = []
        # Genesis block
        self.create_block(proof=1, previous_hash='0')
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': []
        }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def add_transaction(self, user_id, image_hash, prediction):
        """Add a transaction to the current block"""
        self.chain[-1]['transactions'].append({
            'user_id': user_id,
            'image_hash': image_hash,
            'prediction': prediction,
            'timestamp': str(datetime.datetime.now())
        })
        
    def hash_block(self, block):
        """Create SHA-256 hash of a block"""
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

# Initialize blockchain
blockchain = SimpleBlockchain()

# ------ CYBERSECURITY INTEGRATION ------
def secure_image_hash(image_bytes):
    """Create a secure hash of the image"""
    return hashlib.sha256(image_bytes).hexdigest()

def generate_user_token():
    """Generate a secure token for user session"""
    return base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8')

def get_disease_prediction(disease_name, weather_data):
    """Predict future disease progression and outcomes"""
    disease_predictions = {
        'Anthracnose': {
            'week_1': 'Initial lesions will expand to cover 10-20% of leaf area',
            'week_2': 'Disease spreads to new leaves; fruit may show dark sunken spots',
            'week_3': 'Severe defoliation begins; significant fruit damage expected',
            'long_term': 'Without treatment: Complete crop loss within 4-6 weeks in humid conditions',
            'seasonal': 'Peak infection during warm, wet spring and fall seasons',
            'recommendation': 'Start treatment immediately to prevent exponential spread'
        },
        'Bacterial_Blight': {
            'week_1': 'Water-soaked spots expand; lesions turn necrotic (brown)',
            'week_2': 'Lesions merge; entire branches may wilt and die back',
            'week_3': 'Cankers form on stems; branch death accelerates',
            'long_term': 'Without treatment: Plant may become permanently damaged or die within 3-4 weeks',
            'seasonal': 'Most severe in spring with frequent overhead rain',
            'recommendation': 'Prune affected branches immediately; drastic action required'
        },
        'Cercospora_Leaf_Spot': {
            'week_1': 'Circular spots appear on lower leaves; spots grow to 1cm diameter',
            'week_2': 'Centers turn gray; spots appear on middle canopy leaves',
            'week_3': 'Upper leaves affected; significant leaf yellowing and drop',
            'long_term': 'Without treatment: Defoliation within 5-8 weeks; reduced fruit quality',
            'seasonal': 'Progressive throughout growing season; worse in warm, humid conditions',
            'recommendation': 'Regular fungicide applications prevent severe outcomes'
        },
        'Powdery_Mildew': {
            'week_1': 'White powder appears on young leaves; spreads to new growth',
            'week_2': 'Powdery coating thickens; leaves curl and become distorted',
            'week_3': 'Entire canopy may appear white; fruit quality degrades',
            'long_term': 'Without treatment: Reduced photosynthesis leads to poor fruit development and smaller yields',
            'seasonal': 'Develops slowly in cool springs; accelerates in warm days with cool nights',
            'recommendation': 'Early treatment with sulfur or neem prevents widespread infection'
        },
        'Shot_Hole_Disease': {
            'week_1': 'Small circular lesions appear on older leaves',
            'week_2': 'Lesion centers fall out creating "shot holes"; trees look damaged',
            'week_3': 'Multiple holes per leaf; significant aesthetic damage',
            'long_term': 'Without treatment: Weak tree vigor; increased susceptibility to other diseases within 6-8 weeks',
            'seasonal': 'Most problematic in spring during cool, wet periods',
            'recommendation': 'Preventive copper sprays in early season prevent hole formation'
        }
    }
    
    return disease_predictions.get(disease_name, {
        'week_1': 'Disease will begin to show visible symptoms',
        'week_2': 'Symptoms will expand to larger leaf areas',
        'week_3': 'Significant damage expected without treatment',
        'long_term': 'Monitor plant closely for progression',
        'seasonal': 'Disease activity depends on weather conditions',
        'recommendation': 'Implement treatment plan immediately'
    })

def detect_disease_severity(image, disease_name):
    """Analyze image to determine disease severity level"""
    try:
        # Convert to grayscale for analysis
        gray = image.convert('L')

        # Get image dimensions
        width, height = gray.size
        total_pixels = width * height

        # Analyze pixel intensity distribution
        pixels = list(gray.getdata())
        dark_pixels = sum(1 for pixel in pixels if pixel < 100)  # Dark areas (potential disease)
        light_pixels = sum(1 for pixel in pixels if pixel > 200)  # Light areas

        # Calculate affected area percentage
        affected_percentage = (dark_pixels / total_pixels) * 100

        # Disease-specific severity thresholds
        severity_thresholds = {
            'Anthracnose': {'mild': 5, 'moderate': 15, 'severe': 25},
            'Bacterial_Blight': {'mild': 3, 'moderate': 10, 'severe': 20},
            'Cercospora_Leaf_Spot': {'mild': 8, 'moderate': 18, 'severe': 30},
            'Powdery_Mildew': {'mild': 10, 'moderate': 25, 'severe': 40},
            'Shot_Hole_Disease': {'mild': 2, 'moderate': 8, 'severe': 15}
        }

        thresholds = severity_thresholds.get(disease_name, {'mild': 5, 'moderate': 15, 'severe': 25})

        if affected_percentage <= thresholds['mild']:
            severity_level = 'Mild'
            severity_description = f'Less than {thresholds["mild"]:.1f}% of leaf area affected. Early stage disease.'
            action_required = 'Monitor closely, consider preventive treatment.'
            risk_level = 'Low'
        elif affected_percentage <= thresholds['moderate']:
            severity_level = 'Moderate'
            severity_description = f'{thresholds["mild"]:.1f}% to {thresholds["moderate"]:.1f}% of leaf area affected. Disease is progressing.'
            action_required = 'Immediate treatment recommended to prevent spread.'
            risk_level = 'Medium'
        else:
            severity_level = 'Severe'
            severity_description = f'More than {thresholds["moderate"]:.1f}% of leaf area affected. Advanced disease stage.'
            action_required = 'Urgent treatment required. Consider removing affected leaves.'
            risk_level = 'High'

        return {
            'severity_level': severity_level,
            'affected_percentage': affected_percentage,
            'description': severity_description,
            'action_required': action_required,
            'risk_level': risk_level,
            'thresholds': thresholds
        }

    except Exception as e:
        logger.error(f"Severity detection error: {e}")
        return {
            'severity_level': 'Unknown',
            'affected_percentage': 0,
            'description': 'Unable to determine severity',
            'action_required': 'Consult agricultural expert',
            'risk_level': 'Unknown',
            'thresholds': {'mild': 5, 'moderate': 15, 'severe': 25}
        }

# ------ ERP INTEGRATION ------
class SimpleERP:
    def __init__(self):
        self.records = []
    
    def add_analysis_record(self, user_id, prediction, confidence, timestamp):
        """Add analysis record to the ERP system"""
        record = {
            'record_id': str(uuid.uuid4()),
            'user_id': user_id,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': timestamp
        }
        self.records.append(record)
        
        # If cloud is enabled, store in Firestore
        if cloud_enabled:
            try:
                db.collection('analysis_records').add(record)
            except Exception as e:
                logger.error(f"Failed to save to Firestore: {e}")
        
        return record

# Initialize ERP system
erp_system = SimpleERP()

# ------ MODEL FUNCTIONS ------
def load_model():
    """Load the trained model"""
    try:
        model = models.resnet18(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(classes))

        model.load_state_dict(torch.load('my_leaf_disease_model.pth', map_location=device))
        model.to(device)
        model.eval()
        return model

    except Exception as e:
        logger.error(f"Error loading model: {e}")

        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(classes))
        model.to(device)
        model.eval()
        return model


# ✅ LOAD MODEL ONCE WHEN SERVER STARTS
model = load_model()

def predict_image(image_bytes, user_id):

    try:
        # Create image from bytes
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = transform(image).unsqueeze(0).to(device)

        # Get image hash
        image_hash = secure_image_hash(image_bytes)

        # Load model
        model = load_model()

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
            _, predicted = torch.max(outputs, 1)

        prediction = classes[predicted.item()]
        confidence = float(probabilities[predicted.item()]) * 100

        # Validate if the image is actually a leaf
        # If confidence is below 40%, it's likely not a leaf image
        if confidence < 30:
            return {
                "error": "The uploaded image does not appear to be a plant leaf. Please upload a clear image of a plant leaf for disease detection.",
                "is_leaf": False
            }

        # Blockchain record
        blockchain.add_transaction(user_id, image_hash, prediction)

        # ERP record
        timestamp = datetime.datetime.now().isoformat()
        erp_system.add_analysis_record(user_id, prediction, confidence, timestamp)

        # Top predictions
        class_probs = [(classes[i], float(probabilities[i]) * 100) for i in range(len(classes))]
        class_probs.sort(key=lambda x: x[1], reverse=True)

        # Get disease prediction
        disease_prediction = get_disease_prediction(prediction, {})

        # Analyze disease severity
        severity_analysis = detect_disease_severity(image, prediction)

        # Get disease details
        disease_details = disease_info.get(prediction, {})
        if isinstance(disease_details, dict):
            disease_description = disease_details.get('description', 'No information available')
            disease_solutions = disease_details.get('solutions', [])
        else:
            disease_description = disease_details
            disease_solutions = []

        return {
            "prediction": prediction,
            "confidence": confidence,
            "image_hash": image_hash,
            "blockchain_index": blockchain.get_previous_block()["index"],
            "all_predictions": class_probs[:3],
            "disease_info": disease_description,
            "disease_solutions": disease_solutions,
            "disease_prediction": disease_prediction,
            "severity_analysis": severity_analysis,
            "is_leaf": True
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")

        return {
            "error": f"Error processing image: {str(e)}",
            "is_leaf": False
        }
    
# ------ ROUTES ------
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for web application"""
    # Check for user session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['user_token'] = generate_user_token()
    
    result = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file uploaded')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')
        
        if file:
            img_bytes = file.read()
            result = predict_image(img_bytes, session['user_id'])
            
    # Get some ERP statistics for display
    stats = {
        'total_analyses': len(erp_system.records),
        'blockchain_blocks': len(blockchain.chain),
        'cloud_enabled': cloud_enabled
    }
            
    return render_template('index.html', result=result, stats=stats, disease_info=disease_info)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    # Simple API key validation for security
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != 'demo_api_key':
        return jsonify({'error': 'Invalid API key'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    user_id = request.headers.get('X-User-ID', 'api_user')
    img_bytes = file.read()
    result = predict_image(img_bytes, user_id)
    
    return jsonify(result)

@app.route('/dashboard')
def dashboard():
    """Simple ERP dashboard"""
    # Security check
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', 
                          records=erp_system.records,
                          blockchain=blockchain.chain)

# Create templates
def create_templates():
    """Create HTML templates for the application"""
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')


# Generate a simple Firebase key file if needed
def create_firebase_key():
    """Create a placeholder Firebase key file"""
    if not os.path.exists('firebase-key.json'):
        key_data = {
            "type": "service_account",
            "project_id": "leaf-disease-demo",
            "private_key_id": "placeholder",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKj\nMzEfYyjiWA4R4/M2bS1GB4t7NXp98C3SC6dVMvDuictGeurT8jNbvJZHtCSuYEvu\nNMoSfm76oqFvAp8Gy0iz5sxjZmSnXyCdPEovGhLa0VzMaQ8s+CLOyS56YyCFGeJZ\n-----END PRIVATE KEY-----\n",
            "client_email": "demo@leaf-disease-demo.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-q461q%40leaf-disease-demo.iam.gserviceaccount.com"
        }
        
        with open('firebase-key.json', 'w') as f:
            json.dump(key_data, f, indent=2)
        
        print("Created placeholder firebase-key.json file")
        print("For actual deployment, replace with your real Firebase credentials")

# Create a dummy model file for testing if the actual model is not available
def create_dummy_model():
    """Create a dummy model file for demonstration if needed"""
    if not os.path.exists('my_leaf_disease_model.pth'):
        try:
            print("Warning: Your custom model file 'my_leaf_disease_model.pth' is not found.")
            print("Creating a dummy model for testing purposes...")
            model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, len(classes))
            torch.save(model.state_dict(), 'my_leaf_disease_model.pth')
            print("Dummy model created successfully.")
            print("Replace this with your actual trained model file for accurate predictions.")
        except Exception as e:
            print(f"Could not create dummy model: {e}")
            print("You'll need to provide your actual trained model file.")

if __name__ == '__main__':
    # Setup necessary files
    create_templates()
    create_firebase_key()
    create_dummy_model()
    
    print("Starting Leaf Disease Detection Web App...")
    print("Using custom model with 5 diseases: Anthracnose, Bacterial_Blight, Cercospora_Leaf_Spot, Powdery_Mildew, Shot_Hole_Disease")
    print("Access the application at http://127.0.0.1:5000")
    print("\nThis application demonstrates:")
    print("1. Cloud Computing: Firebase integration for data storage")
    print("2. Cybersecurity: Secure sessions, image hashing, and API auth")
    print("3. Blockchain: Simple implementation for record verification")
    print("4. ERP: Integrated management of analysis records")


# Run the app
app.run(debug=True, host='0.0.0.0', port=5000)
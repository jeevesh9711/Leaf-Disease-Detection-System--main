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

# Disease information dictionary
disease_info = {
    'Anthracnose': 'A fungal disease that causes dark, sunken lesions on leaves, stems, flowers and fruits.',
    'Bacterial_Blight': 'A bacterial infection causing water-soaked lesions that eventually turn brown.',
    'Cercospora_Leaf_Spot': 'A fungal disease characterized by circular spots with gray centers and dark borders.',
    'Powdery_Mildew': 'A fungal disease that appears as a white or gray powdery coating on leaf surfaces.',
    'Shot_Hole_Disease': 'A fungal disease where small circular lesions fall out of leaves creating a "shot hole" appearance.'
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
        # Adjust model architecture as needed
        model = models.resnet18(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(classes))  # 5 classes
        
        # Change path to your model file
        model.load_state_dict(torch.load('my_leaf_disease_model.pth', map_location=device))
        model.to(device)
        model.eval()
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        # Fallback to a new untrained model for demo purposes
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(classes))
        model.to(device)
        model.eval()
        return model

def predict_image(image_bytes, user_id):
    """Process image and return prediction"""
    try:
        # Create image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        # Get image hash for security and blockchain
        image_hash = secure_image_hash(image_bytes)
        
        # Make prediction
        model = load_model()
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, 1)[0]
            _, predicted = torch.max(outputs, 1)
        
        prediction = classes[predicted.item()]
        confidence = float(probabilities[predicted.item()]) * 100
        
        # Record transaction in blockchain
        blockchain.add_transaction(user_id, image_hash, prediction)
        
        # Add record to ERP system
        timestamp = datetime.datetime.now().isoformat()
        erp_system.add_analysis_record(user_id, prediction, confidence, timestamp)
        
        # Create results
        class_probs = [(classes[i], float(probabilities[i]) * 100) for i in range(len(classes))]
        class_probs.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'image_hash': image_hash,
            'blockchain_index': blockchain.get_previous_block()['index'],
            'all_predictions': class_probs[:3],  # Top 3 predictions
            'disease_info': disease_info.get(prediction, "No additional information available.")
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {
            'error': str(e),
            'prediction': 'Error in processing',
            'confidence': 0
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
    
    # Create index.html
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Leaf Disease Detection System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
                
        h1, h2, h3, h4 {
            color: #2c7c4e;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .upload-form {
            margin: 20px 0;
            text-align: center;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .prediction {
            font-size: 24px;
            font-weight: bold;
            color: #2c7c4e;
        }
        .disease-info {
            background-color: #f0f8ff;
            border-left: 4px solid #4682b4;
            padding: 10px;
            margin: 10px 0;
        }
        .tech-box {
            background-color: #e6f7ff;
            border-left: 4px solid #1890ff;
            padding: 10px;
            margin: 10px 0;
        }
        .submit-btn {
            background-color: #2c7c4e;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .preview-container {
            margin: 20px auto;
            max-width: 300px;
            display: none;
        }
        #imagePreview {
            width: 100%;
            border-radius: 5px;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }
        .stat-card {
            flex: 1;
            min-width: 200px;
            background: #f0f8ff;
            margin: 5px;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .nav {
            text-align: right;
            margin-bottom: 20px;
        }
        .nav a {
            color: #2c7c4e;
            text-decoration: none;
            padding: 5px 10px;
        }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/dashboard">Dashboard</a>
    </div>
    
    <div class="container">
        <h1>Leaf Disease Detection System</h1>
        <h4>by, Ishaan Agarwal, Kairaa Kaur, Kunal Kumar Mishra, Abhimaniyu Sharma, Shivakshi Laroiya, Ayush chauhan</h4>
        
        <div class="upload-form">
            <form method="post" enctype="multipart/form-data">
                <p>Upload an image of a plant leaf to detect disease:</p>
                <input type="file" name="file" id="file" accept="image/*" onchange="previewImage()">
                <div class="preview-container" id="previewContainer">
                    <img id="imagePreview" src="#" alt="Image Preview">
                </div>
                <br><br>
                <button type="submit" class="submit-btn">Analyze Leaf</button>
            </form>
        </div>
        
        {% if error %}
        <div class="result" style="background-color: #ffebee;">
            <p>Error: {{ error }}</p>
        </div>
        {% endif %}
        
        {% if result %}
        <div class="result" style="background-color: #e8f5e9;">
            <h2>Analysis Results</h2>
            <p class="prediction">Diagnosis: {{ result.prediction|replace('_', ' ') }}</p>
            <p>Confidence: {{ "%.2f"|format(result.confidence) }}%</p>
            
            <div class="disease-info">
                <h3>Disease Information:</h3>
                <p>{{ result.disease_info }}</p>
            </div>
            
            {% if result.all_predictions %}
            <div>
                <h3>Other Possibilities:</h3>
                <ul>
                {% for disease, prob in result.all_predictions[1:] %}
                    <li>{{ disease|replace('_', ' ') }}: {{ "%.2f"|format(prob) }}%</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <div class="tech-box">
                <h3>Cybersecurity & Blockchain:</h3>
                <p>Image Hash: {{ result.image_hash }}</p>
                <p>Blockchain Record: Block #{{ result.blockchain_index }}</p>
                <p>Your secure session is active.</p>
            </div>
        </div>
        {% endif %}
        
        <div class="stats">
            <div class="stat-card">
                <h3>Cloud Status</h3>
                <p>{{ 'Connected' if stats.cloud_enabled else 'Local Mode' }}</p>
            </div>
            <div class="stat-card">
                <h3>Total Analyses</h3>
                <p>{{ stats.total_analyses }}</p>
            </div>
            <div class="stat-card">
                <h3>Blockchain Size</h3>
                <p>{{ stats.blockchain_blocks }} blocks</p>
            </div>
        </div>
    </div>
    
    <div class="container">
        <h2>Disease Information</h2>
        <div>
            {% for disease, info in disease_info.items() %}
            <div class="disease-info">
                <h3>{{ disease|replace('_', ' ') }}</h3>
                <p>{{ info }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="container">
        <h2>Technologies Used</h2>
        <div>
            <h3>Cloud Computing</h3>
            <p>Firebase Firestore for scalable data storage and retrieval.</p>
            
            <h3>Cybersecurity</h3>
            <p>Secure session management, image hashing, and API authentication.</p>
            
            <h3>Blockchain</h3>
            <p>Simple blockchain implementation to record and verify diagnosis history.</p>
            
            <h3>Enterprise Resource Planning (ERP)</h3>
            <p>Integrated system to manage and track all plant disease analyses.</p>
        </div>
    </div>
    
    <div class="footer">
        <p>This is created by, Ishaan Agarwal, Kairaa Kaur, Kunal Kumar Mishra, Abhimaniyu Sharma, Shivakshi Laroiya, Ayush chauhan</p>
    </div>

    <script>
        function previewImage() {
            const fileInput = document.getElementById('file');
            const previewContainer = document.getElementById('previewContainer');
            const previewImage = document.getElementById('imagePreview');
            
            if (fileInput.files && fileInput.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    previewContainer.style.display = 'block';
                }
                
                reader.readAsDataURL(fileInput.files[0]);
            }
        }
    </script>
</body>
</html>
        ''')
    
    # Create dashboard.html
    with open('templates/dashboard.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>ERP Dashboard - Leaf Disease Detection</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3 {
            color: #2c7c4e;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #e8f5e9;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .nav {
            text-align: right;
            margin-bottom: 20px;
        }
        .nav a {
            color: #2c7c4e;
            text-decoration: none;
            padding: 5px 10px;
        }
        .block-info {
            background-color: #e6f7ff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .disease-distribution {
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
    </div>
    
    <div class="container">
        <h1>ERP Dashboard</h1>
        <p>Enterprise Resource Planning System for Leaf Disease Detection</p>
        
        <h2>Analysis Records</h2>
        <table>
            <thead>
                <tr>
                    <th>Record ID</th>
                    <th>User ID</th>
                    <th>Prediction</th>
                    <th>Confidence</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {% for record in records %}
                <tr>
                    <td>{{ record.record_id[:8] }}...</td>
                    <td>{{ record.user_id[:8] }}...</td>
                    <td>{{ record.prediction|replace('_', ' ') }}</td>
                    <td>{{ "%.2f"|format(record.confidence) }}%</td>
                    <td>{{ record.timestamp }}</td>
                </tr>
                {% endfor %}
                {% if not records %}
                <tr>
                    <td colspan="5" style="text-align: center;">No records found. Analyze some leaves to create records!</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <div class="disease-distribution">
            <h2>Disease Distribution</h2>
            <div id="distributionChart" style="height: 300px; background: #f5f5f5; display: flex; align-items: flex-end; padding: 20px;">
                <!-- Placeholder for a real chart implementation -->
                {% set diseases = {'Anthracnose': 0, 'Bacterial_Blight': 0, 'Cercospora_Leaf_Spot': 0, 'Powdery_Mildew': 0, 'Shot_Hole_Disease': 0} %}
                
                {% for record in records %}
                    {% if record.prediction in diseases %}
                        {% set _ = diseases.update({record.prediction: diseases[record.prediction] + 1}) %}
                    {% endif %}
                {% endfor %}
                
                {% for disease, count in diseases.items() %}
                    <div style="margin-right: 10px; text-align: center;">
                        <div style="background-color: #4682b4; width: 40px; height: {{ count * 30 if count else 5 }}px;"></div>
                        <div style="font-size: 12px; margin-top: 5px; writing-mode: vertical-lr; transform: rotate(180deg);">
                            {{ disease|replace('_', ' ') }}
                        </div>
                        <div>{{ count }}</div>
                    </div>
                {% endfor %}
            </div>
        </div>
        
        <h2>Blockchain Ledger</h2>
        {% for block in blockchain %}
        <div class="block-info">
            <h3>Block #{{ block.index }}</h3>
            <p><strong>Timestamp:</strong> {{ block.timestamp }}</p>
            <p><strong>Previous Hash:</strong> {{ block.previous_hash }}</p>
            <p><strong>Proof:</strong> {{ block.proof }}</p>
            
            <h4>Transactions:</h4>
            {% if block.transactions %}
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Image Hash</th>
                        <th>Prediction</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tx in block.transactions %}
                    <tr>
                        <td>{{ tx.user_id[:8] }}...</td>
                        <td>{{ tx.image_hash[:8] }}...</td>
                        <td>{{ tx.prediction|replace('_', ' ') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No transactions in this block.</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        ''')

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
    
    # Create requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('''
Flask==2.0.1
Flask-Session==0.4.0
torch==2.0.0
torchvision==0.15.1
Pillow==9.0.0
firebase-admin==5.0.3
gunicorn==20.1.0
        '''.strip())
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
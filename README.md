# Leaf Disease Detection System 🌱💻

## Introduction 🌟

Welcome to the Leaf Disease Detection System, a comprehensive and innovative solution for identifying plant diseases through advanced image analysis 📸. This project seamlessly integrates cutting-edge technologies to provide a robust, secure, and efficient platform for agricultural diagnostics 🌟.

### Key Features 🎯

- **Cloud Computing Integration** ☁️: Leveraging Firebase Firestore for scalable data storage and retrieval, ensuring that analysis records are securely stored and easily accessible.
- **Cybersecurity Measures** 🔒: Implementing secure session management, image hashing, and API authentication to protect user data and system integrity.
- **Blockchain Technology** 📈: A simple yet effective blockchain implementation to record and verify diagnosis history, adding an extra layer of trust and transparency to the system.
- **Enterprise Resource Planning (ERP)** 📊: An integrated system to manage and track all plant disease analyses, providing valuable insights and analytics.
- **User-Friendly Web Application** 🌐: Built with Flask, offering an intuitive interface for users to upload leaf images and receive instant disease diagnoses.

## Technical Overview 🤖

### 1. **Cloud Computing**
   - **Firebase Firestore**: Used for real-time data storage and retrieval.
   - **Cloud Status**: The system can operate in both cloud-connected and local modes.

### 2. **Cybersecurity**
   - **Secure Sessions**: User sessions are managed securely to prevent unauthorized access.
   - **Image Hashing**: Images are hashed for data integrity and security.
   - **API Authentication**: API endpoints are secured with authentication keys.

### 3. **Blockchain**
   - **Simple Blockchain Implementation**: Records diagnosis history in a blockchain for transparency and trust.
   - **Blockchain Ledger**: Available for viewing on the ERP dashboard.

### 4. **ERP System**
   - **Analysis Records Management**: Tracks all analyses with detailed records.
   - **Disease Distribution Insights**: Provides insights into the distribution of detected diseases.

### 5. **AI Model**
   - **ResNet18 Architecture**: Utilizes a deep learning model trained on a dataset of leaf images.
   - **Disease Classes**: Trained to recognize five common leaf diseases:
     - Anthracnose 🌿
     - Bacterial Blight 🌱
     - Cercospora Leaf Spot 🌻
     - Powdery Mildew ❄️
     - Shot Hole Disease 🔫

### 6. **Web Application**
   - **Flask Framework**: Built with Flask for a lightweight and efficient web interface.
   - **Responsive Design**: Accessible across various devices and screen sizes.

## Code Structure 📁

The code is organized into several key components:

- **`app.py`**: The main Flask application file.
- **`templates/`**: Contains HTML templates for the web interface.
- **`static/`**: Holds static files like CSS and JavaScript.
- **`requirements.txt`**: Lists all dependencies required to run the application.

## Setup Instructions 📝

1. **Clone the Repository**:
   ```bash
   https://github.com/ishaanagarwal78/Leaf-Disease-Detection-System-.git
   ```

2. **Install Dependencies**:
   ```bash
   pip install Flask Flask-Session torch torchvision Pillow requests firebase-admin
   ```

3. **Create Firebase Key File**:
   - If you don't have a Firebase service account key, generate a placeholder using the `create_firebase_key()` function in `app.py`.

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   - Open a web browser and navigate to `http://127.0.0.1:5000`. This is for the local deployement

## Contributing 🤝

Contributions are welcome! Please submit pull requests with detailed explanations of changes.

## License 📜

This project is licensed under the MIT License.

---

### Example Use Cases 📚

1. **Disease Diagnosis**:
   - Upload a leaf image to the web application.
   - Receive instant diagnosis with confidence levels.

2. **ERP Dashboard**:
   - View analysis records and blockchain ledger.
   - Get insights into disease distribution.

3. **API Integration**:
   - Use the API endpoint to integrate with other applications.

---

### Future Enhancements 🚀

- **Expand Disease Database**: Train the model on more diseases.
- **Improve Blockchain Security**: Implement more advanced blockchain features.
- **Enhance User Interface**: Add more interactive features to the web application.

---

This project demonstrates the power of combining AI, cloud computing, blockchain, and enterprise-level features to address critical challenges in plant health management. 🌟

---

### Technologies Used 🛠️

- **Backend**: Python with Flask framework.
- **AI Model**: PyTorch (ResNet18).
- **Database**: Firebase Firestore.
- **Frontend**: HTML, CSS, JavaScript.
- **Security**: Custom implementations for session management and data protection.
- **Deployment**: Ready for cloud deployment with Gunicorn.

---

### Team 🤝

- **Jeevesh**
- **Alisha Gambhir**

---

### Acknowledgments 🙏

Special thanks to all contributors and supporters of this project. Your efforts are greatly appreciated! 🌟

---

### Conclusion 🌟

The Leaf Disease Detection System is a significant leap forward in agricultural technology, offering a secure, scalable, and manageable solution for plant disease diagnostics. By integrating cutting-edge technologies, this project sets a new standard for innovation in the field. 🌟

---

### GitHub Repository 📚

[Link to our GitHub repository](https://github.com/ishaanagarwal78/Leaf-Disease-Detection-System-.git)

# 🐔 PoultryBot — AI-Powered Chatbot for Poultry Disease Management and Breed Care

### 📘 Overview
**PoultryBot** is an AI-driven web application designed to assist poultry farmers—especially smallholders in Kenya—with disease diagnosis and breed-specific care.  
The system uses **machine learning**, **natural language processing**, and **computer vision** to identify poultry diseases through either **symptom descriptions** or **image uploads**, and provides **breed-specific recommendations** on feeding, housing, and disease prevention.  

---

### 🚀 Features
- **Text-Based Disease Diagnosis**: Enter symptoms to get likely diseases ranked by probability.  
- **Image-Based Diagnosis**: Upload a chicken image and get an AI-predicted disease using a fine-tuned ResNet-50 CNN.  
- **Breed Care Chatbot**: Ask breed-related questions and receive intelligent responses powered by a Cohere LLM.  
- **User Accounts**: Farmers can register, log in, and access past diagnosis history.  
- **Admin Dashboard**: Manage diseases, breeds, and user queries efficiently.  

---

### 🧠 System Architecture
- **Frontend**: HTML, Tailwind CSS, JavaScript  
- **Backend**: Flask + FastAPI  
- **Database**: PostgreSQL (via SQLAlchemy ORM)  
- **Cloud Storage**: Cloudinary for image hosting  
- **AI/ML**:  
  - ResNet-50 for image classification  
  - Bayesian reasoning engine for symptom analysis  
  - Cohere LLM for intelligent breed query responses  

---

### 🧩 Core Modules
1. **Symptom-Based Diagnosis** – Bayesian-inspired probability scoring using symptom-disease mappings.  
2. **Image Diagnosis Module** – CNN-based disease classification trained on poultry disease images.  
3. **Breed Query Module** – Uses Cohere’s LLM to interpret user intent and return breed-specific insights.  

---

### 🧰 Installation & Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/derrokip4130/Final-year-project
   cd poultrybot
   ```

2. **Set up the environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # (or venv\Scripts\activate on Windows)
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory with:
   ```
   DATABASE_URL=postgresql://user:password@localhost/poultrybot
   CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
   COHERE_API_KEY=<your_cohere_api_key>
   ```

4. **Run the application**
   ```bash
   flask run
   ```
   or (for API)
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access via browser**  
   Visit `http://127.0.0.1:5000/`  

---

### 🧪 Model Performance
| Component | Model | Accuracy |
|------------|--------|-----------|
| Image Diagnosis | ResNet-50 CNN | **82.35%** |
| Text Diagnosis | Bayesian Rule-Based | **66.7%** |
| Breed Query Chatbot | Cohere LLM | High relevance across test cases |

---

### 🧩 Database Schema (Simplified)
- **Users** — user info, roles, and activity logs  
- **Diseases** — details, causes, symptoms  
- **Symptoms** — mapped to multiple diseases  
- **Diagnosis** — user queries, results, probabilities  
- **Breeds** — feeding, housing, prevention data  
- **Chats / Queries** — breed-related conversations  

---

### 🧱 Project Goals
- Enable rural poultry farmers to identify diseases early  
- Provide reliable, locally relevant breed care advice  
- Support Kenya’s **Digital Agriculture** initiatives under the **Kenya Digital Master Plan**

---

### ⚠️ Limitations
- Limited image dataset (≈70–100 images per disease)  
- Some diseases show visual/symptom overlap  
- Internet connectivity required for LLM queries  
- Currently supports English only  

---

### 🔮 Future Work
- Expand dataset and disease coverage  
- Add offline mode (ONNX + SQLite)  
- Integrate Swahili and local languages  
- Develop a mobile version for Android  

---

### 👨‍💻 Author
**Derrick Kiprop Kipruto**  
Bachelor of Science in Computer Science, University of Nairobi  
Supervisor: **Dr. Evans A.K. Miriti**

---

### 📜 License
This project is released for **academic and research purposes** under an open-use educational license.  

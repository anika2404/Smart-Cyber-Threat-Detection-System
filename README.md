# Smart-Cyber-Threat-Detection-System
AI-powered Digital Forensics and Incident Response (DFIR) system that analyzes network traffic, detects cyber attacks using machine learning, and generates interactive dashboards and automated forensic reports.
# AI DFIR Tool

###  AI-Powered Cyber Threat Detection & Digital Forensics System

> **From raw network traffic → to intelligent cyber insights in seconds**

---

##  Overview

AI DFIR Tool is an intelligent **Digital Forensics and Incident Response (DFIR)** platform that analyzes network traffic data, detects malicious activity using machine learning, and presents actionable insights through an interactive dashboard and automated forensic reports.

---

##  Problem Statement

Analyzing large-scale network traffic to detect cyber threats is complex and time-consuming. Traditional systems lack real-time intelligence and clear visualization.

This project provides an **AI-driven solution** to:

* Automatically detect intrusions
* Classify cyber attacks
* Visualize network behavior
* Generate forensic reports instantly

---

##  Features

*  AI-Based Attack Detection
*  Interactive Dashboard (Streamlit)
*  Real-Time Traffic Analysis
*  Attack Classification (DoS, Exploits, etc.)
*  Automated PDF Report Generation
*  Fast API Backend (FastAPI)
*  CSV Upload & Analysis

---

##  Tech Stack

| Layer         | Technology    |
| ------------- | ------------- |
| Frontend      | Streamlit     |
| Backend       | FastAPI       |
| ML Model      | Scikit-learn  |
| Data          | Pandas, NumPy |
| Visualization | Plotly        |
| Reports       | ReportLab     |
| Storage       | Joblib        |

---

##  Project Structure

forensic/
│
├── backend/
│   ├── main.py
│   ├── analyzer.py
│   ├── model.pkl
│   ├── encoders.pkl
│   ├── report_generator.py
│
├── frontend/
│   ├── app.py
│
├── data/
│
└── README.md

---

## ⚙️ Setup & Installation

### 🔹 Clone Repository

git clone https://github.com/anika2402/smart-cyber-threat-detection-system.git
cd smart-cyber-threat-detection-system

---

### 🔹 Install Dependencies

pip install -r requirements.txt

---

### 🔹 Run Backend

cd backend
uvicorn main:app --reload

---

### 🔹 Run Frontend

cd frontend
streamlit run app.py

---

## 📊 How It Works

1. Upload a network traffic dataset (CSV)
2. Backend processes data & runs ML model
3. Predictions generated (Normal / Attack)
4. Dashboard displays insights
5. Generate downloadable PDF report

---

## 📈 Output Includes

* 📊 Attack Type Distribution
* 🌐 Traffic Composition
* 📉 Traffic Trends
* 🎯 Targeted Ports
* 📄 DFIR Report

---

##  Target Users

* 🛡️ Security Analysts
* 🖥️ SOC Teams
* 🎓 Cybersecurity Students
* 🏢 Organizations

---

## 🌍 SDG Alignment

* SDG 9 – Industry, Innovation & Infrastructure
* SDG 16 – Peace, Justice & Strong Institutions

---

## 🚀 Future Enhancements

* Real-time packet capture
* Deep learning models
* Live monitoring
* Alert system
* Threat intelligence integration

---


#  AI Smart Bus Entry & Exit Monitoring System

An AI-powered real-time vehicle monitoring system that automatically detects vehicle number plates, verifies vehicle authorization, logs entry/exit activities, and sends instant alerts for blocked vehicles through Email and WhatsApp.

---

## 📌 Project Overview

The AI Smart Bus Entry & Exit Monitoring System is designed to improve security and automate vehicle monitoring at educational institutions, industries, residential communities, and corporate campuses.

The system captures live video from a camera, recognizes vehicle registration numbers using Artificial Intelligence (EasyOCR), checks them against a vehicle database, records all vehicle movements, captures evidence for blocked vehicles, uploads images to the cloud, and sends instant notifications to registered administrators.

---

## 🚀 Features

- ✅ Real-time vehicle number plate detection
- ✅ AI-based Optical Character Recognition (EasyOCR)
- ✅ Live webcam monitoring using OpenCV
- ✅ Automatic Entry/Exit detection
- ✅ Vehicle verification (Allowed / Blocked / Not Registered)
- ✅ Automatic vehicle movement logging
- ✅ Capture blocked vehicle images
- ✅ Upload captured images to Cloudinary
- ✅ Send Email alerts for blocked vehicles
- ✅ Send WhatsApp alerts using Twilio API
- ✅ User Login Authentication
- ✅ Live Web Dashboard
- ✅ Search Vehicle History
- ✅ Real-time Dashboard Updates
- ✅ SQLite Database Integration

---

## 🏗️ System Architecture

```
Camera
   │
   ▼
OpenCV
   │
   ▼
EasyOCR (AI Number Plate Recognition)
   │
   ▼
Clean Number Plate
   │
   ▼
Vehicle Database Verification
   │
   ├────────► Allowed
   │             │
   │             ▼
   │       Log Entry / Exit
   │
   └────────► Blocked
                 │
                 ▼
          Capture Vehicle Image
                 │
                 ▼
         Upload to Cloudinary
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
 Email Alert         WhatsApp Alert
      │                     │
      └──────────┬──────────┘
                 ▼
       Dashboard Updated
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend Programming |
| OpenCV | Camera Access & Image Processing |
| EasyOCR | AI Number Plate Recognition |
| SQLite | Database |
| Pandas | CSV Data Handling |
| Tkinter | GUI |
| Cloudinary | Cloud Image Storage |
| Twilio API | WhatsApp Notifications |
| SMTP | Email Notifications |
| Pillow | Image Display |
| Regular Expressions | Number Plate Cleaning |

---

## 📂 Project Structure

```
Smart_Bus_System/
│
├── main.py
├── requirements.txt
├── README.md
├── database.db
├── vehicle_database.csv
├── entry_exit_log.csv
├── blocked_captures/
├── uploads/
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/AI-Smart-Bus-Monitoring-System.git
```

Move into project

```bash
cd AI-Smart-Bus-Monitoring-System
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Project

```bash
python main.py
```

---

## 🔐 Configure API Keys

Update the following inside the source code or `.env` file.

### Cloudinary

- Cloud Name
- API Key
- API Secret

### Gmail SMTP

- Sender Email
- App Password

### Twilio

- Account SID
- Auth Token
- WhatsApp Sandbox Number

---

## 📊 Database

Vehicle Database

| Plate Number | Status |
|--------------|---------|
| HR98AA0000 | Allowed |
| DL1AB2345 | Blocked |

Entry Exit Log

| Plate | Date | Time | Status | Movement |

---

## 🚨 Alert System

When a blocked vehicle is detected:

- Vehicle image captured
- Image uploaded to Cloudinary
- Email sent to registered administrator
- WhatsApp notification sent
- Event stored in database
- Dashboard updated automatically

---

## 📈 Future Enhancements

- YOLOv11 Vehicle Detection
- Face Recognition
- Multiple Camera Support
- RFID Integration
- GPS Tracking
- Attendance Management
- Mobile Application
- Cloud Deployment
- Admin Role Management
- Analytics Dashboard
- PDF Report Generation

---

## 🎯 Applications

- College Bus Monitoring
- School Transport
- Corporate Campuses
- Residential Communities
- Industrial Gate Security
- Smart Parking Systems

---

## 📸 Screenshots

Example
<img width="1920" height="1080" alt="Screenshot (39)" src="https://github.com/user-attachments/assets/fdf17a5b-e8bf-4e54-9c89-cdc3cc100a64" />
<img width="1920" height="1080" alt="Screenshot (40)" src="https://github.com/user-attachments/assets/76cbc7bb-2160-4e8d-87d9-62f570029155" />
<img width="1920" height="1080" alt="Screenshot (41)" src="https://github.com/user-attachments/assets/2e92f4bd-949b-452f-b489-35418e5defcf" />
<img width="1920" height="1080" alt="Screenshot (42)" src="https://github.com/user-attachments/assets/d4edbedf-d16d-453c-a837-b5f6a5d3cd24" />
<img width="1920" height="1080" alt="Screenshot (43)" src="https://github.com/user-attachments/assets/e5ee40d6-941a-4231-b5f2-162366654486" />
<img width="1920" height="1080" alt="Screenshot (44)" src="https://github.com/user-attachments/assets/013199c1-c855-4148-8513-4b9bbcb0c2ea" />
<img width="1920" height="1080" alt="Screenshot (45)" src="https://github.com/user-attachments/assets/e0fcd07b-a917-4e78-bb19-fc4777f32bfa" />
<img width="1920" height="1080" alt="Screenshot (46)" src="https://github.com/user-attachments/assets/ea8c94f0-4671-4e62-bd50-9564a8f5b93f" />
<img width="1920" height="1080" alt="Screenshot (47)" src="https://github.com/user-attachments/assets/0b033d29-e382-4608-a84e-957bc570c1a8" />
<img width="1920" height="1080" alt="Screenshot (53)" src="https://github.com/user-attachments/assets/afebcd3e-354a-4de2-b83f-b333823e881e" />
<img width="1920" height="1080" alt="Screenshot (51)" src="https://github.com/user-attachments/assets/7432454f-48d0-4080-9500-30c276a6da78" />
<img width="1920" height="1080" alt="Screenshot (54)" src="https://github.com/user-attachments/assets/7ba2733e-846b-4b71-8fad-62bff3cb1c99" />
<img width="1920" height="1080" alt="Screenshot (49)" src="https://github.com/user-attachments/assets/7afd0193-cd70-497b-b34a-94ad38ff397f" />
<img width="1920" height="1080" alt="Screenshot (44)" src="https://github.com/user-attachments/assets/efd92498-6c3c-40b8-a2dc-febd19ae6019" />

## 👨‍💻 Developer

**Kabilan S**

Electronics and Communication Engineering

Velammal Engineering College

Java Backend Developer | Python | AI | OpenCV | EasyOCR

GitHub: https://github.com/kabilan1598-lgtm

LinkedIn: [https://linkedin.com/in/yourprofile](https://www.linkedin.com/in/kabilan-s-429b39292?utm_source=share_via&utm_content=profile&utm_medium=member_android)

---

## ⭐ If you like this project

Give this repository a ⭐ on GitHub


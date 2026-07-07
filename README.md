#  AI SMART BUS ENTRY AND EXIT MONITORING SYSTEM

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


NOTE:

## Configuration

Before running the project, replace the placeholder credentials in `main.py` (or configure them using environment variables):

- YOUR_TWILIO_ACCOUNT_SID
- YOUR_TWILIO_AUTH_TOKEN
- YOUR_EMAIL@GMAIL.COM
- YOUR_GMAIL_APP_PASSWORD
- RECEIVER_EMAIL@GMAIL.COM
- YOUR_CLOUDINARY_CLOUD_NAME
- YOUR_CLOUDINARY_API_KEY
- YOUR_CLOUDINARY_API_SECRET


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

CODE PAGE:
<img width="1920" height="1080" alt="Screenshot (34)" src="https://github.com/user-attachments/assets/9d9497c6-36d4-4526-8046-d6ced05598f1" />



LOGIN PAGE:
<img width="1920" height="1080" alt="Screenshot (39)" src="https://github.com/user-attachments/assets/fdf17a5b-e8bf-4e54-9c89-cdc3cc100a64" />


DASHBOARD:
<img width="1920" height="1080" alt="Screenshot (51)" src="https://github.com/user-attachments/assets/7432454f-48d0-4080-9500-30c276a6da78" />


VEHICLE LOG:
<img width="1920" height="1080" alt="Screenshot (52)" src="https://github.com/user-attachments/assets/7e1d2a46-7652-4951-96ac-31be06eaa0c9" />


VEHICLE LOG GRAPH:
<img width="1920" height="1080" alt="Screenshot (42)" src="https://github.com/user-attachments/assets/d4edbedf-d16d-453c-a837-b5f6a5d3cd24" />


BLOCKED VEHICLE GALLERY:
<img width="1920" height="1080" alt="Screenshot (53)" src="https://github.com/user-attachments/assets/38b42e59-95a8-4561-bd4e-72fad40ffead" />


ANALYTICS:
<img width="1920" height="1080" alt="Screenshot (54)" src="https://github.com/user-attachments/assets/193fd0f2-42de-4836-ad7d-3f948871e299" />


DAILY ANALYTICS TIME LINE:
<img width="1920" height="1080" alt="Screenshot (55)" src="https://github.com/user-attachments/assets/d7180d2e-a942-4c85-a30c-72580afd695d" />


REGISTERD VEHICLES:
<img width="1920" height="1080" alt="Screenshot (46)" src="https://github.com/user-attachments/assets/ea8c94f0-4671-4e62-bd50-9564a8f5b93f" />


ADMIN USER - KABEE:
<img width="1920" height="1080" alt="Screenshot (47)" src="https://github.com/user-attachments/assets/0b033d29-e382-4608-a84e-957bc570c1a8" />


WHATSAPP ALERT:
<img width="1920" height="1080" alt="Screenshot (59)" src="https://github.com/user-attachments/assets/1b04541f-4ef9-4f75-9ac7-1c71f63f9b79" />


MAIL ALERT:
<img width="1920" height="1080" alt="Screenshot (61)" src="https://github.com/user-attachments/assets/5168bd7a-5510-4be3-ad8d-2e91a506d698" />



CLOUD UPLOAD:
<img width="1920" height="1080" alt="Screenshot (60)" src="https://github.com/user-attachments/assets/45f87ddf-7bc1-420a-8325-12dc29b67425" />




## 👨‍💻 Developer

**KABILAN S**

Electronics and Communication Engineering

Velammal Engineering College

Java Backend Developer | Python | AI | OpenCV | EasyOCR

GitHub: https://github.com/kabilan1598-lgtm

LinkedIn: [https://linkedin.com/in/yourprofile](https://www.linkedin.com/in/kabilan-s-429b39292?utm_source=share_via&utm_content=profile&utm_medium=member_android)

---

## ⭐ If you like this project

Give this repository a ⭐ on GitHub


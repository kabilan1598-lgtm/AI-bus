"""
AI Smart Bus Entry & Exit Monitoring System
Single file — Detection + Dashboard
Run dashboard : streamlit run main.py
Run detection : python main.py --detect
"""

import sys
import os
import re
import sqlite3
import hashlib
import threading
import smtplib
import urllib.request
import numpy as np
from datetime import datetime
from email.message import EmailMessage

# CREDENTIALS


ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"

SENDER_EMAIL = "YOUR_EMAIL@GMAIL.COM"
APP_PASSWORD = "YOUR_GMAIL_APP_PASSWORD"

RECEIVER_EMAIL = "RECEIVER_EMAIL@GMAIL.COM"

CLOUD_NAME ="YOUR_CLOUDINARY_CLOUD_NAME",
API_KEY ="YOUR_CLOUDINARY_API_KEY",
API_SECRET ="YOUR_CLOUDINARY_API_SECRET"


PLATE_MODEL_PATH  = "license_plate_detector.pt"
PLATE_MODEL_URL   = (
    "https://github.com/Muhammad-Zeerak-Khan/"
    "Automatic-License-Plate-Recognition-using-YOLOv8/"
    "raw/main/license_plate_detector.pt"
)

DB_PATH              = "database.db"
BLOCKED_FOLDER       = "blocked_captures"
PROCESS_EVERY_N      = 5
MIN_PLATE_CONF       = 0.40
MIN_OCR_CONF         = 0.35
GATE_LOCATION        = "Main Gate"

# DATABASE

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c    = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT, phone TEXT,
        created TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS vehicle_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT, status TEXT, movement TEXT,
        date TEXT, time TEXT, image_url TEXT,
        location TEXT, owner TEXT,
        created TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'Allowed',
        owner TEXT
    )""")
    pw = hashlib.sha256("Kabee123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username,password,email,phone) VALUES (?,?,?,?)",
            ("Kabee", pw, "kabee@gmail.com", "+917010286455"))
    for plate, status, owner in [
        ("HY99GX2414","Allowed","RAVI"),
        ("MH14DS7000","Blocked","LOGESH"),
        ("HR98AA7777","Allowed","Kabee"),
        ("ML03MF4477","Blocked","MADHU"),
        ("AB01C1234","Allowed","HARI"),
    ]:
        c.execute("INSERT OR IGNORE INTO vehicles (plate,status,owner) VALUES (?,?,?)",
                (plate, status, owner))
    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_user(username, password):
    conn = get_conn()
    row  = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and row["password"] == hash_pw(password):
        return dict(row)
    return None

def check_vehicle(plate):
    conn = get_conn()
    row  = conn.execute("SELECT * FROM vehicles WHERE plate=?", (plate.upper().strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_last_movement(plate):
    conn = get_conn()
    row  = conn.execute(
        "SELECT movement FROM vehicle_log WHERE plate=? ORDER BY id DESC LIMIT 1", (plate,)
    ).fetchone()
    conn.close()
    return row["movement"] if row else None

def log_vehicle(plate, status, movement, date, time_str, image_url, location, owner):
    conn = get_conn()
    conn.execute("""INSERT INTO vehicle_log
        (plate,status,movement,date,time,image_url,location,owner)
        VALUES (?,?,?,?,?,?,?,?)""",
        (plate, status, movement, date, time_str, image_url, location, owner))
    conn.commit()
    conn.close()

def update_image_url(plate, date, time_str, url):
    conn = get_conn()
    conn.execute("UPDATE vehicle_log SET image_url=? WHERE plate=? AND date=? AND time=?",
                (url, plate, date, time_str))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM vehicle_log ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_today_logs():
    today = datetime.now().strftime("%d-%m-%Y")
    conn  = get_conn()
    rows  = conn.execute("SELECT * FROM vehicle_log WHERE date=? ORDER BY id DESC", (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn    = get_conn()
    today   = datetime.now().strftime("%d-%m-%Y")
    total   = conn.execute("SELECT COUNT(*) FROM vehicle_log").fetchone()[0]
    today_  = conn.execute("SELECT COUNT(*) FROM vehicle_log WHERE date=?", (today,)).fetchone()[0]
    blocked = conn.execute("SELECT COUNT(*) FROM vehicle_log WHERE status='Blocked'").fetchone()[0]
    allowed = conn.execute("SELECT COUNT(*) FROM vehicle_log WHERE status='Allowed'").fetchone()[0]
    entries = conn.execute("SELECT COUNT(*) FROM vehicle_log WHERE movement='Entry'").fetchone()[0]
    exits   = conn.execute("SELECT COUNT(*) FROM vehicle_log WHERE movement='Exit'").fetchone()[0]
    conn.close()
    return dict(total=total, today=today_, blocked=blocked,
                allowed=allowed, entries=entries, exits=exits)

def get_all_vehicles():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM vehicles ORDER BY plate").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_vehicle(plate, status, owner):
    try:
        conn = get_conn()
        conn.execute("INSERT OR REPLACE INTO vehicles (plate,status,owner) VALUES (?,?,?)",
                    (plate.upper().strip(), status, owner))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def delete_vehicle(plate):
    conn = get_conn()
    conn.execute("DELETE FROM vehicles WHERE plate=?", (plate,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT id,username,email,phone,created FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_user(username, password, email, phone):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO users (username,password,email,phone) VALUES (?,?,?,?)",
                    (username, hash_pw(password), email, phone))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def delete_user(uid):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()

# CLOUDINARY

def upload_to_cloudinary(image_path, plate, owner, date, time_str, location):
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD,
            api_key=CLOUDINARY_KEY,
            api_secret=CLOUDINARY_SECRET
        )
        safe = re.sub(r'[^A-Z0-9]', '', plate.upper())
        resp = cloudinary.uploader.upload(
            image_path,
            public_id       = f"{CLOUDINARY_FOLDER}/{safe}_{date}_{time_str}",
            overwrite       = False,
            context         = f"plate={plate}|owner={owner}|date={date}|time={time_str}|location={location}",
            tags            = ["blocked_vehicle", f"plate_{safe}"]
        )
        return resp.get("secure_url", "")
    except Exception as e:
        print(f"  Cloudinary error: {e}")
        return ""

def fetch_gallery():
    try:
        import cloudinary
        import cloudinary.api
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD,
            api_key=CLOUDINARY_KEY,
            api_secret=CLOUDINARY_SECRET
        )
        resp  = cloudinary.api.resources(
            type="upload", prefix=f"{CLOUDINARY_FOLDER}/",
            max_results=60, context=True, tags=True
        )
        items = []
        for r in resp.get("resources", []):
            ctx   = r.get("context", {}).get("custom", {})
            pid   = r.get("public_id","").split("/")[-1]
            parts = pid.split("_")
            items.append({
                "url":      r.get("secure_url",""),
                "plate":    ctx.get("plate",    parts[0] if parts else ""),
                "owner":    ctx.get("owner",    "Unknown"),
                "date":     ctx.get("date",     parts[1] if len(parts)>1 else ""),
                "time":     ctx.get("time",     parts[2] if len(parts)>2 else "").replace("-",":"),
                "location": ctx.get("location", ""),
                "created":  r.get("created_at","")
            })
        items.sort(key=lambda x: x["created"], reverse=True)
        return items
    except Exception as e:
        print(f"  Gallery error: {e}")
        return []


# ALERTS


def send_email(plate, owner, date, time_str, location, image_url, image_path):
    try:
        msg            = EmailMessage()
        msg["Subject"] = f"Blocked Vehicle Alert — {plate}"
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL
        msg.set_content(f"""
Blocked Vehicle Detected

Vehicle Number : {plate}
Owner          : {owner}
Status         : BLOCKED
Date           : {date}
Time           : {time_str}
Location       : {location}

Image : {image_url or "Not available"}

Please take immediate action.
— AI Smart Bus Entry Exit System
""")
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="jpeg",
                                filename=f"blocked_{plate}_{date}.jpg")
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(SENDER_EMAIL, APP_PASSWORD)
        s.send_message(msg)
        s.quit()
        print("  ✅ Email sent")
        return True
    except Exception as e:
        print(f"  Email error: {e}")
        return False

def send_whatsapp(plate, owner, date, time_str, location, image_url):
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        if image_url:
            try:
                client.messages.create(
                    from_=TWILIO_FROM, to=ADMIN_WHATSAPP,
                    body=f"Blocked Vehicle Detected: {plate}",
                    media_url=[image_url]
                )
            except Exception as e:
                print(f"  WhatsApp image error: {e}")
        client.messages.create(
            from_=TWILIO_FROM, to=ADMIN_WHATSAPP,
            body=(
                f"*BLOCKED VEHICLE ALERT*\n\n"
                f"Vehicle : {plate}\n"
                f"Owner   : {owner}\n"
                f"Date    : {date}\n"
                f"Time    : {time_str}\n"
                f"Location: {location}\n\n"
                f"Please take immediate action.\n"
                f"— AI Smart Bus Monitor"
            )
        )
        print("  ✅ WhatsApp sent")
        return True
    except Exception as e:
        print(f"  WhatsApp error: {e}")
        return False

def send_all_alerts(plate, owner, date, time_str, location, image_path):
    def _run():
        print("\n--- Sending alerts ---")
        img_url  = upload_to_cloudinary(image_path, plate, owner, date, time_str, location)
        email_ok = send_email(plate, owner, date, time_str, location, img_url, image_path)
        wa_ok    = send_whatsapp(plate, owner, date, time_str, location, img_url)
        if img_url:
            update_image_url(plate, date, time_str, img_url)
        print(f"  Upload  : {'OK' if img_url  else 'FAILED'}")
        print(f"  Email   : {'OK' if email_ok else 'FAILED'}")
        print(f"  WhatsApp: {'OK' if wa_ok    else 'FAILED'}")
        print("----------------------\n")
    threading.Thread(target=_run, daemon=True).start()

# OCR + DETECTION

def preprocess_plate(crop):
    import cv2
    h, w  = crop.shape[:2]
    scale = min(max(1, 300 // max(h, 1)), 6)
    big   = cv2.resize(crop, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
    gray  = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    eq    = cv2.equalizeHist(gray)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k     = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    return [
        ("color", big), ("gray", gray), ("eq", eq),
        ("thresh", th), ("inv", cv2.bitwise_not(th)),
        ("sharp", cv2.filter2D(big, -1, k))
    ]

def fix_ocr(text):
    text = re.sub(r'[^A-Z0-9]', '', text.upper().strip())
    if len(text) < 4:
        return text
    l2n = {'O':'0','I':'1','L':'1','B':'8','G':'6','S':'5','Z':'2','Q':'0','U':'0'}
    n2l = {'0':'O','1':'I','8':'B','6':'G','5':'S','2':'Z'}
    chars = list(text)
    for i in range(min(2, len(chars))):
        if chars[i].isdigit():
            chars[i] = n2l.get(chars[i], chars[i])
    text  = ''.join(chars)
    state = text[:2]; rest = text[2:]
    dist  = ""; i = 0
    while i < len(rest) and len(dist) < 2:
        f = l2n.get(rest[i], rest[i])
        if f.isdigit(): dist += f; i += 1
        else: break
    rest = rest[i:]
    series = ""; i = 0
    while i < len(rest) and len(series) < 2:
        f = n2l.get(rest[i], rest[i])
        if f.isalpha(): series += f; i += 1
        else: break
    rest = rest[i:]
    num = "".join(l2n.get(c,c) for c in rest if l2n.get(c,c).isdigit())
    return state + dist + series + num

def valid_plate(text):
    return bool(re.match(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', text))

def read_plate(crop, reader):
    candidates = []
    for name, img in preprocess_plate(crop):
        try:
            results = reader.readtext(img,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                batch_size=1, paragraph=False)
            full  = "".join(t.upper() for _,t,p in results if p >= MIN_OCR_CONF)
            fixed = fix_ocr(re.sub(r'[^A-Z0-9]','',full).replace("IND",""))
            if valid_plate(fixed):
                mx = max((p for _,_,p in results), default=0)
                candidates.append((fixed, mx))
            for _,t,p in results:
                if p >= MIN_OCR_CONF:
                    f = fix_ocr(re.sub(r'[^A-Z0-9]','',t.upper().replace("IND","")))
                    if valid_plate(f):
                        candidates.append((f, p))
        except:
            pass
    if not candidates:
        return "", 0.0
    return max(candidates, key=lambda x: x[1])

def detect_plates(frame, model):
    import cv2
    crops = []; boxes = []
    try:
        res  = model(frame, imgsz=640, conf=MIN_PLATE_CONF, verbose=False)[0]
        h, w = frame.shape[:2]
        for box in res.boxes:
            conf         = float(box.conf[0])
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            x1=max(0,x1-6); y1=max(0,y1-6)
            x2=min(w,x2+6); y2=min(h,y2+6)
            crop = frame[y1:y2, x1:x2]
            if crop.size > 0:
                crops.append((crop, conf))
                boxes.append((x1,y1,x2,y2,conf))
    except Exception as e:
        print(f"  Detect error: {e}")
    return crops, boxes

def process_plate(plate, captured_frame):
    import cv2
    now      = datetime.now()
    date     = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%I:%M %p")
    time_fn  = now.strftime("%H-%M-%S")

    vehicle  = check_vehicle(plate)
    status   = vehicle["status"] if vehicle else "Not Registered"
    owner    = vehicle["owner"]  if vehicle else "Unknown"
    last     = get_last_movement(plate)
    movement = "Exit" if last == "Entry" else "Entry"

    print(f"  Plate: {plate} | Status: {status} | {movement}")

    img_path = ""
    if status == "Blocked":
        fname    = os.path.join(BLOCKED_FOLDER, f"{plate}_{date}_{time_fn}.jpg")
        if cv2.imwrite(fname, captured_frame):
            img_path = fname
            print(f"  Saved: {fname}")
        send_all_alerts(plate, owner, date, time_str, GATE_LOCATION, img_path)
        try:
            import winsound
            winsound.Beep(1000,500); winsound.Beep(800,500); winsound.Beep(1000,500)
        except: pass
    elif status == "Not Registered":
        try:
            import winsound
            winsound.Beep(700, 800)
        except: pass
    else:
        try:
            import winsound
            winsound.Beep(1000, 300); winsound.Beep(1000, 300)
        except: pass

    log_vehicle(plate, status, movement, date, time_str,
                img_path, GATE_LOCATION, owner)
    return status

# DETECTION MODE  (python main.py --detect)


def run_detection():
    import cv2
    from ultralytics import YOLO
    import easyocr

    init_db()
    os.makedirs(BLOCKED_FOLDER, exist_ok=True)

    if not os.path.exists(PLATE_MODEL_PATH):
        print("Downloading plate model...")
        urllib.request.urlretrieve(PLATE_MODEL_URL, PLATE_MODEL_PATH)
        print("Downloaded.")

    model  = YOLO(PLATE_MODEL_PATH)
    reader = easyocr.Reader(['en'], gpu=False)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\n✅ Detection started — Ctrl+C to stop\n")

    last_plate  = ""
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % PROCESS_EVERY_N != 0:
                continue

            captured     = frame.copy()
            crops, boxes = detect_plates(frame, model)

            if not crops:
                print(f"Frame {frame_count}: No plate")
                continue

            best_text = ""; best_conf = 0.0
            for crop, yc in crops:
                text, oc = read_plate(crop, reader)
                if not text: continue
                score = yc*0.4 + oc*0.6
                if score > best_conf:
                    best_text = text; best_conf = score

            if best_text and best_text != last_plate:
                print(f"\nNew plate: {best_text} (score={best_conf:.2f})")
                last_plate = best_text
                process_plate(best_text, captured)
            elif best_text:
                print(f"Frame {frame_count}: Same plate {best_text}")

    except KeyboardInterrupt:
        print("\nDetection stopped.")
    finally:
        cap.release()

# DASHBOARD  (streamlit run main.py)


def run_dashboard():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from streamlit_autorefresh import st_autorefresh

    init_db()
    os.makedirs(BLOCKED_FOLDER, exist_ok=True)

    st.set_page_config(
        page_title="Bus Monitor by kabee",
        page_icon="🚌",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    #  CSS 

    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    .stApp { background:#0f1117; color:#f1f5f9; }
    #MainMenu, footer, header { visibility:hidden; }
    .block-container { padding-top:1.5rem; padding-bottom:2rem; }

    [data-testid="stSidebar"] {
        background:#1a1d27 !important;
        border-right:1px solid #2d3748;
    }
    [data-testid="stSidebar"] * { color:#f1f5f9 !important; }

    /* metric cards */
    [data-testid="stMetric"] {
        background:#1a1d27;
        border:1px solid #2d3748;
        border-radius:8px;
        padding:20px !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size:12px !important;
        font-weight:600 !important;
        letter-spacing:0.5px !important;
        color:#64748b !important;
        text-transform:uppercase;
        font-family:'Inter',sans-serif !important;
    }
    [data-testid="stMetricValue"] {
        font-size:32px !important;
        font-weight:700 !important;
        color:#f1f5f9 !important;
        font-family:'Inter',sans-serif !important;
    }

    /* inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"],
    .stTextArea textarea {
        background:#1a1d27 !important;
        border:1px solid #2d3748 !important;
        color:#f1f5f9 !important;
        border-radius:6px !important;
        font-family:'Inter',sans-serif !important;
    }

    /* buttons */
    .stButton > button {
        background:#3b82f6 !important;
        color:#ffffff !important;
        border:none !important;
        border-radius:6px !important;
        font-weight:600 !important;
        font-family:'Inter',sans-serif !important;
        padding:8px 20px !important;
        transition:background .2s !important;
    }
    .stButton > button:hover { background:#2563eb !important; }

    /* download button */
    .stDownloadButton > button {
        background:transparent !important;
        color:#3b82f6 !important;
        border:1px solid #3b82f6 !important;
        border-radius:6px !important;
        font-weight:600 !important;
    }

    /* dataframe */
    [data-testid="stDataFrame"] {
        border:1px solid #2d3748;
        border-radius:8px;
        overflow:hidden;
    }

    /* tabs */
    .stTabs [data-baseweb="tab-list"] {
        background:#1a1d27;
        border-radius:8px;
        padding:4px;
        gap:4px;
        border:1px solid #2d3748;
    }
    .stTabs [data-baseweb="tab"] {
        background:transparent !important;
        color:#64748b !important;
        border-radius:6px !important;
        font-weight:500 !important;
        font-family:'Inter',sans-serif !important;
        padding:8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background:#3b82f6 !important;
        color:#ffffff !important;
    }

    /* page cards */
    .stat-card {
        background:#1a1d27;
        border:1px solid #2d3748;
        border-radius:8px;
        padding:20px 24px;
    }
    .stat-card-title {
        font-size:12px; font-weight:600;
        color:#64748b; text-transform:uppercase;
        letter-spacing:0.5px; margin-bottom:8px;
    }
    .stat-card-val {
        font-size:28px; font-weight:700; color:#f1f5f9;
    }

    /* status pills */
    .pill {
        display:inline-block; padding:3px 10px;
        border-radius:999px; font-size:12px;
        font-weight:600; letter-spacing:0.3px;
    }
    .pill-blocked { background:#fca5a520; color:#f87171; border:1px solid #f8717140; }
    .pill-allowed { background:#86efac20; color:#4ade80; border:1px solid #4ade8040; }
    .pill-unknown { background:#fde68a20; color:#fbbf24; border:1px solid #fbbf2440; }

    /* alert box */
    .alert-box {
        background:#7f1d1d20;
        border:1px solid #dc262660;
        border-left:4px solid #dc2626;
        border-radius:8px;
        padding:16px 20px;
        margin-bottom:20px;
    }
    .alert-box-title { color:#f87171; font-weight:700; font-size:16px; }
    .alert-box-sub   { color:#64748b; font-size:13px; margin-top:4px;
                    font-family:'JetBrains Mono',monospace; }

    /* section headers */
    .section-header {
        font-size:18px; font-weight:700; color:#f1f5f9;
        margin:24px 0 16px; padding-bottom:10px;
        border-bottom:1px solid #2d3748;
    }

    /* gallery card */
    .gal-card {
        background:#1a1d27;
        border:1px solid #2d3748;
        border-radius:8px;
        overflow:hidden;
        margin-bottom:16px;
    }
    .gal-info { padding:12px 16px; }
    .gal-plate {
        font-family:'JetBrains Mono',monospace;
        font-size:16px; font-weight:600;
        color:#f87171; letter-spacing:1px;
    }
    .gal-meta {
        font-size:12px; color:#64748b;
        margin-top:4px; line-height:1.6;
    }

    /* sidebar nav */
    div[data-testid="stSidebarNav"] { display:none; }

    /* info note */
    .info-note {
        background:#1e3a5f20;
        border:1px solid #3b82f660;
        border-radius:8px;
        padding:14px 18px;
        color:#93c5fd;
        font-size:13px;
        margin-bottom:16px;
        font-family:'JetBrains Mono',monospace;
    }

    /* form row */
    .form-hint {
        font-size:12px; color:#64748b; margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    #  SESSION STATE
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "tab" not in st.session_state:
        st.session_state.tab = "Dashboard"

    # LOGIN
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("<br/><br/>", unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align:center; margin-bottom:32px;">
            <div style="font-size:48px; margin-bottom:12px;">🚌</div>
            <div style="font-size:24px; font-weight:700; color:#f1f5f9;">Bus Entry & Exit Monitor</div>
            <div style="font-size:14px; color:#64748b; margin-top:6px;">Sign in to access the control panel</div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user      = username
                        st.rerun()
                    else:
                        st.error("Wrong username or password. Try again.")

            st.markdown("""
            <div style="text-align:center; font-size:12px; color:#475569; margin-top:16px;">
            Default login: admin / admin123
            </div>""", unsafe_allow_html=True)
        return

    #  SIDEBAR 
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:8px 0 16px;">
        <div style="font-size:16px; font-weight:700; color:#f1f5f9;">🚌 Bus Monitor</div>
        <div style="font-size:12px; color:#64748b; margin-top:4px;">
            Logged in as <b style="color:#93c5fd;">{st.session_state.user}</b>
        </div>
        </div>
        <hr style="border:none; border-top:1px solid #2d3748; margin-bottom:16px;"/>
        """, unsafe_allow_html=True)

        nav_items = [
            ("📊", "Dashboard"),
            ("📋", "Vehicle Log"),
            ("📷", "Gallery"),
            ("📈", "Analytics"),
            ("🚗", "Vehicles"),
            ("👤", "Users"),
        ]
        for icon, label in nav_items:
            is_active = st.session_state.tab == label
            btn_style = "background:#3b82f6 !important;" if is_active else ""
            if st.button(f"{icon}  {label}", key=f"nav_{label}",
                        use_container_width=True):
                st.session_state.tab = label
                st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid #2d3748;margin:16px 0;'/>",
                    unsafe_allow_html=True)

        auto = st.checkbox("Auto refresh (5s)", value=True)
        if auto:
            st_autorefresh(interval=5000, key="refresh")

        st.markdown(f"""
        <div style="font-size:12px; color:#475569; margin-top:8px;
            font-family:'JetBrains Mono',monospace;">
        {datetime.now().strftime('%d %b %Y  %H:%M:%S')}
        </div>""", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="logout"):
            st.session_state.logged_in = False
            st.rerun()

    #  HELPERS 
    def pill(status):
        if status == "Blocked":
            return '<span class="pill pill-blocked">Blocked</span>'
        if status == "Allowed":
            return '<span class="pill pill-allowed">Allowed</span>'
        return '<span class="pill pill-unknown">Unknown</span>'

    def color_row(row):
        if row.Status == "Blocked":
            return ['background:#7f1d1d18; color:#fca5a5'] * len(row)
        if row.Status == "Allowed":
            return ['background:#14532d18; color:#86efac'] * len(row)
        return ['background:#78350f18; color:#fde68a'] * len(row)

    tab = st.session_state.tab

    # DASHBOARD TAB
 
    if tab == "Dashboard":
        st.markdown("## Dashboard")

        stats      = get_stats()
        today_logs = get_today_logs()
        blocked_td = [l for l in today_logs if l["status"] == "Blocked"]

        # Alert banner
        if blocked_td:
            latest = blocked_td[0]
            st.markdown(f"""
            <div class="alert-box">
            <div class="alert-box-title">⚠️  Blocked vehicle detected — {latest['plate']}</div>
            <div class="alert-box-sub">
                {latest['date']}  ·  {latest['time']}  ·  {latest['location']}
                &nbsp;·&nbsp; {len(blocked_td)} blocked today
            </div>
            </div>""", unsafe_allow_html=True)

        # Metrics
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total Vehicles",  stats["total"])
        c2.metric("Today",           stats["today"])
        c3.metric("Entries",         stats["entries"])
        c4.metric("Exits",           stats["exits"])
        c5.metric("Allowed",         stats["allowed"])
        c6.metric("Blocked",         stats["blocked"])

        st.markdown("<div class='section-header'>Live Activity</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            all_logs = get_all_logs()
            if all_logs:
                import pandas as pd
                df = pd.DataFrame(all_logs[:30])
                display = df[["plate","status","movement","date","time","location","owner"]].copy()
                display.columns = ["Plate","Status","Movement","Date","Time","Location","Owner"]
                st.dataframe(
                    display.style.apply(color_row, axis=1),
                    use_container_width=True, height=340
                )
            else:
                st.markdown("""
                <div class="info-note">
                No vehicles detected yet.<br/>
                Run: <b>python main.py --detect</b> in a second terminal to start detection.
                </div>""", unsafe_allow_html=True)

        with col2:
            # Donut chart
            fig = go.Figure(data=[go.Pie(
                labels=["Allowed","Blocked","Unknown"],
                values=[
                    stats["allowed"], stats["blocked"],
                    max(0, stats["total"]-stats["allowed"]-stats["blocked"])
                ],
                hole=.6,
                marker=dict(colors=["#4ade80","#f87171","#fbbf24"]),
                textinfo="label+percent",
                textfont=dict(color="#f1f5f9", family="Inter", size=12),
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                font=dict(color="#f1f5f9", family="Inter"),
                margin=dict(l=0,r=0,t=0,b=0), height=280,
                showlegend=False,
            )
            fig.add_annotation(
                text=f"<b>{stats['total']}</b><br><span style='font-size:11px'>Total</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=18, color="#f1f5f9", family="Inter")
            )
            st.plotly_chart(fig, use_container_width=True)

            # System status
            st.markdown("""
            <div class="stat-card" style="margin-top:12px;">
            <div class="stat-card-title">System Status</div>
            <div style="display:flex;justify-content:space-between;
                font-size:13px;padding:6px 0;border-bottom:1px solid #2d3748;">
                <span style="color:#64748b;">Detection</span>
                <span style="color:#4ade80;">● Running</span>
            </div>
            <div style="display:flex;justify-content:space-between;
                font-size:13px;padding:6px 0;">
                <span style="color:#64748b;">Camera</span>
                <span style="color:#4ade80;">● Live</span>
            </div>
            </div>""", unsafe_allow_html=True)
            
    # VEHICLE LOG TAB

    elif tab == "Vehicle Log":
        import pandas as pd
        st.markdown("## Vehicle Log")

        logs = get_all_logs()
        if not logs:
            st.info("No records yet. Start detection to see vehicle logs here.")
            return

        df = pd.DataFrame(logs)

        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search = st.text_input("Search plate", placeholder="e.g. HR98AA")
        with col2:
            status_f = st.selectbox("Status", ["All","Allowed","Blocked","Not Registered"])
        with col3:
            move_f   = st.selectbox("Movement", ["All","Entry","Exit"])
        with col4:
            dates    = ["All"] + sorted(df["date"].unique().tolist(), reverse=True)
            date_f   = st.selectbox("Date", dates)

        filtered = df.copy()
        if search:
            filtered = filtered[filtered["plate"].str.contains(search.upper(), na=False)]
        if status_f != "All":
            filtered = filtered[filtered["status"] == status_f]
        if move_f != "All":
            filtered = filtered[filtered["movement"] == move_f]
        if date_f != "All":
            filtered = filtered[filtered["date"] == date_f]

        st.caption(f"{len(filtered)} records found")

        display = filtered[["plate","status","movement","date","time",
                            "location","owner"]].copy()
        display.columns = ["Plate","Status","Movement","Date","Time","Location","Owner"]

        st.dataframe(
            display.style.apply(color_row, axis=1),
            use_container_width=True, height=400
        )

        # View images for blocked rows
        blocked_with_img = filtered[
            (filtered["status"] == "Blocked") &
            (filtered["image_url"].str.startswith("http", na=False))
        ]
        if not blocked_with_img.empty:
            st.markdown("<div class='section-header'>Blocked Vehicle Images</div>",
                        unsafe_allow_html=True)
            for _, row in blocked_with_img.head(10).iterrows():
                with st.expander(f"📷  {row['plate']}  —  {row['date']}  {row['time']}"):
                    c1, c2 = st.columns([1,1])
                    with c1:
                        st.image(row["image_url"], use_container_width=True)
                    with c2:
                        st.markdown(f"""
                        **Plate:** `{row['plate']}`  
                        **Owner:** {row['owner']}  
                        **Status:** 🔴 {row['status']}  
                        **Movement:** {row['movement']}  
                        **Date:** {row['date']}  
                        **Time:** {row['time']}  
                        **Location:** {row['location']}
                        """)

        # Download
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv,
                        file_name=f"vehicle_log_{datetime.now().strftime('%d%m%Y')}.csv",
                        mime="text/csv")

    # GALLERY TAB

    elif tab == "Gallery":
        st.markdown("## Blocked Vehicle Gallery")
        st.markdown("""
        <div class="info-note">
        Images are uploaded to Cloudinary automatically when a blocked vehicle is detected.
        This page fetches them directly from the cloud — no manual upload needed.
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([4,1])
        with col2:
            if st.button("Refresh", use_container_width=True):
                st.rerun()

        with st.spinner("Loading images from Cloudinary..."):
            items = fetch_gallery()

        if not items:
            st.markdown("""
            <div style="text-align:center; padding:60px 0; color:#475569;">
            <div style="font-size:40px; margin-bottom:12px;">📷</div>
            <div style="font-size:15px;">No images yet.</div>
            <div style="font-size:13px; margin-top:6px;">
                Images appear here as soon as a blocked vehicle is detected.
            </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.caption(f"{len(items)} captures in cloud")
            cols = st.columns(3)
            for i, item in enumerate(items):
                with cols[i % 3]:
                    st.markdown('<div class="gal-card">', unsafe_allow_html=True)
                    try:
                        st.image(item["url"], use_container_width=True)
                    except:
                        st.markdown("Image unavailable")
                    st.markdown(f"""
                    <div class="gal-info">
                    <div class="gal-plate">🚗 {item['plate']}</div>
                    <div class="gal-meta">
                        👤 {item['owner']}<br/>
                        📅 {item['date']}&nbsp;&nbsp;🕐 {item['time']}<br/>
                        📍 {item['location'] or 'Main Gate'}
                    </div>
                    <div style="margin-top:8px;">
                        <span class="pill pill-blocked">Blocked</span>
                    </div>
                    </div>
                    </div>""", unsafe_allow_html=True)
                    if item.get("location","").startswith("http"):
                        st.markdown(f"[View on map]({item['location']})")
                    st.markdown("<br/>", unsafe_allow_html=True)

    # ANALYTICS TAB
    
    elif tab == "Analytics":
        import pandas as pd
        st.markdown("## Analytics")

        logs = get_all_logs()
        if not logs:
            st.info("No data yet. Start detection to see analytics.")
            return

        df    = pd.DataFrame(logs)
        stats = get_stats()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total",   stats["total"])
        c2.metric("Allowed", stats["allowed"])
        c3.metric("Blocked", stats["blocked"])
        c4.metric("Today",   stats["today"])

        col1, col2 = st.columns(2)

        with col1:
            sc = df["status"].value_counts().reset_index()
            sc.columns = ["Status","Count"]
            fig = px.bar(sc, x="Status", y="Count",
                color="Status",
                color_discrete_map={"Allowed":"#4ade80","Blocked":"#f87171","Not Registered":"#fbbf24"},
                title="Vehicles by Status")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f1f5f9", family="Inter"), showlegend=False,
                title_font=dict(size=14, color="#94a3b8"),
            )
            fig.update_xaxes(gridcolor="#2d3748"); fig.update_yaxes(gridcolor="#2d3748")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            mc = df["movement"].value_counts().reset_index()
            mc.columns = ["Movement","Count"]
            fig2 = px.pie(mc, names="Movement", values="Count", hole=.5,
                color="Movement",
                color_discrete_map={"Entry":"#3b82f6","Exit":"#a78bfa"},
                title="Entry vs Exit")
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f1f5f9", family="Inter"),
                title_font=dict(size=14, color="#94a3b8"),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Daily trend
        if "date" in df.columns:
            daily = df.groupby("date").size().reset_index(name="Detections")
            fig3  = px.line(daily, x="date", y="Detections",
                markers=True, title="Daily Detections",
                color_discrete_sequence=["#3b82f6"])
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f1f5f9", family="Inter"),
                title_font=dict(size=14, color="#94a3b8"),
            )
            fig3.update_xaxes(gridcolor="#2d3748"); fig3.update_yaxes(gridcolor="#2d3748")
            st.plotly_chart(fig3, use_container_width=True)

        # Blocked history table
        st.markdown("<div class='section-header'>Blocked Vehicle History</div>",
                    unsafe_allow_html=True)
        bdf = df[df["status"]=="Blocked"][["plate","owner","date","time","movement","location"]]
        bdf.columns = ["Plate","Owner","Date","Time","Movement","Location"]
        if not bdf.empty:
            st.dataframe(bdf, use_container_width=True)
        else:
            st.success("No blocked vehicles in the log.")


    # VEHICLES TAB
    
    elif tab == "Vehicles":
        import pandas as pd
        st.markdown("## Registered Vehicles")

        vehicles = get_all_vehicles()
        if vehicles:
            df = pd.DataFrame(vehicles)
            bl = len(df[df["status"]=="Blocked"])
            al = len(df[df["status"]=="Allowed"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Registered", len(df))
            c2.metric("Allowed",          al)
            c3.metric("Blocked",          bl)

            display = df[["plate","status","owner"]].copy()
            display.columns = ["Plate","Status","Owner"]
            st.dataframe(
                display.style.apply(
                    lambda row: [
                        'background:#14532d18;color:#86efac' if row.Status=="Allowed"
                        else 'background:#7f1d1d18;color:#fca5a5'
                        for _ in row], axis=1),
                use_container_width=True
            )

        st.markdown("<div class='section-header'>Add / Update Vehicle</div>",
                    unsafe_allow_html=True)
        with st.form("add_vehicle"):
            c1, c2, c3, c4 = st.columns([2,1.5,1.5,1])
            with c1: np_ = st.text_input("Plate Number", placeholder="TN01AB1234")
            with c2: ns  = st.selectbox("Status", ["Allowed","Blocked"])
            with c3: no_ = st.text_input("Owner Name", placeholder="Name")
            with c4:
                st.markdown("<br/>", unsafe_allow_html=True)
                save = st.form_submit_button("Save")
            if save:
                if np_.strip():
                    add_vehicle(np_.strip().upper(), ns, no_)
                    st.success(f"Saved: {np_.upper()} → {ns}")
                    st.rerun()
                else:
                    st.error("Enter a plate number.")

        if vehicles:
            st.markdown("<div class='section-header'>Remove Vehicle</div>",
                        unsafe_allow_html=True)
            plates   = [v["plate"] for v in vehicles]
            to_del   = st.selectbox("Select plate", plates)
            if st.button("Remove Vehicle", key="del_v"):
                delete_vehicle(to_del)
                st.success(f"Removed: {to_del}")
                st.rerun()

    # ══════════════════════════════════════════════════════
    # USERS TAB
    # ══════════════════════════════════════════════════════
    elif tab == "Users":
        import pandas as pd
        st.markdown("## Admin Users - kabee")

        users = get_all_users()
        if users:
            df = pd.DataFrame(users)[["id","username","email","phone","created"]]
            df.columns = ["ID","Username","Email","Phone","Created"]
            st.dataframe(df, use_container_width=True)

        st.markdown("<div class='section-header'>Add New User</div>",
                    unsafe_allow_html=True)
        with st.form("add_user"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: nu  = st.text_input("Username")
            with c2: np_ = st.text_input("Password", type="password")
            with c3: ne  = st.text_input("Email")
            with c4: nph = st.text_input("Phone")
            if st.form_submit_button("Add User"):
                if nu and np_:
                    ok = add_user(nu, np_, ne, nph)
                    if ok:
                        st.success(f"User '{nu}' added.")
                        st.rerun()
                    else:
                        st.error("Username already exists.")
                else:
                    st.error("Username and password are required.")

        if users and len(users) > 1:
            st.markdown("<div class='section-header'>Remove User</div>",
                        unsafe_allow_html=True)
            non_admin = [u for u in users if u["username"] != "admin"]
            if non_admin:
                names   = [u["username"] for u in non_admin]
                del_name = st.selectbox("Select user", names)
                uid      = next(u["id"] for u in non_admin if u["username"]==del_name)
                if st.button("Remove User"):
                    delete_user(uid)
                    st.success(f"Removed: {del_name}")
                    st.rerun()


# ENTRY POINT

if __name__ == "__main__":
    if "--detect" in sys.argv:
        run_detection()
    else:
        # When run via streamlit, __name__ != "__main__"
        # so call dashboard directly
        pass

# Streamlit calls this file as a module — run dashboard
try:
    import streamlit as st
    run_dashboard()
except ImportError:
    if "--detect" not in sys.argv:
        print("Run with: streamlit run main.py")
        print("Or:       python main.py --detect")

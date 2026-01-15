from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from googletrans import Translator
import pytesseract
from PIL import Image
from gtts import gTTS
import speech_recognition as sr
import os, uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- MYSQL ----------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'translator_db'
mysql = MySQL(app)

# ---------- TESSERACT ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- FOLDERS ----------
UPLOAD_FOLDER = "static/uploads"
AUDIO_FOLDER = "static/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

translator = Translator()

LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese (Simplified)",
    "ar": "Arabic",
    "bn": "Bengali",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "te": "Telugu",
    "ml": "Malayalam",
    "kn": "Kannada",
    "or": "Odia",
    "fa": "Persian",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "sv": "Swedish"
}


# ---------- UTILITY ----------
def save_history(input_text, output_text, lang):
    if "user" not in session:
        return
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO history(user_id,input_text,translated_text,language) VALUES(%s,%s,%s,%s)",
        (session["user"], input_text, output_text, lang)
    )
    mysql.connection.commit()
    cur.close()

# ---------- AUTH ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return "Email and password required", 400
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[3], password):
            session["user"] = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")
        return "Invalid email or password", 401
    return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password_raw = request.form.get("password")
        if not name or not email or not password_raw:
            return "All fields required", 400
        password = generate_password_hash(password_raw)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close()
            return "Email already exists", 400
        try:
            cur.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)", (name,email,password))
            mysql.connection.commit()
            cur.close()
            return redirect("/")
        except Exception as e:
            cur.close()
            print("Signup ERROR:", e)
            return "Signup failed", 500
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", languages=LANGUAGES)

# ---------- TRANSLATION ROUTES ----------
@app.route("/translate", methods=["POST"])
def translate_text():
    text = request.form.get("text")
    lang = request.form.get("language")
    if not text:
        return jsonify({"error":"No text provided"}),400
    translated = translator.translate(text, dest=lang).text
    save_history(text, translated, lang)
    return jsonify({"translated":translated})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.form.get("text")
    lang = request.form.get("language","en")
    if not text:
        return jsonify({"error":"No text provided"}),400
    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join(AUDIO_FOLDER,filename)
    gTTS(text=text,lang=lang).save(path)
    save_history(text,"[Voice Output]",lang)
    return jsonify({"audio":url_for("static", filename=f"audio/{filename}")})

@app.route("/image-text", methods=["POST"])
def image_text():
    if "image" not in request.files:
        return jsonify({"error":"No image uploaded"}),400
    image = request.files["image"]
    lang = request.form.get("language","en")
    filename = f"{uuid.uuid4()}_{image.filename}"
    path = os.path.join(UPLOAD_FOLDER,filename)
    image.save(path)
    extracted = pytesseract.image_to_string(Image.open(path))
    translated = translator.translate(extracted, dest=lang).text
    save_history(extracted,translated,lang)
    return jsonify({"text":extracted,"translated":translated})

@app.route("/image-voice", methods=["POST"])
def image_voice():
    text = request.form.get("text")
    lang = request.form.get("language","en")
    if not text:
        return jsonify({"error":"No text provided"}),400
    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join(AUDIO_FOLDER,filename)
    gTTS(text=text,lang=lang).save(path)
    save_history(text,"[Voice Output]",lang)
    return jsonify({"audio":url_for("static", filename=f"audio/{filename}")})

@app.route("/voice-text", methods=["POST"])
def voice_text():
    if "audio" not in request.files:
        return jsonify({"error":"No audio uploaded"}),400
    audio = request.files["audio"]
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio) as source:
            data = recognizer.record(source)
            text = recognizer.recognize_google(data)
            save_history("[Voice Input]",text,"en")
        return jsonify({"text":text})
    except Exception as e:
        print("VOICE ERROR:",e)
        return jsonify({"error":"Voice recognition failed"}),503

# ---------- HISTORY ----------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")
    cur = mysql.connection.cursor()
    cur.execute("SELECT input_text,translated_text,language FROM history WHERE user_id=%s",(session["user"],))
    data = cur.fetchall()
    cur.close()
    return render_template("history.html",data=data)

if __name__ == "__main__":
    app.run(debug=True)

# Universal Language Translator

A full-featured translator web application built with **Flask**. This app allows users to translate **text, voice, and images** into 25+ languages, with **text-to-speech**, **speech-to-text**, **image-to-text**, and **image-to-voice** features. Users can securely **signup/login** and track their **translation history**.  

---

## **Features**

### 1. Authentication
- Secure **Signup/Login** with hashed passwords using `Werkzeug`.
- Session-based user management.
- Logout functionality.

### 2. Translation
- **Text → Text** translation in 25+ languages.
- **Text → Voice**: Converts translated text to audio using `gTTS`.
- **Voice → Text**: Convert audio recordings into text using `SpeechRecognition`.
- **Image → Text**: Extract text from images using `pytesseract`.
- **Image → Voice**: Converts extracted text to audio.

### 3. History
- Stores per-user translation history in **MySQL**.
- Viewable in a clean table layout on the history page.

### 4. UI
- Modern **space-themed design** with responsive layout.
- Clear buttons for each feature (Translate, Speak, Clear).
- Supports multi-language dropdown dynamically.

---

## **Supported Languages (25+)**

English, Tamil, Hindi, French, German, Spanish, Italian, Portuguese, Russian, Japanese, Korean, Chinese (Simplified), Arabic, Bengali, Punjabi, Gujarati, Marathi, Telugu, Malayalam, Kannada, Odia, Persian, Turkish, Vietnamese, Indonesian, Swedish.

---

## **Setup Instructions**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<YourUsername>/universal-language-translator.git
cd universal-language-translator

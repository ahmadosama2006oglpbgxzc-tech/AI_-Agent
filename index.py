from flask import Flask, jsonify, request
import google.generativeai as genai
import os
import json

app = Flask(__name__)

# إعداد مفتاح جينيريتيف إيه آي (Gemini API)
# يفضل دائماً استخدام متغيرات البيئة (Environment Variables) على Vercel لـ GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")

# كطريقة احتياطية إذا كنت تستخدم ملف google_creds.json محلياً
creds_path = os.path.join(os.path.dirname(__file__), '..', 'google_creds.json')
if not api_key and os.path.exists(creds_path):
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
            api_key = creds_data.get("GEMINI_API_KEY")
    except Exception as e:
        print(f"Error loading credentials file: {e}")

if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not found!")

# المسار الرئيسي المطلوب لـ Vercel ليقرأ مكتبة Flask عند /flask
@app.route('/flask')
def home():
    return jsonify({
        "status": "success",
        "message": "Flask is running perfectly on Vercel!",
        "project": "AI Agent Platform"
    })

# مسار لإرسال الطلبات إلى الـ AI
@app.route('/flask/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
            
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(user_message)
        
        return jsonify({
            "status": "success",
            "reply": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# مهم جداً لبيئة Vercel Serverless
def handler(request, start_response):
    return app(request, start_response)

if __name__ == '__main__':
    app.run(debug=True)

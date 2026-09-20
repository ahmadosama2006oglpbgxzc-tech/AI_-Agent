import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 1. إعداد ذكاء الآلة والبرومت التأسيسي عاكس اللهجات
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
أنت المساعد الذكي الرسمي والممثل الحصري للمنشأة. دورك إدارة تجربة العميل وتوجيهه لإتمام الحجز بسلاسة.
يجب عليك تحليل اللهجة فوراً والرد بنفس النمط (مصرى، خليجى، فصحى، إنجليزي).
عند اكتمال البيانات (الاسم، الهاتف، الخدمة، الموعد) أطلق ملخصاً بصيغة JSON متضمناً الحالة success.
"""

# 2. إعداد الاتصال السحابي بـ Google Sheets
scope = ["https://google.com", "https://googleapis.com"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)
# اسم جدول البيانات الذي أنشأته على هاتفك
sheet = client.open("العملاء والحجوزات").sheet1

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    chat_history = request.json.get("history", [])
    
    # استدعاء النموذج السحابي لمعالجة النص
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    response = model.generate_content(user_message)
    reply_text = response.text
    
    # الأتمتة: فحص هل اكتملت البيانات لإدخالها في الـ Sheets
    if '"status": "success"' in reply_text or '"status":"success"' in reply_text:
        try:
            # استخراج البيانات وإضافتها تلقائياً كصف جديد
            # كود تبسيط استخراج النص وتحويله لصف في Sheets
            import json
            import re
            json_match = re.search(r'\{.*\}', reply_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                sheet.append_row([
                    data.get("client_name"),
                    data.get("phone"),
                    data.get("service_type"),
                    data.get("appointment_details")
                ])
        except Exception as e:
            print(f"Error syncing to sheet: {e}")

    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

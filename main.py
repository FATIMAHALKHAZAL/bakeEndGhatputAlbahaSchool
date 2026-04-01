import os
import httpx
import json
import re
from fastapi_poe import PoeBot, run_handler
from fastapi_poe.types import QueryRequest

# ضع رابط قوقل شيت (URL) الخاص بك هنا بين القوسين
GOOGLE_SHEET_URL = "رابط_قوقل_شيت_الخاص_بك"

class SchoolBot(PoeBot):
    async def get_response(self, request: QueryRequest):
        # 1. تجميع نص المحادثة بالكامل
        full_transcript = ""
        for message in request.query:
            full_transcript += f"{message.role}: {message.content}\n"

        # 2. البحث عن الـ JSON الذي سيولده الذكاء الاصطناعي (كما برمجناه في Poe)
        json_match = re.search(r'\{.*\}', full_transcript, re.DOTALL)
        
        # تجهيز البيانات الافتراضية
        payload = {
            "CustomerName": "تحليل جاري...",
            "CustomerID": request.user_id,
            "Transcript": full_transcript
        }

        # إذا وجدنا تحليل JSON، نأخذ البيانات منه
        if json_match:
            try:
                analysis = json.loads(json_match.group())
                payload.update(analysis)
            except:
                pass

        # 3. إرسال البيانات فوراً لجدول جوجل في الخلفية
        try:
            async with httpx.AsyncClient() as client:
                await client.post(GOOGLE_SHEET_URL, json=payload)
        except Exception as e:
            print(f"Error sending to Sheets: {e}")

        yield self.text_event("شكراً لك، تم استلام رسالتك وتحديث سجلات المدرسة بنجاح.")

if __name__ == "__main__":
    # هذا المفتاح (Access Key) ستجده في صفحة إنشاء البوت في Poe
    # سنضع أي كلمة الآن وسنغيرها لاحقاً إذا لزم الأمر
    run_handler(SchoolBot(), access_key="SCHOOL_BOT_2026")

import os
import httpx
import json
import re
import uvicorn
from fastapi import FastAPI
from fastapi_poe import PoeBot, make_app
from fastapi_poe.types import QueryRequest

# 1. ضع رابط قوقل شيت (URL) الخاص بك هنا
GOOGLE_SHEET_URL = "رابط_قوقل_شيت_الخاص_بك"

class SchoolBot(PoeBot):
    async def get_response(self, request: QueryRequest):
        # تجميع نص المحادثة
        full_transcript = ""
        for message in request.query:
            role_name = "العميل" if message.role == "user" else "البوت"
            full_transcript += f"{role_name}: {message.content}\n"

        # البحث عن تحليل JSON (الذي يخرجه البوت بناءً على البرومبت)
        json_match = re.search(r'\{.*\}', full_transcript, re.DOTALL)
        
        # البيانات الأساسية التي ستُرسل للجدول
        payload = {
            "CustomerName": "جاري الاستخراج...",
            "CustomerID": request.user_id,
            "CustomerPhone": "غير مسجل",
            "Summary": "محادثة جديدة",
            "Sentiment": "محايد",
            "Category": "استفسار",
            "Improvement": "لا يوجد",
            "Transcript": full_transcript
        }

        # إذا نجح الذكاء الاصطناعي في توليد JSON، نحدث البيانات
        if json_match:
            try:
                analysis = json.loads(json_match.group())
                payload.update(analysis)
            except:
                pass

        # 2. إرسال البيانات لجدول جوجل (Webhook)
        try:
            async with httpx.AsyncClient() as client:
                await client.post(GOOGLE_SHEET_URL, json=payload, timeout=10.0)
        except Exception as e:
            print(f"Error sending to Google Sheets: {e}")

        # الرد الذي يظهر للمستخدم في Poe
        yield self.text_event("شكراً لتواصلك مع مدرسة الباحة. تم تسجيل ملاحظاتك وتحديث السجل تلقائياً بنجاح. هل يمكنني مساعدتك في شيء آخر؟")

# 3. إعداد تشغيل السيرفر بما يتوافق مع Render و Poe
bot = SchoolBot()
# ملاحظة: "SCHOOL_BOT_2026" هو الـ Access Key الذي يجب أن تضعه أيضاً في صفحة Poe
app = make_app(bot, access_key="PRDdwf7hucLOqKazpSYMTjpBIpIbt82d")

if __name__ == "__main__":
    # Render يعطينا منفذ (Port) تلقائياً عبر متغيرات البيئة
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

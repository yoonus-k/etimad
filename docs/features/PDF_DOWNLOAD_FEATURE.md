# ميزة تحميل كراسة الشروط والمواصفات كـ PDF

## الوصف
تم تحسين زر "📥 تحميل المرفقات" ليقوم الآن بوظيفتين:
1. **تحميل المرفقات العادية** (جداول الكميات والملفات المرفقة)
2. **تحميل كراسة الشروط والمواصفات كملف PDF**

## كيف تعمل؟

### Frontend (JavaScript)
عند الضغط على زر "تحميل المرفقات"، يقوم السكريبت بـ:

1. **الخطوة 1: تحميل المرفقات العادية**
   - يرسل طلب إلى `/api/tender/${tenderId}/download`
   - يعرض رسالة "⏳ جاري تحميل المرفقات..."

2. **الخطوة 2: جلب HTML من Etimad**
   - يحصل على `tenderIdString` من بطاقة المنافسة
   - يجلب محتوى HTML من:
     ```
     https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId={tenderIdString}
     ```
   - يعرض رسالة "⏳ جاري تحميل كراسة الشروط..."

3. **الخطوة 3: تحويل HTML إلى PDF**
   - يرسل محتوى HTML إلى `/api/tender/${tenderIdString}/download-pdf`
   - يستقبل ملف PDF
   - يحمّل الملف تلقائياً باسم: `كراسة_الشروط_والمواصفات_{tenderIdString}.pdf`

4. **النتيجة النهائية**
   - يعرض رسالة "✅ تم التحميل بنجاح"
   - الزر يعود لحالته الطبيعية بعد 3 ثوانٍ

### Backend (Python/Flask)

#### Endpoint: `/api/tender/<tender_id_str>/download-pdf`
- **Method:** POST
- **Content-Type:** application/json
- **Body:**
  ```json
  {
    "html": "<!DOCTYPE html>..."
  }
  ```

**الخطوات:**
1. يستقبل محتوى HTML من الـ request
2. يستخدم مكتبة `WeasyPrint` لتحويل HTML إلى PDF
3. يرسل ملف PDF كـ download
4. اسم الملف: `كراسة الشروط والمواصفات_{tender_id_str}.pdf`

## المتطلبات التقنية

### Python Packages
```bash
pip install weasyprint==60.1
```

### الملفات المعدلة
- `app.py`: إضافة endpoint `/api/tender/<tender_id_str>/download-pdf`
- `static/script.js`: تعديل دالة `downloadTenderDocs()`
- `requirements.txt`: إضافة `weasyprint==60.1`

## معالجة الأخطاء

### إذا فشل تحميل PDF
- سيظهر تحذير في الـ console
- لكن المرفقات العادية ستُحمّل بنجاح
- الزر سيعرض "✅ تم التحميل بنجاح" (للمرفقات)

### إذا لم تكن WeasyPrint مثبتة
- سيظهر خطأ: "WeasyPrint is not installed"
- يجب تثبيت المكتبة أولاً

## مثال على الاستخدام

1. المستخدم يفتح التطبيق ويجلب المناقصات
2. يضغط على زر "📥 تحميل المرفقات" لأي مناقصة
3. التطبيق يقوم بـ:
   - تحميل جداول الكميات والمرفقات في مجلد `downloads/`
   - تحميل ملف PDF لكراسة الشروط والمواصفات

## ملاحظات
- عملية التحويل من HTML إلى PDF قد تستغرق ثوانٍ قليلة حسب حجم المحتوى
- ملف PDF يحتوي على كامل محتوى كراسة الشروط والمواصفات بتنسيق قابل للطباعة
- الـ PDF يحتفظ بالتنسيق والجداول والصور من HTML الأصلي

# 📁 تسمية مجلدات التحميل

## ✅ التحديث الجديد

تم تحديث نظام تسمية مجلدات التحميل لتكون أكثر وضوحاً وتنظيماً.

## 📋 التسمية الجديدة للمجلدات

### الصيغة
```
اسم_المناقصة_الرقم_المرجعي
```

### مثال
```
صيانة_وتطوير_ودعم_الإتصالات_الادارية_الحالي_للمديرية_العامة_لمكافحة_المخدرات_9022010158
```

## 🔧 التعديلات التقنية

### 1. Backend - `app.py`
تم تعديل endpoint `/api/tender/<tender_id>/download` ليستقبل معلومات المناقصة:

```python
@app.route('/api/tender/<tender_id>/download')
def download_tender_documents(tender_id):
    # Get tender name and reference number from request
    tender_name = request.args.get('tenderName', '')
    reference_number = request.args.get('referenceNumber', '')
    
    folder_path = scraper.download_tender_documents(
        tender_id, 
        tender_name=tender_name,
        reference_number=reference_number
    )
```

### 2. Scraper - `tender_scraper.py`
تم تحديث دالة `download_tender_documents` لاستخدام اسم المناقصة والرقم المرجعي:

```python
def download_tender_documents(self, tender_id, tender_name='', reference_number=''):
    # Create folder name with tender name and reference number
    if tender_name and reference_number:
        # Clean the tender name to be filesystem-safe
        safe_name = "".join(c if c.isalnum() or c in (...) else '_' for c in tender_name)
        safe_name = safe_name.strip()[:100]  # Limit length
        folder_name = f"{safe_name}_{reference_number}"
    else:
        folder_name = tender_id
```

### 3. Frontend - `script.js`
تم تحديث دالة `downloadTenderDocs` لإرسال معلومات المناقصة:

```javascript
// Get tender info from card
const card = button.closest('.tender-card');
const tenderName = card?.querySelector('.tender-name')?.textContent?.trim() || '';
const referenceNumber = card?.querySelector('.reference-number')?.textContent?.trim() || '';

// Send with download request
const downloadUrl = `/api/tender/${tenderId}/download?tenderName=${encodeURIComponent(tenderName)}&referenceNumber=${encodeURIComponent(referenceNumber)}`;
```

## 🔒 معالجة الأسماء

تتم معالجة اسم المناقصة ليكون آمناً لنظام الملفات:

1. **الأحرف المسموحة**: 
   - الأحرف الأبجدية العربية والإنجليزية
   - الأرقام
   - المسافات والشرطات والشرطات السفلية

2. **الأحرف غير المسموحة**: يتم استبدالها بـ `_`

3. **طول الاسم**: محدود بـ 100 حرف لتجنب مشاكل أنظمة الملفات

## 📂 مسار المجلدات

```
downloads/
└── اسم_المناقصة_الرقم_المرجعي/
    ├── كراسة_الشروط_والمواصفات.pdf
    ├── جدول_الكميات.xlsx
    └── مرفقات_أخرى/
```

## 🎯 الفوائد

1. **سهولة البحث**: يمكن إيجاد مجلد المناقصة بسرعة عن طريق الاسم
2. **التعرف السريع**: لا حاجة لفتح المجلد لمعرفة محتواه
3. **التنظيم**: مجلدات واضحة ومنظمة
4. **الرقم المرجعي**: يضمن عدم التكرار والربط مع النظام

## 🧪 الاختبار

1. قم بجلب المناقصات
2. اضغط على زر "تحميل المرفقات"
3. تحقق من اسم المجلد في مجلد `downloads`

## 📝 ملاحظات

- إذا لم يتوفر اسم المناقصة أو الرقم المرجعي، يتم استخدام `tender_id` الافتراضي
- يتم تنظيف الاسم تلقائياً لتجنب مشاكل نظام الملفات
- الطول المحدود (100 حرف) يضمن التوافق مع جميع أنظمة التشغيل

# 🔧 حل المشاكل - Troubleshooting

## ❌ مشكلة: اسم المجلد لا يزال غريب

### الأعراض:
```
تحميل المرفقات إلى:
downloads/CTawqUkTE7YbwNdHDbc40A==/

بدلاً من:
downloads/صيانة_وتطوير_الإتصالات_9022010158/
```

### السبب:
الصفحة لم يتم تحديثها بعد التعديلات على JavaScript

### ✅ الحل:

1. **تحديث كامل للصفحة** (مهم جداً):
   ```
   اضغط: Ctrl + Shift + R
   
   أو
   
   Ctrl + F5
   ```
   هذا يحذف الذاكرة المؤقتة (Cache) ويجلب أحدث نسخة من JavaScript

2. **اجلب المناقصات مرة أخرى**:
   - اضغط "🔄 جلب مناقصات جديدة"
   - انتظر حتى تظهر البطاقات

3. **جرب التحميل**:
   - اضغر "📥 تحميل المرفقات"
   - تحقق من اسم المجلد في `downloads/`

---

## ❌ مشكلة: خطأ 500 عند تحميل PDF

### الأعراض:
```
GET http://127.0.0.1:5000/api/tender/.../download-pdf 500 (INTERNAL SERVER ERROR)
⚠️ Failed to download PDF, but attachments were downloaded
```

### الأسباب المحتملة:

#### 1. **مشكلة في الكوكيز**
الكوكيز منتهية الصلاحية أو غير صحيحة

**الحل:**
- اضغط "🍪 تحديث الكوكيز"
- الصق كوكيز جديدة من إضافة المتصفح
- جرب مرة أخرى

#### 2. **HTML الصفحة فارغ أو صغير جداً**
الصفحة لا تحتوي على محتوى

**الحل:**
- تحقق من أن المناقصة تحتوي على "كراسة الشروط والمواصفات"
- بعض المناقصات قد لا تحتوي على هذا المستند

#### 3. **مشكلة في WeasyPrint**
مكتبة تحويل PDF غير مثبتة بشكل صحيح

**الحل:**
```powershell
pip uninstall weasyprint
pip install weasyprint==60.2
```

---

## ❌ مشكلة: tenderName و referenceNumber فارغين

### الأعراض:
```
GET /api/tender/.../download?tenderName=&referenceNumber=
```

### السبب:
JavaScript القديم في ذاكرة المتصفح المؤقتة

### ✅ الحل:

**خطوات مهمة:**

1. **تحديث كامل** (إلزامي):
   ```
   Ctrl + Shift + R
   ```

2. **التحقق من Console**:
   - افتح Developer Tools: `F12`
   - اذهب إلى Console
   - احذف الأخطاء القديمة: `Clear console`

3. **إعادة جلب المناقصات**:
   - اضغط "🔄 جلب مناقصات جديدة"
   - يجب أن تحتوي البطاقات على:
     * `.tender-name` class في العنوان
     * `.reference-number` class في الرقم المرجعي

4. **اختبار**:
   - جرب التحميل مرة أخرى
   - تحقق من Console أن URL يحتوي على القيم:
     ```
     tenderName=صيانة%20وتطوير&referenceNumber=9022010158
     ```

---

## 🧪 التحقق من التحديثات

### 1. **تحقق من JavaScript محدث:**

افتح Developer Tools (`F12`) → Console → اكتب:
```javascript
// يجب أن يحتوي العنوان على class "tender-name"
document.querySelector('.tender-name')

// يجب أن يحتوي الرقم المرجعي على class "reference-number"  
document.querySelector('.reference-number')
```

إذا ظهر `null`، معناها التحديث لم يطبق → اضغط `Ctrl + Shift + R`

### 2. **تحقق من Flask يعمل:**

Terminal يجب أن يظهر:
```
✅ Loaded 6 cookies from 2025-10-13T14:39:15.460278
* Debugger is active!
* Running on http://127.0.0.1:5000
```

### 3. **تحقق من المجلد:**

بعد التحميل، المجلد يجب أن يكون:
```
downloads/
└── اسم_واضح_للمناقصة_الرقم_المرجعي/
    ├── كراسة_الشروط_والمواصفات.pdf
    └── مرفقات أخرى...
```

---

## 📋 Checklist للتحميل الناجح

- [ ] Flask يعمل (`python app.py`)
- [ ] الكوكيز محدثة وصالحة (6 cookies أو أكثر)
- [ ] الصفحة تم تحديثها بالكامل (`Ctrl + Shift + R`)
- [ ] المناقصات تم جلبها من API
- [ ] Console نظيف بدون أخطاء CORS
- [ ] اسم المناقصة يظهر في البطاقة
- [ ] الرقم المرجعي يظهر في البطاقة

---

## 🆘 ما زالت المشكلة موجودة؟

### أرسل هذه المعلومات:

1. **من Console** (`F12` → Console):
   ```javascript
   // نسخ output هذا الأمر:
   console.log({
     tenderName: document.querySelector('.tender-name')?.textContent,
     referenceNumber: document.querySelector('.reference-number')?.textContent,
     hasClasses: {
       tenderName: !!document.querySelector('.tender-name'),
       referenceNumber: !!document.querySelector('.reference-number')
     }
   });
   ```

2. **من Terminal** (آخر 20 سطر):
   ```powershell
   # في Terminal Flask
   # نسخ آخر الأسطر بعد الضغط على زر التحميل
   ```

3. **اسم المجلد الحالي**:
   ```
   # المجلد الذي تم إنشاؤه في downloads/
   ```

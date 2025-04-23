# خطة ترحيل من تطبيق Contractors إلى A-List Home Pros

## المقدمة

هذه الوثيقة تحدد خطة الترحيل من تطبيق `contractors` القديم إلى تطبيق `alistpros_profiles` الجديد. الهدف هو إزالة تطبيق `contractors` بالكامل مع الحفاظ على جميع الوظائف والبيانات.

## الملفات التي تحتاج إلى تحديث

بناءً على البحث، هناك العديد من الملفات التي لا تزال تستورد من تطبيق `contractors`:

1. **payments/views.py** - استيراد `ContractorProfile`
2. **scheduling/serializers.py** - استيراد `ContractorProfile`, `ServiceCategory`, `ServiceCategorySerializer`, `ContractorProfileSerializer`
3. **payments/models.py** - استيراد `ContractorProfile`
4. **scheduling/models.py** - استيراد `ContractorProfile`, `ServiceCategory`
5. **payments/serializers.py** - استيراد `ContractorProfileSerializer`
6. **scheduling/views.py** - استيراد `ContractorProfile`
7. **analytics/views.py** - استيراد `ContractorProfile`, `ServiceCategory`
8. **analytics/models.py** - استيراد `ContractorProfile`, `ServiceCategory`
9. **ملفات إنشاء البيانات** - تستخدم نماذج من `contractors`

## خطوات الترحيل

### المرحلة 1: تحديث الاستيرادات والمراجع

1. تحديث جميع الاستيرادات لاستخدام نماذج `alistpros_profiles` بدلاً من `contractors`.
2. تحديث جميع المراجع في الكود لاستخدام النماذج الجديدة.
3. التأكد من أن أسماء الحقول والعلاقات متطابقة أو تم تعديلها بشكل صحيح.

### المرحلة 2: ترحيل البيانات

1. إنشاء سكربت ترحيل لنقل البيانات من نماذج `contractors` إلى نماذج `alistpros_profiles`.
2. التأكد من أن جميع العلاقات والمفاتيح الخارجية تم تحديثها بشكل صحيح.

### المرحلة 3: تحديث نقاط النهاية API

1. التأكد من أن جميع نقاط النهاية API التي كانت تستخدم `contractors` لها مكافئ في `alistpros_profiles`.
2. الاحتفاظ بنقاط النهاية القديمة مؤقتًا للتوافق الخلفي.

### المرحلة 4: الاختبار

1. إجراء اختبارات شاملة للتأكد من أن جميع الوظائف تعمل بشكل صحيح.
2. التأكد من أن جميع نقاط النهاية API تعمل كما هو متوقع.

### المرحلة 5: إزالة تطبيق `contractors`

1. إزالة تطبيق `contractors` من `INSTALLED_APPS` في ملف الإعدادات.
2. إزالة مسار `contractors` من ملف `urls.py` الرئيسي.
3. إزالة مجلد `contractors` من المشروع.

## ملاحظات هامة

- يجب الحفاظ على التوافق الخلفي قدر الإمكان.
- يجب إجراء نسخة احتياطية لقاعدة البيانات قبل أي تغييرات.
- يجب اختبار كل خطوة بشكل منفصل قبل الانتقال إلى الخطوة التالية.

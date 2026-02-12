"""
Comprehensive mock data seeder for testing SEMI_PRIVATE & PRIVATE design plan flows.

Creates:
- 2 new categories with full attributes
- Design plans (PUBLIC, SEMI_PRIVATE, PRIVATE, OWN_DESIGN) per category
- Rich questionnaires with sections, questions (all input types), options, conditional logic
- A DESIGNER user and a second CUSTOMER user
- Orders in various states for each plan type
- Questionnaire answers for SEMI_PRIVATE/PRIVATE orders
- Payments for paid orders

Run from project root:
    docker exec -i sheetaro_backend python /app/scripts/seed_mock_data.py
Or locally (with DATABASE_URL set):
    cd backend && python -m scripts.seed_mock_data
"""

import asyncio
import uuid
import sys
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Adjust path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import text


# ─── IDs (deterministic for easy reference) ──────────────────────────────

# Categories
CAT_LABEL_ID    = uuid.UUID("a0000001-0001-4000-8000-000000000001")
CAT_BROCHURE_ID = uuid.UUID("a0000001-0001-4000-8000-000000000002")

# Attributes
ATTR_LABEL_SIZE_ID    = uuid.UUID("b0000001-0001-4000-8000-000000000001")
ATTR_LABEL_MATERIAL_ID = uuid.UUID("b0000001-0001-4000-8000-000000000002")
ATTR_LABEL_FINISH_ID  = uuid.UUID("b0000001-0001-4000-8000-000000000003")
ATTR_BROCHURE_SIZE_ID = uuid.UUID("b0000001-0001-4000-8000-000000000004")
ATTR_BROCHURE_PAPER_ID = uuid.UUID("b0000001-0001-4000-8000-000000000005")
ATTR_BROCHURE_FOLD_ID  = uuid.UUID("b0000001-0001-4000-8000-000000000006")

# Attribute Options
OPT_IDS = {f"opt{i}": uuid.UUID(f"c0000001-0001-4000-8000-{i:012d}") for i in range(1, 30)}

# Users
USER_CUSTOMER2_ID = uuid.UUID("d0000001-0001-4000-8000-000000000001")
USER_DESIGNER_ID  = uuid.UUID("d0000001-0001-4000-8000-000000000002")

# Design Plans
PLAN_LABEL_PUBLIC_ID      = uuid.UUID("e0000001-0001-4000-8000-000000000001")
PLAN_LABEL_SEMI_ID        = uuid.UUID("e0000001-0001-4000-8000-000000000002")
PLAN_LABEL_PRIVATE_ID     = uuid.UUID("e0000001-0001-4000-8000-000000000003")
PLAN_LABEL_OWN_ID         = uuid.UUID("e0000001-0001-4000-8000-000000000004")
PLAN_BROCHURE_PUBLIC_ID   = uuid.UUID("e0000001-0001-4000-8000-000000000005")
PLAN_BROCHURE_SEMI_ID     = uuid.UUID("e0000001-0001-4000-8000-000000000006")
PLAN_BROCHURE_PRIVATE_ID  = uuid.UUID("e0000001-0001-4000-8000-000000000007")
PLAN_BROCHURE_OWN_ID      = uuid.UUID("e0000001-0001-4000-8000-000000000008")

# Sections
SEC_SEMI_BRAND_ID    = uuid.UUID("f0000001-0001-4000-8000-000000000001")
SEC_SEMI_DESIGN_ID   = uuid.UUID("f0000001-0001-4000-8000-000000000002")
SEC_SEMI_CONTENT_ID  = uuid.UUID("f0000001-0001-4000-8000-000000000003")
SEC_PRIV_BRAND_ID    = uuid.UUID("f0000001-0001-4000-8000-000000000004")
SEC_PRIV_DESIGN_ID   = uuid.UUID("f0000001-0001-4000-8000-000000000005")
SEC_BRO_SEMI_BRAND_ID   = uuid.UUID("f0000001-0001-4000-8000-000000000006")
SEC_BRO_SEMI_CONTENT_ID = uuid.UUID("f0000001-0001-4000-8000-000000000007")

# Questions (many types to test)
Q_IDS = {f"q{i}": uuid.UUID(f"11000001-0001-4000-8000-{i:012d}") for i in range(1, 40)}

# Question Options
QO_IDS = {f"qo{i}": uuid.UUID(f"12000001-0001-4000-8000-{i:012d}") for i in range(1, 50)}

# Orders
ORD_IDS = {f"o{i}": uuid.UUID(f"22000001-0001-4000-8000-{i:012d}") for i in range(1, 20)}

# Payments
PAY_IDS = {f"p{i}": uuid.UUID(f"33000001-0001-4000-8000-{i:012d}") for i in range(1, 20)}

# Answer IDs
ANS_IDS = {f"a{i}": uuid.UUID(f"44000001-0001-4000-8000-{i:012d}") for i in range(1, 60)}

# Existing users
ADMIN_ID = uuid.UUID("5ef322cc-dca1-4d14-a321-c4a927baf27f")
CUSTOMER1_ID = uuid.UUID("3a5156cf-9567-4a07-8103-efa2a252c9d8")
PRINTSHOP1_ID = uuid.UUID("746e87a6-e7d7-491e-8a7c-69bf262fa12b")

NOW = datetime.now(timezone.utc)


async def seed():
    """Insert all mock data."""
    from app.core.database import engine
    
    async with engine.begin() as conn:
        # ─── 1. Users ───────────────────────────────────────
        print("Creating users...")
        
        # Second customer
        await conn.execute(text("""
            INSERT INTO users (id, first_name, last_name, phone_number, role, is_active, phone_verified, city, address, created_at, updated_at)
            VALUES (:id, :fn, :ln, :phone, :role, true, true, :city, :addr, now(), now())
            ON CONFLICT (id) DO NOTHING
        """), {
            "id": USER_CUSTOMER2_ID, "fn": "زهرا", "ln": "احمدی",
            "phone": "09191234567", "role": "CUSTOMER",
            "city": "اصفهان", "addr": "خیابان چهارباغ، پلاک ۱۵"
        })
        
        # Designer user
        await conn.execute(text("""
            INSERT INTO users (id, first_name, last_name, phone_number, role, is_active, phone_verified, city, created_at, updated_at)
            VALUES (:id, :fn, :ln, :phone, :role, true, true, :city, now(), now())
            ON CONFLICT (id) DO NOTHING
        """), {
            "id": USER_DESIGNER_ID, "fn": "علی", "ln": "طراح",
            "phone": "09351234567", "role": "DESIGNER", "city": "تهران"
        })

        # ─── 2. Categories ──────────────────────────────────
        print("Creating categories...")
        
        for cat in [
            (CAT_LABEL_ID, "label", "لیبل و برچسب", "📋", "لیبل و برچسب در انواع جنس و اندازه", 5000, 1),
            (CAT_BROCHURE_ID, "brochure", "بروشور و کاتالوگ", "📰", "بروشور و کاتالوگ تبلیغاتی", 15000, 2),
        ]:
            await conn.execute(text("""
                INSERT INTO categories (id, slug, name_fa, icon, description_fa, base_price, sort_order, is_active, created_at, updated_at)
                VALUES (:id, :slug, :name, :icon, :desc, :price, :sort, true, now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {"id": cat[0], "slug": cat[1], "name": cat[2], "icon": cat[3], "desc": cat[4], "price": cat[5], "sort": cat[6]})

        # ─── 3. Category Attributes ──────────────────────────
        print("Creating attributes...")
        
        # Label attributes
        label_attrs = [
            (ATTR_LABEL_SIZE_ID, CAT_LABEL_ID, "size", "اندازه", "SELECT", 0),
            (ATTR_LABEL_MATERIAL_ID, CAT_LABEL_ID, "material", "جنس", "SELECT", 1),
            (ATTR_LABEL_FINISH_ID, CAT_LABEL_ID, "finish", "روکش", "SELECT", 2),
        ]
        # Brochure attributes
        brochure_attrs = [
            (ATTR_BROCHURE_SIZE_ID, CAT_BROCHURE_ID, "size", "اندازه", "SELECT", 0),
            (ATTR_BROCHURE_PAPER_ID, CAT_BROCHURE_ID, "paper", "جنس کاغذ", "SELECT", 1),
            (ATTR_BROCHURE_FOLD_ID, CAT_BROCHURE_ID, "fold", "نوع تا", "SELECT", 2),
        ]
        
        for attr in label_attrs + brochure_attrs:
            await conn.execute(text("""
                INSERT INTO category_attributes (id, category_id, slug, name_fa, input_type, sort_order, is_active, is_required, created_at, updated_at)
                VALUES (:id, :cat_id, :slug, :name, :input_type, :sort, true, true, now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {"id": attr[0], "cat_id": attr[1], "slug": attr[2], "name": attr[3], "input_type": attr[4], "sort": attr[5]})
        
        # ─── 4. Attribute Options ────────────────────────────
        print("Creating attribute options...")
        
        options = [
            # Label size
            (OPT_IDS["opt1"], ATTR_LABEL_SIZE_ID, "5x5", "۵×۵ سانتی‌متر", 0, 0),
            (OPT_IDS["opt2"], ATTR_LABEL_SIZE_ID, "10x10", "۱۰×۱۰ سانتی‌متر", 2000, 1),
            (OPT_IDS["opt3"], ATTR_LABEL_SIZE_ID, "15x10", "۱۵×۱۰ سانتی‌متر", 4000, 2),
            # Label material
            (OPT_IDS["opt4"], ATTR_LABEL_MATERIAL_ID, "paper", "کاغذی", 0, 0),
            (OPT_IDS["opt5"], ATTR_LABEL_MATERIAL_ID, "pvc", "PVC شفاف", 5000, 1),
            (OPT_IDS["opt6"], ATTR_LABEL_MATERIAL_ID, "metallic", "متالایز", 8000, 2),
            (OPT_IDS["opt7"], ATTR_LABEL_MATERIAL_ID, "kraft", "کرافت", 3000, 3),
            # Label finish
            (OPT_IDS["opt8"], ATTR_LABEL_FINISH_ID, "matte", "مات", 1000, 0),
            (OPT_IDS["opt9"], ATTR_LABEL_FINISH_ID, "glossy", "براق", 1500, 1),
            (OPT_IDS["opt10"], ATTR_LABEL_FINISH_ID, "uv", "یووی موضعی", 3000, 2),
            # Brochure size
            (OPT_IDS["opt11"], ATTR_BROCHURE_SIZE_ID, "a4", "A4", 0, 0),
            (OPT_IDS["opt12"], ATTR_BROCHURE_SIZE_ID, "a5", "A5", 0, 1),
            (OPT_IDS["opt13"], ATTR_BROCHURE_SIZE_ID, "a3", "A3", 10000, 2),
            # Brochure paper
            (OPT_IDS["opt14"], ATTR_BROCHURE_PAPER_ID, "coated135", "گلاسه ۱۳۵ گرم", 0, 0),
            (OPT_IDS["opt15"], ATTR_BROCHURE_PAPER_ID, "coated170", "گلاسه ۱۷۰ گرم", 5000, 1),
            (OPT_IDS["opt16"], ATTR_BROCHURE_PAPER_ID, "matte200", "مات ۲۰۰ گرم", 8000, 2),
            # Brochure fold
            (OPT_IDS["opt17"], ATTR_BROCHURE_FOLD_ID, "bi-fold", "دو لت", 0, 0),
            (OPT_IDS["opt18"], ATTR_BROCHURE_FOLD_ID, "tri-fold", "سه لت", 3000, 1),
            (OPT_IDS["opt19"], ATTR_BROCHURE_FOLD_ID, "z-fold", "زد فولد", 4000, 2),
            (OPT_IDS["opt20"], ATTR_BROCHURE_FOLD_ID, "gate-fold", "گیت فولد", 5000, 3),
        ]
        
        for o in options:
            await conn.execute(text("""
                INSERT INTO attribute_options (id, attribute_id, value, label_fa, price_modifier, sort_order, is_active, created_at)
                VALUES (:id, :attr_id, :val, :label, :price, :sort, true, now())
                ON CONFLICT (id) DO NOTHING
            """), {"id": o[0], "attr_id": o[1], "val": o[2], "label": o[3], "price": o[4], "sort": o[5]})
        
        # ─── 5. Design Plans ────────────────────────────────
        print("Creating design plans...")
        
        plans = [
            # Label plans
            (PLAN_LABEL_PUBLIC_ID, CAT_LABEL_ID, "public", "قالب آماده", "از بین قالب‌های آماده انتخاب کنید", 0, 0, False, True, False, 0),
            (PLAN_LABEL_SEMI_ID, CAT_LABEL_ID, "semi_private", "نیمه اختصاصی", "پرسشنامه پر کنید، طراح برایتان طرح می‌زند", 600000, 3, True, False, False, 1),
            (PLAN_LABEL_PRIVATE_ID, CAT_LABEL_ID, "private", "اختصاصی", "با طراح مستقیم چت کنید تا طرح دلخواهتان آماده شود", 5000000, None, True, False, False, 2),
            (PLAN_LABEL_OWN_ID, CAT_LABEL_ID, "own_design", "طرح خودم", "فایل طراحی خود را آپلود کنید", 0, 0, False, False, True, 3),
            # Brochure plans
            (PLAN_BROCHURE_PUBLIC_ID, CAT_BROCHURE_ID, "public", "قالب آماده", "از بین قالب‌های آماده بروشور انتخاب کنید", 0, 0, False, True, False, 0),
            (PLAN_BROCHURE_SEMI_ID, CAT_BROCHURE_ID, "semi_private", "نیمه اختصاصی", "پرسشنامه پر کنید و طرح بروشور دریافت کنید", 800000, 2, True, False, False, 1),
            (PLAN_BROCHURE_PRIVATE_ID, CAT_BROCHURE_ID, "private", "اختصاصی", "با طراح چت کنید و بروشور کاملا اختصاصی بگیرید", 6000000, None, True, False, False, 2),
            (PLAN_BROCHURE_OWN_ID, CAT_BROCHURE_ID, "own_design", "طرح خودم", "فایل طراحی بروشور خود را آپلود کنید", 0, 0, False, False, True, 3),
        ]
        
        for p in plans:
            await conn.execute(text("""
                INSERT INTO category_design_plans (id, category_id, slug, name_fa, description_fa, price, max_revisions, revision_price, has_questionnaire, has_templates, has_file_upload, sort_order, is_active, created_at, updated_at)
                VALUES (:id, :cat_id, :slug, :name, :desc, :price, :max_rev, 0, :has_q, :has_t, :has_f, :sort, true, now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": p[0], "cat_id": p[1], "slug": p[2], "name": p[3], "desc": p[4],
                "price": p[5], "max_rev": p[6], "has_q": p[7], "has_t": p[8], "has_f": p[9], "sort": p[10]
            })
        
        # ─── 6. Questionnaire Sections ──────────────────────
        print("Creating questionnaire sections...")
        
        sections = [
            # Label Semi-Private sections
            (SEC_SEMI_BRAND_ID, PLAN_LABEL_SEMI_ID, "اطلاعات برند", "اطلاعات کلی برند و کسب‌وکار شما", 0),
            (SEC_SEMI_DESIGN_ID, PLAN_LABEL_SEMI_ID, "ترجیحات طراحی", "سبک و سلیقه طراحی مورد نظر شما", 1),
            (SEC_SEMI_CONTENT_ID, PLAN_LABEL_SEMI_ID, "محتوا و متن", "متن و اطلاعاتی که روی لیبل چاپ می‌شود", 2),
            # Label Private sections
            (SEC_PRIV_BRAND_ID, PLAN_LABEL_PRIVATE_ID, "اطلاعات اولیه", "اطلاعات اولیه برای شروع طراحی اختصاصی", 0),
            (SEC_PRIV_DESIGN_ID, PLAN_LABEL_PRIVATE_ID, "سبک و ایده", "ایده‌ها و الهام‌بخش‌های طراحی", 1),
            # Brochure Semi-Private sections
            (SEC_BRO_SEMI_BRAND_ID, PLAN_BROCHURE_SEMI_ID, "اطلاعات کسب‌وکار", "اطلاعات شرکت و برندتان", 0),
            (SEC_BRO_SEMI_CONTENT_ID, PLAN_BROCHURE_SEMI_ID, "محتوای بروشور", "متن و تصاویری که در بروشور قرار می‌گیرد", 1),
        ]
        
        for s in sections:
            await conn.execute(text("""
                INSERT INTO question_sections (id, plan_id, title_fa, description_fa, sort_order, is_active, created_at, updated_at)
                VALUES (:id, :plan_id, :title, :desc, :sort, true, now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {"id": s[0], "plan_id": s[1], "title": s[2], "desc": s[3], "sort": s[4]})
        
        # ─── 7. Questions ───────────────────────────────────
        print("Creating questionnaire questions...")
        
        # ---- LABEL SEMI-PRIVATE Questions ----
        questions = [
            # Section: Brand Info
            (Q_IDS["q1"], PLAN_LABEL_SEMI_ID, SEC_SEMI_BRAND_ID, "نام برند یا کسب‌وکار شما چیست؟", "TEXT", True, "مثلا: فروشگاه گل‌های بهاری", None, {}, None, None, 0),
            (Q_IDS["q2"], PLAN_LABEL_SEMI_ID, SEC_SEMI_BRAND_ID, "حوزه فعالیت شما چیست؟", "SINGLE_CHOICE", True, None, "حوزه فعالیت به طراح کمک می‌کند سبک مناسب را انتخاب کند", {}, None, None, 1),
            (Q_IDS["q3"], PLAN_LABEL_SEMI_ID, SEC_SEMI_BRAND_ID, "لوگو یا نشانه تصویری دارید؟", "SINGLE_CHOICE", True, None, None, {}, None, None, 2),
            (Q_IDS["q4"], PLAN_LABEL_SEMI_ID, SEC_SEMI_BRAND_ID, "فایل لوگو را آپلود کنید", "IMAGE_UPLOAD", False, None, "فرمت PNG یا SVG با پس‌زمینه شفاف ترجیح داده می‌شود", {}, Q_IDS["q3"], '["yes"]', 3),
            
            # Section: Design Preferences
            (Q_IDS["q5"], PLAN_LABEL_SEMI_ID, SEC_SEMI_DESIGN_ID, "رنگ‌های اصلی برند شما چیست؟", "COLOR_PICKER", False, None, "حداکثر ۳ رنگ اصلی انتخاب کنید", {}, None, None, 0),
            (Q_IDS["q6"], PLAN_LABEL_SEMI_ID, SEC_SEMI_DESIGN_ID, "سبک طراحی مورد نظر شما کدام است؟", "SINGLE_CHOICE", True, None, None, {}, None, None, 1),
            (Q_IDS["q7"], PLAN_LABEL_SEMI_ID, SEC_SEMI_DESIGN_ID, "المان‌های بصری خاصی مد نظر دارید؟", "MULTI_CHOICE", False, None, "می‌توانید چند مورد انتخاب کنید", {}, None, None, 2),
            (Q_IDS["q8"], PLAN_LABEL_SEMI_ID, SEC_SEMI_DESIGN_ID, "از ۱ تا ۵ چقدر طراحی رنگارنگ می‌خواهید؟", "SCALE", False, None, "۱ = بسیار ساده و تک‌رنگ، ۵ = رنگارنگ و پر جزئیات", {"min": 1, "max": 5}, None, None, 3),
            
            # Section: Content
            (Q_IDS["q9"], PLAN_LABEL_SEMI_ID, SEC_SEMI_CONTENT_ID, "متن اصلی لیبل چیست؟", "TEXTAREA", True, "مثلا: نام محصول، وزن، ترکیبات...", "تمام متنی که روی لیبل چاپ می‌شود را بنویسید", {"min_length": 5, "max_length": 500}, None, None, 0),
            (Q_IDS["q10"], PLAN_LABEL_SEMI_ID, SEC_SEMI_CONTENT_ID, "آیا بارکد یا QR Code نیاز دارید؟", "SINGLE_CHOICE", False, None, None, {}, None, None, 1),
            (Q_IDS["q11"], PLAN_LABEL_SEMI_ID, SEC_SEMI_CONTENT_ID, "اطلاعات تماس (شماره تلفن/وبسایت)", "TEXT", False, "مثلا: ۰۲۱-۱۲۳۴۵۶۷۸ یا www.example.com", None, {}, None, None, 2),
            (Q_IDS["q12"], PLAN_LABEL_SEMI_ID, SEC_SEMI_CONTENT_ID, "تاریخ تولید/انقضا لازم است؟", "SINGLE_CHOICE", False, None, None, {}, None, None, 3),
            
            # ---- LABEL PRIVATE Questions ----
            (Q_IDS["q13"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_BRAND_ID, "نام برند یا پروژه", "TEXT", True, "نام برند یا پروژه‌ای که لیبل برایش طراحی می‌شود", None, {}, None, None, 0),
            (Q_IDS["q14"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_BRAND_ID, "توضیح کامل محصول و کاربرد آن", "TEXTAREA", True, "هرچه جزئیات بیشتر بدهید طراحی بهتر خواهد بود", None, {"min_length": 20, "max_length": 2000}, None, None, 1),
            (Q_IDS["q15"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_BRAND_ID, "مخاطب هدف محصول شما کیست؟", "SINGLE_CHOICE", True, None, None, {}, None, None, 2),
            (Q_IDS["q16"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_BRAND_ID, "فایل لوگو (در صورت وجود)", "IMAGE_UPLOAD", False, None, None, {}, None, None, 3),
            
            (Q_IDS["q17"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_DESIGN_ID, "لینک یا تصویر نمونه طراحی‌هایی که دوست دارید", "IMAGE_UPLOAD", False, None, "نمونه‌های مشابه از اینترنت یا رقبا", {}, None, None, 0),
            (Q_IDS["q18"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_DESIGN_ID, "توضیحات تکمیلی درباره سلیقه طراحی", "TEXTAREA", False, "هر توضیح اضافه‌ای که به طراح کمک می‌کند", None, {}, None, None, 1),
            (Q_IDS["q19"], PLAN_LABEL_PRIVATE_ID, SEC_PRIV_DESIGN_ID, "بازه زمانی تحویل طرح اولیه", "SINGLE_CHOICE", False, None, None, {}, None, None, 2),
            
            # ---- BROCHURE SEMI-PRIVATE Questions ----
            (Q_IDS["q20"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_BRAND_ID, "نام شرکت/برند", "TEXT", True, "نام رسمی شرکت", None, {}, None, None, 0),
            (Q_IDS["q21"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_BRAND_ID, "حوزه فعالیت", "SINGLE_CHOICE", True, None, None, {}, None, None, 1),
            (Q_IDS["q22"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_BRAND_ID, "لوگوی شرکت", "IMAGE_UPLOAD", False, None, "فرمت PNG با پس‌زمینه شفاف", {}, None, None, 2),
            (Q_IDS["q23"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_BRAND_ID, "رنگ‌های سازمانی", "COLOR_PICKER", False, None, None, {}, None, None, 3),
            
            (Q_IDS["q24"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_CONTENT_ID, "عنوان اصلی بروشور", "TEXT", True, "مثلا: کاتالوگ محصولات ۱۴۰۵", None, {}, None, None, 0),
            (Q_IDS["q25"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_CONTENT_ID, "متن معرفی (درباره ما)", "TEXTAREA", True, None, "متن معرفی شرکت یا خدمات", {"min_length": 50, "max_length": 2000}, None, None, 1),
            (Q_IDS["q26"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_CONTENT_ID, "تصاویر محصولات/خدمات", "IMAGE_UPLOAD", False, None, "تصاویر باکیفیت محصولات", {}, None, None, 2),
            (Q_IDS["q27"], PLAN_BROCHURE_SEMI_ID, SEC_BRO_SEMI_CONTENT_ID, "اطلاعات تماس", "TEXTAREA", False, "آدرس، تلفن، وبسایت، شبکه‌های اجتماعی", None, {}, None, None, 3),
        ]
        
        for q in questions:
            # q = (id, plan_id, section_id, question_fa, input_type, is_required, placeholder, help, validation, dep_id, dep_vals, sort_order)
            dep_id = q[9]
            dep_vals = q[10]
            import json
            validation_json = json.dumps(q[8]) if q[8] else "{}"
            dep_vals_json = json.dumps(dep_vals) if dep_vals else "[]"
            await conn.execute(text("""
                INSERT INTO design_questions (id, plan_id, section_id, question_fa, input_type, is_required, placeholder_fa, help_text_fa, validation_rules, depends_on_question_id, depends_on_values, sort_order, is_active, created_at, updated_at)
                VALUES (:id, :plan_id, :section_id, :question, :input_type, :required, :placeholder, :help, CAST(:validation AS jsonb), :dep_id, CAST(:dep_vals AS jsonb), :sort, true, now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": q[0], "plan_id": q[1], "section_id": q[2], "question": q[3],
                "input_type": q[4], "required": q[5], "placeholder": q[6], "help": q[7],
                "validation": validation_json,
                "dep_id": dep_id,
                "dep_vals": dep_vals_json,
                "sort": q[11]
            })
        
        # ─── 8. Question Options ─────────────────────────────
        print("Creating question options...")
        
        q_options = [
            # Q2: Business field
            (QO_IDS["qo1"], Q_IDS["q2"], "food", "مواد غذایی", 0, 0),
            (QO_IDS["qo2"], Q_IDS["q2"], "cosmetics", "آرایشی بهداشتی", 0, 1),
            (QO_IDS["qo3"], Q_IDS["q2"], "clothing", "پوشاک", 0, 2),
            (QO_IDS["qo4"], Q_IDS["q2"], "industry", "صنعتی", 0, 3),
            (QO_IDS["qo5"], Q_IDS["q2"], "other", "سایر", 0, 4),
            
            # Q3: Has logo?
            (QO_IDS["qo6"], Q_IDS["q3"], "yes", "بله، لوگو دارم", 0, 0),
            (QO_IDS["qo7"], Q_IDS["q3"], "no", "خیر، لوگو هم طراحی شود", 200000, 1),
            (QO_IDS["qo8"], Q_IDS["q3"], "text_only", "فقط متن (بدون لوگو)", 0, 2),
            
            # Q6: Design style
            (QO_IDS["qo9"], Q_IDS["q6"], "modern", "مدرن و مینیمال", 0, 0),
            (QO_IDS["qo10"], Q_IDS["q6"], "classic", "کلاسیک و سنتی", 0, 1),
            (QO_IDS["qo11"], Q_IDS["q6"], "luxury", "لوکس و لاکچری", 100000, 2),
            (QO_IDS["qo12"], Q_IDS["q6"], "playful", "شاد و بازیگوش", 0, 3),
            (QO_IDS["qo13"], Q_IDS["q6"], "organic", "طبیعی و ارگانیک", 0, 4),
            
            # Q7: Visual elements (multi-choice)
            (QO_IDS["qo14"], Q_IDS["q7"], "pattern", "پترن و الگو", 0, 0),
            (QO_IDS["qo15"], Q_IDS["q7"], "illustration", "تصویرسازی", 50000, 1),
            (QO_IDS["qo16"], Q_IDS["q7"], "photo", "عکس محصول", 0, 2),
            (QO_IDS["qo17"], Q_IDS["q7"], "icon", "آیکون‌ها", 0, 3),
            (QO_IDS["qo18"], Q_IDS["q7"], "gold_foil", "طلاکوب", 150000, 4),
            
            # Q10: Barcode/QR
            (QO_IDS["qo19"], Q_IDS["q10"], "barcode", "بارکد", 10000, 0),
            (QO_IDS["qo20"], Q_IDS["q10"], "qrcode", "QR Code", 10000, 1),
            (QO_IDS["qo21"], Q_IDS["q10"], "both", "هر دو", 15000, 2),
            (QO_IDS["qo22"], Q_IDS["q10"], "none", "نیازی نیست", 0, 3),
            
            # Q12: Date on label
            (QO_IDS["qo23"], Q_IDS["q12"], "yes", "بله", 0, 0),
            (QO_IDS["qo24"], Q_IDS["q12"], "no", "خیر", 0, 1),
            
            # Q15: Target audience (Private)
            (QO_IDS["qo25"], Q_IDS["q15"], "young", "جوانان (۱۸-۳۰)", 0, 0),
            (QO_IDS["qo26"], Q_IDS["q15"], "adult", "بزرگسالان (۳۰-۵۰)", 0, 1),
            (QO_IDS["qo27"], Q_IDS["q15"], "luxury", "بازار لوکس", 0, 2),
            (QO_IDS["qo28"], Q_IDS["q15"], "kids", "کودکان", 0, 3),
            (QO_IDS["qo29"], Q_IDS["q15"], "general", "عمومی", 0, 4),
            
            # Q19: Timeline (Private)
            (QO_IDS["qo30"], Q_IDS["q19"], "urgent", "فوری (۳ روز)", 200000, 0),
            (QO_IDS["qo31"], Q_IDS["q19"], "normal", "عادی (۷ روز)", 0, 1),
            (QO_IDS["qo32"], Q_IDS["q19"], "relaxed", "بدون عجله (۱۴ روز)", 0, 2),
            
            # Q21: Brochure Business field
            (QO_IDS["qo33"], Q_IDS["q21"], "tech", "فناوری", 0, 0),
            (QO_IDS["qo34"], Q_IDS["q21"], "health", "بهداشت و سلامت", 0, 1),
            (QO_IDS["qo35"], Q_IDS["q21"], "education", "آموزشی", 0, 2),
            (QO_IDS["qo36"], Q_IDS["q21"], "real_estate", "املاک", 0, 3),
            (QO_IDS["qo37"], Q_IDS["q21"], "food", "رستوران و کافه", 0, 4),
        ]
        
        for qo in q_options:
            await conn.execute(text("""
                INSERT INTO question_options (id, question_id, value, label_fa, price_modifier, sort_order, is_active, created_at)
                VALUES (:id, :q_id, :val, :label, :price, :sort, true, now())
                ON CONFLICT (id) DO NOTHING
            """), {"id": qo[0], "q_id": qo[1], "val": qo[2], "label": qo[3], "price": qo[4], "sort": qo[5]})
        
        # ─── 9. Orders in Various States ─────────────────────
        print("Creating mock orders...")
        
        now = NOW
        
        orders = [
            # ──── SEMI_PRIVATE ORDERS (Label) ────
            
            # O1: Semi-Private — Just created, awaiting payment
            {
                "id": ORD_IDS["o1"], "user_id": CUSTOMER1_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "SEMI_PRIVATE", "status": "PENDING_PAYMENT",
                "quantity": 500,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt2"]), "value": None, "price_modifier": 2000},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt5"]), "value": None, "price_modifier": 5000},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt9"]), "value": None, "price_modifier": 1500},
                ],
                "base_price": 5000, "attributes_price": 8500, "design_price": 600000,
                "validation_price": 0, "fix_price": 0, "print_price": 50000,
                "total_price": 663500,
                "customer_notes": "لطفا رنگ‌های گرم استفاده شود",
                "validation_requested": False, "revision_count": 0, "max_revisions": 3,
                "created_at": now - timedelta(hours=2),
            },
            
            # O2: Semi-Private — Payment approved, now DESIGNING (designer assigned)
            {
                "id": ORD_IDS["o2"], "user_id": CUSTOMER1_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "SEMI_PRIVATE", "status": "DESIGNING",
                "quantity": 1000,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt3"]), "value": None, "price_modifier": 4000},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt6"]), "value": None, "price_modifier": 8000},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt10"]), "value": None, "price_modifier": 3000},
                ],
                "base_price": 5000, "attributes_price": 15000, "design_price": 600000,
                "validation_price": 50000, "fix_price": 0, "print_price": 80000,
                "total_price": 750000,
                "customer_notes": "لیبل برای عسل طبیعی است، لطفا حس طبیعی داشته باشد",
                "validation_requested": True, "revision_count": 0, "max_revisions": 3,
                "assigned_designer_id": USER_DESIGNER_ID,
                "created_at": now - timedelta(days=1),
            },
            
            # O3: Semi-Private — Designer uploaded first draft, customer needs to approve/reject (revision 1 of 3)
            {
                "id": ORD_IDS["o3"], "user_id": USER_CUSTOMER2_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "SEMI_PRIVATE", "status": "DESIGNING",
                "quantity": 2000,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt1"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt7"]), "value": None, "price_modifier": 3000},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt8"]), "value": None, "price_modifier": 1000},
                ],
                "base_price": 5000, "attributes_price": 4000, "design_price": 600000,
                "validation_price": 0, "fix_price": 0, "print_price": 120000,
                "total_price": 729000,
                "customer_notes": "لیبل قهوه تخصصی، حس حرفه‌ای و مدرن",
                "validation_requested": False, "revision_count": 1, "max_revisions": 3,
                "assigned_designer_id": USER_DESIGNER_ID,
                "design_file_url": "/uploads/mock_design_draft_v1.png",
                "created_at": now - timedelta(days=3),
            },
            
            # O4: Semi-Private — All 3 revisions used, design auto-approved, now READY_FOR_PRINT
            {
                "id": ORD_IDS["o4"], "user_id": CUSTOMER1_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "SEMI_PRIVATE", "status": "READY_FOR_PRINT",
                "quantity": 500,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt2"]), "value": None, "price_modifier": 2000},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt4"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt8"]), "value": None, "price_modifier": 1000},
                ],
                "base_price": 5000, "attributes_price": 3000, "design_price": 600000,
                "validation_price": 0, "fix_price": 0, "print_price": 40000,
                "total_price": 648000,
                "validation_requested": False, "revision_count": 3, "max_revisions": 3,
                "assigned_designer_id": USER_DESIGNER_ID,
                "design_file_url": "/uploads/mock_design_final_v3.png",
                "created_at": now - timedelta(days=7),
            },
            
            # ──── PRIVATE ORDERS (Label) ────
            
            # O5: Private — Just created, awaiting payment
            {
                "id": ORD_IDS["o5"], "user_id": USER_CUSTOMER2_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "PRIVATE", "status": "PENDING_PAYMENT",
                "quantity": 300,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt3"]), "value": None, "price_modifier": 4000},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt6"]), "value": None, "price_modifier": 8000},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt10"]), "value": None, "price_modifier": 3000},
                ],
                "base_price": 5000, "attributes_price": 15000, "design_price": 5000000,
                "validation_price": 50000, "fix_price": 0, "print_price": 30000,
                "total_price": 5100000,
                "customer_notes": "طراحی کاملا اختصاصی برای برند آرایشی لوکس",
                "validation_requested": True, "revision_count": 0, "max_revisions": None,
                "created_at": now - timedelta(hours=5),
            },
            
            # O6: Private — DESIGNING, designer assigned, chat ongoing (revision 2)
            {
                "id": ORD_IDS["o6"], "user_id": CUSTOMER1_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "PRIVATE", "status": "DESIGNING",
                "quantity": 1000,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt2"]), "value": None, "price_modifier": 2000},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt5"]), "value": None, "price_modifier": 5000},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt9"]), "value": None, "price_modifier": 1500},
                ],
                "base_price": 5000, "attributes_price": 8500, "design_price": 5000000,
                "validation_price": 50000, "fix_price": 0, "print_price": 80000,
                "total_price": 5143500,
                "customer_notes": "لیبل ویژه عطر، باید خیلی لوکس باشد",
                "validation_requested": True, "revision_count": 2, "max_revisions": None,
                "assigned_designer_id": USER_DESIGNER_ID,
                "design_file_url": "/uploads/mock_private_draft_v2.png",
                "created_at": now - timedelta(days=5),
            },
            
            # O7: Private — Design approved by customer, now printing
            {
                "id": ORD_IDS["o7"], "user_id": USER_CUSTOMER2_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "PRIVATE", "status": "PRINTING",
                "quantity": 5000,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt1"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt4"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt8"]), "value": None, "price_modifier": 1000},
                ],
                "base_price": 5000, "attributes_price": 1000, "design_price": 5000000,
                "validation_price": 0, "fix_price": 0, "print_price": 200000,
                "total_price": 5206000,
                "validation_requested": False, "revision_count": 4, "max_revisions": None,
                "assigned_designer_id": USER_DESIGNER_ID,
                "assigned_printshop_id": PRINTSHOP1_ID,
                "design_file_url": "/uploads/mock_private_final.png",
                "accepted_at": now - timedelta(days=1),
                "created_at": now - timedelta(days=10),
            },
            
            # ──── BROCHURE SEMI_PRIVATE ORDERS ────
            
            # O8: Brochure Semi-Private — DESIGNING
            {
                "id": ORD_IDS["o8"], "user_id": CUSTOMER1_ID, "category_id": CAT_BROCHURE_ID,
                "design_plan": "SEMI_PRIVATE", "status": "DESIGNING",
                "quantity": 200,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_BROCHURE_SIZE_ID), "option_id": str(OPT_IDS["opt11"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_BROCHURE_PAPER_ID), "option_id": str(OPT_IDS["opt15"]), "value": None, "price_modifier": 5000},
                    {"attribute_id": str(ATTR_BROCHURE_FOLD_ID), "option_id": str(OPT_IDS["opt18"]), "value": None, "price_modifier": 3000},
                ],
                "base_price": 15000, "attributes_price": 8000, "design_price": 800000,
                "validation_price": 0, "fix_price": 0, "print_price": 100000,
                "total_price": 923000,
                "customer_notes": "بروشور معرفی رستوران ایتالیایی",
                "validation_requested": False, "revision_count": 0, "max_revisions": 2,
                "assigned_designer_id": USER_DESIGNER_ID,
                "created_at": now - timedelta(days=2),
            },
            
            # O9: Brochure Private — DESIGNING with 1 revision
            {
                "id": ORD_IDS["o9"], "user_id": USER_CUSTOMER2_ID, "category_id": CAT_BROCHURE_ID,
                "design_plan": "PRIVATE", "status": "DESIGNING",
                "quantity": 500,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_BROCHURE_SIZE_ID), "option_id": str(OPT_IDS["opt13"]), "value": None, "price_modifier": 10000},
                    {"attribute_id": str(ATTR_BROCHURE_PAPER_ID), "option_id": str(OPT_IDS["opt16"]), "value": None, "price_modifier": 8000},
                    {"attribute_id": str(ATTR_BROCHURE_FOLD_ID), "option_id": str(OPT_IDS["opt20"]), "value": None, "price_modifier": 5000},
                ],
                "base_price": 15000, "attributes_price": 23000, "design_price": 6000000,
                "validation_price": 50000, "fix_price": 0, "print_price": 250000,
                "total_price": 6338000,
                "customer_notes": "کاتالوگ جامع محصولات شرکت دارویی",
                "validation_requested": True, "revision_count": 1, "max_revisions": None,
                "assigned_designer_id": USER_DESIGNER_ID,
                "design_file_url": "/uploads/mock_brochure_draft_v1.png",
                "created_at": now - timedelta(days=4),
            },
            
            # O10: Semi-Private — DELIVERED (complete flow, for testing review)
            {
                "id": ORD_IDS["o10"], "user_id": CUSTOMER1_ID, "category_id": CAT_LABEL_ID,
                "design_plan": "SEMI_PRIVATE", "status": "DELIVERED",
                "quantity": 500,
                "selected_attributes": [
                    {"attribute_id": str(ATTR_LABEL_SIZE_ID), "option_id": str(OPT_IDS["opt1"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_LABEL_MATERIAL_ID), "option_id": str(OPT_IDS["opt4"]), "value": None, "price_modifier": 0},
                    {"attribute_id": str(ATTR_LABEL_FINISH_ID), "option_id": str(OPT_IDS["opt8"]), "value": None, "price_modifier": 1000},
                ],
                "base_price": 5000, "attributes_price": 1000, "design_price": 600000,
                "validation_price": 0, "fix_price": 0, "print_price": 40000,
                "total_price": 646000,
                "validation_requested": False, "revision_count": 2, "max_revisions": 3,
                "assigned_designer_id": USER_DESIGNER_ID,
                "assigned_printshop_id": PRINTSHOP1_ID,
                "design_file_url": "/uploads/mock_semi_delivered_final.png",
                "accepted_at": now - timedelta(days=12),
                "printed_at": now - timedelta(days=10),
                "shipped_at": now - timedelta(days=8),
                "delivered_at": now - timedelta(days=6),
                "created_at": now - timedelta(days=14),
            },
        ]
        
        for o in orders:
            import json as json_mod
            sa_json = json_mod.dumps(o["selected_attributes"])
            await conn.execute(text("""
                INSERT INTO orders (
                    id, user_id, category_id, design_plan, status, quantity,
                    selected_attributes, base_price, attributes_price, design_price,
                    validation_price, fix_price, print_price, total_price,
                    customer_notes, validation_requested, revision_count, max_revisions,
                    assigned_designer_id, assigned_printshop_id, design_file_url,
                    accepted_at, printed_at, shipped_at, delivered_at,
                    created_at, updated_at
                ) VALUES (
                    :id, :user_id, :category_id, :design_plan, :status, :quantity,
                    CAST(:sa AS jsonb), :base_price, :attributes_price, :design_price,
                    :validation_price, :fix_price, :print_price, :total_price,
                    :customer_notes, :validation_requested, :revision_count, :max_revisions,
                    :designer_id, :printshop_id, :design_file_url,
                    :accepted_at, :printed_at, :shipped_at, :delivered_at,
                    :created_at, now()
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": o["id"], "user_id": o["user_id"], "category_id": o["category_id"],
                "design_plan": o["design_plan"], "status": o["status"], "quantity": o["quantity"],
                "sa": sa_json,
                "base_price": o["base_price"], "attributes_price": o["attributes_price"],
                "design_price": o["design_price"], "validation_price": o["validation_price"],
                "fix_price": o["fix_price"], "print_price": o["print_price"], "total_price": o["total_price"],
                "customer_notes": o.get("customer_notes"),
                "validation_requested": o["validation_requested"],
                "revision_count": o["revision_count"], "max_revisions": o.get("max_revisions"),
                "designer_id": o.get("assigned_designer_id"),
                "printshop_id": o.get("assigned_printshop_id"),
                "design_file_url": o.get("design_file_url"),
                "accepted_at": o.get("accepted_at"), "printed_at": o.get("printed_at"),
                "shipped_at": o.get("shipped_at"), "delivered_at": o.get("delivered_at"),
                "created_at": o.get("created_at", now),
            })
        
        # ─── 10. Payments for Orders that passed payment ─────
        print("Creating payments...")
        
        paid_orders = [
            (PAY_IDS["p1"], ORD_IDS["o2"], CUSTOMER1_ID, 750000, "SUCCESS"),
            (PAY_IDS["p2"], ORD_IDS["o3"], USER_CUSTOMER2_ID, 729000, "SUCCESS"),
            (PAY_IDS["p3"], ORD_IDS["o4"], CUSTOMER1_ID, 648000, "SUCCESS"),
            (PAY_IDS["p4"], ORD_IDS["o6"], CUSTOMER1_ID, 5143500, "SUCCESS"),
            (PAY_IDS["p5"], ORD_IDS["o7"], USER_CUSTOMER2_ID, 5206000, "SUCCESS"),
            (PAY_IDS["p6"], ORD_IDS["o8"], CUSTOMER1_ID, 923000, "SUCCESS"),
            (PAY_IDS["p7"], ORD_IDS["o9"], USER_CUSTOMER2_ID, 6338000, "SUCCESS"),
            (PAY_IDS["p8"], ORD_IDS["o10"], CUSTOMER1_ID, 646000, "SUCCESS"),
        ]
        
        for p in paid_orders:
            await conn.execute(text("""
                INSERT INTO payments (id, order_id, user_id, type, amount, status, paid_at, created_at, updated_at)
                VALUES (:id, :order_id, :user_id, 'FULL', :amount, :status, now(), now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {"id": p[0], "order_id": p[1], "user_id": p[2], "amount": p[3], "status": p[4]})
        
        # ─── 11. Questionnaire Answers for SEMI_PRIVATE orders ───
        print("Creating questionnaire answers...")
        
        # Answers for O2 (Semi-Private, Label, DESIGNING)
        o2_answers = [
            (ANS_IDS["a1"], ORD_IDS["o2"], Q_IDS["q1"], "عسل آناهیتا", None, None),
            (ANS_IDS["a2"], ORD_IDS["o2"], Q_IDS["q2"], "food", None, None),
            (ANS_IDS["a3"], ORD_IDS["o2"], Q_IDS["q3"], "yes", None, None),
            (ANS_IDS["a4"], ORD_IDS["o2"], Q_IDS["q5"], "#D4A017", None, None),
            (ANS_IDS["a5"], ORD_IDS["o2"], Q_IDS["q6"], "organic", None, None),
            (ANS_IDS["a6"], ORD_IDS["o2"], Q_IDS["q7"], None, ["illustration", "pattern"], None),
            (ANS_IDS["a7"], ORD_IDS["o2"], Q_IDS["q8"], "4", None, None),
            (ANS_IDS["a8"], ORD_IDS["o2"], Q_IDS["q9"], "عسل طبیعی کوهستان - ۵۰۰ گرم\nتولید: آذربایجان غربی\nترکیبات: عسل خالص طبیعی", None, None),
            (ANS_IDS["a9"], ORD_IDS["o2"], Q_IDS["q10"], "barcode", None, None),
            (ANS_IDS["a10"], ORD_IDS["o2"], Q_IDS["q11"], "www.anahita-honey.ir - ۰۴۴۱۲۳۴۵۶۷۸", None, None),
            (ANS_IDS["a11"], ORD_IDS["o2"], Q_IDS["q12"], "yes", None, None),
        ]
        
        # Answers for O3 (Semi-Private, Label, DESIGNING with 1 revision)
        o3_answers = [
            (ANS_IDS["a12"], ORD_IDS["o3"], Q_IDS["q1"], "قهوه تخصصی ریسا", None, None),
            (ANS_IDS["a13"], ORD_IDS["o3"], Q_IDS["q2"], "food", None, None),
            (ANS_IDS["a14"], ORD_IDS["o3"], Q_IDS["q3"], "yes", None, None),
            (ANS_IDS["a15"], ORD_IDS["o3"], Q_IDS["q5"], "#3C1518", None, None),
            (ANS_IDS["a16"], ORD_IDS["o3"], Q_IDS["q6"], "modern", None, None),
            (ANS_IDS["a17"], ORD_IDS["o3"], Q_IDS["q7"], None, ["icon", "pattern"], None),
            (ANS_IDS["a18"], ORD_IDS["o3"], Q_IDS["q8"], "3", None, None),
            (ANS_IDS["a19"], ORD_IDS["o3"], Q_IDS["q9"], "قهوه عربیکا اتیوپی - ۲۵۰ گرم\nدرجه برشته: مدیوم\nیادداشت طعمی: توت‌فرنگی، شکلات", None, None),
            (ANS_IDS["a20"], ORD_IDS["o3"], Q_IDS["q10"], "qrcode", None, None),
            (ANS_IDS["a21"], ORD_IDS["o3"], Q_IDS["q11"], "www.risa-coffee.com", None, None),
            (ANS_IDS["a22"], ORD_IDS["o3"], Q_IDS["q12"], "no", None, None),
        ]
        
        # Answers for O4 (Semi-Private, completed and delivered)
        o4_answers = [
            (ANS_IDS["a23"], ORD_IDS["o4"], Q_IDS["q1"], "صابون دستساز گلنار", None, None),
            (ANS_IDS["a24"], ORD_IDS["o4"], Q_IDS["q2"], "cosmetics", None, None),
            (ANS_IDS["a25"], ORD_IDS["o4"], Q_IDS["q3"], "no", None, None),
            (ANS_IDS["a26"], ORD_IDS["o4"], Q_IDS["q6"], "luxury", None, None),
            (ANS_IDS["a27"], ORD_IDS["o4"], Q_IDS["q9"], "صابون دستساز گلنار\nحاوی روغن زیتون و عصاره گل رز\nوزن خالص: ۱۰۰ گرم", None, None),
            (ANS_IDS["a28"], ORD_IDS["o4"], Q_IDS["q10"], "none", None, None),
        ]
        
        # Answers for O6 (Private, Label, DESIGNING)
        o6_answers = [
            (ANS_IDS["a29"], ORD_IDS["o6"], Q_IDS["q13"], "عطر مارال", None, None),
            (ANS_IDS["a30"], ORD_IDS["o6"], Q_IDS["q14"], "برند عطر مارال یک برند لوکس ایرانی است که عطرهای دست‌ساز با مواد اولیه فرانسوی تولید می‌کند. لیبل باید حس لوکس و اصالت را منتقل کند. رنگ‌های مشکی و طلایی ترجیح داده می‌شود. فونت‌های ظریف و شیک مورد نظر است.", None, None),
            (ANS_IDS["a31"], ORD_IDS["o6"], Q_IDS["q15"], "luxury", None, None),
            (ANS_IDS["a32"], ORD_IDS["o6"], Q_IDS["q18"], "از طلاکوب و امباس استفاده شود. لوگو به صورت مینیمال و تایپوگرافی باشد. نمونه مشابه: برندهای Jo Malone و Byredo", None, None),
            (ANS_IDS["a33"], ORD_IDS["o6"], Q_IDS["q19"], "normal", None, None),
        ]
        
        # Answers for O8 (Brochure Semi-Private)
        o8_answers = [
            (ANS_IDS["a34"], ORD_IDS["o8"], Q_IDS["q20"], "رستوران ایتالیایی لا وِنِزیا", None, None),
            (ANS_IDS["a35"], ORD_IDS["o8"], Q_IDS["q21"], "food", None, None),
            (ANS_IDS["a36"], ORD_IDS["o8"], Q_IDS["q23"], "#8B0000", None, None),
            (ANS_IDS["a37"], ORD_IDS["o8"], Q_IDS["q24"], "منوی ویژه تابستان ۱۴۰۵", None, None),
            (ANS_IDS["a38"], ORD_IDS["o8"], Q_IDS["q25"], "رستوران لا ونزیا با بیش از ۱۵ سال سابقه، ارائه‌دهنده اصیل‌ترین غذاهای ایتالیایی در تهران. سرآشپز ما مستقیم از ناپل آمده و هر غذا را با عشق و مواد اولیه تازه آماده می‌کند. از پاستاهای دست‌ساز تا پیتزای تنوری، همه چیز یک تجربه ایتالیایی واقعی است.", None, None),
            (ANS_IDS["a39"], ORD_IDS["o8"], Q_IDS["q27"], "خیابان ولیعصر، نبش کوچه هفتم\nتلفن: ۰۲۱-۸۸۸۸۹۹۹۹\nاینستاگرام: @lavenezia_tehran", None, None),
        ]
        
        # Answers for O10 (Semi-Private, DELIVERED)
        o10_answers = [
            (ANS_IDS["a40"], ORD_IDS["o10"], Q_IDS["q1"], "چای ارگانیک سبزینه", None, None),
            (ANS_IDS["a41"], ORD_IDS["o10"], Q_IDS["q2"], "food", None, None),
            (ANS_IDS["a42"], ORD_IDS["o10"], Q_IDS["q3"], "yes", None, None),
            (ANS_IDS["a43"], ORD_IDS["o10"], Q_IDS["q6"], "organic", None, None),
            (ANS_IDS["a44"], ORD_IDS["o10"], Q_IDS["q9"], "چای سبز ارگانیک سبزینه\nکشت: گیلان\nوزن: ۱۵۰ گرم", None, None),
            (ANS_IDS["a45"], ORD_IDS["o10"], Q_IDS["q10"], "both", None, None),
        ]
        
        all_answers = o2_answers + o3_answers + o4_answers + o6_answers + o8_answers + o10_answers
        
        for a in all_answers:
            await conn.execute(text("""
                INSERT INTO question_answers (id, order_id, question_id, answer_text, answer_values, answer_file_url, created_at, updated_at)
                VALUES (:id, :order_id, :q_id, :text, :vals, :file, now(), now())
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": a[0], "order_id": a[1], "q_id": a[2],
                "text": a[3], "vals": a[4], "file": a[5],
            })

        print("\n" + "=" * 60)
        print("  MOCK DATA SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nCategories: 2 new (لیبل و برچسب, بروشور و کاتالوگ)")
        print(f"Users: 1 designer (علی طراح), 1 customer (زهرا احمدی)")
        print(f"Design Plans: 8 (4 per category)")
        print(f"Questionnaire Sections: 7")
        print(f"Questions: 27 (various input types)")
        print(f"Question Options: 37")
        print(f"Orders: 10 in various states")
        print(f"Payments: 8")
        print(f"Answers: {len(all_answers)}")
        print()
        print("Key test orders:")
        print(f"  O1 {ORD_IDS['o1']} - Semi-Private, PENDING_PAYMENT")
        print(f"  O2 {ORD_IDS['o2']} - Semi-Private, DESIGNING (with answers)")
        print(f"  O3 {ORD_IDS['o3']} - Semi-Private, DESIGNING (1 revision, needs approval)")
        print(f"  O4 {ORD_IDS['o4']} - Semi-Private, READY_FOR_PRINT (3/3 revisions used)")
        print(f"  O5 {ORD_IDS['o5']} - Private, PENDING_PAYMENT")
        print(f"  O6 {ORD_IDS['o6']} - Private, DESIGNING (2 revisions, unlimited)")
        print(f"  O7 {ORD_IDS['o7']} - Private, PRINTING (approved)")
        print(f"  O8 {ORD_IDS['o8']} - Brochure Semi-Private, DESIGNING")
        print(f"  O9 {ORD_IDS['o9']} - Brochure Private, DESIGNING (1 revision)")
        print(f"  O10 {ORD_IDS['o10']} - Semi-Private, DELIVERED (complete)")
        print()
        print("Login:")
        print(f"  Customer 1 (existing): 09990000099")
        print(f"  Customer 2 (new):      09191234567")
        print(f"  Designer (new):        09351234567")
        print(f"  Admin (existing):      09121234567")


if __name__ == "__main__":
    asyncio.run(seed())

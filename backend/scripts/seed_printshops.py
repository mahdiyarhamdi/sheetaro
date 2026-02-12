"""Seed script: creates mock printshop users, profiles, orders, and reviews for testing.

Usage:
    cd backend && python -m scripts.seed_printshops

Requires:
    - Database up and running with migrations applied
    - ADMIN user already present
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select

# Bootstrap the app configuration so settings / engine are available
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.order import Order
from app.models.enums import UserRole, OrderStatus, DesignPlan
from app.models.printshop_profile import PrintShopProfile
from app.models.review import Review


# ---------- Data ----------

MOCK_PRINTSHOPS = [
    {
        "first_name": "چاپخانه",
        "last_name": "آریا",
        "phone_number": "09120000001",
        "password": "Test1234",
        "city": "تهران",
        "description": "چاپخانه آریا با بیش از ۱۰ سال سابقه در چاپ افست و دیجیتال آماده خدمت‌رسانی به شما است.",
        "capabilities": ["چاپ افست", "چاپ دیجیتال", "لمینت و سلفون", "برش و دایکات"],
        "service_areas": ["تهران", "کرج", "قم"],
        "max_daily_capacity": 50,
    },
    {
        "first_name": "چاپخانه",
        "last_name": "نوین",
        "phone_number": "09130000002",
        "password": "Test1234",
        "city": "اصفهان",
        "description": "چاپخانه نوین متخصص در چاپ دیجیتال و وایدفرمت با استفاده از به‌روزترین تجهیزات.",
        "capabilities": ["چاپ دیجیتال", "چاپ بزرگ (وایدفرمت)", "UV موضعی"],
        "service_areas": ["اصفهان", "شیراز"],
        "max_daily_capacity": 30,
    },
    {
        "first_name": "چاپخانه",
        "last_name": "سپهر",
        "phone_number": "09140000003",
        "password": "Test1234",
        "city": "مشهد",
        "description": "چاپخانه سپهر ارائه‌دهنده خدمات جامع چاپ شامل افست، دیجیتال، فلکسو و صحافی.",
        "capabilities": [
            "چاپ افست",
            "چاپ دیجیتال",
            "چاپ فلکسو",
            "چاپ سیلک",
            "صحافی و بسته‌بندی",
            "طلاکوب و نقره‌کوب",
            "برش و دایکات",
        ],
        "service_areas": ["مشهد", "نیشابور", "سبزوار"],
        "max_daily_capacity": 80,
    },
]


MOCK_REVIEWS = [
    {"rating": 5, "comment": "کیفیت عالی بود، خیلی راضی هستم. تحویل سریع و بسته‌بندی مناسب."},
    {"rating": 4, "comment": "کار خوبی بود ولی کمی تاخیر داشت."},
    {"rating": 5, "comment": "بهترین چاپخانه‌ای که تا حالا کار کردم."},
    {"rating": 3, "comment": "کیفیت متوسط بود، رنگ‌ها کمی فرق داشت."},
    {"rating": 4, "comment": None},
    {"rating": 5, "comment": "سرعت بالا و کیفیت خوب."},
]


async def seed():
    async with AsyncSessionLocal() as db:
        print("=== Seeding Print Shop Data ===\n")

        # --------------------------------------------------
        # 1) Find admin user and create their profile
        # --------------------------------------------------
        admin_result = await db.execute(
            select(User).where(User.role == UserRole.ADMIN).limit(1)
        )
        admin_user = admin_result.scalar_one_or_none()

        if admin_user:
            existing_profile = await db.execute(
                select(PrintShopProfile).where(PrintShopProfile.user_id == admin_user.id)
            )
            if not existing_profile.scalar_one_or_none():
                admin_profile = PrintShopProfile(
                    id=uuid.uuid4(),
                    user_id=admin_user.id,
                    description="حساب مدیر سیستم – دارای قابلیت پذیرش سفارش‌های چاپ.",
                    capabilities=["چاپ دیجیتال", "چاپ افست"],
                    service_areas=["سراسر ایران"],
                    max_daily_capacity=100,
                    is_featured=True,
                )
                db.add(admin_profile)
                print(f"  [+] Admin profile created for {admin_user.first_name} ({admin_user.id})")
            else:
                print(f"  [=] Admin profile already exists for {admin_user.first_name}")
        else:
            print("  [!] No admin user found, skipping admin profile")

        # --------------------------------------------------
        # 2) Create mock printshop users + profiles
        # --------------------------------------------------
        created_printshops: list[User] = []
        for ps_data in MOCK_PRINTSHOPS:
            existing = await db.execute(
                select(User).where(User.phone_number == ps_data["phone_number"])
            )
            user = existing.scalar_one_or_none()
            if user:
                print(f"  [=] {ps_data['first_name']} {ps_data['last_name']} already exists, reusing")
                created_printshops.append(user)
                continue

            full_name = f"{ps_data['first_name']} {ps_data['last_name']}".strip()
            new_user = User(
                id=uuid.uuid4(),
                first_name=ps_data["first_name"],
                last_name=ps_data["last_name"],
                full_name=full_name,
                phone_number=ps_data["phone_number"],
                password_hash=get_password_hash(ps_data["password"]),
                city=ps_data["city"],
                role=UserRole.PRINT_SHOP,
                is_active=True,
                phone_verified=True,
            )
            db.add(new_user)
            await db.flush()

            profile = PrintShopProfile(
                id=uuid.uuid4(),
                user_id=new_user.id,
                description=ps_data["description"],
                capabilities=ps_data["capabilities"],
                service_areas=ps_data["service_areas"],
                max_daily_capacity=ps_data["max_daily_capacity"],
            )
            db.add(profile)

            created_printshops.append(new_user)
            print(f"  [+] Created printshop: {full_name} ({new_user.id})")

        # --------------------------------------------------
        # 3) Create a dummy customer for reviews
        # --------------------------------------------------
        cust_phone = "09990000099"
        cust_result = await db.execute(select(User).where(User.phone_number == cust_phone))
        customer = cust_result.scalar_one_or_none()
        if not customer:
            customer = User(
                id=uuid.uuid4(),
                first_name="مشتری",
                last_name="تست",
                full_name="مشتری تست",
                phone_number=cust_phone,
                password_hash=get_password_hash("Test1234"),
                city="تهران",
                role=UserRole.CUSTOMER,
                is_active=True,
                phone_verified=True,
            )
            db.add(customer)
            await db.flush()
            print(f"  [+] Created test customer: {customer.full_name}")
        else:
            print(f"  [=] Test customer already exists")

        # --------------------------------------------------
        # 4) Create dummy DELIVERED orders + reviews for each printshop
        # --------------------------------------------------
        review_idx = 0
        now = datetime.now(timezone.utc)

        for ps_user in created_printshops:
            # Check if reviews already exist for this printshop
            existing_reviews = await db.execute(
                select(Review).where(Review.printshop_id == ps_user.id).limit(1)
            )
            if existing_reviews.scalar_one_or_none():
                print(f"  [=] Reviews already exist for {ps_user.full_name}, skipping")
                continue

            for i in range(2):
                if review_idx >= len(MOCK_REVIEWS):
                    review_idx = 0
                rv = MOCK_REVIEWS[review_idx]
                review_idx += 1

                # Create a dummy delivered order
                order_id = uuid.uuid4()
                order = Order(
                    id=order_id,
                    user_id=customer.id,
                    design_plan=DesignPlan.OWN_DESIGN,
                    status=OrderStatus.DELIVERED,
                    quantity=1000 * (i + 1),
                    total_price=60000 * (i + 1),
                    base_price=50000 * (i + 1),
                    assigned_printshop_id=ps_user.id,
                    accepted_at=now - timedelta(days=10 - i),
                    printed_at=now - timedelta(days=8 - i),
                    shipped_at=now - timedelta(days=5 - i),
                    delivered_at=now - timedelta(days=2 - i),
                    shipping_address="آدرس تست",
                    tracking_code=f"TRACK-{str(order_id)[:8].upper()}",
                )
                db.add(order)
                await db.flush()

                # Create review
                review = Review(
                    id=uuid.uuid4(),
                    order_id=order_id,
                    user_id=customer.id,
                    printshop_id=ps_user.id,
                    rating=rv["rating"],
                    comment=rv["comment"],
                    is_approved=True,
                )
                db.add(review)
                await db.flush()
                print(f"    [+] Order + Review (rating={rv['rating']}) for {ps_user.full_name}")

        await db.commit()
        print("\n=== Seed Complete ===")


if __name__ == "__main__":
    asyncio.run(seed())

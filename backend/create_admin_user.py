"""
Zorlu Force - Admin Kullanıcı Oluşturma Script'i
Kullanıcı: kbozurdilerim (Yahya Öner)
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import hashlib
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

async def create_admin_user():
    # MongoDB bağlantısı
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔧 Admin kullanıcı oluşturuluyor...")
    
    # Kullanıcı bilgileri
    username = "kbozurdilerim"
    password = "EnsYhy0316+"
    email = "yahyax1453@gmail.com"
    
    # Önce varsa sil
    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        await db.users.delete_one({"username": username})
        print(f"⚠️  Mevcut kullanıcı silindi: {username}")
    
    # Yeni kullanıcı oluştur
    user_data = {
        "id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "password_hash": get_password_hash(password),
        "role": "super_admin",
        "first_name": "Yahya",
        "last_name": "Öner",
        "phone": "+90 538 672 8079",
        "company_name": "NEXAVEN",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True
    }
    
    await db.users.insert_one(user_data)
    
    print(f"✅ Admin kullanıcı başarıyla oluşturuldu!")
    print(f"   👤 Kullanıcı Adı: {username}")
    print(f"   🔑 Şifre: {password}")
    print(f"   📧 Email: {email}")
    print(f"   🏢 Şirket: NEXAVEN")
    print(f"   📱 Telefon: +90 538 672 8079")
    print(f"   🎭 Rol: Super Admin")
    print(f"   🆔 ID: {user_data['id']}")
    
    # Boş AI config oluştur
    ai_config = {
        "id": str(uuid.uuid4()),
        "user_id": user_data['id'],
        "providers": [],
        "active_provider": None,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ai_configs.insert_one(ai_config)
    print(f"✅ AI yapılandırması oluşturuldu")
    
    client.close()
    print("\n🎉 İşlem tamamlandı! Artık giriş yapabilirsiniz.")

if __name__ == "__main__":
    asyncio.run(create_admin_user())

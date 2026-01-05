#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid

load_dotenv()

async def create_franchise_users():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Franchise demo users
    franchise_users = [
        # Super Admin
        {
            "id": str(uuid.uuid4()),
            "username": "superadmin",
            "email": "superadmin@zorluforce.com",
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "super_admin",
            "profile": {
                "first_name": "Super",
                "last_name": "Admin", 
                "phone": "+90 555 000 0000",
                "company": "ZorluForce HQ",
                "department": "System Administration"
            },
            "status": "active",
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "permissions": ["all"]
        },
        
        # Server Account
        {
            "id": str(uuid.uuid4()),
            "username": "server_istanbul",
            "email": "server.istanbul@zorluforce.com",
            "password_hash": hashlib.sha256("server123".encode()).hexdigest(),
            "role": "server",
            "server_config": {
                "server_name": "Istanbul Main Server",
                "location": "Istanbul, Turkey",
                "public_access": True,
                "auto_approve_enabled": True,
                "max_concurrent_clients": 100,
                "allowed_countries": ["all"]
            },
            "profile": {
                "first_name": "Istanbul",
                "last_name": "Server",
                "company": "ZorluForce"
            },
            "status": "active",
            "created_by": "superadmin",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "permissions": ["server_mode", "client_management", "tuning", "auto_approve"]
        },
        
        # ZorluForce Client
        {
            "id": str(uuid.uuid4()),
            "username": "umut_zorluforce",
            "email": "umut@zorluforce.com",
            "password_hash": hashlib.sha256("umut123".encode()).hexdigest(),
            "role": "client",
            "profile": {
                "first_name": "Umut",
                "last_name": "Tekniker",
                "phone": "+90 555 111 1111",
                "company": "ZorluForce",
                "department": "ECU Tuning",
                "display_name": "Umut | ZorluForce"
            },
            "client_config": {
                "tuning_level": "expert",
                "allowed_operations": ["stage1", "stage2", "stage3", "dtc_removal", "dpf_removal", "egr_removal"],
                "daily_file_limit": 100,
                "notification_preferences": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            "status": "active", 
            "created_by": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "permissions": ["tuning", "file_analysis", "customer_support"]
        },
        
        # Customer 1 - ABC Automotive
        {
            "id": str(uuid.uuid4()),
            "username": "abc_automotive",
            "email": "info@abcautomotive.com",
            "password_hash": hashlib.sha256("abc123".encode()).hexdigest(),
            "role": "customer",
            "profile": {
                "first_name": "Mehmet",
                "last_name": "Yılmaz",
                "phone": "+90 555 222 2222",
                "company_name": "ABC Automotive",
                "display_name": "ABC Automotive"
            },
            "customer_config": {
                "subscription_type": "premium",
                "monthly_file_limit": 50,
                "allowed_services": ["stage1", "stage2", "dtc_removal", "dpf_removal"],
                "auto_approve": True,
                "priority_support": True,
                "notification_preferences": {
                    "email": True,
                    "sms": True
                }
            },
            "billing": {
                "address": "Atatürk Cad. No:123 Kadıköy/İstanbul",
                "tax_id": "1234567890",
                "payment_method": "bank_transfer",
                "balance": 1500.0
            },
            "status": "active",
            "created_by": "admin", 
            "created_at": datetime.now(timezone.utc).isoformat(),
            "permissions": ["file_upload", "request_tuning", "view_status"]
        },
        
        # Customer 2 - XYZ Motors
        {
            "id": str(uuid.uuid4()),
            "username": "xyz_motors",
            "email": "contact@xyzmotors.com",
            "password_hash": hashlib.sha256("xyz123".encode()).hexdigest(),
            "role": "customer",
            "profile": {
                "first_name": "Ahmet",
                "last_name": "Kaya",
                "phone": "+90 555 333 3333", 
                "company_name": "XYZ Motors",
                "display_name": "XYZ Motors"
            },
            "customer_config": {
                "subscription_type": "basic",
                "monthly_file_limit": 10,
                "allowed_services": ["stage1", "dtc_removal"],
                "auto_approve": False,
                "priority_support": False,
                "notification_preferences": {
                    "email": True,
                    "sms": False
                }
            },
            "billing": {
                "address": "Bağdat Cad. No:456 Üsküdar/İstanbul",
                "tax_id": "0987654321",
                "payment_method": "credit_card",
                "balance": 250.0
            },
            "status": "active",
            "created_by": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "permissions": ["file_upload", "request_tuning", "view_status"]
        }
    ]
    
    for user_data in franchise_users:
        # Check if user already exists
        existing_user = await db.users.find_one({"username": user_data["username"]})
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            continue
            
        await db.users.insert_one(user_data)
        print(f"Created {user_data['role']} user: {user_data['username']} ({user_data.get('profile', {}).get('display_name', user_data['username'])})")
    
    client.close()
    print("\n🎉 Franchise demo users created successfully!")
    print("\nLogin credentials:")
    print("Super Admin: superadmin/admin123")
    print("Server: server_istanbul/server123") 
    print("ZorluForce Client: umut_zorluforce/umut123")
    print("Customer 1: abc_automotive/abc123 (ABC Automotive - Premium)")
    print("Customer 2: xyz_motors/xyz123 (XYZ Motors - Basic)")

if __name__ == "__main__":
    asyncio.run(create_franchise_users())
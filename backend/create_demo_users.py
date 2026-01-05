#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

async def create_demo_users():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Demo users
    demo_users = [
        {
            "username": "admin",
            "email": "admin@zorluforce.com",
            "password": "admin",
            "role": "admin"
        },
        {
            "username": "tech1",
            "email": "tech1@zorluforce.com", 
            "password": "password123",
            "role": "technician"
        },
        {
            "username": "engineer1",
            "email": "engineer1@zorluforce.com",
            "password": "password123",
            "role": "engineer"
        }
    ]
    
    for user_data in demo_users:
        # Check if user already exists
        existing_user = await db.users.find_one({"username": user_data["username"]})
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            continue
            
        # Hash password (simple hash for demo)
        hashed_password = hashlib.sha256(user_data["password"].encode()).hexdigest()
        
        # Create user document
        user_doc = {
            "username": user_data["username"],
            "email": user_data["email"],
            "password_hash": hashed_password,
            "role": user_data["role"],
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        await db.users.insert_one(user_doc)
        print(f"Created user: {user_data['username']} (role: {user_data['role']})")
    
    client.close()
    print("Demo users created successfully!")

if __name__ == "__main__":
    asyncio.run(create_demo_users())
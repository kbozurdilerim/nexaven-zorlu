import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid
import asyncio

class UserManagementService:
    """
    Zorlu Force Franchise User Management System
    Multi-tenant yapı: Admin, Server, Client, Customer rolleri
    """
    
    def __init__(self):
        self.user_roles = {
            "super_admin": {
                "name": "Super Admin", 
                "permissions": ["all"],
                "description": "Sistem yöneticisi - Tüm yetkiler"
            },
            "admin": {
                "name": "Admin",
                "permissions": ["user_management", "tuning", "server_management", "reports"],
                "description": "Franchise admin - Kullanıcı yönetimi + Tuning"
            },
            "server": {
                "name": "Server",
                "permissions": ["server_mode", "client_management", "tuning", "auto_approve"],
                "description": "Sunucu hesabı - Server modu + Otomatik onay"
            },
            "client": {
                "name": "ZorluForce Client",
                "permissions": ["tuning", "file_analysis", "customer_support"],
                "description": "ZorluForce çalışanı - ECU tuning operations"
            },
            "customer": {
                "name": "Customer",
                "permissions": ["file_upload", "request_tuning", "view_status"],
                "description": "Müşteri hesabı - Dosya gönderme + Talep"
            }
        }
        
        self.franchise_settings = {
            "auto_approve_requests": True,
            "ai_auto_tuning": True,
            "notification_enabled": True,
            "mobile_notifications": True,
            "remember_me_enabled": True,
            "global_server_access": True
        }

    async def create_user_by_admin(self, admin_user: Dict, user_data: Dict) -> Dict:
        """Admin tarafından yeni kullanıcı oluşturma"""
        
        # Admin yetkisi kontrolü
        if admin_user.get("role") not in ["super_admin", "admin"]:
            return {
                "status": "error",
                "message": "Bu işlem için yeterli yetkiniz yok"
            }
        
        try:
            # Kullanıcı tipine göre işlem
            role = user_data.get("role")
            
            if role == "server":
                return await self._create_server_account(admin_user, user_data)
            elif role == "client":
                return await self._create_client_account(admin_user, user_data)
            elif role == "customer":
                return await self._create_customer_account(admin_user, user_data)
            elif role == "admin":
                return await self._create_admin_account(admin_user, user_data)
            else:
                return {
                    "status": "error",
                    "message": "Geçersiz kullanıcı tipi"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Kullanıcı oluşturma hatası: {str(e)}"
            }

    async def _create_server_account(self, admin_user: Dict, user_data: Dict) -> Dict:
        """Sunucu hesabı oluşturma"""
        
        server_user = {
            "id": str(uuid.uuid4()),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "password_hash": hashlib.sha256(user_data.get("password").encode()).hexdigest(),
            "role": "server",
            "server_config": {
                "server_name": user_data.get("server_name", "ZorluForce Server"),
                "location": user_data.get("location", "Unknown"),
                "public_access": True,
                "auto_approve_enabled": True,
                "max_concurrent_clients": user_data.get("max_clients", 100),
                "allowed_countries": user_data.get("allowed_countries", ["all"])
            },
            "status": "active",
            "created_by": admin_user.get("username"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "permissions": self.user_roles["server"]["permissions"]
        }
        
        return {
            "status": "success",
            "message": "Sunucu hesabı başarıyla oluşturuldu",
            "user": server_user
        }

    async def _create_client_account(self, admin_user: Dict, user_data: Dict) -> Dict:
        """ZorluForce Client hesabı oluşturma"""
        
        # Otomatik username: isim + ZorluForce
        first_name = user_data.get("first_name", "")
        username = f"{first_name.lower()}_zorluforce" if first_name else user_data.get("username")
        
        client_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": user_data.get("email"),
            "password_hash": hashlib.sha256(user_data.get("password").encode()).hexdigest(),
            "role": "client",
            "profile": {
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "phone": user_data.get("phone"),
                "company": "ZorluForce",
                "department": user_data.get("department", "Tuning"),
                "display_name": f"{first_name} | ZorluForce" if first_name else "ZorluForce Client"
            },
            "client_config": {
                "tuning_level": user_data.get("tuning_level", "standard"), # standard, advanced, expert
                "allowed_operations": user_data.get("allowed_operations", ["stage1", "stage2", "dtc_removal"]),
                "daily_file_limit": user_data.get("daily_limit", 50),
                "notification_preferences": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            "status": "active",
            "created_by": admin_user.get("username"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "permissions": self.user_roles["client"]["permissions"]
        }
        
        return {
            "status": "success",
            "message": f"ZorluForce client hesabı oluşturuldu: {client_user['profile']['display_name']}",
            "user": client_user
        }

    async def _create_customer_account(self, admin_user: Dict, user_data: Dict) -> Dict:
        """Müşteri hesabı oluşturma"""
        
        company_name = user_data.get("company_name", "")
        first_name = user_data.get("first_name", "")
        
        customer_user = {
            "id": str(uuid.uuid4()),
            "username": user_data.get("username") or f"{first_name.lower()}_{company_name.lower().replace(' ', '_')}",
            "email": user_data.get("email"),
            "password_hash": hashlib.sha256(user_data.get("password").encode()).hexdigest(),
            "role": "customer",
            "profile": {
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "phone": user_data.get("phone"),
                "company_name": company_name,
                "display_name": company_name if company_name else f"{first_name} {user_data.get('last_name', '')}"
            },
            "customer_config": {
                "subscription_type": user_data.get("subscription", "basic"), # basic, premium, enterprise
                "monthly_file_limit": user_data.get("monthly_limit", 10),
                "allowed_services": user_data.get("services", ["stage1", "dtc_removal"]),
                "auto_approve": user_data.get("auto_approve", False),
                "priority_support": user_data.get("priority", False),
                "notification_preferences": {
                    "email": True,
                    "sms": user_data.get("sms_notifications", False)
                }
            },
            "billing": {
                "address": user_data.get("address", ""),
                "tax_id": user_data.get("tax_id", ""),
                "payment_method": user_data.get("payment_method", ""),
                "balance": 0.0
            },
            "status": "active",
            "created_by": admin_user.get("username"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "permissions": self.user_roles["customer"]["permissions"]
        }
        
        return {
            "status": "success",
            "message": f"Müşteri hesabı oluşturuldu: {customer_user['profile']['display_name']}",
            "user": customer_user
        }

    async def _create_admin_account(self, admin_user: Dict, user_data: Dict) -> Dict:
        """Yeni admin hesabı oluşturma (sadece super_admin yapabilir)"""
        
        if admin_user.get("role") != "super_admin":
            return {
                "status": "error",
                "message": "Admin hesabı oluşturmak için Super Admin yetkisi gerekli"
            }
        
        new_admin = {
            "id": str(uuid.uuid4()),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "password_hash": hashlib.sha256(user_data.get("password").encode()).hexdigest(),
            "role": "admin",
            "profile": {
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "phone": user_data.get("phone"),
                "company": user_data.get("company", "ZorluForce"),
                "department": "Administration"
            },
            "admin_config": {
                "franchise_id": user_data.get("franchise_id"),
                "territory": user_data.get("territory", "Global"),
                "max_users": user_data.get("max_users", 1000),
                "features_enabled": user_data.get("features", ["user_management", "tuning", "reports"])
            },
            "status": "active",
            "created_by": admin_user.get("username"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "permissions": self.user_roles["admin"]["permissions"]
        }
        
        return {
            "status": "success",
            "message": "Admin hesabı başarıyla oluşturuldu",
            "user": new_admin
        }

    async def setup_server_mode(self, server_user: Dict, network_config: Dict) -> Dict:
        """Sunucu modunu aktive etme"""
        
        if server_user.get("role") != "server":
            return {
                "status": "error",
                "message": "Bu özellik sadece server hesapları için kullanılabilir"
            }
        
        server_setup = {
            "server_id": server_user.get("id"),
            "public_ip": network_config.get("public_ip"),
            "port": network_config.get("port", 8001),
            "domain": network_config.get("domain"),
            "ssl_enabled": network_config.get("ssl", True),
            "global_access": True,
            "status": "online",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "connected_clients": 0,
            "max_clients": server_user.get("server_config", {}).get("max_concurrent_clients", 100)
        }
        
        return {
            "status": "success",
            "message": "Sunucu modu aktif edildi - Dünyadan erişilebilir",
            "server_info": server_setup
        }

    async def create_customer_request(self, customer_user: Dict, request_data: Dict) -> Dict:
        """Müşteri tuning talebi oluşturma"""
        
        if customer_user.get("role") != "customer":
            return {
                "status": "error",
                "message": "Bu özellik sadece müşteri hesapları için kullanılabilir"
            }
        
        request = {
            "id": str(uuid.uuid4()),
            "customer_id": customer_user.get("id"),
            "customer_name": customer_user.get("profile", {}).get("display_name"),
            "file_id": request_data.get("file_id"),
            "services_requested": request_data.get("services", []), # ["stage1", "egr_removal", "dtc_removal"]
            "message": request_data.get("message", ""),
            "priority": request_data.get("priority", "normal"), # normal, high, urgent
            "auto_approve": customer_user.get("customer_config", {}).get("auto_approve", False),
            "status": "pending", # pending, approved, processing, completed, rejected
            "created_at": datetime.now(timezone.utc).isoformat(),
            "estimated_completion": None,
            "assigned_to": None
        }
        
        # Otomatik onay kontrolü
        if request["auto_approve"] and self.franchise_settings["auto_approve_requests"]:
            request["status"] = "approved"
            request["auto_approved"] = True
            request["approved_at"] = datetime.now(timezone.utc).isoformat()
            
            # Admin'lere bildirim gönder
            await self._send_notification_to_admins({
                "type": "auto_approved_request",
                "customer": customer_user.get("profile", {}).get("display_name"),
                "services": request_data.get("services", []),
                "request_id": request["id"]
            })
        
        return {
            "status": "success",
            "message": "Tuning talebi oluşturuldu" + (" ve otomatik onaylandı" if request.get("auto_approved") else ""),
            "request": request
        }

    async def _send_notification_to_admins(self, notification_data: Dict):
        """Admin'lere bildirim gönderme"""
        
        notification = {
            "id": str(uuid.uuid4()),
            "type": notification_data.get("type"),
            "title": self._generate_notification_title(notification_data),
            "message": self._generate_notification_message(notification_data),
            "data": notification_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "platforms": ["web", "mobile", "email"] if self.franchise_settings["mobile_notifications"] else ["web", "email"]
        }
        
        # Bu notification gerçek push notification service'e gönderilecek
        # Firebase, APNs, email service integration yapılacak
        
        return notification

    def _generate_notification_title(self, data: Dict) -> str:
        """Bildirim başlığı oluşturma"""
        
        if data.get("type") == "auto_approved_request":
            return f"🚗 Yeni Otomatik Onaylanmış Talep - {data.get('customer')}"
        elif data.get("type") == "new_customer_request":
            return f"📋 Yeni Müşteri Talebi - {data.get('customer')}"
        elif data.get("type") == "tuning_completed":
            return f"✅ Tuning Tamamlandı - {data.get('customer')}"
        else:
            return "ZorluForce Bildirimi"

    def _generate_notification_message(self, data: Dict) -> str:
        """Bildirim mesajı oluşturma"""
        
        if data.get("type") == "auto_approved_request":
            services = ", ".join(data.get("services", []))
            return f"{data.get('customer')} için {services} işlemleri otomatik onaylandı ve işleme başlandı."
        elif data.get("type") == "new_customer_request":
            return f"Yeni müşteri talebi incelemenizi bekliyor."
        else:
            return "Yeni bir aktivite gerçekleşti."

    def get_user_role_info(self, role: str) -> Dict:
        """Rol bilgilerini getirme"""
        return self.user_roles.get(role, {})

    def check_permission(self, user_role: str, permission: str) -> bool:
        """Yetki kontrolü"""
        role_info = self.user_roles.get(user_role, {})
        permissions = role_info.get("permissions", [])
        return "all" in permissions or permission in permissions

# Global user management service instance
user_management_service = UserManagementService()
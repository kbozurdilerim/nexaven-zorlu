import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationService:
    """
    Zorlu Force Notification Service
    Push notifications, Email, SMS support
    Mobile (iOS/Android) compatible
    """
    
    def __init__(self):
        self.notification_channels = {
            "email": True,
            "push": True,  # Web Push + Mobile Push
            "sms": False,  # SMS gateway integration
            "in_app": True  # In-app notifications
        }
        
        self.mobile_config = {
            "firebase_enabled": False,  # Firebase Cloud Messaging
            "apns_enabled": False,      # Apple Push Notification Service
            "web_push_enabled": True    # Web Push API
        }
        
        self.push_subscriptions = []  # Store push subscriptions (in production: use database)
        self.notification_queue = []  # Queue for offline notifications
        
        self.email_templates = {
            "new_request": {
                "subject": "🚗 Yeni ECU Tuning Talebi - {customer_name}",
                "template": """
                <h2>Yeni Tuning Talebi</h2>
                <p><strong>Müşteri:</strong> {customer_name}</p>
                <p><strong>İstenen Hizmetler:</strong> {services}</p>
                <p><strong>Öncelik:</strong> {priority}</p>
                <p><strong>Mesaj:</strong> {message}</p>
                <p><strong>Tarih:</strong> {created_at}</p>
                
                <p>Talebi incelemek için <a href="{dashboard_url}">buraya tıklayın</a></p>
                """
            },
            "request_approved": {
                "subject": "✅ Talebiniz Onaylandı - {request_id}",
                "template": """
                <h2>Talebiniz Onaylandı!</h2>
                <p>Sayın {customer_name},</p>
                <p>ECU tuning talebiniz onaylanmış ve işleme alınmıştır.</p>
                <p><strong>Talep ID:</strong> {request_id}</p>
                <p><strong>İstenen Hizmetler:</strong> {services}</p>
                <p><strong>Tahmini Tamamlanma:</strong> {estimated_completion}</p>
                
                <p>İlerlemeyi takip etmek için <a href="{portal_url}">müşteri portalınıza</a> giriş yapabilirsiniz.</p>
                """
            },
            "tuning_completed": {
                "subject": "🎉 ECU Tuning Tamamlandı - {request_id}",
                "template": """
                <h2>ECU Tuning Tamamlandı!</h2>
                <p>Sayın {customer_name},</p>
                <p>ECU tuning işleminiz başarıyla tamamlanmıştır.</p>
                <p><strong>Talep ID:</strong> {request_id}</p>
                <p><strong>Yapılan İşlemler:</strong> {completed_services}</p>
                <p><strong>Tamamlanma Tarihi:</strong> {completed_at}</p>
                
                <p>Tuned dosyanızı indirmek için <a href="{download_url}">buraya tıklayın</a></p>
                """
            }
        }

    async def send_notification_to_admins(self, notification_data: Dict) -> Dict:
        """Admin'lere bildirim gönderme"""
        
        try:
            notification_id = str(uuid.uuid4())
            
            # Notification kaydı oluştur
            notification = {
                "id": notification_id,
                "type": notification_data.get("type"),
                "title": self._generate_title(notification_data),
                "message": self._generate_message(notification_data),
                "data": notification_data,
                "recipients": await self._get_admin_recipients(),
                "channels": ["email", "push", "in_app"],
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "sent_at": None,
                "delivery_status": {}
            }
            
            # Email notification gönder
            if self.notification_channels["email"]:
                email_result = await self._send_email_notification(notification)
                notification["delivery_status"]["email"] = email_result
            
            # Push notification gönder
            if self.notification_channels["push"]:
                push_result = await self._send_push_notification(notification)
                notification["delivery_status"]["push"] = push_result
            
            # In-app notification kaydet
            if self.notification_channels["in_app"]:
                inapp_result = await self._save_inapp_notification(notification)
                notification["delivery_status"]["in_app"] = inapp_result
            
            notification["status"] = "sent"
            notification["sent_at"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "status": "success",
                "notification_id": notification_id,
                "notification": notification
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Bildirim gönderme hatası: {str(e)}"
            }

    async def send_customer_notification(self, customer_data: Dict, notification_data: Dict) -> Dict:
        """Müşteriye bildirim gönderme"""
        
        try:
            notification_id = str(uuid.uuid4())
            
            notification = {
                "id": notification_id,
                "type": notification_data.get("type"),
                "title": self._generate_title(notification_data),
                "message": self._generate_message(notification_data),
                "recipient": customer_data,
                "data": notification_data,
                "channels": self._get_customer_channels(customer_data),
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Müşteri tercihlerine göre bildirim gönder
            channels = customer_data.get("customer_config", {}).get("notification_preferences", {})
            
            if channels.get("email", True):
                email_result = await self._send_customer_email(customer_data, notification_data)
                notification["delivery_status"] = {"email": email_result}
            
            if channels.get("sms", False):
                sms_result = await self._send_sms_notification(customer_data, notification_data)
                notification["delivery_status"]["sms"] = sms_result
            
            return {
                "status": "success",
                "notification_id": notification_id,
                "notification": notification
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Müşteri bildirimi hatası: {str(e)}"
            }

    async def register_mobile_device(self, user_id: str, device_data: Dict) -> Dict:
        """Mobile cihaz kaydı (iOS/Android)"""
        
        try:
            device_registration = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "device_token": device_data.get("device_token"),
                "platform": device_data.get("platform"), # ios, android, web
                "app_version": device_data.get("app_version"),
                "device_info": {
                    "model": device_data.get("device_model"),
                    "os_version": device_data.get("os_version"),
                    "app_build": device_data.get("app_build")
                },
                "preferences": {
                    "notifications_enabled": True,
                    "sound_enabled": True,
                    "vibration_enabled": True,
                    "badge_enabled": True
                },
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "last_active": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }
            
            return {
                "status": "success",
                "device_id": device_registration["id"],
                "message": "Cihaz başarıyla kaydedildi"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Device registration error: {str(e)}"
            }
    
    async def register_push_device(self, device_data: Dict) -> Dict:
        """
        Mobile cihaz push notification kaydı
        iOS ve Android desteği
        """
        
        device_id = device_data.get("device_id")
        device_token = device_data.get("device_token")
        platform = device_data.get("platform")  # 'ios' or 'android'
        user_id = device_data.get("user_id")
        
        if not all([device_id, device_token, platform, user_id]):
            return {
                "status": "error",
                "message": "Missing required fields"
            }
        
        subscription = {
            "id": str(uuid.uuid4()),
            "device_id": device_id,
            "device_token": device_token,
            "platform": platform,
            "user_id": user_id,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "active": True
        }
        
        # Check if device already registered
        existing = next((s for s in self.push_subscriptions if s["device_id"] == device_id), None)
        
        if existing:
            # Update token
            existing["device_token"] = device_token
            existing["updated_at"] = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "message": "Push subscription updated",
                "subscription_id": existing["id"]
            }
        else:
            # Add new subscription
            self.push_subscriptions.append(subscription)
            return {
                "status": "success",
                "message": "Push subscription registered",
                "subscription_id": subscription["id"]
            }
    
    async def unregister_push_device(self, device_id: str) -> Dict:
        """Mobile cihaz push notification kaydını kaldır"""
        
        subscription = next((s for s in self.push_subscriptions if s["device_id"] == device_id), None)
        
        if subscription:
            subscription["active"] = False
            subscription["unregistered_at"] = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "message": "Push subscription removed"
            }
        
        return {
            "status": "error",
            "message": "Device not found"
        }
    
    async def send_push_notification(
        self, 
        user_id: str, 
        title: str, 
        body: str, 
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Push notification gönder
        Firebase (Android) ve APNS (iOS) desteği
        """
        
        # Get user's devices
        user_devices = [s for s in self.push_subscriptions if s["user_id"] == user_id and s["active"]]
        
        if not user_devices:
            return {
                "status": "warning",
                "message": "No active devices found for user",
                "queued": True
            }
        
        sent_count = 0
        failed_count = 0
        results = []
        
        for device in user_devices:
            try:
                notification_payload = {
                    "notification_id": str(uuid.uuid4()),
                    "title": title,
                    "body": body,
                    "data": data or {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "priority": "high",
                    "sound": "default"
                }
                
                if device["platform"] == "android":
                    # Firebase Cloud Messaging (simulated)
                    if self.mobile_config["firebase_enabled"]:
                        # In production: Use Firebase Admin SDK
                        # message = messaging.Message(
                        #     notification=messaging.Notification(title=title, body=body),
                        #     token=device["device_token"],
                        #     data=data
                        # )
                        # response = messaging.send(message)
                        pass
                    
                    results.append({
                        "device_id": device["device_id"],
                        "platform": "android",
                        "status": "sent" if self.mobile_config["firebase_enabled"] else "simulated"
                    })
                    sent_count += 1
                    
                elif device["platform"] == "ios":
                    # Apple Push Notification Service (simulated)
                    if self.mobile_config["apns_enabled"]:
                        # In production: Use APNs HTTP/2 API
                        # from aioapns import APNs, NotificationRequest
                        # client = APNs(...)
                        # await client.send_notification(NotificationRequest(...))
                        pass
                    
                    results.append({
                        "device_id": device["device_id"],
                        "platform": "ios",
                        "status": "sent" if self.mobile_config["apns_enabled"] else "simulated"
                    })
                    sent_count += 1
                
            except Exception as e:
                failed_count += 1
                results.append({
                    "device_id": device["device_id"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "sent": sent_count,
            "failed": failed_count,
            "total_devices": len(user_devices),
            "results": results,
            "firebase_enabled": self.mobile_config["firebase_enabled"],
            "apns_enabled": self.mobile_config["apns_enabled"]
        }
    
    async def send_customer_request_notification(
        self, 
        request_data: Dict, 
        admin_users: List[Dict]
    ) -> Dict:
        """
        Müşteri talebinde bulunduğunda admin'lere bildirim gönder
        Email + Push notification kombinasyonu
        """
        
        customer_name = request_data.get("customer_name", "Bilinmeyen")
        services = request_data.get("services", "Belirtilmedi")
        message = request_data.get("message", "")
        
        results = {
            "email_sent": [],
            "push_sent": [],
            "errors": []
        }
        
        for admin in admin_users:
            # Email notification
            try:
                email_result = await self.send_email_notification(
                    to_email=admin.get("email"),
                    template_name="new_request",
                    template_data={
                        "customer_name": customer_name,
                        "services": services,
                        "priority": request_data.get("priority", "normal"),
                        "message": message,
                        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                        "dashboard_url": "http://localhost:3000/admin/requests"
                    }
                )
                results["email_sent"].append(admin.get("username"))
            except Exception as e:
                results["errors"].append(f"Email to {admin.get('username')}: {str(e)}")
            
            # Push notification
            try:
                push_result = await self.send_push_notification(
                    user_id=admin.get("id"),
                    title="🚗 Yeni ECU Tuning Talebi",
                    body=f"{customer_name} - {services}",
                    data={
                        "type": "customer_request",
                        "request_id": request_data.get("id"),
                        "customer_name": customer_name
                    }
                )
                if push_result["sent"] > 0:
                    results["push_sent"].append(admin.get("username"))
            except Exception as e:
                results["errors"].append(f"Push to {admin.get('username')}: {str(e)}")
        
        return {
            "status": "success",
            "notifications_sent": {
                "email": len(results["email_sent"]),
                "push": len(results["push_sent"])
            },
            "details": results
        }

    async def _get_admin_recipients(self) -> List[Dict]:
        """Admin kullanıcılarını getir"""
        # MongoDB'den admin kullanıcıları çek (gerçek implementasyonda)
        return [
            {
                "user_id": "admin1",
                "email": "admin@zorluforce.com",
                "role": "admin",
                "notification_preferences": {
                    "email": True,
                    "push": True
                }
            }
        ]

    async def _send_email_notification(self, notification: Dict) -> Dict:
        """Email bildirim gönder"""
        try:
            # SMTP konfigürasyonu (gerçek implementasyonda environment'dan alınacak)
            # smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            # smtp_port = int(os.environ.get('SMTP_PORT', 587))
            # smtp_username = os.environ.get('SMTP_USERNAME')
            # smtp_password = os.environ.get('SMTP_PASSWORD')
            
            # Şimdilik mock success response
            return {
                "status": "success",
                "sent_count": len(notification.get("recipients", [])),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def _send_push_notification(self, notification: Dict) -> Dict:
        """Push notification gönder"""
        try:
            # Firebase/APNS integration (gerçek implementasyonda)
            # Bu kısımda Firebase Cloud Messaging veya Apple Push Notification Service kullanılacak
            
            push_payload = {
                "title": notification["title"],
                "body": notification["message"],
                "icon": "/icons/zorlu-force-icon.png",
                "badge": 1,
                "sound": "default",
                "data": notification["data"]
            }
            
            return {
                "status": "success", 
                "push_payload": push_payload,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def _save_inapp_notification(self, notification: Dict) -> Dict:
        """In-app notification kaydet"""
        try:
            # Database'e in-app notification kaydet
            return {
                "status": "success",
                "saved": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }

    async def _send_customer_email(self, customer_data: Dict, notification_data: Dict) -> Dict:
        """Müşteriye email gönder"""
        try:
            email_type = notification_data.get("type", "general")
            template = self.email_templates.get(email_type, {})
            
            if template:
                subject = template["subject"].format(**notification_data)
                body = template["template"].format(**notification_data)
                
                # Email gönder (gerçek implementasyonda SMTP)
                return {
                    "status": "success",
                    "email": customer_data.get("email"),
                    "subject": subject,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            return {"status": "error", "message": "Template bulunamadı"}
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def _send_sms_notification(self, customer_data: Dict, notification_data: Dict) -> Dict:
        """SMS bildirim gönder"""
        try:
            # SMS gateway integration (Twilio, Nexmo, vb.)
            phone = customer_data.get("profile", {}).get("phone")
            
            if not phone:
                return {"status": "error", "message": "Telefon numarası bulunamadı"}
            
            sms_message = f"ZorluForce: {notification_data.get('title', '')}"
            
            # SMS gönder (gerçek implementasyonda SMS API)
            return {
                "status": "success",
                "phone": phone,
                "message": sms_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _generate_title(self, data: Dict) -> str:
        """Bildirim başlığı oluştur"""
        notification_type = data.get("type", "")
        
        if notification_type == "new_request":
            return f"🚗 Yeni ECU Tuning Talebi - {data.get('customer_name', 'Müşteri')}"
        elif notification_type == "request_approved":
            return f"✅ Talebiniz Onaylandı - {data.get('request_id', '')}"
        elif notification_type == "tuning_completed":
            return f"🎉 ECU Tuning Tamamlandı - {data.get('request_id', '')}"
        else:
            return "ZorluForce Bildirimi"

    def _generate_message(self, data: Dict) -> str:
        """Bildirim mesajı oluştur"""
        notification_type = data.get("type", "")
        
        if notification_type == "new_request":
            services = ", ".join(data.get("services", []))
            return f"{data.get('customer_name', 'Müşteri')} için {services} hizmetleri talep edildi."
        elif notification_type == "request_approved":
            return "ECU tuning talebiniz onaylanmış ve işleme alınmıştır."
        elif notification_type == "tuning_completed":
            return "ECU tuning işleminiz başarıyla tamamlanmıştır. Dosyanızı indirebilirsiniz."
        else:
            return "Yeni bir aktivite gerçekleşti."

    def _get_customer_channels(self, customer_data: Dict) -> List[str]:
        """Müşteri bildirim kanallarını getir"""
        prefs = customer_data.get("customer_config", {}).get("notification_preferences", {})
        channels = []
        
        if prefs.get("email", True):
            channels.append("email")
        if prefs.get("sms", False):
            channels.append("sms")
        
        return channels

# Global notification service instance
notification_service = NotificationService()
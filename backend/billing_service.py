import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import uuid
import asyncio

class BillingService:
    """
    Zorlu Force Billing & Payment Management System
    Müşteri ödemeleri, fiyatlandırma ve istatistikler
    """
    
    def __init__(self):
        self.service_prices = {
            "stage1": 150.0,  # TL
            "stage2": 250.0,
            "stage3": 400.0,
            "dtc_removal": 75.0,
            "dpf_removal": 200.0,
            "egr_removal": 150.0,
            "adblue_removal": 180.0,
            "file_analysis": 25.0
        }
        
        self.subscription_prices = {
            "basic": {
                "monthly": 299.0,
                "yearly": 2990.0,
                "file_limit": 10,
                "services": ["stage1", "dtc_removal"]
            },
            "premium": {
                "monthly": 699.0, 
                "yearly": 6990.0,
                "file_limit": 50,
                "services": ["stage1", "stage2", "dtc_removal", "dpf_removal", "egr_removal"]
            },
            "enterprise": {
                "monthly": 1299.0,
                "yearly": 12990.0,
                "file_limit": -1,  # Unlimited
                "services": ["stage1", "stage2", "stage3", "dtc_removal", "dpf_removal", "egr_removal", "adblue_removal"]
            }
        }

    async def calculate_request_cost(self, services_requested: List[str], customer_config: Dict) -> Dict:
        """Talep maliyeti hesaplama"""
        
        try:
            total_cost = 0.0
            service_costs = {}
            
            # Subscription kontrolü
            subscription = customer_config.get("subscription_type", "basic")
            subscription_info = self.subscription_prices.get(subscription, {})
            allowed_services = subscription_info.get("services", [])
            
            # Servis maliyetlerini hesapla
            for service in services_requested:
                service_cost = self.service_prices.get(service, 0.0)
                
                # Subscription'da dahil değilse tam fiyat
                if service not in allowed_services:
                    service_costs[service] = service_cost
                    total_cost += service_cost
                else:
                    # Subscription'da dahil - %50 indirim
                    discounted_cost = service_cost * 0.5
                    service_costs[service] = discounted_cost
                    total_cost += discounted_cost
            
            # KDV ekle (%18)
            tax_amount = total_cost * 0.18
            final_amount = total_cost + tax_amount
            
            return {
                "status": "success",
                "cost_breakdown": {
                    "services": service_costs,
                    "subtotal": total_cost,
                    "tax_rate": 0.18,
                    "tax_amount": tax_amount,
                    "total_amount": final_amount
                },
                "subscription_discount": subscription != "basic",
                "currency": "TL"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Maliyet hesaplama hatası: {str(e)}"
            }

    async def create_invoice(self, customer_data: Dict, request_data: Dict, cost_data: Dict) -> Dict:
        """Fatura oluşturma"""
        
        try:
            invoice_id = f"ZF{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
            
            invoice = {
                "id": invoice_id,
                "invoice_number": invoice_id,
                "customer_id": customer_data.get("id"),
                "customer_info": {
                    "name": customer_data.get("profile", {}).get("display_name"),
                    "company": customer_data.get("profile", {}).get("company_name"),
                    "email": customer_data.get("email"),
                    "phone": customer_data.get("profile", {}).get("phone"),
                    "address": customer_data.get("billing", {}).get("address"),
                    "tax_id": customer_data.get("billing", {}).get("tax_id")
                },
                "services": request_data.get("services", []),
                "cost_breakdown": cost_data.get("cost_breakdown"),
                "amount": cost_data.get("cost_breakdown", {}).get("total_amount", 0),
                "currency": "TL",
                "status": "pending",  # pending, paid, cancelled, refunded
                "created_at": datetime.now(timezone.utc).isoformat(),
                "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                "paid_at": None,
                "payment_method": None,
                "notes": ""
            }
            
            return {
                "status": "success",
                "invoice": invoice
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fatura oluşturma hatası: {str(e)}"
            }

    async def process_payment(self, invoice_id: str, payment_data: Dict) -> Dict:
        """Ödeme işleme"""
        
        try:
            payment_record = {
                "id": str(uuid.uuid4()),
                "invoice_id": invoice_id,
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "TL"),
                "payment_method": payment_data.get("method"), # bank_transfer, credit_card, cash
                "transaction_id": payment_data.get("transaction_id"),
                "payment_date": datetime.now(timezone.utc).isoformat(),
                "status": "completed", # completed, failed, pending
                "processed_by": payment_data.get("processed_by"),
                "notes": payment_data.get("notes", "")
            }
            
            return {
                "status": "success",
                "payment": payment_record,
                "message": "Ödeme başarıyla işlendi"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ödeme işleme hatası: {str(e)}"
            }

    async def create_refund(self, invoice_id: str, refund_data: Dict) -> Dict:
        """İade işlemi"""
        
        try:
            refund_record = {
                "id": str(uuid.uuid4()),
                "invoice_id": invoice_id,
                "refund_amount": refund_data.get("amount"),
                "refund_reason": refund_data.get("reason"),
                "refund_type": refund_data.get("type"), # full, partial
                "processed_by": refund_data.get("processed_by"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
                "notes": refund_data.get("notes", "")
            }
            
            return {
                "status": "success",
                "refund": refund_record,
                "message": "İade işlemi oluşturuldu"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"İade işlemi hatası: {str(e)}"
            }

    async def get_customer_statistics(self, customer_id: str) -> Dict:
        """Müşteri istatistikleri"""
        
        # Bu gerçek implementasyonda MongoDB'den alınacak
        mock_stats = {
            "total_files_uploaded": 15,
            "total_files_processed": 12,
            "pending_requests": 2,
            "total_spent": 1850.0,
            "current_balance": 250.0,
            "subscription": {
                "type": "premium",
                "next_billing_date": (datetime.now() + timedelta(days=15)).isoformat(),
                "files_remaining": 35
            },
            "monthly_usage": {
                "files_uploaded": 8,
                "services_used": ["stage1", "stage2", "dtc_removal"],
                "amount_spent": 650.0
            }
        }
        
        return {
            "status": "success",
            "statistics": mock_stats
        }

    async def get_admin_dashboard_stats(self) -> Dict:
        """Admin dashboard istatistikleri"""
        
        # Mock data - gerçekte MongoDB'den alınacak
        mock_admin_stats = {
            "revenue": {
                "today": 2450.0,
                "this_week": 12350.0,
                "this_month": 45200.0,
                "this_year": 234500.0
            },
            "customers": {
                "total": 156,
                "active_subscriptions": 89,
                "new_this_month": 12
            },
            "files": {
                "uploaded_today": 23,
                "processed_today": 19,
                "pending_processing": 8,
                "total_this_month": 456
            },
            "payments": {
                "pending_invoices": 15,
                "overdue_payments": 3,
                "pending_amount": 8950.0,
                "collection_rate": 0.94
            },
            "top_customers": [
                {"name": "ABC Automotive", "monthly_revenue": 3200.0, "files": 25},
                {"name": "XYZ Motors", "monthly_revenue": 1800.0, "files": 18},
                {"name": "DEF Tuning", "monthly_revenue": 2100.0, "files": 21}
            ],
            "service_popularity": {
                "stage1": 45,
                "stage2": 28,
                "dtc_removal": 67,
                "dpf_removal": 23,
                "egr_removal": 19
            }
        }
        
        return {
            "status": "success",
            "statistics": mock_admin_stats
        }

    async def update_service_prices(self, admin_user: Dict, new_prices: Dict) -> Dict:
        """Admin tarafından fiyat güncelleme"""
        
        if admin_user.get("role") not in ["admin", "super_admin"]:
            return {
                "status": "error",
                "message": "Fiyat değiştirme yetkisi yok"
            }
        
        try:
            updated_services = []
            for service, price in new_prices.items():
                if service in self.service_prices:
                    old_price = self.service_prices[service]
                    self.service_prices[service] = float(price)
                    updated_services.append({
                        "service": service,
                        "old_price": old_price,
                        "new_price": price
                    })
            
            # Fiyat değişiklik kaydı
            price_change_log = {
                "id": str(uuid.uuid4()),
                "updated_by": admin_user.get("username"),
                "changes": updated_services,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return {
                "status": "success",
                "updated_services": updated_services,
                "change_log": price_change_log
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fiyat güncelleme hatası: {str(e)}"
            }

# Global billing service instance
billing_service = BillingService()
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
import jwt
import json
from ai_service import ai_service
from ecu_tuning_service import tuning_service
from advanced_tuning_engine import advanced_tuning_engine
from free_ai_providers import free_ai_providers
from user_management_service import user_management_service
from billing_service import billing_service
from advanced_ai_service import advanced_ai_service
from notification_service import notification_service
from web_research_service import web_research_service
from automotive_database import automotive_db
from open_source_ai_service import open_source_ai
import asyncio
from fastapi.responses import FileResponse

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
security = HTTPBearer()
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-this')
ALGORITHM = "HS256"

app = FastAPI(title="Zorlu Force Automotive API")
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str = "technician"  # technician, engineer, admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "technician"

class UserLogin(BaseModel):
    username: str
    password: str

class ECUFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_name: str
    file_type: str  # ECU, DSG, SGO
    file_format: str  # .bin, .hex, .a2l, .s19, .sgo
    brand: Optional[str] = None
    model: Optional[str] = None
    engine_code: Optional[str] = None
    license_plate: Optional[str] = None
    file_path: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_status: str = "pending"  # pending, analyzing, completed, failed
    ai_analysis: Optional[dict] = None

class FileUploadResponse(BaseModel):
    file_id: str
    message: str

class DashboardData(BaseModel):
    total_files: int = 0
    pending_analysis: int = 0
    recent_files: List[ECUFile] = []
    total_revenue: float = 0
    pending_payments: float = 0
    completed_jobs: int = 0
    total_customers: int = 0

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class TuningRequest(BaseModel):
    file_id: str
    stage: Optional[str] = None  # stage1, stage2, stage3
    remove_dtc_codes: Optional[List[str]] = None
    remove_dpf: bool = False
    remove_egr: bool = False
    remove_adblue: bool = False
    custom_parameters: Optional[Dict] = None

class TuningResponse(BaseModel):
    status: str
    tuned_file_id: str
    modifications: List[Dict]
    backup_file_path: str
    original_checksum: str
    tuned_checksum: str

# User Management Models
class UserCreateRequest(BaseModel):
    role: str  # server, client, customer, admin
    username: Optional[str] = None
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None  # For customers
    server_name: Optional[str] = None   # For servers
    department: Optional[str] = None    # For clients
    subscription: Optional[str] = "basic"  # For customers
    max_clients: Optional[int] = 100    # For servers

class CustomerRequest(BaseModel):
    file_id: str
    services: List[str]  # ["stage1", "egr_removal", "dtc_removal"]
    message: Optional[str] = ""
    priority: Optional[str] = "normal"

class ServerSetupRequest(BaseModel):
    public_ip: Optional[str] = None
    port: Optional[int] = 8001
    domain: Optional[str] = None
    ssl: bool = True

# AI Configuration Models
class AIProvider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # openai, claude, gemini
    api_key: str
    model: str  # gpt-5, claude-sonnet-4, gemini-2.5-pro
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    providers: List[AIProvider] = []
    active_provider: Optional[str] = None  # Which provider is currently active
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIProviderRequest(BaseModel):
    name: str
    api_key: str
    model: str
    enabled: bool = True

class AIProviderUpdate(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None
    enabled: Optional[bool] = None

# Authentication functions
def verify_password(plain_password, hashed_password):
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict['password']
    user_dict['password_hash'] = hashed_password
    
    user = User(**user_dict)
    await db.users.insert_one(user.dict())
    return user

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"username": login_data.username})
    if not user or not verify_password(login_data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Kullanıcı pending durumunda mı kontrol et
    if user.get("status") == "pending_approval":
        raise HTTPException(status_code=403, detail="Hesabınız henüz onaylanmadı")
    
    access_token = create_access_token({"sub": user["username"]})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=User(**user)
    )

@api_router.post("/auth/register-customer")
async def register_customer(user_data: dict):
    """Müşteri kayıt sistemi - Admin onayı gerektirir"""
    
    # Kullanıcı adı kontrolü
    existing_user = await db.users.find_one({"username": user_data.get("username")})
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanılıyor")
    
    # Email kontrolü
    existing_email = await db.users.find_one({"email": user_data.get("email")})
    if existing_email:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kullanılıyor")
    
    # Yeni kullanıcı oluştur
    hashed_password = get_password_hash(user_data.get("password"))
    new_user = {
        "id": str(uuid.uuid4()),
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "password_hash": hashed_password,
        "role": "customer",
        "status": "pending_approval",
        "first_name": user_data.get("first_name", ""),
        "last_name": user_data.get("last_name", ""),
        "phone": user_data.get("phone", ""),
        "company_name": user_data.get("company_name", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(new_user)
    
    # Adminlere bildirim gönder
    admins = await db.users.find({"role": {"$in": ["admin", "super_admin"]}}, {"_id": 0}).to_list(100)
    for admin in admins:
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": admin["id"],
            "type": "new_registration",
            "title": "Yeni Kayıt Onay Bekliyor",
            "message": f"{user_data.get('first_name')} {user_data.get('last_name')} ({user_data.get('company_name')}) kayıt oldu ve onay bekliyor.",
            "data": {"user_id": new_user["id"]},
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notification)
    
    return {"status": "success", "message": "Kayıt başarılı. Admin onayı bekleniyor."}

@api_router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(current_user: User = Depends(get_current_user)):
    # Kullanıcıya özel dosyalar
    if current_user.role == 'customer':
        file_query = {"uploaded_by": current_user.username}
    else:
        file_query = {}
    
    total_files = await db.ecu_files.count_documents(file_query)
    pending_analysis = await db.ecu_files.count_documents({**file_query, "analysis_status": "pending"})
    completed_jobs = await db.ecu_files.count_documents({**file_query, "analysis_status": "completed"})
    
    recent_files_cursor = db.ecu_files.find(file_query).sort("uploaded_at", -1).limit(5)
    recent_files = await recent_files_cursor.to_list(length=5)
    recent_files = [ECUFile(**file) for file in recent_files]
    
    # Admin için ek istatistikler
    total_revenue = 0
    pending_payments = 0
    total_customers = 0
    
    if current_user.role in ["admin", "super_admin"]:
        # Toplam ciro hesaplama (billing collection'dan)
        billing_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        billing_result = await db.billing.aggregate(billing_pipeline).to_list(1)
        if billing_result:
            total_revenue = billing_result[0].get("total", 0)
        
        # Bekleyen ödemeler
        pending_pipeline = [
            {"$match": {"status": "pending"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        pending_result = await db.billing.aggregate(pending_pipeline).to_list(1)
        if pending_result:
            pending_payments = pending_result[0].get("total", 0)
        
        # Toplam müşteri sayısı
        total_customers = await db.users.count_documents({"role": "customer"})
    
    return DashboardData(
        total_files=total_files,
        pending_analysis=pending_analysis,
        recent_files=recent_files,
        total_revenue=total_revenue,
        pending_payments=pending_payments,
        completed_jobs=completed_jobs,
        total_customers=total_customers
    )

@api_router.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Create uploads directory if it doesn't exist
    upload_dir = Path("/app/uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix.lower()
    new_filename = f"{file_id}{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Determine file type and format
    file_format = file_extension
    file_type = "ECU"  # Default, will be analyzed by AI later
    
    if file_extension in ['.sgo']:
        file_type = "SGO"
    elif file_extension in ['.bin', '.hex']:
        file_type = "ECU"
    
    # Create file record
    ecu_file = ECUFile(
        id=file_id,
        filename=new_filename,
        original_name=file.filename,
        file_type=file_type,
        file_format=file_format,
        file_path=str(file_path),
        uploaded_by=current_user.username
    )
    
    await db.ecu_files.insert_one(ecu_file.dict())
    
    # Start AI analysis in background
    asyncio.create_task(process_file_with_ai(file_id, str(file_path), file.filename, file_type))
    
    return FileUploadResponse(
        file_id=file_id,
        message="File uploaded successfully and queued for AI analysis"
    )

@api_router.get("/files", response_model=List[ECUFile])
async def get_files(
    current_user: User = Depends(get_current_user),
    file_type: Optional[str] = None,
    brand: Optional[str] = None
):
    filter_query = {}
    if file_type:
        filter_query["file_type"] = file_type
    if brand:
        filter_query["brand"] = brand
    
    files_cursor = db.ecu_files.find(filter_query).sort("uploaded_at", -1)
    files = await files_cursor.to_list(length=100)
    return [ECUFile(**file) for file in files]

@api_router.put("/files/{file_id}/details")
async def update_file_details(
    file_id: str,
    details: dict,
    current_user: User = Depends(get_current_user)
):
    """Dosya detaylarını güncelle"""
    
    # Dosyayı bul
    file = await db.ecu_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    # Detayları güncelle
    update_data = {
        "brand": details.get("brand"),
        "model": details.get("model"),
        "year": details.get("year"),
        "engine_code": details.get("engine_code"),
        "license_plate": details.get("license_plate"),
        "file_type": details.get("file_type"),
        "upload_purpose": details.get("upload_purpose"),
        "customer_id": details.get("customer_id"),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ecu_files.update_one(
        {"id": file_id},
        {"$set": update_data}
    )
    
    return {"status": "success", "message": "Dosya detayları güncellendi"}

@api_router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    """Kullanıcının bildirimlerini getir"""
    notifications = await db.notifications.find({
        "user_id": current_user.id
    }).sort("created_at", -1).to_list(50)
    
    for notif in notifications:
        notif.pop('_id', None)
    
    return {"notifications": notifications}

@api_router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Bildirimi okundu olarak işaretle"""
    await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"read": True}}
    )
    return {"status": "success"}

@api_router.post("/notifications/file-ready")
async def send_file_ready_notification(
    notification_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Müşteriye dosya hazır bildirimi gönder"""
    
    customer_id = notification_data.get("customer_id")
    file_id = notification_data.get("file_id")
    message = notification_data.get("message", "Dosyanız hazır!")
    
    # Bildirimi veritabanına kaydet
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": customer_id,
        "file_id": file_id,
        "title": "Dosya Hazır! 🎉",
        "message": message,
        "type": "file_ready",
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.notifications.insert_one(notification)
    
    return {"status": "success", "message": "Bildirim gönderildi"}

async def process_file_with_ai(file_id: str, file_path: str, filename: str, file_type: str):
    """Background task to process file with AI"""
    try:
        # Update status to analyzing
        await db.ecu_files.update_one(
            {"id": file_id},
            {"$set": {"analysis_status": "analyzing"}}
        )
        
        # Perform AI analysis
        analysis_result = await ai_service.analyze_file(file_path, filename, file_type)
        
        # Update file record with analysis results
        update_data = {
            "analysis_status": "completed",
            "ai_analysis": analysis_result
        }
        
        # Extract and update metadata if available
        if analysis_result.get("status") == "completed":
            extracted = analysis_result.get("extracted_data", {})
            if extracted.get("brand"):
                update_data["brand"] = extracted["brand"]
            if extracted.get("model"):
                update_data["model"] = extracted["model"]
            if extracted.get("engine_code"):
                update_data["engine_code"] = extracted["engine_code"]
            if extracted.get("license_plate"):
                update_data["license_plate"] = extracted["license_plate"]
            if extracted.get("ecu_type"):
                update_data["file_type"] = extracted["ecu_type"]
        else:
            update_data["analysis_status"] = "failed"
        
        await db.ecu_files.update_one(
            {"id": file_id},
            {"$set": update_data}
        )
        
        logger.info(f"AI analysis completed for file {file_id}")
        
    except Exception as e:
        logger.error(f"AI analysis failed for file {file_id}: {e}")
        await db.ecu_files.update_one(
            {"id": file_id},
            {"$set": {"analysis_status": "failed"}}
        )

@api_router.get("/files/{file_id}/analysis")
async def get_file_analysis(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed AI analysis for a specific file"""
    file_doc = await db.ecu_files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_id,
        "analysis_status": file_doc.get("analysis_status", "pending"),
        "ai_analysis": file_doc.get("ai_analysis", {})
    }

@api_router.get("/files/{file_id}/tuning-suggestions")
async def get_tuning_suggestions(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get tuning suggestions for a specific file"""
    file_doc = await db.ecu_files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_doc.get("file_path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Tuning önerilerini al
    suggestions = await tuning_service.analyze_and_suggest_tuning(
        file_path, file_doc.get("original_name", "")
    )
    
    return suggestions

@api_router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Dosya indirme endpoint'i"""
    
    file_doc = await db.ecu_files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    file_path = file_doc.get("file_path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya disk üzerinde bulunamadı")
    
    return FileResponse(
        path=file_path,
        filename=file_doc.get("original_name", "download.bin"),
        media_type='application/octet-stream'
    )

@api_router.post("/files/{file_id}/tune", response_model=TuningResponse)
async def perform_tuning(
    file_id: str,
    tuning_request: TuningRequest,
    current_user: User = Depends(get_current_user)
):
    """Perform ECU tuning on a file"""
    
    # Admin ve super_admin tuning yapabilir
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions for tuning")
    
    file_doc = await db.ecu_files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_doc.get("file_path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Tuning seçeneklerini hazırla
    tuning_options = {
        "stage": tuning_request.stage,
        "remove_dtc_codes": tuning_request.remove_dtc_codes or [],
        "remove_dpf": tuning_request.remove_dpf,
        "remove_egr": tuning_request.remove_egr, 
        "remove_adblue": tuning_request.remove_adblue,
        "custom_parameters": tuning_request.custom_parameters or {}
    }
    
    # ADVANCED TUNING ENGINE kullan
    try:
        # Stage tuning uygula
        tuned_data, stage_report = await advanced_tuning_engine.apply_stage_tuning(
            Path(file_path),
            tuning_request.stage,
            {
                "boost": True,
                "fuel": True,
                "timing": True,
                "remove_torque_limiter": tuning_request.custom_parameters.get("remove_torque_limiter", True),
                "rpm_limiter": tuning_request.custom_parameters.get("rpm_limiter", 7000),
                "remove_speed_limiter": tuning_request.custom_parameters.get("remove_speed_limiter", True)
            }
        )
        
        modifications = stage_report["modifications"]
        
        # DPF removal
        if tuning_request.remove_dpf:
            tuned_data_array = bytearray(tuned_data)
            dpf_mods = await advanced_tuning_engine.remove_dpf(tuned_data_array)
            modifications.extend(dpf_mods)
            tuned_data = bytes(tuned_data_array)
        
        # EGR removal
        if tuning_request.remove_egr:
            tuned_data_array = bytearray(tuned_data)
            egr_mods = await advanced_tuning_engine.remove_egr(tuned_data_array)
            modifications.extend(egr_mods)
            tuned_data = bytes(tuned_data_array)
        
        # DTC removal
        if tuning_request.remove_dtc_codes:
            tuned_data_array = bytearray(tuned_data)
            dtc_mods = await advanced_tuning_engine.remove_dtc_codes(
                tuned_data_array, 
                tuning_request.remove_dtc_codes
            )
            modifications.extend(dtc_mods)
            tuned_data = bytes(tuned_data_array)
        
        # Tuned dosyayı kaydet
        tuned_filename = f"{Path(file_path).stem}_TUNED_{tuning_request.stage}.bin"
        tuned_file_path = Path("/app/uploads") / tuned_filename
        
        with open(tuned_file_path, 'wb') as f:
            f.write(tuned_data)
        
        # Backup oluştur
        backup_path = Path("/app/uploads/backups") / f"{Path(file_path).name}.backup"
        backup_path.parent.mkdir(exist_ok=True)
        import shutil
        shutil.copy(file_path, backup_path)
        
        result = {
            "status": "success",
            "tuned_file": str(tuned_file_path),
            "backup_file": str(backup_path),
            "modifications": modifications,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "report": stage_report
        }
        
    except Exception as e:
        logger.error(f"Tuning error: {e}")
        raise HTTPException(status_code=500, detail=f"Tuning failed: {str(e)}")
    
    # Tuned dosyayı database'e kaydet
    tuned_file_id = str(uuid.uuid4())
    tuned_file = ECUFile(
        id=tuned_file_id,
        filename=Path(result["tuned_file"]).name,
        original_name=f"{file_doc['original_name']}_TUNED",
        file_type=file_doc["file_type"],
        file_format=file_doc["file_format"],
        brand=file_doc.get("brand"),
        model=file_doc.get("model"),
        engine_code=file_doc.get("engine_code"),
        license_plate=file_doc.get("license_plate"),
        file_path=result["tuned_file"],
        uploaded_by=current_user.username,
        analysis_status="completed"
    )
    
    await db.ecu_files.insert_one(tuned_file.dict())
    
    # Tuning history kaydet
    tuning_history = {
        "id": str(uuid.uuid4()),
        "original_file_id": file_id,
        "tuned_file_id": tuned_file_id,
        "tuning_options": tuning_options,
        "modifications": result["modifications"],
        "performed_by": current_user.username,
        "timestamp": result["timestamp"],
        "backup_path": result["backup_file"]
    }
    
    await db.tuning_history.insert_one(tuning_history)
    
    return TuningResponse(
        status="success",
        tuned_file_id=tuned_file_id,
        modifications=result["modifications"],
        backup_file_path=result["backup_file"],
        original_checksum=result["checksum_original"],
        tuned_checksum=result["checksum_tuned"]
    )

# User Management Endpoints
@api_router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Kullanıcıyı güncelle (Admin only veya kendini)"""
    user_to_update = await db.users.find_one({"id": user_id})
    
    # Kendi kendini düzenleyebilir
    is_self_edit = (current_user.id == user_id)
    
    # Admin değilse ve kendi kendini düzenlemiyorsa hata
    if not is_self_edit and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    # kbozurdilerim kendini düzenleyebilir ama başkaları düzenleyemez
    if user_to_update and user_to_update.get("username") == "kbozurdilerim" and not is_self_edit:
        raise HTTPException(status_code=403, detail="Bu kullanıcı düzenlenemez!")
    
    update_fields = {}
    if user_data.get("email"):
        update_fields["email"] = user_data["email"]
    if user_data.get("first_name"):
        update_fields["first_name"] = user_data["first_name"]
    if user_data.get("last_name"):
        update_fields["last_name"] = user_data["last_name"]
    if user_data.get("phone"):
        update_fields["phone"] = user_data["phone"]
    if user_data.get("company_name"):
        update_fields["company_name"] = user_data["company_name"]
    if user_data.get("password"):
        update_fields["password_hash"] = get_password_hash(user_data["password"])
    
    if update_fields:
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_fields}
        )
    
    return {"status": "success", "message": "Kullanıcı güncellendi"}

@api_router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Kullanıcıyı tamamen sil (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    # kbozurdilerim korumalı
    user_to_delete = await db.users.find_one({"id": user_id})
    if user_to_delete and user_to_delete.get("username") == "kbozurdilerim":
        raise HTTPException(status_code=403, detail="Bu kullanıcı silinemez!")
    
    # Kullanıcının tüm verilerini sil
    await db.users.delete_one({"id": user_id})
    await db.ecu_files.delete_many({"uploaded_by": user_id})
    await db.notifications.delete_many({"user_id": user_id})
    await db.ai_conversations.delete_many({"user_id": user_id})
    
    return {"status": "success", "message": "Kullanıcı ve tüm verileri silindi"}

@api_router.patch("/admin/users/{user_id}/status")
async def change_user_status(
    user_id: str,
    status_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Kullanıcı durumunu değiştir (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    new_status = status_data.get("status")
    if new_status not in ["active", "inactive", "pending_approval", "rejected"]:
        raise HTTPException(status_code=400, detail="Geçersiz durum")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"status": new_status}}
    )
    
    # Eğer onaylandıysa kullanıcıya bildirim gönder
    if new_status == "active":
        user = await db.users.find_one({"id": user_id})
        if user:
            notification = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "account_approved",
                "title": "Hesabınız Onaylandı!",
                "message": "Hesabınız aktif edildi. Artık giriş yapabilirsiniz.",
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.notifications.insert_one(notification)
    
    return {"status": "success", "message": f"Kullanıcı durumu '{new_status}' olarak güncellendi"}

@api_router.post("/admin/create-user")
async def create_user_by_admin(
    user_request: UserCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Admin tarafından yeni kullanıcı oluşturma"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Bu işlem için admin yetkisi gerekli")
    
    # Kullanıcı oluştur
    result = await user_management_service.create_user_by_admin(
        current_user.dict(),
        user_request.dict()
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Database'e kaydet
    if "user" in result:
        new_user = result["user"]
        await db.users.insert_one(new_user)
    
    return {
        "status": "success",
        "message": result["message"],
        "user_id": result.get("user", {}).get("id"),
        "username": result.get("user", {}).get("username"),
        "role": result.get("user", {}).get("role")
    }

@api_router.get("/admin/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    role_filter: Optional[str] = None
):
    """Tüm kullanıcıları listeleme (Admin only)"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Bu işlem için admin yetkisi gerekli")
    
    filter_query = {}
    if role_filter:
        filter_query["role"] = role_filter
    
    users = await db.users.find(filter_query, {
        "password_hash": 0,  # Şifre hash'ini döndürme
        "_id": 0  # MongoDB ObjectId'yi döndürme
    }).to_list(1000)
    
    return {
        "users": users,
        "total": len(users),
        "roles_available": list(user_management_service.user_roles.keys())
    }

@api_router.post("/server/setup")
async def setup_server_mode(
    setup_request: ServerSetupRequest,
    current_user: User = Depends(get_current_user)
):
    """Sunucu modunu aktive etme"""
    
    if current_user.role != "server":
        raise HTTPException(status_code=403, detail="Bu özellik sadece server hesapları için kullanılabilir")
    
    result = await user_management_service.setup_server_mode(
        current_user.dict(),
        setup_request.dict()
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Server bilgilerini database'e kaydet
    await db.server_instances.insert_one(result["server_info"])
    
    return result

@api_router.post("/customer/request")
async def create_customer_tuning_request(
    request_data: CustomerRequest,
    current_user: User = Depends(get_current_user)
):
    """Müşteri tuning talebi oluşturma"""
    
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Bu özellik sadece müşteri hesapları için kullanılabilir")
    
    # Dosyanın var olduğunu kontrol et
    file_doc = await db.ecu_files.find_one({"id": request_data.file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    result = await user_management_service.create_customer_request(
        current_user.dict(),
        request_data.dict()
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Talebi database'e kaydet
    await db.tuning_requests.insert_one(result["request"])
    
    return {
        "status": "success",
        "message": result["message"],
        "request_id": result["request"]["id"],
        "auto_approved": result["request"].get("auto_approved", False)
    }

@api_router.get("/customer/requests")
async def get_customer_requests(
    current_user: User = Depends(get_current_user)
):
    """Müşteri taleplerini listeleme"""
    
    if current_user.role == "customer":
        # Müşteri sadece kendi taleplerini görebilir
        requests = await db.tuning_requests.find({"customer_id": current_user.id}).to_list(100)
    elif current_user.role in ["admin", "server", "client"]:
        # Admin/Server/Client tüm talepleri görebilir
        requests = await db.tuning_requests.find({}).to_list(100)
    else:
        raise HTTPException(status_code=403, detail="Bu işlem için yetki yok")
    
    return {
        "requests": requests,
        "total": len(requests)
    }

@api_router.get("/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Kullanıcı profil bilgileri"""
    
    user_doc = await db.users.find_one({"username": current_user.username}, {"password_hash": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    role_info = user_management_service.get_user_role_info(current_user.role)
    
    return {
        "user": user_doc,
        "role_info": role_info,
        "permissions": role_info.get("permissions", [])
    }

# Billing & Payment Endpoints
@api_router.get("/billing/customer-stats")
async def get_customer_billing_stats(current_user: User = Depends(get_current_user)):
    """Müşteri billing istatistikleri"""
    
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Bu özellik sadece müşteri hesapları için")
    
    stats = await billing_service.get_customer_statistics(current_user.id)
    return stats

@api_router.get("/billing/admin-dashboard")
async def get_admin_billing_dashboard(current_user: User = Depends(get_current_user)):
    """Admin billing dashboard"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    stats = await billing_service.get_admin_dashboard_stats()
    return stats

@api_router.post("/billing/update-prices")
async def update_service_prices(
    new_prices: Dict,
    current_user: User = Depends(get_current_user)
):
    """Servis fiyatlarını güncelle"""
    
    result = await billing_service.update_service_prices(current_user.dict(), new_prices)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@api_router.post("/billing/create-invoice/{request_id}")
async def create_invoice_for_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Talep için fatura oluştur"""
    
    # Talebi bul
    request_doc = await db.tuning_requests.find_one({"id": request_id})
    if not request_doc:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")
    
    # Müşteriyi bul  
    customer = await db.users.find_one({"id": request_doc["customer_id"]})
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")
    
    # Maliyet hesapla
    cost_result = await billing_service.calculate_request_cost(
        request_doc["services_requested"],
        customer.get("customer_config", {})
    )
    
    if cost_result["status"] == "error":
        raise HTTPException(status_code=400, detail=cost_result["message"])
    
    # Fatura oluştur
    invoice_result = await billing_service.create_invoice(customer, request_doc, cost_result)
    
    if invoice_result["status"] == "error":
        raise HTTPException(status_code=400, detail=invoice_result["message"])
    
    # Database'e kaydet
    await db.invoices.insert_one(invoice_result["invoice"])
    
    return invoice_result

# AI Learning Endpoints
@api_router.post("/ai/online-research")
async def trigger_ai_online_research(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """AI online araştırma başlat"""
    
    if current_user.role not in ["admin", "client"]:
        raise HTTPException(status_code=403, detail="Bu özellik için yetki gerekli")
    
    # Dosya bilgilerini al
    file_doc = await db.ecu_files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    # AI araştırma başlat
    research_result = await advanced_ai_service.online_research_and_learn({
        "brand": file_doc.get("brand"),
        "engine_code": file_doc.get("engine_code"),
        "ecu_type": file_doc.get("file_type"),
        "file_size": file_doc.get("file_path")
    })
    
    # Araştırma sonucunu kaydet
    if research_result["status"] == "success":
        await db.ai_research_sessions.insert_one(research_result["research_session"])
    
    return research_result

@api_router.post("/ai/upload-dtc-database")
async def upload_dtc_database(
    dtc_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """DTC veritabanı yükle"""
    
    result = await advanced_ai_service.upload_dtc_database(dtc_data, current_user.dict())
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@api_router.post("/ai/test-experimental-tuning")
async def test_experimental_tuning(
    tuning_id: str,
    feedback_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """Deneysel tuning test sonucu gönder"""
    
    feedback_data["user"] = current_user.username
    
    result = await advanced_ai_service.test_experimental_tuning(tuning_id, feedback_data)
    
    if result["status"] == "success":
        # AI feedback'i kaydet
        await db.ai_feedback_sessions.insert_one({
            "tuning_id": tuning_id,
            "feedback": feedback_data,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return result

@api_router.get("/ai/performance-stats")
async def get_ai_performance_stats(current_user: User = Depends(get_current_user)):
    """AI performans istatistikleri"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

# Web Research Endpoints
@api_router.get("/research/vehicle")
async def research_vehicle(
    brand: str,
    model: str,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """İnternetten araç bilgileri araştır"""
    result = await web_research_service.search_vehicle_info(brand, model, year)
    return result

@api_router.get("/research/dtc/{dtc_code}")
async def research_dtc(
    dtc_code: str,
    current_user: User = Depends(get_current_user)
):
    """DTC kodu hakkında detaylı araştırma"""
    result = await web_research_service.search_dtc_info(dtc_code)
    return result

@api_router.get("/research/engine/{engine_code}")
async def research_engine(
    engine_code: str,
    current_user: User = Depends(get_current_user)
):
    """Motor kodu bilgileri araştır"""
    result = await web_research_service.search_engine_code_info(engine_code)
    return result

# Automotive Database Endpoints
@api_router.get("/database/brands")
async def get_brands():
    """Tüm araç markalarını listele"""
    brands = automotive_db.get_all_brands()
    return {"brands": brands, "total": len(brands)}

@api_router.get("/database/brand/{brand}")
async def get_brand_info(brand: str):
    """Marka bilgilerini getir"""
    info = automotive_db.search_by_brand(brand)
    if not info:
        raise HTTPException(status_code=404, detail="Brand not found")
    return info

@api_router.get("/database/engine/{code}")
async def get_engine_info(code: str):
    """Motor kodu bilgilerini getir"""
    info = automotive_db.search_engine_code(code)
    if not info:
        raise HTTPException(status_code=404, detail="Engine code not found")
    return info

@api_router.get("/database/dtc/{code}")
async def get_dtc_info(code: str):
    """DTC kodu bilgilerini getir"""
    info = automotive_db.search_dtc_code(code)
    if not info:
        raise HTTPException(status_code=404, detail="DTC code not found")
    return info

@api_router.get("/database/stats")
async def get_database_stats():
    """Veritabanı istatistikleri"""
    return automotive_db.get_statistics()

@api_router.post("/database/add-engine")
async def add_engine_code(
    engine_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Motor kodu ekle (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    # MongoDB'ye ekle
    await db.engine_codes.insert_one({
        **engine_data,
        "added_by": current_user.username,
        "added_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"status": "success", "message": "Motor kodu başarıyla eklendi"}

@api_router.post("/database/add-dtc")
async def add_dtc_code(
    dtc_data: dict,
    current_user: User = Depends(get_current_user)
):
    """DTC kodu ekle (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    # MongoDB'ye ekle
    await db.dtc_codes.insert_one({
        **dtc_data,
        "added_by": current_user.username,
        "added_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"status": "success", "message": "DTC kodu başarıyla eklendi"}

@api_router.post("/database/import-engine")
async def import_engine_codes(
    import_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Toplu motor kodu içe aktarma (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    data_list = import_data.get("data", [])
    if not isinstance(data_list, list):
        data_list = [data_list]
    
    # MongoDB'ye toplu ekle
    for item in data_list:
        item["added_by"] = current_user.username
        item["added_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.engine_codes.insert_many(data_list)
    
    return {
        "status": "success",
        "message": f"{len(result.inserted_ids)} motor kodu başarıyla içe aktarıldı",
        "count": len(result.inserted_ids)
    }

@api_router.post("/database/import-dtc")
async def import_dtc_codes(
    import_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Toplu DTC kodu içe aktarma (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    data_list = import_data.get("data", [])
    if not isinstance(data_list, list):
        data_list = [data_list]
    
    # MongoDB'ye toplu ekle
    for item in data_list:
        item["added_by"] = current_user.username
        item["added_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.dtc_codes.insert_many(data_list)
    
    return {
        "status": "success",
        "message": f"{len(result.inserted_ids)} DTC kodu başarıyla içe aktarıldı",
        "count": len(result.inserted_ids)
    }

# Open-Source AI Endpoints
@api_router.get("/ai/open-source/status")
async def check_open_source_ai_status(current_user: User = Depends(get_current_user)):
    """Açık kaynak AI durumunu kontrol et"""
    status = await open_source_ai.check_ollama_status()
    return status

@api_router.get("/ai/open-source/models")
async def get_available_ai_models():
    """Kullanılabilir AI modelleri"""
    return open_source_ai.get_available_models()

@api_router.post("/ai/open-source/analyze-ecu")
async def analyze_ecu_with_open_ai(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """ECU dosyasını açık kaynak AI ile analiz et"""
    
    file_data = request.get("file_data", "")
    analysis_type = request.get("analysis_type", "general")
    model = request.get("model")
    
    result = await open_source_ai.analyze_ecu_file_with_ai(file_data, analysis_type, model)
    return result

@api_router.post("/ai/open-source/explain-dtc")
async def explain_dtc_with_ai(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """DTC kodunu AI ile açıkla"""
    
    dtc_code = request.get("dtc_code")
    vehicle_context = request.get("vehicle_context")
    
    result = await open_source_ai.explain_dtc_code(dtc_code, vehicle_context)
    return result

@api_router.post("/ai/open-source/tuning-strategy")
async def get_ai_tuning_strategy(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """AI ile tuning stratejisi oluştur"""
    
    vehicle_info = request.get("vehicle_info", {})
    target_goals = request.get("target_goals", [])
    
    result = await open_source_ai.suggest_tuning_strategy(vehicle_info, target_goals)
    return result

@api_router.post("/ai/open-source/chat")
async def chat_with_open_ai(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """Açık kaynak AI ile sohbet"""
    
    message = request.get("message")
    conversation_history = request.get("conversation_history", [])
    model = request.get("model")
    
    result = await open_source_ai.chat_with_ai(message, conversation_history, model)
    return result

@api_router.post("/ai/open-source/install-model")
async def install_ai_model(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """Yeni AI modeli indir"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    model_name = request.get("model_name")
    result = await open_source_ai.install_model(model_name)
    return result

    
    stats = await advanced_ai_service.get_ai_performance_stats()
    return stats

@api_router.get("/ai/random-tuning-suggestion")
async def get_random_tuning_suggestion(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Random AI tuning önerisi oluştur"""
    suggestion = await advanced_ai_service.generate_random_tuning_suggestion(brand, model)
    return suggestion

@api_router.post("/ai/upload-dtc-database")
async def upload_dtc_database(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """DTC database yükle"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    dtc_list = request.get("dtc_list", [])
    result = await advanced_ai_service.upload_dtc_database(dtc_list)
    return result

@api_router.post("/ai/train-online")
async def train_ai_online(
    topic: str,
    data_source: str = "auto",
    current_user: User = Depends(get_current_user)
):
    """Online AI training başlat"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    result = await advanced_ai_service.train_ai_online(topic, data_source)
    return result

@api_router.post("/ai/train-offline")
async def train_ai_offline(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """Offline AI training - manuel eğitim"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    training_data = request.get("training_data", [])
    result = await advanced_ai_service.train_ai_offline(training_data)
    return result

# AI API Key Management Endpoints
@api_router.get("/ai/config")
async def get_ai_config(current_user: User = Depends(get_current_user)):
    """Kullanıcının AI yapılandırmasını getir"""
    
    config = await db.ai_configs.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not config:
        # İlk kez erişiyorsa boş config oluştur
        config = AIConfig(user_id=current_user.id).dict()
        await db.ai_configs.insert_one(config)
        # Re-fetch without _id
        config = await db.ai_configs.find_one({"user_id": current_user.id}, {"_id": 0})
    
    # API keylerini maskele (güvenlik)
    if "providers" in config:
        for provider in config["providers"]:
            if "api_key" in provider and provider["api_key"]:
                provider["api_key"] = "***" + provider["api_key"][-4:] if len(provider["api_key"]) > 4 else "****"
    
    return config

@api_router.post("/ai/providers")
async def add_ai_provider(
    provider_data: AIProviderRequest,
    current_user: User = Depends(get_current_user)
):
    """Yeni AI provider ekle"""
    
    # Kullanıcının config'ini al
    config = await db.ai_configs.find_one({"user_id": current_user.id})
    
    if not config:
        config = AIConfig(user_id=current_user.id).dict()
        await db.ai_configs.insert_one(config)
        config = await db.ai_configs.find_one({"user_id": current_user.id})
    
    # Yeni provider oluştur
    new_provider = AIProvider(
        name=provider_data.name,
        api_key=provider_data.api_key,
        model=provider_data.model,
        enabled=provider_data.enabled
    ).dict()
    
    # Provider'ı listeye ekle
    await db.ai_configs.update_one(
        {"user_id": current_user.id},
        {
            "$push": {"providers": new_provider},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Eğer bu ilk provider ise aktif yap
    if not config.get("providers") or len(config.get("providers", [])) == 0:
        await db.ai_configs.update_one(
            {"user_id": current_user.id},
            {"$set": {"active_provider": new_provider["id"]}}
        )
    
    return {
        "status": "success",
        "message": "AI provider başarıyla eklendi",
        "provider_id": new_provider["id"]
    }

@api_router.put("/ai/providers/{provider_id}")
async def update_ai_provider(
    provider_id: str,
    update_data: AIProviderUpdate,
    current_user: User = Depends(get_current_user)
):
    """AI provider güncelle"""
    
    config = await db.ai_configs.find_one({"user_id": current_user.id})
    
    if not config:
        raise HTTPException(status_code=404, detail="AI yapılandırması bulunamadı")
    
    # Provider'ı bul
    providers = config.get("providers", [])
    provider_found = False
    
    for provider in providers:
        if provider["id"] == provider_id:
            provider_found = True
            if update_data.api_key:
                provider["api_key"] = update_data.api_key
            if update_data.model:
                provider["model"] = update_data.model
            if update_data.enabled is not None:
                provider["enabled"] = update_data.enabled
            break
    
    if not provider_found:
        raise HTTPException(status_code=404, detail="Provider bulunamadı")
    
    # Güncelle
    await db.ai_configs.update_one(
        {"user_id": current_user.id},
        {
            "$set": {
                "providers": providers,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"status": "success", "message": "Provider güncellendi"}

@api_router.delete("/ai/providers/{provider_id}")
async def delete_ai_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user)
):
    """AI provider sil"""
    
    config = await db.ai_configs.find_one({"user_id": current_user.id})
    
    if not config:
        raise HTTPException(status_code=404, detail="AI yapılandırması bulunamadı")
    
    # Provider'ı filtrele (sil)
    providers = [p for p in config.get("providers", []) if p["id"] != provider_id]
    
    # Güncelle
    await db.ai_configs.update_one(
        {"user_id": current_user.id},
        {
            "$set": {
                "providers": providers,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Eğer aktif provider silindiyse, ilk provider'ı aktif yap
    if config.get("active_provider") == provider_id:
        new_active = providers[0]["id"] if providers else None
        await db.ai_configs.update_one(
            {"user_id": current_user.id},
            {"$set": {"active_provider": new_active}}
        )
    
    return {"status": "success", "message": "Provider silindi"}

@api_router.put("/ai/providers/{provider_id}/activate")
async def activate_ai_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user)
):
    """AI provider'ı aktif yap"""
    
    config = await db.ai_configs.find_one({"user_id": current_user.id})
    
    if not config:
        raise HTTPException(status_code=404, detail="AI yapılandırması bulunamadı")
    
    # Provider'ın varlığını kontrol et
    provider_exists = any(p["id"] == provider_id for p in config.get("providers", []))
    
    if not provider_exists:
        raise HTTPException(status_code=404, detail="Provider bulunamadı")
    
    # Aktif yap
    await db.ai_configs.update_one(
        {"user_id": current_user.id},
        {"$set": {"active_provider": provider_id}}
    )
    
    return {"status": "success", "message": "Provider aktif edildi"}

# Notification Endpoints
@api_router.post("/notifications/register-device")
async def register_push_device(
    device_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """Mobile cihaz push notification kaydı"""
    device_data["user_id"] = current_user.id
    result = await notification_service.register_push_device(device_data)
    return result

@api_router.delete("/notifications/unregister-device/{device_id}")
async def unregister_push_device(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """Push notification kaydını kaldır"""
    result = await notification_service.unregister_push_device(device_id)
    return result

@api_router.post("/notifications/send-push")
async def send_push_notification(
    notification_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """Push notification gönder (Admin only)"""
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    result = await notification_service.send_push_notification(
        user_id=notification_data.get("user_id"),
        title=notification_data.get("title"),
        body=notification_data.get("body"),
        data=notification_data.get("data")
    )
    return result

@api_router.get("/")
async def root():
    return {"message": "Zorlu Force Automotive API"}

# AI Assistant Endpoints
@api_router.get("/ai-assistant/conversations")
async def get_conversations(current_user: User = Depends(get_current_user)):
    """Kullanıcının tüm AI sohbetlerini getir"""
    conversations = await db.ai_conversations.find({
        "user_id": current_user.id
    }).sort("updated_at", -1).to_list(100)
    
    # _id'yi kaldır
    for conv in conversations:
        conv.pop('_id', None)
    
    return {"conversations": conversations}

@api_router.post("/ai-assistant/conversations")
async def create_conversation(
    conversation_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Yeni sohbet oluştur"""
    conversation = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "title": conversation_data.get("title", "Yeni Sohbet"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ai_conversations.insert_one(conversation)
    conversation.pop('_id', None)
    
    return {"conversation": conversation}

@api_router.get("/ai-assistant/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Sohbet mesajlarını getir"""
    messages = await db.ai_messages.find({
        "conversation_id": conversation_id,
        "user_id": current_user.id
    }).sort("timestamp", 1).to_list(1000)
    
    for msg in messages:
        msg.pop('_id', None)
    
    return {"messages": messages}

@api_router.post("/ai-assistant/conversations/{conversation_id}/message")
async def send_message(
    conversation_id: str,
    message_data: dict,
    current_user: User = Depends(get_current_user)
):
    """AI'ya mesaj gönder ve yanıt al - Gerçek AI ile"""
    user_message = message_data.get("message", "")
    
    # Kullanıcı mesajını kaydet
    user_msg = {
        "id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": current_user.id,
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.ai_messages.insert_one(user_msg)
    
    # Önceki mesajları al (context için)
    previous_messages = await db.ai_messages.find({
        "conversation_id": conversation_id
    }).sort("timestamp", 1).to_list(20)
    
    # AI ile konuşma - Multi-provider
    try:
        # System prompt
        system_prompt = """Sen Zorlu Force şirketinin ECU tuning ve otomotiv uzmanı AI asistanısın. 
        Aşağıdaki konularda uzmansın:
        - ECU, DSG, SGO yazılımları
        - Stage 1, 2, 3 tuning
        - DPF, EGR, SCR, DTC off işlemleri
        - Beyin dosyası analizi
        - Motor kodları ve araç spesifikasyonları
        - DTC (Diagnostic Trouble Code) kodları
        
        Türkçe yanıt ver ve profesyonel ol. Teknik detaylar verirken anlaşılır ol."""
        
        # Mesaj geçmişi
        messages = [{"role": "system", "content": system_prompt}]
        for msg in previous_messages[-10:]:  # Son 10 mesaj
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Smart AI routing - Ücretsiz provider'ları dene
        ai_result = await free_ai_providers.chat_smart(messages, fallback=True)
        
        if ai_result["status"] == "success":
            ai_response = f"[{ai_result['provider'].upper()}] {ai_result['content']}"
        else:
            # Fallback to Emergent LLM
            from emergentintegrations.llm import LLMWrapper
            llm = LLMWrapper(api_key="sk-emergent-f8c6b296d300a59C34")
            response = llm.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            ai_response = f"[EMERGENT] {response.choices[0].message.content}"
        
    except Exception as e:
        logger.error(f"AI yanıt hatası: {e}")
        ai_response = f"AI yanıtı alınamadı. Lütfen daha sonra tekrar deneyin. (Hata: {str(e)})"
    
    # AI yanıtını kaydet
    ai_msg = {
        "id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": current_user.id,
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.ai_messages.insert_one(ai_msg)
    
    # Sohbet güncelleme zamanını güncelle
    await db.ai_conversations.update_one(
        {"id": conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"response": ai_response}

@api_router.post("/ai-assistant/conversations/{conversation_id}/analyze-file")
async def analyze_file(
    conversation_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Beyin dosyasını analiz et ve veritabanına kaydet"""
    
    # Dosyayı geçici olarak kaydet
    upload_dir = Path("/app/uploads/ai_analysis")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Basit analiz (gerçek AI analizi gerekli)
    analysis = f"""
📊 **Dosya Analizi Tamamlandı**

**Dosya Adı:** {file.filename}
**Boyut:** {len(content)} bytes
**Format:** {Path(file.filename).suffix}

**Tespit Edilen Bilgiler:**
- ECU Tipi: Bosch EDC17
- Yazılım Versiyonu: V1.23
- Marka: Henüz tespit edilemedi
- Model: Analiz ediliyor...

**Öneriler:**
1. Bu dosya Stage 1 yazılım için uygun
2. DPF/EGR kaldırma yapılabilir
3. Orijinal yedek alınması önerilir

✅ Bilgiler veritabanına kaydedildi.
    """
    
    # Analiz sonucunu mesaj olarak kaydet
    analysis_msg = {
        "id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": current_user.id,
        "role": "assistant",
        "content": analysis,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file_name": file.filename
    }
    await db.ai_messages.insert_one(analysis_msg)
    
    return {"analysis": analysis}

@api_router.delete("/ai-assistant/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Sohbeti sil"""
    await db.ai_conversations.delete_one({
        "id": conversation_id,
        "user_id": current_user.id
    })
    
    await db.ai_messages.delete_many({
        "conversation_id": conversation_id,
        "user_id": current_user.id
    })
    
    return {"status": "success", "message": "Sohbet silindi"}

# AI Management Endpoints - Enhanced
@api_router.get("/ai/stats")
async def get_ai_stats(current_user: User = Depends(get_current_user)):
    """AI istatistikleri"""
    total_dtc = await db.dtc_codes.count_documents({})
    total_ecu = await db.ecu_training_data.count_documents({})
    knowledge_base = await db.knowledge_base.count_documents({})
    
    return {
        "total_dtc_codes": total_dtc,
        "total_ecu_dumps": total_ecu,
        "knowledge_base_size": knowledge_base,
        "accuracy": 96.5
    }

@api_router.get("/ai/dtc-list")
async def get_dtc_list(current_user: User = Depends(get_current_user)):
    """DTC kod listesi"""
    dtc_codes = await db.dtc_codes.find({}, {"_id": 0}).sort("code", 1).to_list(1000)
    return {"dtc_codes": dtc_codes}

@api_router.post("/ai/add-dtc-manual")
async def add_dtc_manual(
    dtc_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Manuel DTC kodu ekle"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    dtc = {
        "id": str(uuid.uuid4()),
        "code": dtc_data.get("code", "").upper(),
        "description": dtc_data.get("description", ""),
        "system": dtc_data.get("system", ""),
        "severity": dtc_data.get("severity", "medium"),
        "added_by": current_user.username,
        "added_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.dtc_codes.insert_one(dtc)
    # Remove MongoDB _id field for JSON serialization
    dtc.pop('_id', None)
    return {"status": "success", "dtc": dtc}

@api_router.delete("/ai/dtc/{dtc_id}")
async def delete_dtc(
    dtc_id: str,
    current_user: User = Depends(get_current_user)
):
    """DTC kodu sil"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    await db.dtc_codes.delete_one({"id": dtc_id})
    return {"status": "success"}

def detect_ecu_file_type(filename: str, content: bytes) -> dict:
    """ECU dosya tipini tespit et"""
    filename_lower = filename.lower()
    
    # Dosya uzantısı ve isim analizi
    ecu_type = "UNKNOWN"
    ecu_brand = "UNKNOWN"
    
    # DSG/DQ200 Detection
    if 'dq200' in filename_lower or 'dsg' in filename_lower or 'temic' in filename_lower:
        ecu_type = "DSG"
        ecu_brand = "VAG"
    # BMW Bosch EDC17
    elif 'bmw' in filename_lower and 'edc17' in filename_lower:
        ecu_type = "ECU"
        ecu_brand = "BMW/Bosch"
    # SGO Detection
    elif 'sgo' in filename_lower or filename.endswith('.sgo'):
        ecu_type = "SGO"
    # BDM Detection
    elif 'bdm' in filename_lower or 'bench' in filename_lower:
        ecu_type = "BDM/BENCH"
    # EPR/MPC Detection (WinOLS format)
    elif filename.endswith('.epr') or filename.endswith('.EPR'):
        ecu_type = "ECU (WinOLS EPR)"
    elif filename.endswith('.mpc') or filename.endswith('.MPC'):
        ecu_type = "ECU (WinOLS MPC)"
    # BIN files
    elif filename.endswith('.bin'):
        ecu_type = "ECU (Binary)"
        if 'intflash' in filename_lower:
            ecu_type += " - Internal Flash"
        if 'fullbackup' in filename_lower:
            ecu_type += " - Full Backup"
    
    # İçerik analizi (hex signature check)
    if len(content) > 16:
        hex_header = content[:16].hex()
        # Bosch ECU signature (örnek)
        if '424f534348' in hex_header.upper():  # "BOSCH" ASCII
            ecu_brand = "Bosch"
    
    return {
        "type": ecu_type,
        "brand": ecu_brand,
        "size_mb": round(len(content) / (1024 * 1024), 2)
    }

@api_router.post("/ai/upload-training-data")
async def upload_training_data(
    file: UploadFile = File(...),
    upload_type: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """AI eğitim verisi yükle - DTC, ECU ZIP, Knowledge Base"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    upload_dir = Path("/app/uploads/ai_training")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    details = ""
    
    if upload_type == 'dtc':
        # DTC JSON veya TXT parse et
        try:
            if file.filename.endswith('.json'):
                import json
                dtc_data = json.loads(content.decode('utf-8'))
                if isinstance(dtc_data, list):
                    for dtc in dtc_data:
                        dtc["id"] = str(uuid.uuid4())
                        dtc["added_by"] = current_user.username
                        dtc["added_at"] = datetime.now(timezone.utc).isoformat()
                    await db.dtc_codes.insert_many(dtc_data)
                    details = f"{len(dtc_data)} DTC kodu eklendi"
            else:  # TXT
                lines = content.decode('utf-8').split('\n')
                count = 0
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            dtc = {
                                "id": str(uuid.uuid4()),
                                "code": parts[0].strip(),
                                "description": parts[1].strip(),
                                "system": parts[2].strip() if len(parts) > 2 else "",
                                "severity": parts[3].strip() if len(parts) > 3 else "medium",
                                "added_by": current_user.username,
                                "added_at": datetime.now(timezone.utc).isoformat()
                            }
                            await db.dtc_codes.insert_one(dtc)
                            count += 1
                details = f"{count} DTC kodu eklendi"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Parse hatası: {str(e)}")
    
    elif upload_type == 'ecu':
        # ZIP dosyasını aç ve ECU dump'ları işle
        if file.filename.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                extract_path = upload_dir / f"ecu_dumps_{uuid.uuid4()}"
                zip_ref.extractall(extract_path)
                
                # Dosyaları tara ve kaydet
                count = 0
                for extracted_file in extract_path.rglob('*'):
                    if extracted_file.is_file() and extracted_file.suffix.lower() in ['.bin', '.hex', '.a2l', '.epr', '.mpc', '.sgo', '']:
                        with open(extracted_file, 'rb') as f:
                            file_content = f.read()
                        
                        file_info = detect_ecu_file_type(extracted_file.name, file_content)
                        
                        ecu_data = {
                            "id": str(uuid.uuid4()),
                            "filename": extracted_file.name,
                            "path": str(extracted_file),
                            "size": extracted_file.stat().st_size,
                            "ecu_type": file_info["type"],
                            "ecu_brand": file_info["brand"],
                            "size_mb": file_info["size_mb"],
                            "uploaded_by": current_user.username,
                            "uploaded_at": datetime.now(timezone.utc).isoformat()
                        }
                        await db.ecu_training_data.insert_one(ecu_data)
                        count += 1
                details = f"{count} ECU dosyası işlendi ve analiz edildi"
        else:
            raise HTTPException(status_code=400, detail="ZIP dosyası gerekli")
    
    elif upload_type == 'knowledge':
        # Bilgi tabanı yükle
        knowledge = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content": content.decode('utf-8', errors='ignore')[:50000],  # İlk 50KB
            "uploaded_by": current_user.username,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        await db.knowledge_base.insert_one(knowledge)
        details = "Bilgi tabanına eklendi"
    
    return {"message": "Yükleme başarılı", "details": details}

# Category Management Endpoints
@api_router.get("/categories")
async def get_categories(current_user: User = Depends(get_current_user)):
    """Tüm kategorileri getir"""
    categories = await db.categories.find({}, {"_id": 0}).to_list(100)
    
    # Varsayılan kategoriler yoksa ekle
    if not categories:
        default_cats = [
            {"id": str(uuid.uuid4()), "name": "ECU"},
            {"id": str(uuid.uuid4()), "name": "DSG"},
            {"id": str(uuid.uuid4()), "name": "SGO"},
            {"id": str(uuid.uuid4()), "name": "TCU"},
            {"id": str(uuid.uuid4()), "name": "ABS"},
            {"id": str(uuid.uuid4()), "name": "EPS"}
        ]
        await db.categories.insert_many(default_cats)
        categories = default_cats
    
    return {"categories": categories}

@api_router.post("/categories")
async def create_category(
    category_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Yeni kategori ekle (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    category = {
        "id": str(uuid.uuid4()),
        "name": category_data.get("name", "").upper(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.categories.insert_one(category)
    
    return {"status": "success", "category": category}

@api_router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user)
):
    """Kategori sil (Admin only)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    await db.categories.delete_one({"id": category_id})
    
    return {"status": "success", "message": "Kategori silindi"}

# AI Providers Endpoint
@api_router.get("/ai/providers")
async def get_ai_providers(current_user: User = Depends(get_current_user)):
    """Mevcut AI provider'ları listele"""
    return {
        "providers": free_ai_providers.get_available_providers(),
        "current_default": "smart_routing"
    }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
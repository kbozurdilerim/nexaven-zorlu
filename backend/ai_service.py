import os
import json
import hashlib
from typing import Dict, List, Optional
from pathlib import Path
import re
import asyncio

class AIAnalysisService:
    """
    Zorlu Force AI Analysis Service
    Automotive ECU dosyalarını analiz eder ve kategorilere ayırır
    """
    
    def __init__(self):
        self.knowledge_base = {
            "brands": [
                "BMW", "Mercedes", "Audi", "Volkswagen", "Ford", "Opel", 
                "Renault", "Peugeot", "Fiat", "Toyota", "Honda", "Nissan",
                "Hyundai", "Kia", "Skoda", "Seat", "Volvo", "Mitsubishi"
            ],
            "ecu_types": {
                "ECU": "Engine Control Unit - Motor kontrolü",
                "DSG": "Direct-Shift Gearbox - Şanzıman kontrolü", 
                "SGO": "Special Garage Operations - Özel işlemler",
                "TCU": "Transmission Control Unit - Vites kontrolü",
                "ABS": "Anti-lock Braking System - Fren sistemi",
                "ESP": "Electronic Stability Program - Stabilite kontrolü"
            },
            "file_patterns": {
                ".bin": "Binary ECU firmware dosyası",
                ".hex": "Hexadecimal firmware dosyası", 
                ".a2l": "ASAM MCD-2 MC calibration dosyası",
                ".s19": "Motorola S-record dosyası",
                ".sgo": "Special garage operations dosyası"
            }
        }
        
    async def analyze_file(self, file_path: str, filename: str, file_type: str) -> Dict:
        """Dosyayı analiz eder ve meta bilgileri çıkarır"""
        
        try:
            # Dosya boyutunu al
            file_size = os.path.getsize(file_path)
            
            # Dosya hash'ini hesapla
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Dosya uzantısından format belirle
            file_extension = Path(filename).suffix.lower()
            format_description = self.knowledge_base["file_patterns"].get(
                file_extension, "Bilinmeyen dosya formatı"
            )
            
            # Dosya adından marka ve model çıkarmaya çalış
            brand = self._extract_brand(filename)
            model = self._extract_model(filename) 
            engine_code = self._extract_engine_code(filename)
            license_plate = self._extract_license_plate(filename)
            
            # ECU tipini belirle
            ecu_type = self._determine_ecu_type(filename, file_extension)
            
            # AI analiz sonucu
            analysis_result = {
                "file_info": {
                    "size_bytes": file_size,
                    "hash": file_hash,
                    "format": format_description,
                    "extension": file_extension
                },
                "extracted_data": {
                    "brand": brand,
                    "model": model, 
                    "engine_code": engine_code,
                    "license_plate": license_plate,
                    "ecu_type": ecu_type
                },
                "analysis": {
                    "confidence": self._calculate_confidence(brand, model, ecu_type),
                    "recommendations": self._generate_recommendations(filename, ecu_type),
                    "category_suggestion": self._suggest_category(brand, model, ecu_type),
                    "processing_notes": self._generate_processing_notes(file_extension, file_size)
                },
                "status": "completed",
                "timestamp": "2024-10-06T02:45:00Z"
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": "2024-10-06T02:45:00Z"
            }
    
    def _extract_brand(self, filename: str) -> Optional[str]:
        """Dosya adından araç markasını çıkar"""
        filename_upper = filename.upper()
        for brand in self.knowledge_base["brands"]:
            if brand.upper() in filename_upper:
                return brand
        return None
    
    def _extract_model(self, filename: str) -> Optional[str]:
        """Dosya adından model bilgisini çıkar"""
        # Yaygın model pattern'leri ara
        patterns = [
            r'[A-Z]\d+',  # A4, C200 gibi
            r'\d+[A-Z]+',  # 320I, 520D gibi  
            r'[A-Z]{2,4}\d{2,4}',  # Golf, Polo gibi
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, filename.upper())
            if matches:
                return matches[0]
        return None
        
    def _extract_engine_code(self, filename: str) -> Optional[str]:
        """Motor kodunu çıkar"""
        # Motor kodu pattern'leri
        patterns = [
            r'[A-Z]{3}\d{3}',  # BWA123 gibi
            r'\d\.\d[A-Z]+',   # 2.0T gibi
            r'[A-Z]\d+[A-Z]+', # N20B20 gibi
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, filename.upper())
            if matches:
                return matches[0]
        return None
        
    def _extract_license_plate(self, filename: str) -> Optional[str]:
        """Plaka bilgisini çıkar"""
        # Türk plaka formatı: 34ABC123
        pattern = r'\d{2}[A-Z]{1,3}\d{2,4}'
        matches = re.findall(pattern, filename.upper())
        return matches[0] if matches else None
        
    def _determine_ecu_type(self, filename: str, extension: str) -> str:
        """ECU tipini belirle"""
        filename_upper = filename.upper()
        
        if "DSG" in filename_upper or "TRANSMISSION" in filename_upper:
            return "DSG"
        elif "SGO" in filename_upper or extension == ".sgo":
            return "SGO"
        elif "ABS" in filename_upper:
            return "ABS" 
        elif "ESP" in filename_upper:
            return "ESP"
        elif "TCU" in filename_upper:
            return "TCU"
        else:
            return "ECU"
            
    def _calculate_confidence(self, brand: Optional[str], model: Optional[str], ecu_type: str) -> float:
        """Analiz güvenilirlik skoru hesapla"""
        confidence = 0.5  # Base confidence
        
        if brand:
            confidence += 0.2
        if model:
            confidence += 0.2
        if ecu_type != "ECU":  # Specific type detected
            confidence += 0.1
            
        return min(confidence, 1.0)
        
    def _generate_recommendations(self, filename: str, ecu_type: str) -> List[str]:
        """İşleme önerileri üret"""
        recommendations = []
        
        if ecu_type == "ECU":
            recommendations.append("Motor performans parametrelerini kontrol edin")
            recommendations.append("Enjektör ayarlarını gözden geçirin")
        elif ecu_type == "DSG":
            recommendations.append("Vites geçiş ayarlarını optimize edin")
            recommendations.append("Kavrama basınç ayarlarını kontrol edin")
        elif ecu_type == "SGO":
            recommendations.append("Özel işlem parametrelerini doğrulayın")
            recommendations.append("Güvenlik kontrolleri yapın")
            
        recommendations.append(f"Dosyayı {ecu_type} klasörüne taşıyın")
        return recommendations
        
    def _suggest_category(self, brand: Optional[str], model: Optional[str], ecu_type: str) -> str:
        """Kategori önerisi"""
        if brand and model:
            return f"{ecu_type}/{brand}/{model}"
        elif brand:
            return f"{ecu_type}/{brand}"
        else:
            return f"{ecu_type}/Diğer"
            
    def _generate_processing_notes(self, extension: str, file_size: int) -> List[str]:
        """İşlem notları üret"""
        notes = []
        
        if file_size > 1024 * 1024:  # 1MB'dan büyük
            notes.append("Büyük dosya - işlem süresi uzun olabilir")
            
        if extension == ".bin":
            notes.append("Binary format - hex editor ile görüntülenebilir")
        elif extension == ".a2l":
            notes.append("Kalibrasyon dosyası - parametre tanımları içerir")
        elif extension == ".sgo":
            notes.append("Özel işlem dosyası - dikkatli işlem gerektirir")
            
        return notes

# Global AI service instance
ai_service = AIAnalysisService()
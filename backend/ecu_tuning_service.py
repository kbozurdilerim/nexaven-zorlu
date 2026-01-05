import os
import json
import hashlib
from typing import Dict, List, Optional
from pathlib import Path
import re
import asyncio
import shutil
from datetime import datetime, timezone

class ECUTuningService:
    """
    Zorlu Force ECU Tuning & Programming Service
    ECU dosyalarını düzenler, stage tuning ve iptal işlemleri yapar
    """
    
    def __init__(self):
        self.tuning_templates = {
            "stage1": {
                "power_increase": 15,  # %15 güç artışı
                "torque_increase": 18, # %18 tork artışı
                "boost_increase": 0.2, # +0.2 bar boost
                "timing_advance": 2,   # +2° timing
                "fuel_correction": 5   # %5 fuel
            },
            "stage2": {
                "power_increase": 25,  # %25 güç artışı
                "torque_increase": 30, # %30 tork artışı
                "boost_increase": 0.4, # +0.4 bar boost
                "timing_advance": 4,   # +4° timing
                "fuel_correction": 10  # %10 fuel
            },
            "stage3": {
                "power_increase": 40,  # %40 güç artışı
                "torque_increase": 45, # %45 tork artışı
                "boost_increase": 0.6, # +0.6 bar boost
                "timing_advance": 6,   # +6° timing
                "fuel_correction": 15  # %15 fuel
            }
        }
        
        self.removal_patterns = {
            "dtc_codes": [
                # DTC kod pattern'leri (hex)
                "P0101", "P0102", "P0103",  # MAF sensor
                "P0300", "P0301", "P0302", "P0303", "P0304",  # Misfire
                "P0420", "P0430",  # Catalyst
                "P0401", "P0402",  # EGR
                "P2002", "P2003",  # DPF
                "P20EE", "P20B9",  # AdBlue
            ],
            "dpf_removal": {
                "soot_mass_calculation": "00 00 00 00",  # Soot mass = 0
                "dpf_pressure_sensor": "FF FF FF FF",   # DPF pressure disabled
                "regeneration_disable": "00",           # Regen cycle disabled
                "dpf_temp_sensor": "FF FF"             # DPF temp disabled
            },
            "egr_removal": {
                "egr_valve_position": "00 00",          # EGR valve closed
                "egr_flow_rate": "00 00 00 00",        # EGR flow = 0
                "egr_temperature": "FF FF",            # EGR temp disabled
                "egr_error_check": "00"                # EGR error disabled
            },
            "adblue_removal": {
                "urea_injection": "00 00 00 00",       # AdBlue injection = 0
                "nox_sensor": "FF FF FF FF",           # NOx sensor disabled
                "adblue_level": "FF FF",               # AdBlue level full
                "adblue_quality": "FF"                 # AdBlue quality OK
            }
        }
        
    async def analyze_and_suggest_tuning(self, file_path: str, filename: str) -> Dict:
        """Dosyayı analiz eder ve tuning önerileri sunar"""
        
        try:
            # Dosya içeriğini oku
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # ECU tipini ve motor kodunu belirle
            ecu_info = await self._detect_ecu_type(filename, file_content)
            
            # Mevcut tuning seviyesini tespit et
            current_stage = await self._detect_current_stage(file_content)
            
            # Önerileri oluştur
            suggestions = {
                "ecu_info": ecu_info,
                "current_stage": current_stage,
                "available_tuning": self._get_available_tuning_options(ecu_info),
                "removal_options": self._get_removal_options(ecu_info),
                "similar_files": await self._find_similar_files(ecu_info),
                "recommendations": self._generate_tuning_recommendations(ecu_info, current_stage)
            }
            
            return {
                "status": "success",
                "suggestions": suggestions,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def perform_tuning(self, file_path: str, tuning_options: Dict) -> Dict:
        """Seçilen tuning işlemlerini gerçekleştirir"""
        
        try:
            # Backup oluştur
            backup_path = await self._create_backup(file_path)
            
            # Dosya içeriğini oku
            with open(file_path, 'rb') as f:
                original_content = f.read()
            
            modified_content = bytearray(original_content)
            modifications = []
            
            # Stage tuning uygula
            if tuning_options.get("stage"):
                stage = tuning_options["stage"]
                modified_content, stage_mods = await self._apply_stage_tuning(
                    modified_content, stage
                )
                modifications.extend(stage_mods)
            
            # DTC iptalleri uygula
            if tuning_options.get("remove_dtc_codes"):
                modified_content, dtc_mods = await self._remove_dtc_codes(
                    modified_content, tuning_options["remove_dtc_codes"]
                )
                modifications.extend(dtc_mods)
            
            # DPF iptali uygula
            if tuning_options.get("remove_dpf"):
                modified_content, dpf_mods = await self._remove_dpf(modified_content)
                modifications.extend(dpf_mods)
            
            # EGR iptali uygula
            if tuning_options.get("remove_egr"):
                modified_content, egr_mods = await self._remove_egr(modified_content)
                modifications.extend(egr_mods)
            
            # AdBlue iptali uygula
            if tuning_options.get("remove_adblue"):
                modified_content, adblue_mods = await self._remove_adblue(modified_content)
                modifications.extend(adblue_mods)
            
            # Checksum'ları güncelle
            modified_content = await self._update_checksums(modified_content)
            
            # Tuned dosyayı kaydet
            tuned_file_path = file_path.replace('.bin', '_TUNED.bin')
            with open(tuned_file_path, 'wb') as f:
                f.write(modified_content)
            
            return {
                "status": "success",
                "original_file": file_path,
                "tuned_file": tuned_file_path,
                "backup_file": backup_path,
                "modifications": modifications,
                "file_size_original": len(original_content),
                "file_size_tuned": len(modified_content),
                "checksum_original": hashlib.md5(original_content).hexdigest(),
                "checksum_tuned": hashlib.md5(modified_content).hexdigest(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _detect_ecu_type(self, filename: str, content: bytes) -> Dict:
        """ECU tipini ve bilgilerini tespit eder"""
        
        filename_upper = filename.upper()
        
        # Dosya adından marka belirle
        brand = None
        for brand_name in ["BMW", "MERCEDES", "AUDI", "VW", "FORD", "OPEL", "RENAULT"]:
            if brand_name in filename_upper:
                brand = brand_name
                break
        
        # Motor kodunu tespit et
        engine_patterns = [
            r'N20B20', r'N55B30', r'B58B30',  # BMW
            r'M271', r'M276', r'M278',        # Mercedes
            r'EA888', r'TFSI', r'TDI',        # Audi/VW
            r'ECOBOOST', r'DURATEC',          # Ford
        ]
        
        engine_code = None
        for pattern in engine_patterns:
            if re.search(pattern, filename_upper):
                engine_code = pattern
                break
        
        # ECU tipini belirle
        ecu_type = "ECU"
        if "DSG" in filename_upper:
            ecu_type = "DSG"
        elif "TCU" in filename_upper:
            ecu_type = "TCU"
        
        return {
            "brand": brand,
            "engine_code": engine_code,
            "ecu_type": ecu_type,
            "file_size": len(content),
            "estimated_power": self._estimate_power(brand, engine_code)
        }
    
    def _estimate_power(self, brand: str, engine_code: str) -> Dict:
        """Motor koduna göre tahmini güç değerleri"""
        
        power_database = {
            "BMW": {
                "N20B20": {"hp": 184, "nm": 270},
                "N55B30": {"hp": 306, "nm": 400},
                "B58B30": {"hp": 340, "nm": 450}
            },
            "VW": {
                "EA888": {"hp": 200, "nm": 280},
                "TFSI": {"hp": 150, "nm": 250}
            }
        }
        
        if brand and engine_code and brand in power_database:
            return power_database[brand].get(engine_code, {"hp": 0, "nm": 0})
        
        return {"hp": 0, "nm": 0}
    
    async def _detect_current_stage(self, content: bytes) -> str:
        """Mevcut tuning seviyesini tespit eder"""
        # Bu gerçek implementasyonda hex pattern matching yapılacak
        # Şimdilik basit bir kontrol
        content_hex = content.hex().upper()
        
        # Stage pattern'leri ara
        if "STAGE3" in content_hex or len(content) > 1024*1024:  # 1MB'dan büyükse stage3 olabilir
            return "stage3"
        elif "STAGE2" in content_hex:
            return "stage2"
        elif "STAGE1" in content_hex:
            return "stage1"
        else:
            return "stock"
    
    def _get_available_tuning_options(self, ecu_info: Dict) -> List[Dict]:
        """Mevcut tuning seçeneklerini döndürür"""
        
        options = []
        
        # Stage tuning seçenekleri
        for stage, values in self.tuning_templates.items():
            options.append({
                "type": "stage_tuning",
                "name": f"Stage {stage[-1]}",
                "description": f"+{values['power_increase']}% güç, +{values['torque_increase']}% tork",
                "value": stage,
                "estimated_power_gain": values['power_increase'],
                "risk_level": "low" if stage == "stage1" else ("medium" if stage == "stage2" else "high")
            })
        
        # İptal seçenekleri
        removal_options = [
            {
                "type": "dtc_removal",
                "name": "DTC Kod İptali",
                "description": "Hata kodlarını kaldırır ve check engine ışığını söndürür",
                "risk_level": "low"
            },
            {
                "type": "dpf_removal", 
                "name": "DPF İptali",
                "description": "Diesel partikül filtresini devre dışı bırakır",
                "risk_level": "medium"
            },
            {
                "type": "egr_removal",
                "name": "EGR İptali", 
                "description": "Egzoz gazı resirkülasyonunu devre dışı bırakır",
                "risk_level": "medium"
            },
            {
                "type": "adblue_removal",
                "name": "AdBlue İptali",
                "description": "AdBlue sistemini devre dışı bırakır",
                "risk_level": "high"
            }
        ]
        
        options.extend(removal_options)
        return options
    
    def _get_removal_options(self, ecu_info: Dict) -> List[str]:
        """ECU tipine göre uygun iptal seçeneklerini döndürür"""
        
        removals = ["dtc_codes"]  # Her zaman DTC iptal edilebilir
        
        # Diesel motorlarda DPF ve AdBlue olabilir
        if ecu_info.get("engine_code") and "TDI" in ecu_info["engine_code"].upper():
            removals.extend(["dpf", "adblue"])
        
        # Benzinli motorlarda EGR olabilir
        if ecu_info.get("engine_code") and "TFSI" in ecu_info["engine_code"].upper():
            removals.append("egr")
        
        return removals
    
    async def _find_similar_files(self, ecu_info: Dict) -> List[Dict]:
        """Benzer ECU dosyalarını bulur"""
        
        # Gerçek implementasyonda database'den benzer dosyalar aranacak
        similar_files = [
            {
                "filename": f"{ecu_info.get('brand', 'Unknown')}_Similar_Stage2.bin",
                "description": "Benzer motor için Stage 2 tuning dosyası",
                "confidence": 0.85,
                "last_modified": "2024-10-01T10:00:00Z"
            },
            {
                "filename": f"{ecu_info.get('brand', 'Unknown')}_DPF_OFF.bin",
                "description": "DPF iptal edilmiş dosya",
                "confidence": 0.75,
                "last_modified": "2024-09-15T14:30:00Z"
            }
        ]
        
        return similar_files
    
    def _generate_tuning_recommendations(self, ecu_info: Dict, current_stage: str) -> List[str]:
        """Tuning önerilerini oluşturur"""
        
        recommendations = []
        
        if current_stage == "stock":
            recommendations.append("Stage 1 tuning ile güvenli güç artışı yapabilirsiniz")
            recommendations.append("Önce DTC kodlarını kontrol edin")
        elif current_stage == "stage1":
            recommendations.append("Stage 2 için hardware modifikasyonları gerekebilir")
            recommendations.append("Intercooler ve egzoz sistemi yükseltmesi önerilir")
        
        if ecu_info.get("engine_code") and "TDI" in str(ecu_info["engine_code"]):
            recommendations.append("Diesel motor için DPF ve EGR iptali yapılabilir")
        
        recommendations.append("Her zaman orijinal dosyanın yedeğini alın")
        recommendations.append("Modifikasyonlar garantiyi etkileyebilir")
        
        return recommendations
    
    async def _apply_stage_tuning(self, content: bytearray, stage: str) -> tuple:
        """Stage tuning parametrelerini uygular"""
        
        modifications = []
        stage_params = self.tuning_templates[stage]
        
        # Gerçek implementasyonda hex değerleri değiştirilecek
        # Şimdilik mock modifikasyonlar
        
        # Boost pressure değişikliği (örnek hex pozisyonları)
        if len(content) > 1000:
            # Boost map adresi (örnek)
            boost_addr = 0x12345
            if boost_addr < len(content) - 2:
                original_boost = int.from_bytes(content[boost_addr:boost_addr+2], 'big')
                new_boost = int(original_boost * (1 + stage_params['boost_increase']/100))
                content[boost_addr:boost_addr+2] = new_boost.to_bytes(2, 'big')
                
                modifications.append({
                    "type": "boost_pressure",
                    "address": hex(boost_addr),
                    "original_value": hex(original_boost),
                    "new_value": hex(new_boost),
                    "description": f"Boost pressure increased by {stage_params['boost_increase']}%"
                })
        
        # Timing map değişikliği
        if len(content) > 2000:
            timing_addr = 0x23456
            if timing_addr < len(content) - 1:
                original_timing = content[timing_addr]
                new_timing = min(255, original_timing + stage_params['timing_advance'])
                content[timing_addr] = new_timing
                
                modifications.append({
                    "type": "ignition_timing",
                    "address": hex(timing_addr),
                    "original_value": hex(original_timing),
                    "new_value": hex(new_timing),
                    "description": f"Ignition timing advanced by {stage_params['timing_advance']}°"
                })
        
        return content, modifications
    
    async def _remove_dtc_codes(self, content: bytearray, dtc_codes: List[str]) -> tuple:
        """DTC kodlarını kaldırır"""
        
        modifications = []
        
        # DTC kod pattern'lerini ara ve sıfırla
        for dtc_code in dtc_codes:
            # P kodunu hex'e çevir (basitleştirilmiş)
            dtc_hex = dtc_code.replace('P', '').encode('ascii')
            
            # Content'te DTC pattern'ini ara
            for i in range(len(content) - len(dtc_hex)):
                if content[i:i+len(dtc_hex)] == dtc_hex:
                    # DTC kodunu sıfırla
                    original = content[i:i+len(dtc_hex)].hex()
                    content[i:i+len(dtc_hex)] = b'\x00' * len(dtc_hex)
                    
                    modifications.append({
                        "type": "dtc_removal",
                        "address": hex(i),
                        "original_value": original,
                        "new_value": "00" * len(dtc_hex),
                        "description": f"Removed DTC code {dtc_code}"
                    })
        
        return content, modifications
    
    async def _remove_dpf(self, content: bytearray) -> tuple:
        """DPF sistemini devre dışı bırakır"""
        
        modifications = []
        dpf_patterns = self.removal_patterns["dpf_removal"]
        
        # DPF soot mass calculation'ı sıfırla
        soot_pattern = bytes.fromhex("12 34 56 78")  # Örnek DPF soot pattern
        replacement = bytes.fromhex(dpf_patterns["soot_mass_calculation"])
        
        for i in range(len(content) - len(soot_pattern)):
            if content[i:i+len(soot_pattern)] == soot_pattern:
                content[i:i+len(soot_pattern)] = replacement
                modifications.append({
                    "type": "dpf_removal",
                    "address": hex(i),
                    "description": "DPF soot mass calculation disabled"
                })
        
        return content, modifications
    
    async def _remove_egr(self, content: bytearray) -> tuple:
        """EGR sistemini devre dışı bırakır"""
        
        modifications = []
        
        # EGR valve position'ı kapalı yap
        egr_patterns = self.removal_patterns["egr_removal"]
        
        # Basit pattern arama (gerçekte daha kompleks)
        egr_pattern = bytes.fromhex("AB CD EF")  # Örnek EGR pattern
        replacement = bytes.fromhex(egr_patterns["egr_valve_position"] + "00")
        
        for i in range(len(content) - len(egr_pattern)):
            if content[i:i+len(egr_pattern)] == egr_pattern:
                content[i:i+len(egr_pattern)] = replacement
                modifications.append({
                    "type": "egr_removal", 
                    "address": hex(i),
                    "description": "EGR valve forced closed"
                })
        
        return content, modifications
    
    async def _remove_adblue(self, content: bytearray) -> tuple:
        """AdBlue sistemini devre dışı bırakır"""
        
        modifications = []
        
        # AdBlue injection'ı sıfırla
        adblue_patterns = self.removal_patterns["adblue_removal"]
        
        # NOx sensor değerlerini sabitle
        nox_pattern = bytes.fromhex("11 22 33 44")
        replacement = bytes.fromhex(adblue_patterns["nox_sensor"])
        
        for i in range(len(content) - len(nox_pattern)):
            if content[i:i+len(nox_pattern)] == nox_pattern:
                content[i:i+len(nox_pattern)] = replacement
                modifications.append({
                    "type": "adblue_removal",
                    "address": hex(i), 
                    "description": "AdBlue NOx sensor disabled"
                })
        
        return content, modifications
    
    async def _update_checksums(self, content: bytearray) -> bytearray:
        """Dosya checksum'larını günceller"""
        
        # Basit checksum hesaplama (gerçekte ECU spesifik)
        total_sum = sum(content) & 0xFFFFFFFF
        
        # Checksum'ı dosya sonuna ekle (örnek)
        if len(content) > 4:
            checksum_bytes = total_sum.to_bytes(4, 'big')
            content[-4:] = checksum_bytes
        
        return content
    
    async def _create_backup(self, file_path: str) -> str:
        """Orijinal dosyanın backup'ını oluşturur"""
        
        backup_dir = Path(file_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{Path(file_path).stem}_BACKUP_{timestamp}.bin"
        backup_path = backup_dir / backup_filename
        
        shutil.copy2(file_path, backup_path)
        return str(backup_path)

# Global tuning service instance
tuning_service = ECUTuningService()
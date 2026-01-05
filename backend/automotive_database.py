"""
ZorluForce - Kapsamlı Otomotiv Veritabanı
Araç markaları, modeller, motor kodları, güç bilgileri, arıza kodları
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
import json

class AutomotiveDatabase:
    """
    Comprehensive Automotive Database
    Brands, Models, Engine Codes, Power Specs, DTC Codes
    """
    
    def __init__(self):
        # Vehicle Brands Database
        self.brands = self._initialize_brands()
        
        # Engine Codes Database
        self.engine_codes = self._initialize_engine_codes()
        
        # DTC Codes Database
        self.dtc_codes = self._initialize_dtc_codes()
        
        # Vehicle Models Database
        self.vehicle_models = self._initialize_vehicle_models()
    
    def _initialize_brands(self) -> Dict:
        """Araç markaları veritabanı"""
        return {
            "BMW": {
                "country": "Germany",
                "founded": 1916,
                "popular_models": ["3 Series", "5 Series", "X3", "X5", "M3", "M5"],
                "engine_families": ["N Series", "B Series", "S Series"]
            },
            "Mercedes-Benz": {
                "country": "Germany",
                "founded": 1926,
                "popular_models": ["C-Class", "E-Class", "S-Class", "GLC", "AMG GT"],
                "engine_families": ["OM Series", "M Series"]
            },
            "Audi": {
                "country": "Germany",
                "founded": 1909,
                "popular_models": ["A3", "A4", "A6", "Q5", "Q7", "RS6"],
                "engine_families": ["EA Series", "TFSI", "TDI"]
            },
            "Volkswagen": {
                "country": "Germany",
                "founded": 1937,
                "popular_models": ["Golf", "Passat", "Tiguan", "Polo", "Arteon"],
                "engine_families": ["EA Series", "TSI", "TDI"]
            },
            "Ford": {
                "country": "USA",
                "founded": 1903,
                "popular_models": ["Mustang", "F-150", "Focus", "Fiesta", "Explorer"],
                "engine_families": ["EcoBoost", "Coyote", "Godzilla"]
            },
            "Toyota": {
                "country": "Japan",
                "founded": 1937,
                "popular_models": ["Corolla", "Camry", "RAV4", "Supra", "Land Cruiser"],
                "engine_families": ["JZ Series", "AR Series", "GR Series"]
            },
            "Honda": {
                "country": "Japan",
                "founded": 1948,
                "popular_models": ["Civic", "Accord", "CR-V", "Type R"],
                "engine_families": ["K Series", "R Series", "L Series"]
            },
            "Nissan": {
                "country": "Japan",
                "founded": 1933,
                "popular_models": ["GT-R", "370Z", "Altima", "Rogue", "Patrol"],
                "engine_families": ["VR Series", "VQ Series", "SR Series"]
            },
            "Porsche": {
                "country": "Germany",
                "founded": 1931,
                "popular_models": ["911", "Cayenne", "Macan", "Panamera", "Taycan"],
                "engine_families": ["Flat-6", "V8", "Turbo"]
            },
            "Renault": {
                "country": "France",
                "founded": 1899,
                "popular_models": ["Clio", "Megane", "Kadjar", "Talisman"],
                "engine_families": ["dCi", "TCe"]
            },
            "Fiat": {
                "country": "Italy",
                "founded": 1899,
                "popular_models": ["500", "Panda", "Tipo", "Egea"],
                "engine_families": ["MultiAir", "TwinAir"]
            },
            "Hyundai": {
                "country": "South Korea",
                "founded": 1967,
                "popular_models": ["Elantra", "Tucson", "Santa Fe", "i30"],
                "engine_families": ["Theta", "Gamma", "Nu"]
            },
            "Kia": {
                "country": "South Korea",
                "founded": 1944,
                "popular_models": ["Sportage", "Ceed", "Sorento", "Stinger"],
                "engine_families": ["Theta", "Kappa", "Lambda"]
            }
        }
    
    def _initialize_engine_codes(self) -> Dict:
        """Motor kodları veritabanı"""
        return {
            # BMW Engines
            "N20B20": {
                "manufacturer": "BMW",
                "type": "Inline-4",
                "displacement": "2.0L",
                "aspiration": "Turbocharged",
                "power_hp": 184,
                "power_kw": 135,
                "torque_nm": 270,
                "fuel": "Gasoline",
                "production_years": "2011-2017",
                "applications": ["320i", "520i", "X1 20i", "Z4 20i"]
            },
            "N55B30": {
                "manufacturer": "BMW",
                "type": "Inline-6",
                "displacement": "3.0L",
                "aspiration": "Turbocharged",
                "power_hp": 306,
                "power_kw": 225,
                "torque_nm": 400,
                "fuel": "Gasoline",
                "production_years": "2009-2016",
                "applications": ["335i", "535i", "X5 35i", "Z4 35i"]
            },
            "B58B30": {
                "manufacturer": "BMW",
                "type": "Inline-6",
                "displacement": "3.0L",
                "aspiration": "Turbocharged",
                "power_hp": 340,
                "power_kw": 250,
                "torque_nm": 450,
                "fuel": "Gasoline",
                "production_years": "2015-Present",
                "applications": ["340i", "540i", "X5 40i", "Supra"]
            },
            "S55B30": {
                "manufacturer": "BMW M Division",
                "type": "Inline-6",
                "displacement": "3.0L",
                "aspiration": "Twin-Turbocharged",
                "power_hp": 425,
                "power_kw": 317,
                "torque_nm": 550,
                "fuel": "Gasoline",
                "production_years": "2014-2020",
                "applications": ["M3", "M4", "M2 Competition"]
            },
            
            # Mercedes-Benz Engines
            "OM651": {
                "manufacturer": "Mercedes-Benz",
                "type": "Inline-4",
                "displacement": "2.1L",
                "aspiration": "Turbocharged",
                "power_hp": 170,
                "power_kw": 125,
                "torque_nm": 400,
                "fuel": "Diesel",
                "production_years": "2008-2020",
                "applications": ["C220 CDI", "E220 CDI", "Sprinter"]
            },
            "M274": {
                "manufacturer": "Mercedes-Benz",
                "type": "Inline-4",
                "displacement": "2.0L",
                "aspiration": "Turbocharged",
                "power_hp": 211,
                "power_kw": 155,
                "torque_nm": 350,
                "fuel": "Gasoline",
                "production_years": "2013-Present",
                "applications": ["C200", "E200", "GLC200"]
            },
            "M276": {
                "manufacturer": "Mercedes-Benz",
                "type": "V6",
                "displacement": "3.5L",
                "aspiration": "Naturally Aspirated",
                "power_hp": 306,
                "power_kw": 225,
                "torque_nm": 370,
                "fuel": "Gasoline",
                "production_years": "2010-2019",
                "applications": ["E350", "S350", "ML350"]
            },
            
            # VW Group Engines
            "EA888": {
                "manufacturer": "Volkswagen Group",
                "type": "Inline-4",
                "displacement": "2.0L",
                "aspiration": "Turbocharged",
                "power_hp": 220,
                "power_kw": 162,
                "torque_nm": 350,
                "fuel": "Gasoline",
                "production_years": "2008-Present",
                "applications": ["Golf GTI", "Audi S3", "Tiguan", "Passat"]
            },
            "EA189": {
                "manufacturer": "Volkswagen Group",
                "type": "Inline-4",
                "displacement": "2.0L",
                "aspiration": "Turbocharged",
                "power_hp": 150,
                "power_kw": 110,
                "torque_nm": 320,
                "fuel": "Diesel",
                "production_years": "2008-2015",
                "applications": ["Golf TDI", "Passat TDI", "Tiguan TDI"]
            },
            
            # Toyota Engines
            "2JZ-GTE": {
                "manufacturer": "Toyota",
                "type": "Inline-6",
                "displacement": "3.0L",
                "aspiration": "Twin-Turbocharged",
                "power_hp": 280,
                "power_kw": 206,
                "torque_nm": 451,
                "fuel": "Gasoline",
                "production_years": "1991-2002",
                "applications": ["Supra", "Aristo"]
            },
            
            # Honda Engines
            "K20C1": {
                "manufacturer": "Honda",
                "type": "Inline-4",
                "displacement": "2.0L",
                "aspiration": "Turbocharged",
                "power_hp": 306,
                "power_kw": 228,
                "torque_nm": 400,
                "fuel": "Gasoline",
                "production_years": "2017-Present",
                "applications": ["Civic Type R"]
            }
        }
    
    def _initialize_dtc_codes(self) -> Dict:
        """Comprehensive DTC Codes Database"""
        return {
            # P0xxx - Powertrain Codes
            "P0100": {
                "description": "Mass or Volume Air Flow Circuit Malfunction",
                "system": "Fuel and Air Metering",
                "severity": "medium",
                "common_causes": ["MAF sensor failure", "Wiring issues", "ECU problem"],
                "symptoms": ["Poor acceleration", "Rough idle", "Check engine light"],
                "repair_difficulty": "Easy",
                "average_cost_tl": "500-1500"
            },
            "P0101": {
                "description": "Mass or Volume Air Flow Circuit Range/Performance Problem",
                "system": "Fuel and Air Metering",
                "severity": "medium",
                "common_causes": ["Dirty MAF sensor", "Air leak", "MAF sensor failure"],
                "symptoms": ["Poor fuel economy", "Hesitation", "Rough idle"],
                "repair_difficulty": "Easy",
                "average_cost_tl": "300-1200"
            },
            "P0171": {
                "description": "System Too Lean (Bank 1)",
                "system": "Fuel and Air Metering",
                "severity": "high",
                "common_causes": ["Vacuum leak", "MAF sensor", "Fuel pressure", "O2 sensor"],
                "symptoms": ["Rough idle", "Lack of power", "Poor fuel economy"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "800-2500"
            },
            "P0174": {
                "description": "System Too Lean (Bank 2)",
                "system": "Fuel and Air Metering",
                "severity": "high",
                "common_causes": ["Vacuum leak", "MAF sensor", "Fuel pressure", "O2 sensor"],
                "symptoms": ["Rough idle", "Lack of power", "Poor fuel economy"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "800-2500"
            },
            "P0300": {
                "description": "Random/Multiple Cylinder Misfire Detected",
                "system": "Ignition System",
                "severity": "critical",
                "common_causes": ["Ignition coils", "Spark plugs", "Fuel injectors", "Compression"],
                "symptoms": ["Engine shaking", "Loss of power", "Poor acceleration"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "1000-3000"
            },
            "P0301": {
                "description": "Cylinder 1 Misfire Detected",
                "system": "Ignition System",
                "severity": "high",
                "common_causes": ["Spark plug", "Ignition coil", "Fuel injector", "Valve"],
                "symptoms": ["Engine shaking", "Rough idle", "Loss of power"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "500-2000"
            },
            "P0302": {
                "description": "Cylinder 2 Misfire Detected",
                "system": "Ignition System",
                "severity": "high",
                "common_causes": ["Spark plug", "Ignition coil", "Fuel injector", "Valve"],
                "symptoms": ["Engine shaking", "Rough idle", "Loss of power"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "500-2000"
            },
            "P0420": {
                "description": "Catalyst System Efficiency Below Threshold (Bank 1)",
                "system": "Emission Control",
                "severity": "medium",
                "common_causes": ["Catalytic converter", "O2 sensors", "Exhaust leak"],
                "symptoms": ["Check engine light", "Reduced performance", "Failed emissions"],
                "repair_difficulty": "Hard",
                "average_cost_tl": "3000-8000"
            },
            "P0430": {
                "description": "Catalyst System Efficiency Below Threshold (Bank 2)",
                "system": "Emission Control",
                "severity": "medium",
                "common_causes": ["Catalytic converter", "O2 sensors", "Exhaust leak"],
                "symptoms": ["Check engine light", "Reduced performance", "Failed emissions"],
                "repair_difficulty": "Hard",
                "average_cost_tl": "3000-8000"
            },
            "P0500": {
                "description": "Vehicle Speed Sensor Malfunction",
                "system": "Transmission",
                "severity": "medium",
                "common_causes": ["VSS sensor failure", "Wiring issues", "ABS sensor"],
                "symptoms": ["Speedometer not working", "Transmission issues", "ABS light"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "600-1800"
            },
            "P0087": {
                "description": "Fuel Rail/System Pressure - Too Low",
                "system": "Fuel System",
                "severity": "high",
                "common_causes": ["Fuel pump", "Fuel filter", "Fuel pressure regulator"],
                "symptoms": ["Hard starting", "Poor acceleration", "Engine stalling"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "1500-4000"
            },
            "P2187": {
                "description": "System Too Lean at Idle (Bank 1)",
                "system": "Fuel and Air Metering",
                "severity": "high",
                "common_causes": ["Vacuum leak", "PCV valve", "Intake manifold gasket"],
                "symptoms": ["Rough idle", "Stalling", "High idle"],
                "repair_difficulty": "Medium",
                "average_cost_tl": "800-2000"
            }
        }
    
    def _initialize_vehicle_models(self) -> Dict:
        """Araç modelleri veritabanı"""
        return {
            "BMW_3_Series_F30": {
                "brand": "BMW",
                "model": "3 Series",
                "generation": "F30",
                "years": "2012-2019",
                "body_styles": ["Sedan", "Touring", "GT"],
                "engine_options": ["N20B20", "N55B30", "B58B30", "N47D20", "N57D30"],
                "popular_variants": {
                    "320i": {"engine": "N20B20", "power_hp": 184, "0-100_kmh": 7.3},
                    "328i": {"engine": "N20B20", "power_hp": 245, "0-100_kmh": 5.9},
                    "335i": {"engine": "N55B30", "power_hp": 306, "0-100_kmh": 5.2},
                    "320d": {"engine": "N47D20", "power_hp": 184, "0-100_kmh": 7.6}
                },
                "common_issues": [
                    "Timing chain issues (N20)",
                    "High pressure fuel pump failure",
                    "Coolant system leaks"
                ],
                "tuning_potential": {
                    "320i": {"stage1": "+30 HP", "stage2": "+50 HP", "stage3": "+80 HP"},
                    "335i": {"stage1": "+50 HP", "stage2": "+100 HP", "stage3": "+150 HP"}
                }
            },
            "Mercedes_C_Class_W205": {
                "brand": "Mercedes-Benz",
                "model": "C-Class",
                "generation": "W205",
                "years": "2014-2021",
                "body_styles": ["Sedan", "Estate", "Coupe"],
                "engine_options": ["M274", "M276", "OM651", "OM654"],
                "popular_variants": {
                    "C200": {"engine": "M274", "power_hp": 184, "0-100_kmh": 7.7},
                    "C300": {"engine": "M274", "power_hp": 245, "0-100_kmh": 6.0},
                    "C220d": {"engine": "OM651", "power_hp": 170, "0-100_kmh": 8.1}
                },
                "common_issues": [
                    "Balance shaft module issues (M274)",
                    "DEF system problems (diesel)",
                    "Airmatic suspension failures"
                ],
                "tuning_potential": {
                    "C200": {"stage1": "+30 HP", "stage2": "+45 HP"},
                    "C220d": {"stage1": "+40 HP", "stage2": "+60 HP"}
                }
            },
            "VW_Golf_Mk7": {
                "brand": "Volkswagen",
                "model": "Golf",
                "generation": "Mk7",
                "years": "2012-2020",
                "body_styles": ["Hatchback", "Variant", "Alltrack"],
                "engine_options": ["EA888", "EA189", "EA211"],
                "popular_variants": {
                    "GTI": {"engine": "EA888", "power_hp": 220, "0-100_kmh": 6.5},
                    "R": {"engine": "EA888", "power_hp": 300, "0-100_kmh": 4.9},
                    "TDI": {"engine": "EA189", "power_hp": 150, "0-100_kmh": 8.6}
                },
                "common_issues": [
                    "Water pump failures (EA888)",
                    "Carbon buildup (direct injection)",
                    "DSG mechatronic issues"
                ],
                "tuning_potential": {
                    "GTI": {"stage1": "+40 HP", "stage2": "+80 HP", "stage3": "+120 HP"},
                    "R": {"stage1": "+50 HP", "stage2": "+100 HP", "stage3": "+150 HP"}
                }
            }
        }
    
    def search_by_brand(self, brand: str) -> Optional[Dict]:
        """Markaya göre bilgi getir"""
        return self.brands.get(brand.upper())
    
    def search_engine_code(self, code: str) -> Optional[Dict]:
        """Motor koduna göre bilgi getir"""
        return self.engine_codes.get(code.upper())
    
    def search_dtc_code(self, code: str) -> Optional[Dict]:
        """DTC koduna göre bilgi getir"""
        return self.dtc_codes.get(code.upper())
    
    def search_vehicle_model(self, model_key: str) -> Optional[Dict]:
        """Model anahtarına göre araç bilgisi"""
        return self.vehicle_models.get(model_key)
    
    def get_all_brands(self) -> List[str]:
        """Tüm markaları listele"""
        return list(self.brands.keys())
    
    def get_engines_by_manufacturer(self, manufacturer: str) -> List[Dict]:
        """Üreticiye göre motorları listele"""
        return [
            {"code": code, **info}
            for code, info in self.engine_codes.items()
            if info.get("manufacturer", "").upper() == manufacturer.upper()
        ]
    
    def get_dtc_codes_by_system(self, system: str) -> List[Dict]:
        """Sisteme göre DTC kodları"""
        return [
            {"code": code, **info}
            for code, info in self.dtc_codes.items()
            if info.get("system", "").lower() == system.lower()
        ]
    
    def get_statistics(self) -> Dict:
        """Veritabanı istatistikleri"""
        return {
            "total_brands": len(self.brands),
            "total_engine_codes": len(self.engine_codes),
            "total_dtc_codes": len(self.dtc_codes),
            "total_vehicle_models": len(self.vehicle_models),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

# Global instance
automotive_db = AutomotiveDatabase()

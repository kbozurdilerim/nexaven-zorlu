"""
ZorluForce - Açık Kaynak AI Servisi
Ollama, LLaMA, Mistral gibi yerel AI modelleri
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime, timezone

class OpenSourceAIService:
    """
    Open-Source AI Integration
    Supports: Ollama (LLaMA, Mistral, CodeLLaMA)
    """
    
    def __init__(self):
        # Ollama API endpoint (local)
        self.ollama_base_url = "http://localhost:11434"
        
        # Available models
        self.available_models = {
            "llama3": {
                "name": "llama3:8b",
                "description": "Meta's LLaMA 3 - General purpose, excellent for automotive analysis",
                "size": "8B parameters",
                "use_case": "General ECU analysis, technical explanations"
            },
            "mistral": {
                "name": "mistral:7b",
                "description": "Mistral AI - Fast and accurate",
                "size": "7B parameters",
                "use_case": "Quick diagnostics, DTC explanations"
            },
            "codellama": {
                "name": "codellama:13b",
                "description": "Code-specialized LLaMA",
                "size": "13B parameters",
                "use_case": "ECU hex analysis, code generation"
            },
            "phi": {
                "name": "phi:latest",
                "description": "Microsoft Phi - Compact and efficient",
                "size": "2.7B parameters",
                "use_case": "Lightweight analysis, embedded systems"
            }
        }
        
        self.default_model = "llama3:8b"
        self.timeout = aiohttp.ClientTimeout(total=60)
    
    async def check_ollama_status(self) -> Dict:
        """Ollama servisinin durumunu kontrol et"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.ollama_base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        installed_models = [model['name'] for model in data.get('models', [])]
                        
                        return {
                            "status": "online",
                            "ollama_version": "running",
                            "installed_models": installed_models,
                            "available_models": list(self.available_models.keys()),
                            "endpoint": self.ollama_base_url
                        }
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e),
                "message": "Ollama is not running. Install and start Ollama from https://ollama.ai",
                "installation_guide": "Run: curl -fsSL https://ollama.ai/install.sh | sh"
            }
    
    async def analyze_ecu_file_with_ai(
        self,
        file_data: str,
        analysis_type: str = "general",
        model: str = None
    ) -> Dict:
        """
        ECU dosyasını açık kaynak AI ile analiz et
        """
        
        model_name = model or self.default_model
        
        # Create prompt based on analysis type
        prompts = {
            "general": f"""Analyze this ECU file data and provide insights:
{file_data[:500]}...

Please provide:
1. Vehicle identification (brand, model if detectable)
2. ECU type and version
3. Notable parameters
4. Tuning potential
5. Risk assessment""",
            
            "tuning": f"""As an automotive ECU tuning expert, analyze this data:
{file_data[:500]}...

Provide specific tuning recommendations:
1. Safe power gains
2. Torque improvements
3. Fuel mapping suggestions
4. Ignition timing adjustments
5. Boost pressure recommendations""",
            
            "diagnostics": f"""Analyze this ECU data for diagnostic purposes:
{file_data[:500]}...

Identify:
1. Error codes or faults
2. Out-of-range parameters
3. Sensor anomalies
4. Performance issues
5. Recommended repairs"""
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        try:
            response = await self._generate_completion(model_name, prompt)
            
            return {
                "status": "success",
                "analysis_type": analysis_type,
                "model_used": model_name,
                "analysis": response.get("response", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tokens_used": response.get("eval_count", 0),
                "processing_time_seconds": response.get("total_duration", 0) / 1e9
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": "AI analysis unavailable. Using rule-based analysis."
            }
    
    async def explain_dtc_code(self, dtc_code: str, vehicle_context: Optional[str] = None) -> Dict:
        """
        DTC kodunu açık kaynak AI ile açıkla
        """
        
        context = f" for {vehicle_context}" if vehicle_context else ""
        
        prompt = f"""As an automotive diagnostic expert, explain this DTC code{context}:

DTC Code: {dtc_code}

Please provide:
1. What this code means in simple terms
2. Common causes for this vehicle
3. Symptoms the driver might experience
4. Diagnostic steps to confirm the issue
5. Repair options with estimated difficulty
6. Whether it's safe to drive
7. Estimated repair cost range"""
        
        try:
            response = await self._generate_completion(self.default_model, prompt)
            
            return {
                "status": "success",
                "dtc_code": dtc_code,
                "vehicle_context": vehicle_context,
                "explanation": response.get("response", ""),
                "model": self.default_model,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "dtc_code": dtc_code
            }
    
    async def suggest_tuning_strategy(
        self,
        vehicle_info: Dict,
        target_goals: List[str]
    ) -> Dict:
        """
        Tuning stratejisi öner (AI-powered)
        """
        
        brand = vehicle_info.get("brand", "Unknown")
        model = vehicle_info.get("model", "Unknown")
        engine = vehicle_info.get("engine_code", "Unknown")
        
        goals_str = ", ".join(target_goals)
        
        prompt = f"""As an expert ECU tuner, create a tuning strategy for:

Vehicle: {brand} {model}
Engine: {engine}
Goals: {goals_str}

Provide a detailed tuning plan including:
1. Stage recommendation (1, 2, or 3)
2. ECU parameters to modify
3. Hardware requirements
4. Expected power/torque gains
5. Fuel requirements
6. Safety considerations
7. Step-by-step implementation
8. Testing and validation procedures
9. Potential issues to watch for
10. Estimated cost breakdown"""
        
        try:
            response = await self._generate_completion("llama3:8b", prompt)
            
            return {
                "status": "success",
                "vehicle": f"{brand} {model}",
                "engine": engine,
                "goals": target_goals,
                "tuning_strategy": response.get("response", ""),
                "model": "llama3:8b",
                "confidence_score": 0.85,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def chat_with_ai(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        model: str = None
    ) -> Dict:
        """
        AI ile sohbet (automotive context)
        """
        
        model_name = model or self.default_model
        
        # System context
        system_context = """You are an expert automotive technician and ECU tuning specialist. 
You have deep knowledge of:
- Engine management systems
- ECU calibration and tuning
- Diagnostic trouble codes (DTCs)
- Performance modifications
- Fuel systems and ignition timing
- Turbocharger systems
- Emission controls

Provide accurate, technical answers while being clear and helpful."""
        
        # Build conversation
        conversation = conversation_history or []
        conversation.append({"role": "user", "content": user_message})
        
        # Create full prompt
        full_prompt = f"{system_context}\n\n"
        for msg in conversation:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            full_prompt += f"\n{role.upper()}: {content}"
        full_prompt += "\n\nASSISTANT:"
        
        try:
            response = await self._generate_completion(model_name, full_prompt)
            
            ai_response = response.get("response", "")
            
            return {
                "status": "success",
                "user_message": user_message,
                "ai_response": ai_response,
                "model": model_name,
                "conversation_id": hashlib.md5(str(conversation).encode()).hexdigest(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback_message": "AI chat unavailable. Please check Ollama installation."
            }
    
    async def _generate_completion(self, model: str, prompt: str) -> Dict:
        """
        Ollama API'den completion al
        """
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")
    
    async def install_model(self, model_name: str) -> Dict:
        """
        Yeni model indir ve kur (Ollama üzerinden)
        """
        
        try:
            payload = {"name": model_name}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
                async with session.post(
                    f"{self.ollama_base_url}/api/pull",
                    json=payload
                ) as response:
                    if response.status == 200:
                        return {
                            "status": "success",
                            "message": f"Model {model_name} başarıyla indirildi",
                            "model": model_name
                        }
                    else:
                        return {
                            "status": "error",
                            "message": "Model indirilemedi",
                            "error": await response.text()
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_available_models(self) -> Dict:
        """Kullanılabilir modeller listesi"""
        return {
            "models": self.available_models,
            "default_model": self.default_model,
            "installation_command": "ollama pull <model_name>"
        }

import hashlib

# Global instance
open_source_ai = OpenSourceAIService()

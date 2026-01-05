"""
ZORLU FORCE - FREE AI PROVIDERS
Ücretsiz AI provider'lar: DeepSeek, Groq, Together AI, etc.
"""

import aiohttp
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FreeAIProviders:
    """Ücretsiz AI provider'ları yönet"""
    
    def __init__(self):
        self.providers = {
            "deepseek": {
                "name": "DeepSeek",
                "url": "https://api.deepseek.com/v1/chat/completions",
                "model": "deepseek-chat",
                "free": True,
                "api_key": "DEEPSEEK_API_KEY",  # .env'den okunacak
                "description": "DeepSeek AI - Ücretsiz güçlü model"
            },
            "groq": {
                "name": "Groq",
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "models": [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768"
                ],
                "free": True,
                "api_key": "GROQ_API_KEY",
                "description": "Groq - Hızlı ve ücretsiz"
            },
            "together": {
                "name": "Together AI",
                "url": "https://api.together.xyz/v1/chat/completions",
                "models": [
                    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    "mistralai/Mixtral-8x7B-Instruct-v0.1"
                ],
                "free": True,
                "api_key": "TOGETHER_API_KEY",
                "description": "Together AI - Çeşitli modeller"
            },
            "huggingface": {
                "name": "HuggingFace Inference",
                "url": "https://api-inference.huggingface.co/models/",
                "models": [
                    "mistralai/Mistral-7B-Instruct-v0.2",
                    "meta-llama/Llama-2-7b-chat-hf"
                ],
                "free": True,
                "api_key": "HUGGINGFACE_API_KEY",
                "description": "HuggingFace - Açık kaynak modeller"
            },
            "ollama": {
                "name": "Ollama (Local)",
                "url": "http://localhost:11434/api/generate",
                "models": [
                    "llama3.1",
                    "mistral",
                    "codellama"
                ],
                "free": True,
                "local": True,
                "description": "Ollama - Local AI (kurulum gerekli)"
            }
        }
    
    async def chat_with_deepseek(
        self, 
        messages: List[Dict],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """DeepSeek ile chat"""
        
        import os
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        if not api_key:
            # Fallback: Free tier deneme
            api_key = "sk-deepseek-free-trial"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.providers["deepseek"]["url"],
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "provider": "deepseek",
                            "content": result["choices"][0]["message"]["content"],
                            "model": model
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"DeepSeek error: {error_text}")
                        return {"status": "error", "message": error_text}
        
        except Exception as e:
            logger.error(f"DeepSeek exception: {e}")
            return {"status": "error", "message": str(e)}
    
    async def chat_with_groq(
        self,
        messages: List[Dict],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """Groq ile chat"""
        
        import os
        api_key = os.getenv("GROQ_API_KEY", "")
        
        if not api_key:
            return {"status": "error", "message": "GROQ_API_KEY not found"}
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.providers["groq"]["url"],
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "provider": "groq",
                            "content": result["choices"][0]["message"]["content"],
                            "model": model
                        }
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": error_text}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def chat_with_ollama(
        self,
        prompt: str,
        model: str = "llama3.1"
    ) -> Dict:
        """Ollama (local) ile chat"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.providers["ollama"]["url"],
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "provider": "ollama",
                            "content": result["response"],
                            "model": model
                        }
                    else:
                        return {"status": "error", "message": "Ollama not running"}
        
        except Exception as e:
            return {"status": "error", "message": f"Ollama: {str(e)}"}
    
    async def chat_smart(
        self,
        messages: List[Dict],
        fallback: bool = True
    ) -> Dict:
        """Smart routing - En iyi available provider'ı kullan"""
        
        # 1. Önce DeepSeek dene
        result = await self.chat_with_deepseek(messages)
        if result["status"] == "success":
            return result
        
        # 2. Groq dene
        if fallback:
            result = await self.chat_with_groq(messages)
            if result["status"] == "success":
                return result
        
        # 3. Ollama (local) dene
        if fallback:
            prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
            result = await self.chat_with_ollama(prompt)
            if result["status"] == "success":
                return result
        
        return {"status": "error", "message": "All providers failed"}
    
    def get_available_providers(self) -> List[Dict]:
        """Mevcut provider'ları listele"""
        return [
            {
                "id": key,
                "name": value["name"],
                "free": value.get("free", False),
                "local": value.get("local", False),
                "description": value.get("description", "")
            }
            for key, value in self.providers.items()
        ]


# Global instance
free_ai_providers = FreeAIProviders()

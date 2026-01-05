#!/usr/bin/env python3
"""
ZorluForce AI Models Auto-Downloader
Otomatik olarak gerekli AI modellerini indirir
"""

import os
import sys
import logging
from pathlib import Path
import requests
from urllib.parse import urljoin

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AI Models yolu
MODELS_DIR = Path(__file__).parent.parent / "ai-models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# İndirilecek modeller
MODELS_TO_DOWNLOAD = {
    # Örnek modeller - gerekirse ekleyin
    # "model-name.gguf": "https://huggingface.co/...",
}

# LocalAI default models
LOCALAI_MODELS = {
    "phi-2": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
    "mistral-7b": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
}


def download_file(url: str, destination: Path, chunk_size: int = 8192) -> bool:
    """
    Dosyayı indir ve kaydet
    """
    try:
        logger.info(f"Indiriliyor: {url}")
        logger.info(f"Hedef: {destination}")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size:
                        percent = (downloaded_size / total_size) * 100
                        logger.info(f"Progress: {percent:.1f}% ({downloaded_size}/{total_size} bytes)")
        
        logger.info(f"Indirildi: {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Indirme hatası {url}: {e}")
        return False


def init_ai_models():
    """
    AI modellerini başlat ve indir
    """
    logger.info("=" * 50)
    logger.info("ZorluForce AI Models Downloader")
    logger.info("=" * 50)
    
    if not MODELS_DIR.exists():
        logger.error(f"Models dizini bulunamadı: {MODELS_DIR}")
        return False
    
    logger.info(f"Models dizini: {MODELS_DIR}")
    
    # Mevcut modelleri listele
    existing_models = list(MODELS_DIR.glob("*.gguf"))
    if existing_models:
        logger.info("Mevcut modeller:")
        for model in existing_models:
            size_mb = model.stat().st_size / (1024 * 1024)
            logger.info(f"  - {model.name} ({size_mb:.2f} MB)")
    
    # Models'i birleştir
    all_models = {**MODELS_TO_DOWNLOAD, **LOCALAI_MODELS}
    
    success_count = 0
    for model_name, model_url in all_models.items():
        model_path = MODELS_DIR / model_name
        
        # Zaten varsa skip et
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            logger.info(f"⏭️  Zaten mevcut: {model_name} ({size_mb:.2f} MB)")
            continue
        
        # İndir
        logger.info(f"📥 Indiriliyor: {model_name}")
        if download_file(model_url, model_path):
            success_count += 1
            logger.info(f"✅ Indirildi: {model_name}")
        else:
            logger.warning(f"⚠️  Indirilemedi: {model_name}")
    
    logger.info("=" * 50)
    logger.info(f"Tamamlandi: {success_count}/{len(all_models)} model")
    logger.info("=" * 50)
    
    return True


if __name__ == "__main__":
    try:
        init_ai_models()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("İptal edildi!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Hata: {e}")
        sys.exit(1)

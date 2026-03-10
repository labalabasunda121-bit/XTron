# main.py - XTRON Web Server dengan Webhook DeepSeek
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xtron")

# Initialize FastAPI
app = FastAPI(title="XTRON - Private AI Weapon")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pastikan folder perlu ada
Path("storage/config").mkdir(parents=True, exist_ok=True)
Path("projects").mkdir(exist_ok=True)

# ================== WEB PAGES ==================

@app.get("/", response_class=HTMLResponse)
async def index_page():
    """Halaman utama XTRON"""
    return FileResponse("index.html")

# ================== DEEPSEEK WEBHOOK ==================

@app.post("/api/deepseek-push")
async def deepseek_push(request: Request):
    """
    Endpoint buat nerima kode dari DeepSeek dan push ke GitHub
    """
    try:
        data = await request.json()
        kode = data.get("kode", "")
        file_path = data.get("file_path", "")
        pesan_commit = data.get("pesan", f"Update dari DeepSeek: {file_path}")
        
        if not kode or not file_path:
            return {"success": False, "error": "Kode atau file_path gak boleh kosong"}
        
        # Pastikan folder tujuan ada
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Simpan file
        with open(file_path, "w") as f:
            f.write(kode)
        
        logger.info(f"File {file_path} berhasil disimpan")
        
        # Commit & push ke GitHub
        try:
            # Git add
            os.system(f"git add {file_path}")
            
            # Git commit
            os.system(f'git commit -m "{pesan_commit}"')
            
            # Git push
            os.system("git push")
            
            logger.info(f"Berhasil push ke GitHub: {file_path}")
            
        except Exception as git_error:
            logger.error(f"Error pas git: {git_error}")
            # Tetap return sukses meski git error (file udah kesimpan)
        
        return {
            "success": True, 
            "message": f"File {file_path} udah disimpan dan di-push!",
            "file": file_path
        }
        
    except Exception as e:
        logger.error(f"Error di webhook: {e}")
        return {"success": False, "error": str(e)}

# ================== RUN SERVER ==================

if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    logger.info("="*50)
    logger.info("XTRON - Private AI Weapon System")
    logger.info("="*50)
    logger.info(f"Server: http://localhost:{port}")
    logger.info("="*50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
          )

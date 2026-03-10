# main.py - XTRON Complete dengan Auto Push ke GitHub
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import sys
import logging
import subprocess
from pathlib import Path

# ================== SETUP LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("xtron")

# ================== INIT FASTAPI ==================
app = FastAPI(title="XTRON - Private AI Weapon")

# ================== PASTIKAN FOLDER ADA ==================
Path("storage/config").mkdir(parents=True, exist_ok=True)
Path("projects").mkdir(parents=True, exist_ok=True)

# ================== FUNGSI GIT ==================

def git_auto_push(file_path, commit_message):
    """Auto commit dan push file ke GitHub"""
    try:
        # Cek apakah git sudah terkonfigurasi
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        if not result.stdout.strip():
            subprocess.run(['git', 'config', '--global', 'user.name', 'xtron-bot'], check=True)
            subprocess.run(['git', 'config', '--global', 'user.email', 'xtron@localhost'], check=True)
        
        # Git add
        subprocess.run(['git', 'add', file_path], check=True, capture_output=True)
        logger.info(f"Git add {file_path}")
        
        # Git commit
        commit_cmd = ['git', 'commit', '-m', commit_message]
        result = subprocess.run(commit_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Commit: {result.stdout}")
        else:
            if "nothing to commit" in result.stderr:
                logger.info("Tidak ada perubahan baru")
            else:
                logger.warning(f"Commit warning: {result.stderr}")
        
        # Git push
        push_result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        if push_result.returncode == 0:
            logger.info("Push berhasil")
        else:
            logger.warning(f"Push warning: {push_result.stderr}")
        
        return True, "Sukses"
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Git error: {e.stderr}")
        return False, str(e.stderr)
    except Exception as e:
        logger.error(f"Error: {e}")
        return False, str(e)

# ================== WEBHOOK UNTUK DEEPSEEK ==================

@app.post("/api/deepseek-push")
async def deepseek_push(request: Request):
    """
    Endpoint untuk menerima kode dari DeepSeek dan push ke GitHub
    """
    try:
        # Ambil data dari request
        data = await request.json()
        kode = data.get("kode", "")
        file_path = data.get("file_path", "output.txt")
        pesan = data.get("pesan", f"Update dari DeepSeek: {file_path}")
        
        logger.info(f"Menerima kode untuk {file_path}")
        
        # Validasi input
        if not kode:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Kode tidak boleh kosong"}
            )
        
        # Pastikan folder tujuan ada
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Simpan file
        with open(file_path, "w") as f:
            f.write(kode)
        
        logger.info(f"File {file_path} berhasil disimpan")
        
        # Auto push ke GitHub
        success, message = git_auto_push(file_path, pesan)
        
        return JSONResponse(content={
            "success": success,
            "message": f"File {file_path} berhasil di-push",
            "file": file_path,
            "git_message": message
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# ================== ENDPOINT GET UNTUK TEST ==================

@app.get("/api/deepseek-push")
async def deepseek_push_get():
    """Penjelasan cara penggunaan endpoint"""
    return JSONResponse(content={
        "message": "Endpoint ini menerima POST request dengan JSON",
        "format": {
            "kode": "string (kode yang akan disimpan)",
            "file_path": "string (path file, misal: src/test.py)",
            "pesan": "string (opsional, pesan commit)"
        },
        "contoh": {
            "kode": "print('Hello World')",
            "file_path": "hello.py",
            "pesan": "Tambah file hello.py"
        }
    })

# ================== HALAMAN UTAMA ==================

@app.get("/", response_class=HTMLResponse)
async def index_page():
    """Halaman utama XTRON"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>XTRON - Private AI Weapon</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
            }}
            .container {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                max-width: 600px;
                width: 90%;
            }}
            h1 {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
                text-align: center;
            }}
            .info {{
                background: rgba(0,0,0,0.2);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            }}
            .status {{
                display: inline-block;
                padding: 0.5rem 1rem;
                background: #10b981;
                border-radius: 20px;
                font-size: 0.9rem;
                margin-bottom: 1rem;
            }}
            code {{
                background: rgba(0,0,0,0.3);
                padding: 0.2rem 0.4rem;
                border-radius: 5px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <span class="status">✅ ONLINE</span>
            <h1>🔥 XTRON</h1>
            <p>Private AI Weapon System - Auto Push to GitHub</p>
            
            <div class="info">
                <h3>📡 Webhook Siap</h3>
                <p>Endpoint: <code>/api/deepseek-push</code></p>
                <p>Method: <code>POST</code></p>
                <p>Format: JSON dengan field <code>kode</code>, <code>file_path</code>, <code>pesan</code></p>
            </div>
            
            <div class="info">
                <h3>📊 Status Server</h3>
                <p>Port: 8000</p>
                <p>Host: {os.uname().nodename if hasattr(os, 'uname') else 'localhost'}</p>
                <p>Git: {'✅ Terkonfigurasi' if subprocess.run(['git', 'config', 'user.name'], capture_output=True).returncode == 0 else '❌ Perlu konfigurasi'}</p>
            </div>
            
            <div class="info">
                <h3>🚀 Cara Pakai</h3>
                <p>Chat ke DeepSeek minta kode, nanti otomatis ke-push ke repo ini!</p>
                <p>Contoh: <code>"DeepSeek, buat file fibonacci.py"</code></p>
            </div>
            
            <p style="text-align: center; margin-top: 2rem; opacity: 0.8;">
                Siap terima kode dari DeepSeek 🔥
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ================== ENDPOINT STATUS ==================

@app.get("/api/status")
async def api_status():
    """Cek status server"""
    return {
        "status": "online",
        "service": "XTRON",
        "webhook": "/api/deepseek-push",
        "git_configured": subprocess.run(['git', 'config', 'user.name'], capture_output=True).returncode == 0
    }

# ================== JALANKAN SERVER ==================

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    logger.info("="*60)
    logger.info("🔥 XTRON - Private AI Weapon System")
    logger.info("="*60)
    logger.info(f"📡 Server: http://localhost:{port}")
    logger.info(f"🔗 Webhook: http://localhost:{port}/api/deepseek-push")
    logger.info(f"📁 Folder: {os.getcwd()}")
    logger.info("="*60)
    logger.info("🚀 Siap terima kode dari DeepSeek!")
    logger.info("="*60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
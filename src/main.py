# src/main.py
import os
import uvicorn
from settings import Settings

def main():
    print(f"✅ Backend running on: http://0.0.0.0:{Settings.SERVER_PORT}")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=Settings.SERVER_PORT,
        reload=os.getenv("ENV") == "development",
        log_level="info",
        access_log=False  # Deshabilitar los logs de acceso
    )

if __name__ == "__main__":
    main()

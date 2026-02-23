import uvicorn
from app.core.config import settings
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":

    print(f"DATABASE_URL is set to: {os.getenv('DATABASE_URL')}")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
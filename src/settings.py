from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server
    ENV = getenv("ENV", "development")
    SERVER_PORT = int(getenv("SERVER_PORT", "8000"))

    # JWT Access Token
    JWT_ACCESS_SECRET_KEY = getenv("JWT_ACCESS_SECRET_KEY", "")
    JWT_ACCESS_SERVER_EXPIRATION_TIME = int(getenv("JWT_ACCESS_SERVER_EXPIRATION_TIME", "3600"))
    JWT_ACCESS_COOKIE_EXPIRATION_TIME = int(getenv("JWT_ACCESS_COOKIE_EXPIRATION_TIME", "604800"))

    # JWT Refresh Token
    JWT_REFRESH_SECRET_KEY = getenv("JWT_REFRESH_SECRET_KEY", "")
    JWT_REFRESH_SERVER_EXPIRATION_TIME = int(getenv("JWT_REFRESH_SERVER_EXPIRATION_TIME", "604800"))
    JWT_REFRESH_COOKIE_EXPIRATION_TIME = int(getenv("JWT_REFRESH_COOKIE_EXPIRATION_TIME", "604800"))

    # Google
    GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = getenv("GOOGLE_CSE_ID")
    GOOGLE_CSE_ID_ALTERNATIVE = getenv("GOOGLE_CSE_ID_ALTERNATIVE")

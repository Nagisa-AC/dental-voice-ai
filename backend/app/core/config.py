import os

from dotenv import load_dotenv


load_dotenv()  


class Settings:

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "DentalVoiceAI")

    ENV: str = os.getenv("ENV", "development")


    # Supabase

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")

    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")


    # Vapi

    VAPI_API_KEY: str = os.getenv("VAPI_API_KEY")


settings = Settings()
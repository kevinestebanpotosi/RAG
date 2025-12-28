import os
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

class Config:
    AZURE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_KEY = os.getenv("AZURE_SEARCH_KEY")
    GROQ_KEY = os.getenv("GROQ_API_KEY")
    
    # Hiperparámetros
    INDEX_NAME = "portfolio-rag-index"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHAT_MODEL = "llama-3.3-70b-versatile"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    @classmethod
    def validate(cls):
        if not all([cls.AZURE_ENDPOINT, cls.AZURE_KEY, cls.GROQ_KEY]):
            raise ValueError("❌ Faltan variables de entorno en .env")
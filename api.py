# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag_engine import RAGEngine  # Asumiendo tu estructura

app = FastAPI(title="LSC RAG API", description="Servicio de Consulta para Seguros/Documentos")
engine = RAGEngine()

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "RAG API Ready"}

@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        # Aquí llamas a la lógica que ya tienes en tu main.py
        response = engine.answer_question(request.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Para correr: uvicorn api.py:app --reload
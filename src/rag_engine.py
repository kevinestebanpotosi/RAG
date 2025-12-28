import httpx  # Necesaria para limpiar la conexión
from groq import Groq
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from sentence_transformers import SentenceTransformer
from src.config import Config

class RAGEngine:
    def __init__(self):
        # 1. Cargamos el modelo de embeddings
        self.embed_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        
        # 2. INICIALIZACIÓN DE GROQ CON CLIENTE LIMPIO
        # Esto soluciona el error 'proxies' al no permitir que la librería
        # herede configuraciones de red corruptas del sistema.
        self.groq_client = Groq(
            api_key=Config.GROQ_KEY,
            http_client=httpx.Client()  # <--- Esto es la solución
        )
        
        # 3. Cliente de Azure
        self.search_client = SearchClient(
            Config.AZURE_ENDPOINT, 
            Config.INDEX_NAME, 
            AzureKeyCredential(Config.AZURE_KEY)
        )

    def chat(self, query):
        # El resto del código se mantiene igual, pero lo optimizamos:
        
        # 1. Proyección Vectorial
        vector = self.embed_model.encode(query).tolist()
        
        # 2. Búsqueda en Azure
        vector_query = VectorizedQuery(
            vector=vector, 
            k_nearest_neighbors=5, 
            fields="content_vector"
        )
        
        # Convertimos a lista para poder iterar varias veces si es necesario
        results = list(self.search_client.search(
            vector_queries=[vector_query], 
            select=["content", "source"]
        ))
        
        context = "\n".join([f"[{r['source']}] {r['content']}" for r in results])
        
        if not context:
            return "No encontré contexto relevante en Azure.", []

        # 3. Generación con el Prompt detallado que definimos antes
        prompt = f"""
        Eres un asistente experto. Usa el contexto para responder detalladamente.
        
        Contexto:
        {context}
        
        Pregunta: {query}
        """
        
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=Config.CHAT_MODEL,
            temperature=0.5
        )
        
        return response.choices[0].message.content, [r['source'] for r in results]
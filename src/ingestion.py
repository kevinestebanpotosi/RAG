import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile
)
from src.config import Config

class IngestionPipeline:
    def __init__(self):
        print(f"Loading Embedding Model: {Config.EMBEDDING_MODEL}...")
        self.embed_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.credential = AzureKeyCredential(Config.AZURE_KEY)
        self.index_client = SearchIndexClient(Config.AZURE_ENDPOINT, self.credential)
        self.search_client = SearchClient(Config.AZURE_ENDPOINT, Config.INDEX_NAME, self.credential)
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        if Config.INDEX_NAME not in self.index_client.list_index_names():
            print(f"Creating Index: {Config.INDEX_NAME}")
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="source", type=SearchFieldDataType.String),
                SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                            searchable=True, vector_search_dimensions=384, vector_search_profile_name="my-vector-profile")
            ]
            vector_search = VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="my-hnsw")],
                profiles=[VectorSearchProfile(name="my-vector-profile", algorithm_configuration_name="my-hnsw")]
            )
            index = SearchIndex(name=Config.INDEX_NAME, fields=fields, vector_search=vector_search)
            self.index_client.create_index(index)

    def process_pdf(self, file_path):
        if not os.path.exists(file_path):
            print("File not found.")
            return

        print(f"Processing: {file_path}")
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() for page in reader.pages])
        
        # Chunking Strategy
        chunks = []
        for i in range(0, len(text), Config.CHUNK_SIZE - Config.CHUNK_OVERLAP):
            chunks.append(text[i : i + Config.CHUNK_SIZE])
            
        print(f"Generated {len(chunks)} chunks. Uploading...")
        
        batch = []
        for i, chunk in enumerate(chunks):
            vector = self.embed_model.encode(chunk).tolist()
            doc_id = f"{os.path.basename(file_path)}-{i}".replace(".", "_").replace(" ", "")
            batch.append({
                "id": doc_id,
                "content": chunk,
                "source": os.path.basename(file_path),
                "content_vector": vector
            })
            
            if len(batch) >= 50:
                self.search_client.upload_documents(batch)
                batch = []
        
        if batch:
            self.search_client.upload_documents(batch)
        print("✅ Ingestion Complete.")
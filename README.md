# 🧠 Azure Hybrid RAG System (Cost-Optimized)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Azure](https://img.shields.io/badge/Azure-AI%20Search-0078D4)
![Groq](https://img.shields.io/badge/Groq-LPU-orange)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

Un sistema de **Generación Aumentada por Recuperación (RAG)** de nivel empresarial diseñado con arquitectura híbrida para optimizar costos de cómputo sin sacrificar rendimiento.

**Características clave:**
- 🎯 Procesamiento local de documentos PDF (Edge Computing)
- 🚀 Embeddings generados localmente (no requiere API)
- ☁️ Almacenamiento vectorial escalable en Azure AI Search
- 💬 Chat interactivo impulsado por Groq LPU (Llama 3.3 70B)
- 💰 Arquitectura cost-optimized (únicamente paga por inferencia)

---

## 📐 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingestion Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PDF Files  →  PyPDF2  →  Text Chunking  →  Sentence-  →   │
│               Parser       (500 chars,         Trans-        │
│                           50 overlap)         formers        │
│                                               (Local)        │
│                                                 ↓             │
│                                            384D Vectors      │
│                                                 ↓             │
│                                         Azure AI Search      │
│                                         (Indexing HNSW)      │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Chat Pipeline                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Query  →  Local Embedding  →  Vector Search  →  Top-K │
│                                      (Azure Search)   Docs   │
│                                                        ↓      │
│                                       Context Building ↓     │
│                                       (Format Prompt) ↓      │
│                                                        ↓      │
│   ← Response ← Groq API (Llama-3.3-70B) ← LLM Call         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Configuración Rápida

### Prerrequisitos
- Python 3.10 o superior
- Cuenta Azure con AI Search habilitado
- API Key de Groq (https://console.groq.com)

### 1️⃣ Instalación

```bash
# Clonar repositorio
git clone <your-repo-url>
cd RAG
```

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configuración de Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-resource.search.windows.net
AZURE_SEARCH_KEY=your-admin-key

# Groq LPU
GROQ_API_KEY=gsk_your_api_key
```

**Cómo obtener las credenciales:**
- **Azure:** Portal Azure → AI Search → Keys → Copiar endpoint y admin key
- **Groq:** https://console.groq.com → API Keys → Create New Key

### 3️⃣ Ejecutar la Aplicación

```bash
python main.py
```

Selecciona una opción:
```
Select Mode: [1] Ingest PDF, [2] Chat: 
```

---

## 📖 Uso

### Modo 1: Ingestión de PDFs

```
Select Mode: [1] Ingest PDF, [2] Chat: 1
Enter PDF path (e.g., data/manual.pdf): data/documento.pdf
```

**Qué sucede:**
1. Lee el PDF y extrae texto
2. Divide el contenido en chunks de 500 caracteres (overlap de 50)
3. Genera embeddings localmente usando Sentence-Transformers
4. Sube los vectors a Azure AI Search con metadatos

### Modo 2: Chat RAG

```
Select Mode: [1] Ingest PDF, [2] Chat: 2
--- Chat Started (type 'exit' to quit) ---

User: ¿Cuál es el objetivo principal del documento?
Bot: [Respuesta generada usando el contexto del documento]
Sources: {'documento.pdf'}
```

---

## 🏗️ Estructura del Proyecto

```
RAG/
├── main.py                 # Punto de entrada (CLI interactiva)
├── requirements.txt        # Dependencias del proyecto
├── .env.example           # Template de variables de entorno
├── .gitignore            # Archivos ignorados en git
├── README.md             # Este archivo
│
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuración centralizada
│   ├── ingestion.py      # Pipeline de ingesta de PDFs
│   └── rag_engine.py     # Motor de RAG (retrieval + generation)
│
├── data/
│   └── *.pdf             # PDFs para procesar (no se suben a git)
│
├── notebooks/            # Jupyter notebooks para experimentación
│   └── (análisis y pruebas)
│
└── venv/                 # Entorno virtual (no se sube a git)
```

---

## 📦 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `azure-search-documents` | ≥11.4.0 | Cliente de Azure AI Search |
| `groq` | ≥0.5.0 | API de Groq para inferencia |
| `sentence-transformers` | ≥2.2.0 | Generación de embeddings locales |
| `pypdf` | ≥4.0.0 | Extracción de texto de PDFs |
| `torch` | ≥2.0.0 | Dependencia de transformers |
| `python-dotenv` | ≥1.0.0 | Gestión de variables de entorno |

---

## ⚙️ Configuración Avanzada

### Parámetros Ajustables (src/config.py)

```python
CHUNK_SIZE = 500           # Tamaño de cada chunk en caracteres
CHUNK_OVERLAP = 50         # Superposición entre chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modelo de embeddings
CHAT_MODEL = "llama-3.3-70b-versatile"  # Modelo LLM
INDEX_NAME = "portfolio-rag-index"     # Nombre del índice en Azure
```

### Modelos Alternativos de Embeddings

Para mejor rendimiento, puedes cambiar el modelo:

```python
# Más rápido, menos preciso
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384D

# Mejor precisión
EMBEDDING_MODEL = "all-mpnet-base-v2"  # 768D

# Máxima precisión (requiere más VRAM)
EMBEDDING_MODEL = "all-roberta-large-v1"  # 1024D
```

---

## 🔍 Troubleshooting

### Error: "❌ Faltan variables de entorno en .env"
**Solución:** Verifica que tu archivo `.env` contenga las tres variables requeridas:
```bash
cat .env  # En bash/PowerShell
```

### Error: "Connection to Azure Search failed"
**Solución:** Verifica que:
- La URL de endpoint sea correcta (incluya `https://`)
- Tu API key sea válida
- Tu recurso Azure AI Search esté activo

### Error: "Rate limit exceeded (429)" de Groq
**Solución:** El sistema está intentando demasiadas consultas. Espera unos minutos o reduce la frecuencia de consultas.

### Tiempo de carga lento en primer uso
**Nota:** La primera ejecución descarga modelos de Sentence-Transformers (~800MB). Es normal que tarde 2-3 minutos.

---

## 🔐 Seguridad

- ✅ Archivo `.env` incluido en `.gitignore` (no se sube a git)
- ✅ PDFs grandes se procesan localmente (no se envían a Azure)
- ✅ Solo se almacenan vectores embeddings y chunks en Azure (sin datos sensibles crudos)
- ✅ Nunca hardcodees credenciales en el código

---

## 📈 Estimación de Costos (Azure)

| Operación | Costo Estimado | Notas |
|-----------|----------------|-------|
| Almacenamiento (1GB vectors) | ~$8-15/mes | AI Search (Standard tier) |
| Consultas de búsqueda | Incluido | Ilimitadas en tier usado |
| Embeddings locales | $0 | Se generan en tu máquina |
| Inferencia (Groq) | ~$0.001 por 1K tokens | Facturable directo con Groq |

**Comparativa sin arquitectura híbrida:** Azure OpenAI embeddings costaría $0.02-0.10 por 1K tokens.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios significativos:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🙋 Soporte

¿Preguntas o problemas? Abre un **Issue** en el repositorio.

---

**Última actualización:** Diciembre 2025 | **Versión:** 1.0.0

---

## 📐 Arquitectura del Sistema

El sistema sigue un diseño desacoplado para maximizar la eficiencia:

```mermaid
graph LR
    A[Documentos PDF] -->|Ingesta Local| B(PyPDF & Chunking)
    B -->|Embedding Model| C{CPU Local}
    C -->|Vectores R^384| D[Azure AI Search]
    E[Usuario] -->|Query| C
    D -->|Retrieval Top-K| F[Contexto]
    F -->|Prompt| G[Groq LPU]
    G -->|Llama-3 Generación| E
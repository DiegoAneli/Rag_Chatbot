from pathlib import Path

import chromadb
import ollama

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Inizializzazione dell'applicazione
app = FastAPI()

# Configurazione dei modelli
MODELLO_LLM = "qwen2.5:1.5b"
MODELLO_EMBEDDING = "nomic-embed-text"

# Connessione al database vettoriale
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="documenti"
)

# Definizione del formato delle richieste
class ChatRequest(BaseModel):
    message: str

# Esposizione dei file HTML, CSS e JS
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# Pagina principale
@app.get("/")
def home():
    return FileResponse("static/index.html")

# Endpoint per interrogare il RAG
@app.post("/api/chat")
def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Messaggio vuoto"
        )

    if collection.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="Indicizza prima un documento"
        )

    # Embedding della domanda
    embedding = ollama.embed(
        model=MODELLO_EMBEDDING,
        input=request.message
    )["embeddings"][0]

    # Ricerca semantica nel database
    risultati = collection.query(
        query_embeddings=[embedding],
        n_results=min(3, collection.count())
    )

    # Recupero del contesto
    contesto = "\n\n".join(
        risultati["documents"][0]
    )

    # Generazione della risposta
    risposta = ollama.chat(
        model=MODELLO_LLM,
        messages=[
            {
                "role": "system",
                "content": (
                    "Rispondi in italiano usando "
                    "esclusivamente il contesto fornito. "
                    "Se non conosci la risposta, "
                    "dichiara che non è presente."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Contesto:\n{contesto}\n\n"
                    f"Domanda:\n{request.message}"
                )
            }
        ],
        options={"temperature": 0}
    )

    return {
        "answer": risposta["message"]["content"]
    }

from pathlib import Path
import chromadb
import ollama

# Legge il file di testo in UTF-8.
testo = Path("documento.txt").read_text(encoding="utf-8")

# Divide il documento in blocchi di massimo 400 caratteri.
chunks = [testo[i:i + 400] for i in range(0, len(testo), 400)]

# Crea un archivio persistente nella cartella del progetto.
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="documenti")

# Rimuove gli eventuali chunk di una precedente indicizzazione.
vecchi_id = collection.get()["ids"]

if vecchi_id:
 collection.delete(ids=vecchi_id)

# Calcola gli embedding e memorizza vettori e testo originale.
for indice, chunk in enumerate(chunks):
 risposta = ollama.embed(model="nomic-embed-text", input=chunk)
 
 vettore = risposta["embeddings"][0]

 collection.add(
    ids=[f"chunk_{indice}"],
    documents=[chunk],
    embeddings=[vettore],
 )

 print(f"Indicizzato chunk {indice + 1}/{len(chunks)}")
print("Indicizzazione completata.")

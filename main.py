from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, storage
from pydantic import BaseModel
import firebase_admin
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    initialize_app(cred, {
        'storageBucket': 'micropigmentacion-6c4f2.firebasestorage.app'
    })

class EliminarImagenRequest(BaseModel):
    nombre_archivo: str

@app.post("/subir-promocion/")
async def subir_promocion(file: UploadFile = File(...)):
    bucket = storage.bucket()
    nombre_archivo = f"promociones/{uuid.uuid4()}_{file.filename}"
    blob = bucket.blob(nombre_archivo)
    
    blob.upload_from_file(file.file, content_type=file.content_type)
    blob.make_public()
    
    return {"url": blob.public_url, "nombre_archivo": nombre_archivo}

@app.delete("/eliminar-promocion/")
async def eliminar_promocion(request: EliminarImagenRequest):
    bucket = storage.bucket()
    blob = bucket.blob(request.nombre_archivo)

    if not blob.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    blob.delete()
    return {"mensaje": "Imagen eliminada correctamente"}

@app.get("/listar-promociones/")
async def listar_promociones():
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix="promociones/")
    
    promociones = []
    for blob in blobs:
        if blob.name.endswith("/"):  # Evita directorios vacíos
            continue
        blob.make_public()
        promociones.append({
            "nombre_archivo": blob.name,
            "url": blob.public_url
        })

    return promociones


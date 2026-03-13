from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database

app = FastAPI(title="API Compartiendo Espacio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ESQUEMAS ---
class UserCreate(BaseModel):
    nombre_completo: str
    rut: str
    correo: str
    password: str
    patente: str
    rol: str

class UserLogin(BaseModel):
    correo: str
    password: str

# --- FUNCIÓN VALIDADORA DE RUT CHILENO (Algoritmo Módulo 11) ---
def validar_rut_chileno(rut: str) -> bool:
    rut = rut.replace(".", "").replace("-", "").upper()
    if len(rut) < 2: return False
    
    cuerpo = rut[:-1]
    dv_ingresado = rut[-1]

    try:
        if not cuerpo.isdigit(): return False
        
        # Lógica matemática oficial del Registro Civil
        suma = 0
        multiplo = 2
        for d in reversed(cuerpo):
            suma += int(d) * multiplo
            multiplo = multiplo + 1 if multiplo < 7 else 2
        
        dv_esperado = 11 - (suma % 11)
        if dv_esperado == 11: dv_esperado = '0'
        elif dv_esperado == 10: dv_esperado = 'K'
        else: dv_esperado = str(dv_esperado)

        return dv_ingresado == dv_esperado
    except:
        return False

# --- RUTAS DE LA API ---
@app.post("/api/registro")
def registrar_usuario(user: UserCreate, db: Session = Depends(database.get_db)):
    
    # 1. Validación Estricta del RUT
    if not validar_rut_chileno(user.rut):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El RUT ingresado no es válido. Verifica el formato (ej: 12345678-9)."
        )

    # 2. Verificamos si ya existe el usuario
    db_user = db.query(database.User).filter(
        (database.User.correo == user.correo) | (database.User.rut == user.rut)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="El correo o RUT ya están registrados.")
    
    # 3. Guardamos en la base de datos
    nuevo_usuario = database.User(
        nombre_completo=user.nombre_completo, rut=user.rut,
        correo=user.correo, password=user.password,
        patente=user.patente, rol=user.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Usuario creado exitosamente"}


@app.post("/api/login")
def iniciar_sesion(user: UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(database.User).filter(database.User.correo == user.correo).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    return {
        "mensaje": "Login exitoso", 
        "usuario": {"nombre": db_user.nombre_completo, "rol": db_user.rol, "patente": db_user.patente}
    }


@app.get("/api/estacionamientos")
def obtener_estacionamientos():
    return [
        {"id": 1, "name": "Mall Plaza Central", "lat": -33.4569, "lng": -70.6483, "totalSpots": 200, "occupiedSpots": 190, "owner": "Juan Pérez", "rating": "⭐ 4.8"},
        {"id": 2, "name": "Patio Central Providencia", "lat": -33.4250, "lng": -70.6150, "totalSpots": 50, "occupiedSpots": 15, "owner": "María Silva", "rating": "⭐ 4.9"},
        {"id": 3, "name": "Estacionamiento Norte Conchalí", "lat": -33.3830, "lng": -70.6750, "totalSpots": 100, "occupiedSpots": 70, "owner": "Carlos Ruiz", "rating": "⭐ 4.5"},
        {"id": 4, "name": "Aparcamiento Seguro Centro", "lat": -33.4400, "lng": -70.6500, "totalSpots": 30, "occupiedSpots": 10, "owner": "Empresa Park", "rating": "⭐ 4.2"}
    ]
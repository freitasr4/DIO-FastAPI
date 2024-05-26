# app/main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurações do SQLAlchemy
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definição do modelo Atleta
class Atleta(Base):
    __tablename__ = "atletas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cpf = Column(String, unique=True, index=True)

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Adicionar paginação à API
add_pagination(app)

# Query parameters nos endpoints
@app.get("/atletas/")
async def read_atletas(limit: int = 10, offset: int = 0, nome: str = None, cpf: str = None):
    db = SessionLocal()
    atletas_query = db.query(Atleta)
    if nome:
        atletas_query = atletas_query.filter(Atleta.nome == nome)
    if cpf:
        atletas_query = atletas_query.filter(Atleta.cpf == cpf)
    atletas = atletas_query.offset(offset).limit(limit).all()
    return atletas

# Customizar response de retorno de endpoints
class AtletaResponse(BaseModel):
    nome: str
    centro_treinamento: str
    categoria: str

@app.get("/atletas/all", response_model=Page[AtletaResponse])
async def read_all_atletas(limit: int = 10, offset: int = 0):
    db = SessionLocal()
    atletas = db.query(Atleta).offset(offset).limit(limit).all()
    atletas_response = []
    for atleta in atletas:
        atleta_response = AtletaResponse(
            nome=atleta.nome,
            centro_treinamento="Centro de Treinamento X",
            categoria="Categoria X"
        )
        atletas_response.append(atleta_response)
    return atletas_response

# Manipular exceção de integridade dos dados
@app.exception_handler(HTTPException)
async def integrity_error_handler(request, exc):
    if exc.status_code == 422 and "cpf" in exc.detail:
        raise HTTPException(status_code=303, detail=f"Já existe um atleta cadastrado com o cpf: {exc.detail['cpf']}")
    return exc


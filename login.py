from security import gerar_jwt
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from conectar import database

router = APIRouter(prefix="/contas")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Criar conta
@router.post("/cadastro/")
def criar_conta(sign_in: dict):
    username = sign_in["username"]
    password = sign_in["password"]
    nasce = sign_in["nasce"]
    email = sign_in["email"]
    db = database()
    conn = db.conectar()
    cursor = conn.cursor()

    # Verifica se o usuário já existe
    cursor.execute("SELECT id FROM usuarios WHERE nome = %s", (username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Usuário já existe")

    # Hash da senha
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Insere no banco
    cursor.execute("INSERT INTO usuarios (nome, senha, nascimento, email, tipo, ativo) VALUES (%s, %s, %s, %s, %s, %s)",
                   (username, hashed_password.decode(), nasce, email, "user", True))
    conn.commit()
    conn.close()

    return {"message": "Usuário cadastrado com sucesso"}

# Login
@router.post("/login/")
def login(log_in:dict):
    username = log_in["username"]
    password = log_in["password"]
    db = database()
    conn = db.conectar()
    cursor = conn.cursor()

    # Busca usuário no banco
    cursor.execute("SELECT id, senha, nome, email FROM usuarios WHERE (nome = %s OR email = %s) AND ativo = true", (username, username))
    user = cursor.fetchone()

    if not user or not bcrypt.checkpw(password.encode(), user[1].encode()):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")


    conn.close()


    # Gera JWT
    token = gerar_jwt(user[0], user[2])
    return {"access_token": token, "token_type": "bearer"}

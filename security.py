import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import datetime
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
# Gera um token JWT
# Credenciais principais
SECRET_KEY = "700896547"
ALGORITHM = "HS256"
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJyb2xlIjoiSm9cdTAwZTNvIiwiZXhwIjoxNzQxNzE3MjMwfQ.XGsEYqN_ILLHHBA_zAfEGqsRXHX4p-qP9BhIC3AWw_0"
# Tabelas
preferencias = "restricoes_usuario"
banco = "extratos"
dividas = "divida"
investimentos = "investimentos"
gastos = "gastos"
metas = "meta"
renda = "rendas"
pgto_meta = "meta_pgto"
pgto_gasto = "pagamentos"
pgto_divida = "divida_pgto"
def gerar_jwt(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)  # Expira em 5 horas
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Valida um token JWT
def verificar_jwt(token):
    try:
        # O jwt.decode() já lida com o token em string sem precisar de conversão manual
        dec = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar se as chaves necessárias estão no payload
        required_keys = ['user_id', 'role', 'exp']
        for key in required_keys:
            if key not in dec:
                raise ValueError(f"Falta a chave: {key}")

        return dec  # Retorna o payload decodificado
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except InvalidTokenError as e:
        print(f"Erro ao validar token: {str(e)}")  # Adiciona um print para debugar
        raise HTTPException(status_code=401, detail="Token inválido")
    except ValueError as e:
        print(f"Erro de chave ausente: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Middleware para validar token antes de acessar as rotas protegidas
# Função que valida o token apenas se fornecido
def verificar_usuario(token = None):
    if token:  # Se o token for fornecido
        return verificar_jwt(token)
    else:  # Se não for fornecido
        return {"message": "Token não fornecido ou inválido."}
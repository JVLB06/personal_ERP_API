from fastapi import APIRouter, Depends, HTTPException
from security import verificar_usuario, oauth2_scheme
import user

router = APIRouter(prefix="/api")

# Rota protegida
@router.post("/user/")
def dados(usuario: dict):
    user = verificar_usuario(usuario["access_token"])
    return {"message": "Acesso autorizado", "user": user}

@router.post("/protegido")
async def protegido(token: str = Depends(oauth2_scheme)):
    print(f"Token recebido: {token}")  # Verifica se o token está correto
    return {"token_recebido": token}

# Adicionar rotas dos caminhos seguros
router.include_router(user.router)

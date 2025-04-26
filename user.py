from fastapi import APIRouter, HTTPException, Depends
from conectar import database
import user_data

router = APIRouter(prefix="/user")
conection = database()

@router.put("/edit")
def editar_usuario(info: dict, id: int):
    conection.atualizar("usuarios", info, id)
    return conection.ler_um("usuarios", id)

@router.get("/obter")
def ler_usuario(id=0, nome=None, email=None):
    ret = None
    if nome != None:
        ret = conection.ler_um("usuarios", "nome", nome)
    if email != None:
        ret = conection.ler_um("usuarios", "email", email)
    if id != 0:
        ret = conection.ler_um("usuarios", "id", id)
    return ret

@router.get("/dados")
def dados_do_user():
    return {"dados": "Acesso aos dados específicos dos usuários"}

router.include_router(user_data.router)

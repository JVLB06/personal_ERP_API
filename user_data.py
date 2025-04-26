from fastapi import APIRouter, HTTPException, Request
from conectar import database
from security import verificar_usuario, oauth2_scheme
import thinking
from security import banco, investimentos, dividas, gastos, metas, renda, pgto_meta, pgto_gasto, pgto_divida
router = APIRouter(prefix="/user/dados")
conection = database()
# Registros padrão
def obter_id(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    return usuario["user_id"]
# renda .get .post .update .delete
@router.get("/renda/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(renda, "user_id", user_id)
@router.post("/renda/post")
def criar(novos_dados: dict):
    return conection.criar(renda, novos_dados, "id_renda")
@router.put("/renda/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(renda, novos_dados, id)
@router.delete("/renda/delete")
def delete(id):
    return conection.atualizar(renda, {"ativo":False}, id)

# extrato .get .post .update .delete
@router.get("/extrato/get")
def ler(request: Request):
    user_id = obter_id(request)
    return conection.ler_um(banco, "user_id", user_id)
@router.post("/extrato/post")
def criar(request: Request, novos_dados: dict, id:int):
    user_id = obter_id(request)
    create = conection.criar(banco, novos_dados, "id_lcto")
    conection.recalcular_saldo(banco, id, user_id)
    return create
@router.put("/extrato/put")
def atualizar(request: Request, novos_dados: dict, id: int):
    user_id = obter_id(request)
    update = conection.atualizar(banco, novos_dados, id) 
    conection.recalcular_saldo(banco, id, user_id)
    return update
@router.delete("/extrato/delete")
def delete(request: Request, dados: dict):
    id = dados["id"]
    user_id = obter_id(request)
    excluir = conection.atualizar(banco, {"ativo":False}, id)
    conection.recalcular_saldo(banco, id, user_id)
    return excluir

# metas .get .post .update .delete
@router.get("/metas/get")
def ler(request: Request):
    user_id = obter_id(request)
    return conection.ler_um(metas, "user_id", user_id)
@router.post("/metas/post")
def criar(novos_dados: dict):
    return conection.criar(metas, novos_dados, "id_meta")
@router.put("/metas/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(metas, novos_dados, id)
@router.delete("/metas/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(metas, {"ativo":False}, id)

# dívidas .get .post .update .delete
@router.get("/dividas/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(dividas, "user_id", user_id)
@router.post("/dividas/post")
def criar(novos_dados: dict):
    return conection.criar(dividas, novos_dados, "id_divida")
@router.put("/dividas/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(dividas, novos_dados, id)
@router.delete("/dividas/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(dividas, {"ativo":False}, id)

# investimentos .get .post .update .delete
@router.get("/investimentos/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(investimentos, "user_id", user_id)
@router.post("/investimentos/post")
def criar(novos_dados: dict):
    return conection.criar(investimentos, novos_dados, "id_invest")
@router.put("/investimentos/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(investimentos, novos_dados, id)
@router.delete("/investimentos/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(investimentos, {"ativo":False}, id)

# gastos .get .post .update .delete
@router.get("/gastos/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(gastos, "user_id", user_id)
@router.post("/gastos/post")
def criar(novos_dados: dict):
    return conection.criar(gastos, novos_dados, "id_gasto")
@router.put("/gastos/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(gastos, novos_dados, id)
@router.delete("/gastos/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(gastos, {"ativo":False}, id)

# Pagamentos

# Meta_pagamentos
@router.get("/pgto_meta/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(pgto_meta, "user_id", user_id)
@router.post("/pgto_meta/post")
def criar(novos_dados: dict):
    return conection.criar(pgto_meta, novos_dados, "id_pgto_meta")
@router.put("/pgto_meta/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(pgto_meta, novos_dados, id)
@router.delete("/pgto_meta/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(pgto_meta, {"ativo":False}, id)

# Gastos_pagamentos
@router.get("/pgto_gasto/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(pgto_gasto, "user_id", user_id)
@router.post("/pgto_gasto/post")
def criar(novos_dados: dict):
    return conection.criar(pgto_gasto, novos_dados, "id_gasto_geral")
@router.put("/pgto_gasto/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(pgto_gasto, novos_dados, id)
@router.delete("/pgto_gasto/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(pgto_gasto, {"ativo":False}, id)

# Divida_pagamentos
@router.get("/pgto_divida/get")
def ler(request: Request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(pgto_divida, "user_id", user_id)
@router.post("/pgto_divida/post")
def criar(novos_dados: dict):
    return conection.criar(pgto_divida, novos_dados, "id_pgto_divida")
@router.put("/pgto_divida/put")
def atualizar(novos_dados: dict, id: int):
    return conection.atualizar(pgto_divida, novos_dados, id)
@router.delete("/pgto_divida/delete")
def delete(dados: dict):
    id = dados["id"]
    return conection.atualizar(pgto_divida, {"ativo":False}, id)

# Machine thinking
router.include_router(thinking.router)

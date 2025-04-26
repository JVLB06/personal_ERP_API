from fastapi import APIRouter, HTTPException, Request
from conectar import database
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from security import preferencias, dividas, gastos, metas, renda, pgto_meta, pgto_gasto, pgto_divida, verificar_usuario

router = APIRouter(prefix="/user/dados/dados_processados")
conection = database()
usuario = "user_id"

# Insights
# Endividamento
def indice_endividamento(id):
    dividas_totais = conection.calcular_total_tabela(dividas, "valor", usuario, id, True)
    renda_total = conection.calcular_total_tabela(renda, "valor", usuario, id, True)
    calc = (dividas_totais / renda_total) * 100
    return round(calc, 2)
# Porcentagem dos gastos contra renda 
def relacao_gastos(id):
    gastos_fixos_min = conection.calcular_total_tabela_mais_param(gastos, "valor_min", usuario, id, "fix/var", "fix", True)
    gastos_fixos_max = conection.calcular_total_tabela_mais_param(gastos, "valor_max", usuario, id, "fix/var", "fix", True)
    gastos_var_min = conection.calcular_total_tabela_mais_param(gastos, "valor_min", usuario, id, "fix/var", "var", True)
    gastos_var_max = conection.calcular_total_tabela_mais_param(gastos, "valor_max", usuario, id, "fix/var", "var", True)
    renda_total = conection.calcular_total_tabela(renda, "valor", usuario, id, True)
    media_fix = (gastos_fixos_min + gastos_fixos_max)/2
    media_var = (gastos_var_min + gastos_var_max)/2
    pct_fix = media_fix/renda_total * 100
    pct_var = media_var/renda_total * 100
    return (round(pct_fix,2), round(pct_var, 2))
# Comparar gastos mensais com gastos previstos 
def gasto_mensal(data_fim, data_init, id):
    recomendacao_1 = 0
    recomendacao_2 = 0
    rec = ""
    gastos_mes = conection.calcular_total_tabela_por_data(pgto_gasto, "valor_min", usuario, id, data_fim, data_init, True)
    gastos_max = conection.calcular_total_tabela(gastos, "valor_max", usuario, id, True)
    gastos_min = conection.calcular_total_tabela(gastos, "valor_min", usuario, id, True)
    indice = gastos_mes/gastos_max
    indice_media = gastos_mes/((gastos_max+gastos_min)/2)
    if indice >= 1:
        recomendacao_1 = -1
    if indice_media >= 1:
        recomendacao_2 = -1
    if indice < 1:
        recomendacao_1 = 1
    if indice_media < 1:
        recomendacao_2 = 1
    if recomendacao_1+recomendacao_2 == 2:
        rec = "bom"
    if recomendacao_1+recomendacao_2 == 0:
        rec = "atenção"
    if recomendacao_1+recomendacao_2 == -2:
        rec = "ruim"
    return rec
# Comparar total de gastos com renda
def saude_renda(id):
    gastos_max = conection.calcular_total_tabela(gastos, "valor_max", usuario, id, True)
    gastos_min = conection.calcular_total_tabela(gastos, "valor_min", usuario, id, True)
    renda_total = conection.calcular_total_tabela(renda, "valor", usuario, id, True)
    ind = (((gastos_max+gastos_min)/2)/renda_total)*100
    if ind >= 70 and ind < 100:
        rec = 2
    if ind >= 100:
        rec = 3
    if ind < 70 and ind > 55:
        rec = 1
    if ind <= 55:
        rec = 0
    return (rec, round(ind, 2))
# Previsões
# Previsão quitação_dívida
def prever_quitacao(id):
    hoje = datetime.now()
    mes_3_atras = hoje - relativedelta(months=3)
    dividas_totais = conection.calcular_total_tabela(dividas, "valor", "id", id, True)
    pgtos_all = conection.calcular_total_tabela(pgto_divida, "valor", "divida_id", id, True)
    pgtos_3 = conection.calcular_total_tabela_por_data(pgto_divida, "valor", "divida_id", id, mes_3_atras, hoje, True)
    calc = (dividas_totais-pgtos_all)/((pgtos_3)/3)
    faltante = dividas_totais-pgtos_all
    mes_inteiro = int(calc)
    dias_extra = int((calc - mes_inteiro)*30)
    data = hoje + relativedelta(months=mes_inteiro) + timedelta(days=dias_extra)
    return (data, round(faltante, 2))
# Previsão cumprimento meta
def prever_meta(id):
    hoje = datetime.now()
    mes_3_atras = hoje - relativedelta(months=3)
    meta_total = conection.calcular_total_tabela(metas, "valor", "id", id, True)
    pgtos_all = conection.calcular_total_tabela(pgto_meta, "valor", "meta_id", id, True)
    pgtos_3 = conection.calcular_total_tabela_por_data(pgto_meta, "valor", "meta_id", id, mes_3_atras, hoje, True)
    calc = (meta_total-pgtos_all)/((pgtos_3)/3)
    faltante = meta_total-pgtos_all
    mes_inteiro = int(calc)
    dias_extra = int((calc - mes_inteiro)*30)
    data = hoje + relativedelta(months=mes_inteiro) + timedelta(days=dias_extra)
    progress = meta_total/pgtos_all * 100
    conection.atualizar(metas, {"progresso":round(progress, 2)}, id)
    return (data, round(faltante, 2), progress)

def avaliar_reducoes(id_usuario, ref_pri):
    """
    Gera sugestões de redução de gastos com base na análise dos dados.
    """
    sugestoes = []
    try:
        gastos = conection.buscar_gastos_reduziveis(id_usuario)
        for gasto in gastos:
            id_gasto, descricao, vlr_min, vlr_max, prioridade = gasto["gasto_id"], gasto["nome"], gasto["vlr_min"], gasto["vlr_max"], gasto["prioridade"]
            valor = (vlr_min + vlr_max)/2
            # Verificar se está bloqueado pelo usuário
            if conection.verificar_restricoes(id_usuario, id_gasto):
                continue  # Ignorar gastos bloqueados
            # Verificar se já há uma redução planejada
            reducao = conection.verificar_reducao_prevista(id_usuario, id_gasto)
            if prioridade <= ref_pri:
                if reducao["excluir"]:
                    sugestoes.append(
                        f"Você já tem planejado a exclusão do gasto com '{descricao}'. ")
                if reducao["reduzir"]:
                    sugestoes.append(
                        f"Você já tem uma redução planejada para '{descricao}'. "
                        f"Podemos reduzir de R${valor:.2f} para R${valor*80/100:.2f}.")
                else:
                    sugestoes.append(
                        f"Considere reduzir o gasto com '{descricao}', atualmente em R${valor:.2f}. "
                        "Este gasto tem baixa prioridade e pode ser ajustado para melhorar sua saúde financeira.")
    finally:
        print("Sugestões processadas")

    return sugestoes


def gerar_sugestoes(id_user, dados):
    sugestoes = []
    reducao = 0

    # Análise do endividamento
    if dados["endividamento"] >= 50:
        sugestoes.append("Seu índice de endividamento está alto. Priorize pagar dívidas antes de novos gastos.")
    elif dados["endividamento"] > 30:
        sugestoes.append("Seu endividamento está moderado. Mantenha o controle para evitar problemas futuros.")

    # Análise da relação de gastos
    if dados["rel_gasto_fix"] > 40:
        sugestoes.append("Seus gastos fixos estão altos. Tente renegociar contratos ou reduzir assinaturas.")
    if dados["rel_gasto_var"] > 30:
        sugestoes.append("Seus gastos variáveis são elevados. Avalie onde pode economizar no dia a dia.")

    # Saúde financeira
    if dados["saude_nota"] == 3:
        sugestoes.append("Sua saúde financeira está comprometida. Revise suas despesas urgentemente.")
        reducao = 5
    elif dados["saude_nota"] == 2:
        sugestoes.append("Atenção! Seus gastos estão próximos do limite saudável da sua renda.")
        reducao = 4
    elif dados["saude_nota"] == 1:
        sugestoes.append("Seus gastos estão saudáveis, pode trabalhar confortávelmente com essa margem")
    elif dados["saude_nota"] == 0:
        sugestoes.append("Sua saúde financeira está perfeita, pode destinar esse dinheiro para investimentos e lazer, confortavelmente")

    # Controle do gasto mensal
    if "bom" in dados["gasto_mensal"].lower():
        sugestoes.append("Parabéns! Seu controle financeiro está adequado este mês.")
    elif "atenção" in dados["gasto_mensal"].lower():
        sugestoes.append("Você está gastando perto do seu limite. Redobre a atenção nos próximos meses.")
    elif "ruim" in dados["gasto_mensal"].lower():
        sugestoes.append("Seus gastos foram muito altos este mês. É essencial rever seu orçamento.")

    # Previsão de quitação de dívidas e metas
    previsoes = []
    for divida in dados["prev_div"]:
        if divida[1] > 5000:  # Exemplo: dívida alta
            previsoes.append(f"Você ainda deve R${divida[1]:,.2f}. Tente aumentar o pagamento mensal para reduzir juros.")
    
    for meta in dados["prev_meta"]:
        if meta[2] < 50:  # Exemplo: progresso menor que 50%
            previsoes.append(f"Seu progresso na meta está em {meta[2]:.2f}%. Tente contribuir mais para alcançar seus objetivos.")
    sugestoes.append(previsoes)
    if reducao != 0:
        sugestoes.append(avaliar_reducoes(id_user, reducao))
    return sugestoes



@router.get("/todos_os_inidicadores")
# dados={"id_usuario":0,"quantidade_metas":0,"quantidade_dividas":0,"id_meta":[0], "id_divida":[0]}
def todos_os_dados(request: Request):
    # Geração de dicionário para análise
    # Declaração de variáveis
    id_div = []
    id_meta = []
    # Obtenção do id do usuário
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    # Leitura de tabelas para obtenção de informações básicas
    divs = conection.ler_um(metas, "user_id", user_id)["listagem"]
    meta = conection.ler_um(dividas, "user_id", user_id)["listagem"]
    for ident in divs:
        id_div.append(ident[0])
    for ident in meta:
        id_meta.append(ident[0])
    # Inclusão das informações no dicionário principal
    dados = {"id_usuario":user_id,
             "quantidade_metas": divs,
             "quantidade_dividas": meta,
             "id_meta":id_div,
             "id_divida":id_meta}
    # Geração de indíces em variáveis específicas
    divida = indice_endividamento(dados["id_usuario"])
    rlg = relacao_gastos(dados["id_usuario"])
    gasto_fix = rlg[0]
    gasto_var = rlg[1]
    sr = saude_renda(dados["id_usuario"])
    nota_saude = sr[0]
    porcentagem_saude = sr[1]
    valor_mes = gasto_mensal(dados["id_usuario"])
    # Formatação de previsões e índices compostos
    prev_div = []
    prev_meta = []
    for i in range(dados["quantidade_metas"]):
        prev_meta.append(prever_meta(dados["id_meta"][i]))
    for i in range(dados["quantidade_dividas"]):
        prev_div.append(prever_quitacao(dados["id_divida"][i]))
    # Geração do primeiro dicionário de índices
    resultado = {"endividamento":divida, 
    "rel_gasto_fix":gasto_fix, 
    "rel_gasto_var":gasto_var, 
    "saude_nota":nota_saude, 
    "saude_pct":porcentagem_saude,
    "gasto_mensal":valor_mes, 
    "prev_div":prev_div, 
    "prev_meta":prev_meta}
    # Geração de sugestões com base nos índices previamente gerados
    sugest = gerar_sugestoes(int(dados["id_usuario"]), resultado)
    # Retorno do dicionário principal com os índices e sugestões respectivas
    return {"indicadores":resultado, "sugestoes":sugest}

# Processamento das preferências
@router.post("/criar_preferencias")
def incluir_preferencias(request: Request, dados:dict):
     # Obtenção do id do usuário
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    dados["user_id"] = user_id
    # informações: id_usuario, id_preferencia, id do gasto, excluir, reduzir, bloqueado, ativo
    return conection.criar(preferencias, dados)

@router.put("/atualizar_preferencias")
def atualizar_preferencias(request: Request, dados:dict):
    # Obtenção do id do usuário
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    # Obtenção de ID do dado
    id_dado = dados["id_dado"]
    dados["user_id"] = user_id
    return conection.atualizar(preferencias, dados, id_dado)
@router.get("/ler_preferencias")
def ler_preferencias(request: Request):
    # Obtenção do id do usuário
    auth_header = request.headers.get("Authorization")
    token = auth_header.split("Bearer ")[1]
    usuario = verificar_usuario(token)
    user_id = usuario["user_id"]
    return conection.ler_um(preferencias, "user_id", user_id)

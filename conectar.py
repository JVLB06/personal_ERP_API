class database():
    def __init__(self):
        self.db = "erp"
        self.user = "postgres"
        self.senha = "2006"
        self.host = "192.168.0.200"
        self.port = 5433
        pass
    def conectar(self):
        import psycopg2
        return psycopg2.connect(
            dbname=self.db,
            user=self.user,
            password=self.senha,
            host=self.host, 
            port=self.port)
    def criar(self, tabela, valores: dict):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {tabela} ({valores.items()}) VALUES ({valores.keys()}) RETURNING id;")
        noticia_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return {"novo": noticia_id}
    def ler_um(self, tabela, tipo, id, state=True):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {tabela} WHERE {tipo}= %s AND ativo= %s;", (id, state))
        leitura = cur.fetchall()
        conn.close()
        return {"listagem": leitura}
    def ler_tudo(self, tabela, state=True):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {tabela} WHERE ativo= %s;", (state))
        leitura = cur.fetchall()
        conn.close()
        return {"listagem": leitura}
    def atualizar(self, tabela, valores: dict, id):
        conn = self.conectar()
        cur = conn.cursor()
        set_clause = ", ".join([f"{key} = %s" for key in valores.keys()])
        query = f"UPDATE {tabela} SET {set_clause} WHERE id = %s;"
        cur.execute(query, tuple(valores.values())+(id,))
        conn.commit()
        conn.close()
    def recalcular_saldo(self, tabela, id, user):
        conn = self.conectar()
        cur = conn.cursor()
        # Recalculando o saldo de todos os lançamentos a partir do id
        query = f"""UPDATE {tabela} SET saldo = (SELECT SUM(valor) FROM {tabela} WHERE id <= %s AND ativo = TRUE AND user_id = %s) WHERE id = %s;"""
        cur.execute(query, (id, user, id))
        conn.commit()
        conn.close()
    def calcular_total_tabela(self, tabela, valor, tipo, id, state=True):
        """
        Calcula a soma de um campo específico para os registros ativos de uma tabela.

        Parâmetros:
        - tabela (str): Nome da tabela no banco de dados.
        - valor (str): Nome da coluna cujo valor será somado.
        - tipo (str): Coluna de referência para a informação (user_id)
        - id (int): Valor do critério de filtragem na coluna especificada por `tipo`.
        - state (bool, opcional): Filtra registros ativos (`True`) ou inativos (`False`). Padrão: `True`.

        Retorno:
        - dict: Dicionário contendo a soma dos valores encontrados, no formato `{valor: soma}`.
        """
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(f"SELECT SUM({valor}) FROM {tabela} WHERE {tipo}= %s AND ativo= %s;", (id, state))
        leitura = cur.fetchone()
        conn.close()
        return {valor: leitura[0] if leitura[0] is not None else 0}
    def calcular_total_tabela_mais_param(self, tabela, valor, tipo, id, parametro_add, vlr_add, state=True):
        """
        Calcula a soma de um campo específico para os registros ativos de uma tabela.

        Parâmetros:
        - tabela (str): Nome da tabela no banco de dados.
        - valor (str): Nome da coluna cujo valor será somado.
        - tipo (str): Coluna de referência para a informação (user_id)
        - id (int): Valor do critério de filtragem na coluna especificada por `tipo`.
        - parametro_add(str): Parâmetro adicional para verificação.
        - vlr_add(str): Valor para o parâmetro adicional.
        - state (bool, opcional): Filtra registros ativos (`True`) ou inativos (`False`). Padrão: `True`.

        Retorno:
        - dict: Dicionário contendo a soma dos valores encontrados, no formato `{valor: soma}`.
        """
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(f"SELECT SUM({valor}) FROM {tabela} WHERE {tipo}= %s AND ativo= %s AND {parametro_add} = %s;", (id, state, vlr_add))
        leitura = cur.fetchone()
        conn.close()
        return {valor: leitura[0] if leitura[0] is not None else 0}
    def calcular_total_tabela_por_data(self, tabela, valor, tipo, id, data_init, data_fim, state=True):
        """
        Calcula a soma de um campo específico para os registros ativos de uma tabela.

        Parâmetros:
        - tabela (str): Nome da tabela no banco de dados.
        - valor (str): Nome da coluna cujo valor será somado.
        - tipo (str): Coluna de referência para a informação (user_id)
        - id (int): Valor do critério de filtragem na coluna especificada por `tipo`.
        - parametro_add(str): Parâmetro adicional para verificação.
        - vlr_add(str): Valor para o parâmetro adicional.
        - state (bool, opcional): Filtra registros ativos (`True`) ou inativos (`False`). Padrão: `True`.

        Retorno:
        - dict: Dicionário contendo a soma dos valores encontrados, no formato `{valor: soma}`.
        """
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(f"SELECT SUM({valor}) FROM {tabela} WHERE {tipo}= %s AND ativo= %s AND data %s BETWEEN %s;", (id, state, data_init, data_fim))
        leitura = cur.fetchone()
        conn.close()
        return {valor: leitura[0] if leitura[0] is not None else 0}
    
    def buscar_gastos_reduziveis(self, id_usuario):
        """
        Busca os gastos de menor prioridade que podem ser reduzidos ou cortados.
        """
        conn = self.conectar()
        cur = conn.cursor()
        query = """
            SELECT gasto_id, nome, vlr_min, vlr_max, prioridade
            FROM gastos
            WHERE user_id = %s
            ORDER BY prioridade ASC, (vlr_min+vlr_max)/2 DESC
            LIMIT 5;"""
        cur.execute(query, (id_usuario,))
        conn.close()
        return cur.fetchall()


    def verificar_restricoes(self, id_usuario, id_gasto):
        """
        Verifica se um gasto foi bloqueado para corte pelo usuário.
        """
        conn = self.conectar()
        cur = conn.cursor()
        query = """
            SELECT bloqueado
            FROM restricoes_usuario
            WHERE user_id = %s AND gasto_id = %s;
        """
        cur.execute(query, (id_usuario, id_gasto))
        resultado = cur.fetchone()
        conn.close()
        return resultado[0] if resultado else False

    def verificar_reducao_prevista(self, id_usuario, id_gasto):
        """
        Verifica se já existe uma previsão de redução para o gasto.
        """
        from psycopg2.extras import DictCursor 
        conn = self.conectar()
        query = """
            SELECT excluir, reduzir
            FROM restricoes_usuario
            WHERE user_id = %s AND gasto_id = %s AND bloqueado = FALSE;
        """
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (id_usuario, id_gasto))
            return cur.fetchone()  # Retorna um dicionário ou None

import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd


class EstatisticasCopaDoRei:
    def __init__(self, url, headers, db_name="dados_copaRei.db"):
        self.url = url
        self.headers = headers
        self.db_name = db_name
        self.soup = self._obter_html()

    def _obter_html(self):
        """Obtém o conteúdo HTML da página."""
        response = requests.get(self.url, headers=self.headers)
        return BeautifulSoup(response.content, "html.parser")

    def _criar_tabela(self):
        """Cria a tabela no banco de dados SQLite."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jogadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    posicao TEXT,
                    jogos INTEGER,
                    gols INTEGER,
                    assistencias INTEGER,
                    amarelos INTEGER,
                    vermelhos INTEGER,
                    UNIQUE (nome, posicao, jogos, gols, assistencias, amarelos, vermelhos)
                )
            """)
            conn.commit()

    def _inserir_dados(self, dados):
        """Insere os dados coletados no banco de dados."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR IGNORE INTO jogadores (nome, posicao, jogos, gols, assistencias, amarelos, vermelhos)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dados)
            conn.commit()

    def _processar_dados(self):
        """Processa os dados do plantel e organiza as informações relevantes."""
        plantel = self.soup.select('table[class="items"] tbody tr')
        jogadores_data = []

        for jogador in plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]

            if len(dados_jogador) >= 12:
                nome = dados_jogador[1]
                sobrenome = dados_jogador[2].split()[-1].strip()
                posicao = dados_jogador[3]
                jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
                gols = int(dados_jogador[7].split()[0]) if dados_jogador[7].split()[0].isdigit() else 0
                assistencias = int(dados_jogador[8].split()[0]) if dados_jogador[8].split()[0].isdigit() else 0
                amarelos = int(dados_jogador[9].split()[0]) if dados_jogador[9].split()[0].isdigit() else 0
                vermelhos = int(dados_jogador[11].split()[0]) if dados_jogador[11].split()[0].isdigit() else 0

                # Corrigindo casos específicos
                if dados_jogador[0] == "11":
                    nome = "Rodrygo"
                    sobrenome = ""
                if dados_jogador[1] == "JoseluJoseluCentroavante":
                    nome = "Joselu"
                    sobrenome = ""

                jogadores_data.append([f"{nome.split()[0]} {sobrenome}", posicao, jogos, gols, assistencias, amarelos, vermelhos])

        return jogadores_data

    def salvar_dados(self):
        """Processa e salva os dados no banco de dados."""
        self._criar_tabela()
        dados = self._processar_dados()
        self._inserir_dados(dados)

    def consultar_dados(self, tipo):
        """Consulta dados do banco de dados e exibe como DataFrame."""
        colunas = {
            "gols": "gols",
            "assistencias": "assistencias",
            "amarelos": "amarelos",
            "vermelhos": "vermelhos"
        }

        if tipo not in colunas:
            print("Tipo inválido! Escolha entre: gols, assistencias, amarelos, vermelhos.")
            return

        with sqlite3.connect(self.db_name) as conn:
            query = f"""
                SELECT nome, posicao, jogos, {colunas[tipo]} AS estatistica
                FROM jogadores
                ORDER BY estatistica DESC
            """
            df = pd.read_sql_query(query, conn)

        print(f"\n{tipo.capitalize()} do Clube - Copa do Rei 2023/24\n")
        print(df.to_string(index=False))


# Configurações
url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=CDR%262023"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# Uso da Classe
estatisticas = EstatisticasCopaDoRei(url, headers)

# Processar e salvar dados no banco de dados
estatisticas.salvar_dados()

# Consultar e exibir dados do banco
estatisticas.consultar_dados("gols")
estatisticas.consultar_dados("assistencias")
estatisticas.consultar_dados("amarelos")
estatisticas.consultar_dados("vermelhos")

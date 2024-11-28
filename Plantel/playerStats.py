import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

class BancoDeDados:
    """Gerencia a interação com o banco de dados SQLite."""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria a tabela para armazenar os dados do plantel."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS plantel (
            numero TEXT,
            nome TEXT,
            posicao TEXT,
            no_plantel TEXT,
            jogos TEXT,
            gols TEXT,
            assistencias TEXT,
            amarelos TEXT,
            expulsao_duplo_amarelo TEXT,
            vermelhos TEXT,
            ppj TEXT,
            minutos_jogados TEXT,
            UNIQUE(numero, nome)  -- Evita duplicatas
        )
        """)
        self.conn.commit()

    def inserir_jogadores(self, dados):
        """Insere os dados no banco, ignorando duplicatas."""
        self.cursor.executemany("""
            INSERT OR IGNORE INTO plantel (numero, nome, posicao, no_plantel, jogos, gols, assistencias, amarelos, expulsao_duplo_amarelo, vermelhos, ppj, minutos_jogados)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, dados)
        self.conn.commit()

    def consultar_jogadores(self):
        """Retorna os dados armazenados no banco."""
        query = "SELECT * FROM plantel"
        return pd.read_sql_query(query, self.conn)

    def fechar(self):
        """Fecha a conexão com o banco."""
        self.conn.close()


class ScraperTransfermarkt:
    """Responsável por realizar o scraping dos dados do Transfermarkt."""
    
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def coletar_dados(self):
        """Coleta os dados do plantel do site Transfermarkt."""
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Lista para armazenar os dados dos jogadores
        jogadores_data = []

        # Coletando dados do plantel
        plantel = soup.select('table[class="items"] tbody tr')
        for jogador in plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]

            if len(dados_jogador) >= 12:  # Verifica se há dados suficientes
                num = dados_jogador[0]
                nome = dados_jogador[1].split()[0]  # Nome curto
                sobreNome = dados_jogador[2].split()[-1].strip()  # Nome curto
                posicao = dados_jogador[3]
                no_plantel = dados_jogador[5]
                jogos = dados_jogador[6]
                gols = dados_jogador[7]
                assistencias = dados_jogador[8]
                amarelos = dados_jogador[9]
                expulsao_duplo_amarelo = dados_jogador[10]
                vermelhos = dados_jogador[11]
                ppj = dados_jogador[12]
                minutos_jogados = dados_jogador[13]

                # Correção para casos específicos de nomes de jogadores
                if dados_jogador[0] == "11":
                    nome = "Rodrygo"
                    sobreNome = ""
                if dados_jogador[1] == "JoseluJoseluCentroavante":
                    nome = "Joselu"
                    sobreNome = ""

                jogadores_data.append([
                    num, f"{nome} {sobreNome}", posicao, no_plantel, jogos, gols, assistencias, 
                    amarelos, expulsao_duplo_amarelo, vermelhos, ppj, minutos_jogados
                ])

        return jogadores_data


class EstatisticasManager:
    """Gerencia o scraping, armazenamento e exibição de dados."""
    
    def __init__(self, url, headers, db_name):
        self.scraper = ScraperTransfermarkt(url, headers)
        self.banco = BancoDeDados(db_name)

    def executar(self):
        """Executa o processo completo de scraping, armazenamento e exibição."""
        # Coleta os dados
        dados_jogadores = self.scraper.coletar_dados()

        # Insere os dados no banco
        self.banco.inserir_jogadores(dados_jogadores)

        # Exibe os dados armazenados no banco
        self._exibir_resultados()

        # Fecha a conexão com o banco
        self.banco.fechar()

    def _exibir_resultados(self):
        """Exibe os dados do banco."""
        print("\n\n\nEstatísticas do Plantel - Temporada 2023/24\n")
        df_jogadores = self.banco.consultar_jogadores()
        print(df_jogadores.to_string(index=False))


# Configurações
URL = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/reldata/%262023/plus/1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
DB_NAME = "estatisticas_real_madrid.db"

# Executando o programa
manager = EstatisticasManager(URL, HEADERS, DB_NAME)
manager.executar()

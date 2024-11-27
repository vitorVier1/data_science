import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

class BancoDeDados:
    """Classe para gerenciar a interação com o banco de dados SQLite."""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria a tabela para armazenar os dados dos jogadores."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS plantel (
            numero TEXT,
            nome TEXT,
            posicao TEXT,
            altura TEXT,
            pe TEXT,
            idade TEXT,
            nacionalidade TEXT,
            valor TEXT,
            UNIQUE(numero, nome)  -- Garante que não haverá duplicatas baseadas em número e nome
        )
        """)
        self.conn.commit()

    def inserir_jogadores(self, dados):
        """Insere os dados dos jogadores no banco de dados, ignorando duplicatas."""    
        self.cursor.executemany("""
            INSERT OR IGNORE INTO plantel (numero, nome, posicao, altura, pe, idade, nacionalidade, valor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, dados)
        self.conn.commit()

    def consultar_jogadores(self):
        """Consulta os dados dos jogadores no banco de dados."""    
        query = "SELECT * FROM plantel"
        return pd.read_sql_query(query, self.conn)

    def fechar(self):
        """Fecha a conexão com o banco de dados."""    
        self.conn.close()


class ScraperTransfermarkt:
    """Classe responsável por realizar o scraping dos dados do Transfermarkt."""
    
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def coletar_dados(self):
        """Coleta os dados do plantel do site Transfermarkt."""
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Coletando Nome da Equipe
        team_name = soup.select_one('h1[class="data-header__headline-wrapper data-header__headline-wrapper--oswald"]').text.split('\n')[-1].strip()
        print(f"\n{team_name} | Temporada 2023/24\n")

        # Coletando dados do Plantel da Equipe
        plantel_madrid = soup.select_one('h2[class="content-box-headline"]').text.split('\n')[1].strip()
        print(f"{plantel_madrid} 2023/24")

        # Lista para armazenar os dados dos jogadores
        jogadores_data = []

        # Coletando dados do plantel
        plantel = soup.select('table[class="items"] tbody tr')
        for jogador in plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]

            if len(dados_jogador) >= 8:  # Verifica se existem dados suficientes
                num = dados_jogador[0]
                nome = dados_jogador[1]
                sobreNome = dados_jogador[2].split()[-1].strip()
                posicao = dados_jogador[3]
                altura = dados_jogador[5]
                pe = dados_jogador[6] if len(dados_jogador) > 7 else "-"  # Pode não haver dados cadastrados
                idade = dados_jogador[4].split()[1]

                # Coletando as nacionalidades a partir das imagens
                nacionalidade_imgs = jogador.select('td img[alt]')
                if len(nacionalidade_imgs) > 1:
                    nacionalidade = nacionalidade_imgs[1]['alt']
                    if len(nacionalidade_imgs) > 4:
                        nacionalidade2 = nacionalidade_imgs[2]['alt']
                        nacionalidade = f"{nacionalidade}/{nacionalidade2}"
                    else:
                        nacionalidade = nacionalidade_imgs[1]['alt']
                else:
                    nacionalidade = ""

                # Ajustes específicos para Joselu e Rodrygo
                if "Joselu" in nome:
                    nacionalidade = ""
                    nome = "Joselu"
                    sobreNome = ""
                if num == "11":
                    nome = "Rodrygo"
                    sobreNome = ""

                valor = dados_jogador[8] if len(dados_jogador) > 8 else "-"  # Pode não haver dados cadastrados

                # Adicionando os dados à lista de jogadores
                jogadores_data.append([num, f"{nome.split()[0]} {sobreNome}", posicao, altura, pe, idade, nacionalidade, valor])

        return jogadores_data


class EstatisticasManager:
    """Classe que gerencia o processo de scraping, armazenamento e exibição de dados."""
    
    def __init__(self, url, headers, db_name):
        self.scraper = ScraperTransfermarkt(url, headers)
        self.banco = BancoDeDados(db_name)

    def executar(self):
        """Executa o processo completo: coleta, armazena e exibe os dados."""    
        # Coletando os dados
        dados_jogadores = self.scraper.coletar_dados()

        # Inserindo no banco de dados
        self.banco.inserir_jogadores(dados_jogadores)

        # Exibindo os dados coletados do banco
        self._exibir_resultados()

        # Fechando a conexão com o banco
        self.banco.fechar()

    def _exibir_resultados(self):
        """Exibe os dados dos jogadores coletados do banco de dados."""    
        print("\n\n\nPlantel Real Madrid - Temporada 2023/24\n")
        
        # Consultando os dados do banco
        df_jogadores = self.banco.consultar_jogadores()

        # Exibindo os dados utilizando pandas DataFrame
        print(df_jogadores.to_string(index=False))


# Configurações
URL = "https://www.transfermarkt.com.br/real-madrid-cf/kader/verein/418/saison_id/2023/plus/1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
DB_NAME = "plantel_real_madrid.db"

# Executando o programa
manager = EstatisticasManager(URL, HEADERS, DB_NAME)
manager.executar()

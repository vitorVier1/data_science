import re
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

url = "https://www.transfermarkt.com.br/real-madrid/startseite/verein/418/saison_id/2023"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers = headers)

soup = BeautifulSoup(response.content, "html.parser")

print("\nBalanço da Temporada 2023/24\n")

print("Competições")
# Criando tabela
table = PrettyTable()
table.field_names = ["Competição", "Resultado"]

balanco = soup.select('div[class="box saison-bilanz"] table tbody')
for comp in balanco:
    dados_comp = [tr.text.strip() for tr in comp.find_all('tr') if tr.text.strip()]
    
    if len(dados_comp) >= 4:  # Verifica se existem dados suficientes
        copaRei = dados_comp[0].split()[3]
        champions = dados_comp[1].split()[2] if len(dados_comp) > 4 else "Campeão"
        laLiga = dados_comp[2] if len(dados_comp) > 4 else "Campeão"
        superCopa = dados_comp[3] if len(dados_comp) > 4 else "Campeão"
        
        # Adicionando dados à tabela
        table.add_row(["Copa do Rei", copaRei])
        table.add_row(["Liga dos Campeões", champions])
        table.add_row(["La Liga", laLiga])
        table.add_row(["Super Copa", superCopa])

# Exibindo tabela
print(table)

print("\n---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

print("Jogos da Temporada")
table_jogos = PrettyTable()
table_jogos.field_names = ["Jogos", "V", "E", "D"]

jogos = soup.select('div[class="box box-slider"] ul li div[class="container-content"] div[class="container-match-record"] table tr')
for stats in jogos:
    jogos_stats = [td.text.strip() for td in stats.find_all('td') if td.text.strip()]
    
    if len(jogos_stats) >= 4:  # Verifica se existem dados suficientes
        jogos = jogos_stats[0].split('Jogos')[0]
        wins = jogos_stats[1].split('V')[0]
        draws = jogos_stats[2].split('E')[0]
        loses = jogos_stats[3].split('D')[0]
        
        # Adicionando dados à tabela
        table_jogos.add_row([jogos, wins, draws, loses])
print(table_jogos)
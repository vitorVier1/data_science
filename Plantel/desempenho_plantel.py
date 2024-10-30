import re
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/reldata/%262023/plus/1"
team_id = url.split('/')[-1]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers = headers)

soup = BeautifulSoup(response.content, "html.parser")

print("Dados de Desempenho da Equipe na Temporada 2023/24")
# Criando tabela
table = PrettyTable()
table.field_names = ["N°", "Jogador", "Posição", "No Plantel", "Jogos", "Gols", "Assistencias", "Cartões Amarelos", "Expulsões (Dois Amarelos)", "Cartões Vermelhos", "PPJ", "Minutos Jogados"]

# Coletando dados do plantel
plantel = soup.select('table[class="items"] tbody tr')
for jogador in plantel:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 12:  # Verifica se existem dados suficientes
        num = dados_jogador[0]
        nome = dados_jogador[1]
        sobreNome = dados_jogador[2].split()[-1].strip()
        posicao = dados_jogador[3]
        noPlantel = dados_jogador[5][0]
        jogos = dados_jogador[6] if len(dados_jogador) > 7 else "-"  # Podem não haver dados cadastrados
        gols = dados_jogador[7].split()[0]
        ass = dados_jogador[8].split()[0]
        amarelos = dados_jogador[9].split()[0]
        amarelos2 = dados_jogador[10].split()[0]
        vermelhos = dados_jogador[11].split()[0]
        ppj = dados_jogador[14].split()[0]
        minJogados = dados_jogador[15].split()[0]

        if dados_jogador[0] == "11":
            nome = "Rodrygo"
            sobreNome = ""
        if dados_jogador[1] == "JoseluJoseluCentroavante":
            nome = "Joselu"
            sobreNome = ""
        
        # Adicionando dados à tabela
        table.add_row([num, nome.split()[0] + " " + sobreNome, posicao, noPlantel, jogos, gols, ass, amarelos, amarelos2, vermelhos, ppj, minJogados])

# Exibindo tabela
print(table)
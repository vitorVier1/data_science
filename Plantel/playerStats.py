import re
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import pandas as pd

url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=%262023"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers = headers)

soup = BeautifulSoup(response.content, "html.parser")

jogadores_data = []

# Coletando dados do plantel
plantel = soup.select('table[class="items"] tbody tr')
for jogador in plantel:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 12:  # Verifica se existem dados suficientes
        nome = dados_jogador[1]
        sobreNome = dados_jogador[2].split()[-1].strip()
        posicao = dados_jogador[3]

        jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
        gols = int(dados_jogador[7].split()[0]) if dados_jogador[7].split()[0].isdigit() else 0

        if dados_jogador[0] == "11":
            nome = "Rodrygo"
            sobreNome = ""
        if dados_jogador[1] == "JoseluJoseluCentroavante":
            nome = "Joselu"
            sobreNome = ""
        
        jogadores_data.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, gols])

# Criando o DataFrame para ordenar
df_jogadores = pd.DataFrame(jogadores_data, columns=["Jogador", "Posição", "Jogos", "Gols"])

# Ordenando por gols em ordem decrescente
df_jogadores = df_jogadores.sort_values(by="Gols", ascending=False).reset_index(drop=True)

# Exibindo a tabela
print("\nArtilharia da Temporada 2023/24\n")
print(df_jogadores.to_string(index=False))

print("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")

jogadores_data_ass = []

# Coletando dados do plantel
for jogador_ass in plantel:
    dados_jogador = [td.text.strip() for td in jogador_ass.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 12:  # Verifica se existem dados suficientes
        nome = dados_jogador[1]
        sobreNome = dados_jogador[2].split()[-1].strip()
        posicao = dados_jogador[3]

        jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
        ass = int(dados_jogador[8].split()[0]) if dados_jogador[8].split()[0].isdigit() else 0

        if dados_jogador[0] == "11":
            nome = "Rodrygo"
            sobreNome = ""
        if dados_jogador[1] == "JoseluJoseluCentroavante":
            nome = "Joselu"
            sobreNome = ""
        
        jogadores_data_ass.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, ass])

# Criando o DataFrame para ordenar
df_jogadores_ass = pd.DataFrame(jogadores_data_ass, columns=["Jogador", "Posição", "Jogos", "Assistencias"])

# Ordenando por ass em ordem decrescente
df_jogadores_ass = df_jogadores_ass.sort_values(by="Assistencias", ascending=False).reset_index(drop=True)

# Exibindo a tabela
print("\n\n\nMaiores Assistentes da Temporada 2023/24\n")
print(df_jogadores_ass.to_string(index=False))

print("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")

jogadores_data_yellow = []

# Coletando dados do plantel
for jogador_yellow in plantel:
    dados_jogador = [td.text.strip() for td in jogador_yellow.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 12:  # Verifica se existem dados suficientes
        nome = dados_jogador[1]
        sobreNome = dados_jogador[2].split()[-1].strip()
        posicao = dados_jogador[3]

        jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
        amarelos = int(dados_jogador[9].split()[0]) if dados_jogador[9].split()[0].isdigit() else 0

        if dados_jogador[0] == "11":
            nome = "Rodrygo"
            sobreNome = ""
        if dados_jogador[1] == "JoseluJoseluCentroavante":
            nome = "Joselu"
            sobreNome = ""
        
        jogadores_data_yellow.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, amarelos])

# Criando o DataFrame para ordenar
df_jogadores_yellow = pd.DataFrame(jogadores_data_yellow, columns=["Jogador", "Posição", "Jogos", "Cartões Amarelos"])

# Ordenando por yellow em ordem decrescente
df_jogadores_yellow = df_jogadores_yellow.sort_values(by="Cartões Amarelos", ascending=False).reset_index(drop=True)

# Exibindo a tabela
print("\n\n\nCartões Amarelos na Temporada 2023/24\n")
print(df_jogadores_yellow.to_string(index=False))

print("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")

jogadores_data_red = []

# Coletando dados do plantel
for jogador_red in plantel:
    dados_jogador = [td.text.strip() for td in jogador_red.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 12:  # Verifica se existem dados suficientes
        nome = dados_jogador[1]
        sobreNome = dados_jogador[2].split()[-1].strip()
        posicao = dados_jogador[3]

        jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
        red = int(dados_jogador[11].split()[0]) if dados_jogador[11].split()[0].isdigit() else 0

        if dados_jogador[0] == "11":
            nome = "Rodrygo"
            sobreNome = ""
        if dados_jogador[1] == "JoseluJoseluCentroavante":
            nome = "Joselu"
            sobreNome = ""
        
        jogadores_data_red.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, red])

# Criando o DataFrame para ordenar
df_jogadores_red = pd.DataFrame(jogadores_data_red, columns=["Jogador", "Posição", "Jogos", "Cartões Vermelhos"])

# Ordenando por red em ordem decrescente
df_jogadores_red = df_jogadores_red.sort_values(by="Cartões Vermelhos", ascending=False).reset_index(drop=True)

# Exibindo a tabela
print("\n\n\nCartões Vermelhos na Temporada 2023/24\n")
print(df_jogadores_red.to_string(index=False))
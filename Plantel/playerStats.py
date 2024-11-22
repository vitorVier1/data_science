import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=%262023"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Função para coletar dados do plantel
def coletar_dados_estatisticos(plantel, estatistica):
    dados_estatisticos = []
    for jogador in plantel:
        dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
        
        if len(dados_jogador) >= 12:
            nome = dados_jogador[1]
            sobreNome = dados_jogador[2].split()[-1].strip()
            posicao = dados_jogador[3]
            jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
            
            # Condições de ajuste de nome para Rodrygo e Joselu
            if dados_jogador[0] == "11":
                nome = "Rodrygo"
                sobreNome = ""
            if dados_jogador[1] == "JoseluJoseluCentroavante":
                nome = "Joselu"
                sobreNome = ""
            
            if estatistica == 'gols':
                valor = int(dados_jogador[7].split()[0]) if dados_jogador[7].split()[0].isdigit() else 0
                dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, valor])
            elif estatistica == 'assistencias':
                valor = int(dados_jogador[8].split()[0]) if dados_jogador[8].split()[0].isdigit() else 0
                dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, valor])
            elif estatistica == 'amarelos':
                valor = int(dados_jogador[9].split()[0]) if dados_jogador[9].split()[0].isdigit() else 0
                dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, valor])
            elif estatistica == 'vermelhos':
                valor = int(dados_jogador[11].split()[0]) if dados_jogador[11].split()[0].isdigit() else 0
                dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, valor])
    
    return dados_estatisticos

# Coletando os dados para cada estatística
plantel = soup.select('table[class="items"] tbody tr')

# Artilharia
gols_data = coletar_dados_estatisticos(plantel, 'gols')
df_gols = pd.DataFrame(gols_data, columns=["Jogador", "Posição", "Jogos", "Gols"])
df_gols = df_gols.sort_values(by="Gols", ascending=False).reset_index(drop=True)
print("\nArtilharia da Temporada 2023/24\n")
print(df_gols.to_string(index=False))

print("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")

# Assistências
assistencias_data = coletar_dados_estatisticos(plantel, 'assistencias')
df_assistencias = pd.DataFrame(assistencias_data, columns=["Jogador", "Posição", "Jogos", "Assistencias"])
df_assistencias = df_assistencias.sort_values(by="Assistencias", ascending=False).reset_index(drop=True)
print("\n\n\nMaiores Assistentes da Temporada 2023/24\n")
print(df_assistencias.to_string(index=False))

print("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")

# Cartões Amarelos
amarelos_data = coletar_dados_estatisticos(plantel, 'amarelos')
df_amarelos = pd.DataFrame(amarelos_data, columns=["Jogador", "Posição", "Jogos", "Cartões Amarelos"])
df_amarelos = df_amarelos.sort_values(by="Cartões Amarelos", ascending=False).reset_index(drop=True)
print("\n\n\nCartões Amarelos na Temporada 2023/24\n")
print(df_amarelos.to_string(index=False))

print("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")

# Cartões Vermelhos
vermelhos_data = coletar_dados_estatisticos(plantel, 'vermelhos')
df_vermelhos = pd.DataFrame(vermelhos_data, columns=["Jogador", "Posição", "Jogos", "Cartões Vermelhos"])
df_vermelhos = df_vermelhos.sort_values(by="Cartões Vermelhos", ascending=False).reset_index(drop=True)
print("\n\n\nCartões Vermelhos na Temporada 2023/24\n")
print(df_vermelhos.to_string(index=False))

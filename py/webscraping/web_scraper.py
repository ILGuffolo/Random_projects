import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
from openpyxl import Workbook, load_workbook

#----------- functions -------------------#
def extract(substring):
    lines = text.splitlines()
    results = []
    
    for i, line in enumerate(lines):
        for sub in substring:
            if sub in line and i + 1 < len(lines):
                results.append(lines[i+1])
    return results
            
#----------------- MAIN ------------------#
#page = urlopen(url)
#html = page.read().decode("utf-8")
#soup = BeautifulSoup(html, "html.parser")

    
urloni = {
    "https://www.fipavonline.it/main/classifica/59192",
    "https://www.fipavonline.it/main/classifica/59183",
    "https://www.fipavonline.it/main/classifica/59182",
    "https://www.fipavonline.it/main/classifica/59166"
    }

# clear file
wb = Workbook()
wb.save("data.xlsx")


for url in urloni:
    headers={'User-Agent': 'Mozilla/5.0'}
    sheetName = ""

    session = requests.Session()
    response = session.get(url, headers=headers)

    text = response.text[5000:60000]
    #print(text)

    punti = extract(['<div class="cla-el punti">', '<div class="cla-el ">'])
    nomi = extract(['<div class="sq-n">'])


    punti = [''.join(('.' if c==',' else c) for c in s if (c.isdigit() or c==',')) for s in punti]
    punti = ["MAX" if s=="" else s for s in punti]

    nomibelli = []
    for s in nomi:
        match = re.search(r'<span class="sq-nLong">(.*?)</span>', s)
        nomibelli.append(match.group(1) if match else "non trovato")

    print(punti)
    print(f"squadre: {len(punti)/16}")
    print(nomibelli)


    #trasnfer to excel
    wb = load_workbook("data.xlsx")
    ws = wb.active

    lineLenght = 16

    for i in range(0, len(punti), lineLenght):
        lis = punti[i:i+lineLenght]
        lis.insert(0, nomibelli[int(i/16)])
        ws.append(lis)

    ws.append([""])
    wb.save("data.xlsx")




            



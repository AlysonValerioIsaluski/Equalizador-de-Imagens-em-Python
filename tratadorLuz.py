import os
import cv2
from pathlib import Path as _P
import matplotlib.pyplot as plt

def transformarImagem(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    nome_arquivo = os.path.basename(img_path)
    # cv2.imwrite(f"Imagens/gray_{nome_arquivo}", img) # exporta imagens em escala de cinza

    img1 = img.copy()
    img2 = img.copy()
    
    histograma = [0]*256
    altura, largura = img.shape
    total_pixels = altura * largura

    for i in range(altura):
        for j in range(largura):
            histograma[img[i][j]] += 1

    acumulado = [0]*256
    acumulado[0] = histograma[0]

    for i in range(1, len(histograma)):
        acumulado[i] = acumulado[i-1] + histograma[i]

    # Normalização 
    a1 = total_pixels / 255
    for i in range(altura):
        for j in range(largura):
            y = acumulado[img[i][j]]
            img1[i][j] = round(y / a1)
    
    # Negativo
    a2 = -total_pixels / 255
    for i in range(altura):
        for j in range(largura):
            y = acumulado[img[i][j]]
            img2[i][j] = round((y - total_pixels) / a2)

    # Eixo X: lista de valores de 0 a 255
    eixo_x = range(256)

    # Cria uma figura contendo 2 gráficos (1 linha, 2 colunas)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # --- 1º Gráfico: Histograma da Imagem ---
    ax1.bar(eixo_x, histograma, color='orange', width=1.0)
    ax1.set_title(f"Histograma da Imagem {nome_arquivo}")
    ax1.set_xlabel("Brilho (0 a 255)")
    ax1.set_ylabel("Valor Relativo (Frequência)")
    ax1.set_xlim([0, 255]) 

    # --- 2º Gráfico: Histograma Acumulado ---
    ax2.bar(eixo_x, acumulado, color='blue', width=1.0, label="Acumulado")
    
    valores_reta = [a1*x for x in eixo_x]
    ax2.plot(eixo_x, valores_reta, color='yellow', linewidth=2.5, label="Reta y = ax + b Normalização")
    ax2.legend() # Mostra a legenda para diferenciar a barra da reta

    valores_reta = [a2*x + total_pixels for x in eixo_x]
    ax2.plot(eixo_x, valores_reta, color='red', linewidth=2.5, label="Reta y = ax + b Negativo")
    ax2.legend() # Mostra a legenda para diferenciar a barra da reta

    ax2.set_title(f"Histograma Acumulado da Imagem {nome_arquivo}")
    ax2.set_xlabel("Brilho (0 a 255)")
    ax2.set_ylabel("Valor Relativo (Frequência Acumulada)")
    ax2.set_xlim([0, 255])

    plt.tight_layout()
    plt.show()
    
    return img1, img2

def transformarImagemBonus(img_path):
    # Lê a imagem mantendo as cores (RGB/BGR)
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        return None
    
    altura, largura = img.shape[:2]
    total_pixels = altura * largura
    a1 = total_pixels / 255 # Inclinação da normalização
    
    # Separa os canais Azul (b), Verde (g) e Vermelho (r)
    b, g, r = cv2.split(img)
    canais = [b, g, r]
    canais_processados = []
    
    # Processa cada cor individualmente
    for canal in canais:
        canal_norm = canal.copy()
        hist = [0]*256
        
        for i in range(altura):
            for j in range(largura):
                hist[canal[i][j]] += 1
                
        acum = [0]*256
        acum[0] = hist[0]
        for i in range(1, 256):
            acum[i] = acum[i-1] + hist[i]
            
        for i in range(altura):
            for j in range(largura):
                y = acum[canal[i][j]]
                canal_norm[i][j] = round(y / a1)
                
        canais_processados.append(canal_norm)
        
    # Junta os canais novamente
    img_final = cv2.merge(canais_processados)
    return img_final

# Exemplo de como chamar no seu script para gerar a imagem final:
# res_bonus = transformarImagemBonus("Imagens/SuaFotoColorida.png")
# cv2.imwrite("Resultados/BonusProcessado.png", res_bonus)

ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}

project_root = _P('.').resolve()
folder_path = str(project_root / 'Imagens')

p = _P(folder_path)
n_images = 4
# rglob para incluir subpastas; filtra por extensão
files = sorted([f for f in p.rglob('*') if f.suffix.lower() in ALLOWED_EXTS])
results1 = []
results2 = []
resultsBonus = []
names = []

for i, f in enumerate(files):
    res1, res2 = transformarImagem(str(f))
    res3 = transformarImagemBonus(str(f))
    '''
    try:
    except Exception as e:
        print(f"Ignorado {f}: {e}")
        continue
    '''

    if res1 is None or res2 is None:
        # Se a função não conseguiu ler/processar o arquivo, avisa e pula
        print(f"Falha ao processar {f}")
        continue
    
    results1.append(res1)
    results2.append(res2)
    resultsBonus.append(res3)
    names.append(f.name)

for i in range(len(results1)):
    if results1[i] is not None:
        # Exporta imagens
        cv2.imwrite(f"Resultados/equalizacao_{names[i]}", results1[i])
        print(f"Imagem {names[i]} exportada com sucesso!")

for i in range(len(results2)):
    if results2[i] is not None:
        # Exporta imagens
        cv2.imwrite(f"Resultados/negativo_{names[i]}", results2[i])
        print(f"Imagem {names[i]} exportada com sucesso!")

for i in range(len(resultsBonus)):
    if resultsBonus[i] is not None:
        # Exporta imagens
        cv2.imwrite(f"Resultados/bonus_{names[i]}", resultsBonus[i])
        print(f"Imagem {names[i]} exportada com sucesso!")
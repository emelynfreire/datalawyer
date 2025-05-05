import os
import time
import fitz
from bs4 import BeautifulSoup  # Para extração de texto em HTML
from queue import Queue  # Fila para comunicação entre threads
import threading  # Para uso de múltiplas threads

# Configurações gerais
DIRETORIO_ENTRADA = "Documentos"              # Pasta com os arquivos de entrada
DIRETORIO_SAIDA = "Documentos_extraidos"      # Pasta onde os .txt serão salvos
RELATORIO = "relatorio.txt"                   # Nome do relatório final
NUM_THREADS_LEITURA = 4                       # Nº de threads para leitura dos arquivos
NUM_THREADS_PROCESSAMENTO = 4                 # Nº de threads para processamento (extração)
NUM_THREADS_ESCRITA = 2                       # Nº de threads para escrita (não usada separadamente aqui)

# Filas para fluxo da pipeline
fila_leitura = Queue()         # Fila entre leitura -> processamento
fila_processamento = Queue()   # Fila entre processamento -> salvamento

# Dicionário para registrar métricas e erros
resultados = {
    "pdf": {"sucesso": 0, "erro": 0, "tempos": []},
    "html": {"sucesso": 0, "erro": 0, "tempos": []}
}

# Lock para evitar condições de corrida ao atualizar resultados
lock = threading.Lock()

# Função executada pelas threads de leitura
def leitor_arquivo():
    while True:
        item = fila_leitura.get()
        if item is None:
            break  # Sinal de parada
        tipo, caminho = item
        try:
            # Leitura dos bytes do arquivo em disco
            with open(caminho, 'rb') as f:
                conteudo = f.read()
            # Envia para a fila de processamento
            fila_processamento.put((tipo, caminho, conteudo))
        except Exception:
            # Em caso de erro na leitura, incrementa contagem de erro
            with lock:
                resultados[tipo]["erro"] += 1
        fila_leitura.task_done()  # Marca tarefa como concluída

# Função executada pelas threads de extração de texto
def extrator_texto():
    while True:
        item = fila_processamento.get()
        if item is None:
            break  # Sinal de parada
        tipo, caminho, conteudo = item
        inicio = time.time()  # Tempo inicial para cálculo da duração

        try:
            # Define nome do arquivo de saída (.txt)
            nome = os.path.splitext(os.path.basename(caminho))[0]
            caminho_txt = os.path.join(DIRETORIO_SAIDA, f"{nome}.txt")

            # Extração de texto dependendo do tipo de arquivo
            if tipo == "pdf":
                # Salva temporariamente o PDF lido em disco para abrir com PyMuPDF
                with open(caminho, 'wb') as temp_pdf:
                    temp_pdf.write(conteudo)
                doc = fitz.open(caminho)
                texto = "\n".join(p.get_text("text") for p in doc if p.get_text("text"))

            elif tipo == "html":
                # Extrai texto do HTML com BeautifulSoup
                texto = BeautifulSoup(conteudo.decode("utf-8", errors="ignore"), "html.parser").get_text(separator="\n")
            else:
                raise ValueError("Tipo desconhecido")

            # Limpa espaços e quebras de linha desnecessárias
            texto = '\n'.join([linha.strip() for linha in texto.splitlines() if linha.strip()])

            # Salva o texto extraído no diretório de saída
            with open(caminho_txt, "w", encoding="utf-8") as f:
                f.write(texto)

            duracao = time.time() - inicio  # Tempo decorrido
            # Atualiza métricas de sucesso
            with lock:
                resultados[tipo]["sucesso"] += 1
                resultados[tipo]["tempos"].append(duracao)

        except Exception:
            # Em caso de erro durante a extração, registra falha
            with lock:
                resultados[tipo]["erro"] += 1
        fila_processamento.task_done()  # Marca tarefa como concluída

# Função para gerar o relatório final
def salvar_relatorio(resultados, tempo_total, caminho_saida):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("📊 RELATÓRIO DE PROCESSAMENTO\n\n")
        f.write(f"⏱️ Tempo total: {tempo_total:.2f} segundos\n\n")

        for tipo in ["pdf", "html"]:
            sucesso = resultados[tipo]["sucesso"]
            erro = resultados[tipo]["erro"]
            tempos = resultados[tipo]["tempos"]
            tempo_medio = sum(tempos) / len(tempos) if tempos else 0

            f.write(f"📁 Arquivos {tipo.upper()}:\n")
            f.write(f"   ✅ Processados com sucesso: {sucesso}\n")
            f.write(f"   ❌ Com erro: {erro}\n")
            f.write(f"   🕒 Tempo médio: {tempo_medio:.2f} segundos\n\n")

# Função principal que coordena todas as etapas
def extrair_texto_arquivos(diretorio=DIRETORIO_ENTRADA, saida=DIRETORIO_SAIDA):
    os.makedirs(saida, exist_ok=True)  # Garante que a pasta de saída existe

    # Lista os arquivos PDF e HTML do diretório de entrada
    arquivos_pdf = sorted([f for f in os.listdir(diretorio) if f.lower().endswith(".pdf")])
    arquivos_html = sorted([f for f in os.listdir(diretorio) if f.lower().endswith(".html")])

    inicio_total = time.time()  # Marca início do tempo total

    # Coloca todos os arquivos nas filas de leitura com tipo
    for arq in arquivos_pdf:
        fila_leitura.put(("pdf", os.path.join(diretorio, arq)))
    for arq in arquivos_html:
        fila_leitura.put(("html", os.path.join(diretorio, arq)))

    # Inicia as threads responsáveis por ler os arquivos
    threads_leitura = []
    for _ in range(NUM_THREADS_LEITURA):
        t = threading.Thread(target=leitor_arquivo)
        t.start()
        threads_leitura.append(t)

    # Inicia as threads responsáveis por processar o conteúdo lido
    threads_processamento = []
    for _ in range(NUM_THREADS_PROCESSAMENTO):
        t = threading.Thread(target=extrator_texto)
        t.start()
        threads_processamento.append(t)

    # Espera todas as leituras terminarem
    fila_leitura.join()
    for _ in threads_leitura:
        fila_leitura.put(None)  # Sinaliza parada para cada thread
    for t in threads_leitura:
        t.join()

    # Espera todos os processamentos terminarem
    fila_processamento.join()
    for _ in threads_processamento:
        fila_processamento.put(None)  # Sinaliza parada para cada thread
    for t in threads_processamento:
        t.join()

    tempo_total = time.time() - inicio_total  # Tempo total decorrido

    # Gera e salva o relatório
    salvar_relatorio(resultados, tempo_total, RELATORIO)

# Ponto de entrada do script
if __name__ == "__main__":
    extrair_texto_arquivos()

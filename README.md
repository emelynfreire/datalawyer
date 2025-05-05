# datalawyer

# 🧠 Extração de Texto de Arquivos PDF e HTML

Este script em Python realiza a **extração de texto** de arquivos `.pdf` e `.html`, salvando os conteúdos em arquivos `.txt`. Ele também gera um **relatório final de desempenho**, incluindo número de arquivos processados, tempo médio e erros.

---

## ⚙️ Requisitos

- Python 3.8 ou superior
- pip

---

## 📦 Instalação

1. **Clone o repositório ou copie os arquivos**

   Certifique-se de que o script `extrator.py` esteja salvo localmente.

2. **Crie um ambiente virtual (opcional, mas recomendado)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**

  No terminal, execute:

   ```bash
   pip install -r requirements.txt
   ```

---


## 🚀 Como Executar

Execute o script com o comando na pasta raiz do projeto:

```bash
python extrator.py
```

---

## 📊 Saída

- Os arquivos `.txt` extraídos serão salvos na pasta `Documentos_extraidos/`.
- Um relatório chamado `relatorio.txt` será gerado no diretório raiz, contendo:
  - Total de arquivos PDF e HTML processados
  - Número de sucessos e erros
  - Tempo médio por tipo de arquivo
  - Tempo total de execução

---

## 🛠️ Tecnologias Utilizadas

- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) – para leitura de PDFs
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) – para parsing de HTML
- [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) – para execução paralela

---

## ❓ Dúvidas Frequentes

- **Funciona com PDFs escaneados?**  
  Não, esse script extrai apenas texto digital. Para escaneados, seria necessário OCR (como `pytesseract`).

- **Aceita outros formatos além de PDF/HTML?**  
  Não por padrão, mas o código pode ser facilmente adaptado.

---
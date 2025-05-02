# 🤖 iFoodJobApp - Automação de Candidaturas no iFood

Este projeto automatiza o processo de candidatura para vagas no site de carreiras do iFood, realizando:

1. Scraping das vagas disponíveis.
2. Mapeamento dinâmico dos campos do formulário.
3. Preenchimento automático dos dados do candidato.
4. Envio da candidatura e registro do status no MongoDB.

---

## 📦 Estrutura do Projeto

```
.
├── executor.py               # Roda o processo completo em lote
├── scraping_ifood.py         # Extrai links de vagas do site do iFood
├── form_map.py               # Mapeia os campos do formulário por label
├── main.py                   # Preenche e envia o formulário com Playwright
├── labels_agrupados.py       # Dicionário dinâmico com mapeamento label → id
├── dados.py                  # Dados do candidato e configurações do Mongo
├── requirements.txt          # Dependências do projeto
```

---

## 🚀 Como usar

### 1. Clone o projeto

```bash
git clone https://github.com/seu-usuario/ifoodjobapp.git
cd ifoodjobapp
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
playwright install
```

### 3. Configure os dados

No arquivo `dados.py`, preencha os seguintes campos:

- Dados pessoais do candidato (nome, e-mail, LinkedIn, etc.)
- Configurações do MongoDB:
  ```python
  MONGO_URI = "mongodb+srv://<user>:<senha>@cluster.mongodb.net/"
  DATABASE = "ifood_carreiras"
  COLLECTION = "vagas_ifood"
  ```

### 4. Execute a automação

```bash
python executor.py
```

---

## 🧠 Tecnologias utilizadas

- [Python 3.10+](https://www.python.org/)
- [Playwright](https://playwright.dev/python/) – automação de navegação
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) – banco de dados de controle
- [PyMongo](https://pymongo.readthedocs.io/) – integração com MongoDB

---

## ✅ O que o sistema faz

- Filtra vagas com **senioridade Júnior ou Pleno** e **localização remota**.
- Realiza scraping e salva os links no MongoDB.
- Mapeia os labels HTML dos formulários de forma dinâmica.
- Preenche automaticamente os campos e dropdowns do formulário.
- Detecta candidaturas já enviadas para evitar duplicidade.
- Salva o status da candidatura e a data no banco.

---

## 📁 Exemplo de documento salvo no MongoDB

```json
{
  "_id": ObjectId("..."),
  "url": "https://carreiras.ifood.com.br/job/...",
  "titulo": "Analista de Dados Pleno",
  "status": "candidatura_enviada",
  "data_envio": "2025-05-02T20:55:00Z"
}
```

---

## 🛡️ Observações

- Este projeto é de uso educacional e pessoal.
- Respeite os termos de uso do site do iFood e evite abusos de scraping.
- Use com responsabilidade: cada envio de formulário é real.

---

## 🧑‍💻 Autor

**Guilherme Caldas**  
🔗 [linkedin.com/in/guilhermebcaldas](https://www.linkedin.com/in/guilhermebcaldas/)
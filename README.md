# iFoodJobApp – Job Application Automation

Automates applying to job openings on the iFood careers site:

1. Scrapes the available openings.
2. Dynamically maps the application form fields by label.
3. Fills in the candidate's data automatically.
4. Submits the application and records its status in MongoDB.

> **Disclaimer:** educational and personal project. Automated access may violate the website's terms of use. Use at your own risk, keep request volume low, and remember that every form submission is a real application.

## Project structure

```
.
├── executor.py          # Runs the full pipeline in batch
├── scraping_ifood.py    # Collects job links from the iFood careers site
├── form_map.py          # Maps form fields by label
├── main.py              # Fills in and submits the form with Playwright
├── labels_agrupados.py  # Label → field id mapping
├── dados.py             # Candidate data and MongoDB settings
├── requirements.txt
└── files/
    └── curriculo.pdf    # Your resume (not versioned, you provide it)
```

## Getting started

```bash
git clone https://github.com/ggcds/ifoodjobapp.git
cd ifoodjobapp
pip install -r requirements.txt
playwright install chromium
```

### Configure

1. Edit `dados.py` and replace every `"PREENCHER"` placeholder with your own data (name, e-mail, LinkedIn, diversity questions, etc.).
2. Set your MongoDB connection:
   ```python
   MONGO_URI = "mongodb+srv://<user>:<password>@cluster.mongodb.net/"
   DATABASE = "ifood_carreiras"
   COLLECTION = "vagas_ifood"
   ```
3. Put your resume at `files/curriculo.pdf`.

Do not commit your personal data or credentials. `files/` and `.env` are git-ignored; consider reading `MONGO_URI` from an environment variable.

### Run

```bash
python executor.py
```

## What it does

- Filters openings by **Junior or Mid-level** seniority and **remote** location.
- Scrapes job links and stores them in MongoDB.
- Maps form labels dynamically.
- Fills in text fields and dropdowns.
- Detects applications already sent to avoid duplicates.
- Stores each application's status and date.

## Example MongoDB document

```json
{
  "_id": "ObjectId(...)",
  "url": "https://carreiras.ifood.com.br/job/...",
  "titulo": "Analista de Dados Pleno",
  "status": "candidatura_enviada",
  "data_envio": "2025-05-02T20:55:00Z"
}
```

## Tech stack

- [Python 3.10+](https://www.python.org/)
- [Playwright](https://playwright.dev/python/) – browser automation
- [PyMongo](https://pymongo.readthedocs.io/) / [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) – application tracking

## Author

**Guilherme Barros Caldas** – [LinkedIn](https://www.linkedin.com/in/guilhermebcaldas/)

## License

[MIT](LICENSE)

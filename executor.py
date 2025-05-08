from scraping_ifood import extrair_links_ifood
from form_map import mapear_todas_as_vagas
from main import preencher_formulario_ifood
from pymongo import MongoClient
from datetime import datetime, timezone
from bson import ObjectId
from dados import MONGO_URI, DATABASE, COLLECTION

def extrair_e_inserir_links():
    """1) Extrai todos os links e faz upsert no Mongo."""
    print("🔎 Iniciando scraping das vagas...")
    extrair_links_ifood()
    print("✅ Scraping concluído.\n")

def verificar_vagas_novas():
    """2) Busca só vagas novas (sem data_envio) ou com status 'erro'."""
    client     = MongoClient(MONGO_URI)
    collection = client[DATABASE][COLLECTION]

    query = {
        "$or": [
            {"data_envio": {"$exists": False}},  # nunca processada
            {"status": "erro"}                    # falhou antes
        ]
    }
    vagas = list(collection.find(query))
    print(f"📊 Vagas novas/erro encontradas: {len(vagas)}\n")
    return vagas, collection

def preencher_em_lote(vagas, collection):
    """4) Para cada vaga filtrada, tenta enviar a candidatura."""
    print("\n🚨 Iniciando preenchimento das vagas filtradas 🚨")
    if not vagas:
        print("⚠️ Não há vagas para processar. Encerrando.")
        return

    for vaga in vagas:
        url    = vaga.get("url")
        titulo = vaga.get("titulo")

        if not url:
            print(f"⚠️ Ignorando vaga sem URL: {titulo!r}")
            continue

        print(f"\n🚀 Aplicando em: {titulo}\n🔗 {url}")
        try:
            novo_status = preencher_formulario_ifood(url)
            collection.update_one(
                {"_id": ObjectId(vaga["_id"])},
                {"$set": {
                    "status":     novo_status,
                    "data_envio": datetime.now(timezone.utc),
                    "erro":       None
                }}
            )
            print(f"✅ Status atualizado: {novo_status}")

        except Exception as e:
            print(f"❌ Erro na candidatura: {e}")
            collection.update_one(
                {"_id": ObjectId(vaga["_id"])},
                {"$set": {
                    "status":     "erro",
                    "data_envio": datetime.now(timezone.utc),
                    "erro":       str(e)
                }}
            )

def executar_em_lote():
    """
    Orquestra o fluxo:
      1) extrair_e_inserir_links
      2) verificar_vagas_novas
      3) mapear_todas_as_vagas (só para essas vagas)
      4) preencher_em_lote
    """
    # 1)
    extrair_e_inserir_links()

    # 2)
    vagas, collection = verificar_vagas_novas()
    if not vagas:
        return  # não há vagas novas/erro — fim do fluxo

    # 3) aplica o mapeamento apenas no subconjunto filtrado
    print("🧭 Mapeando campos dos formulários somente para as vagas filtradas...")
    mapear_todas_as_vagas()

    # 4)
    preencher_em_lote(vagas, collection)

if __name__ == "__main__":
    executar_em_lote()

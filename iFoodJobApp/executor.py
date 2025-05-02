from scraping_ifood import extrair_links_ifood
from form_map import mapear_todas_as_vagas
from main import preencher_formulario_ifood
from pymongo import MongoClient
from datetime import datetime, timezone
from bson import ObjectId
from dados import MONGO_URI, DATABASE, COLLECTION

def executar_em_lote():
    print("🔎 Iniciando scraping das vagas...")
    extrair_links_ifood()
    print("✅ Scraping concluído.")

    print("🧭 Mapeando campos dos formulários...")
    mapear_todas_as_vagas()
    print("✅ Mapeamento concluído.")

    client = MongoClient(MONGO_URI)
    collection = client[DATABASE][COLLECTION]

    vagas = list(collection.find({}))
    print(f"📊 Total de vagas encontradas no banco: {len(vagas)}")

    if not vagas:
        print("⚠️ Nenhuma vaga encontrada para processar.")
        return

    for vaga in vagas:
        url = vaga.get("url")
        titulo = vaga.get("titulo")

        if not url:
            print("⚠️ Documento sem URL, ignorado.")
            continue

        print(f"\n🚀 Iniciando candidatura para: {titulo}\n🔗 {url}")

        try:
            status = preencher_formulario_ifood(url)

            resultado = collection.update_one(
                {"_id": ObjectId(str(vaga["_id"]))},
                {
                    "$set": {
                        "status": status,
                        "data_envio": datetime.now(timezone.utc)
                    }
                }
            )

            if resultado.modified_count == 1:
                print(f"✅ Banco atualizado com status: {status}")
            else:
                print("⚠️ Nenhuma modificação realizada. Verifique o ID.")

        except Exception as e:
            print(f"❌ Erro ao aplicar na vaga: {e}")
            collection.update_one(
                {"_id": ObjectId(str(vaga["_id"]))},
                {
                    "$set": {
                        "status": "erro",
                        "data_envio": datetime.now(timezone.utc),
                        "erro": str(e)
                    }
                }
            )

if __name__ == "__main__":
    executar_em_lote()
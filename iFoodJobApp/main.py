from pathlib import Path
from playwright.sync_api import sync_playwright
from labels_agrupados import labels_agrupados
from dados import SEU_NOME
import re
from datetime import datetime, timezone

TIPO_CAMPO = {
    "Nome": "texto",
    "Sobrenome": "texto",
    "E-mail": "texto",
    "Telefone": "texto",
    "Currículo": "upload",
    "LinkedIn": "texto",
    "Website/Portfólio": "texto",
    "Quais são os seus pronomes?": "dropdown",
    "Onde você descobriu a vaga?": "dropdown",
    "Você já trabalhou no iFood?": "dropdown",
    "Com qual gênero você se identifica?": "dropdown",
    "Qual sua orientação sexual?": "dropdown",
    "Qual é sua cor ou raça?": "dropdown",
    "Você é uma pessoa com deficiência?": "dropdown",
    "Se você é uma pessoa com deficiência, por favor, nos informe qual é a sua deficiência:": "dropdown",
    "Você está ciente de que respondendo esse formulário de diversidade, você aceita o Aviso de Diversidade – D&I?": "dropdown",
    "Possui experiência com planejamento de s&op?": "texto"
}

def limpar_texto_label(texto):
    return re.sub(r'[\s*]+$', '', texto.strip())

def escapar_css_id(css_id):
    return css_id.replace(".", "\\.")

def preencher_dropdowns_dinamicamente(page, labels_dict, dados_dict):
    wrappers = page.query_selector_all("div.sc-fZqnxA.hAztOI, div.sc-edctFj.ijdhhl")
    if not wrappers:
        print("❌ Nenhum wrapper de dropdowns encontrado")
        return

    for wrapper in wrappers:
        form_controls = wrapper.query_selector_all("div.MuiFormControl-root")
        for form_control in form_controls:
            label_element = form_control.query_selector("label")
            if not label_element:
                continue

            texto_label_original = label_element.inner_text().strip()
            texto_label_limpo = limpar_texto_label(texto_label_original)

            if texto_label_limpo not in labels_dict:
                continue

            chave_logica = texto_label_limpo
            valor_a_preencher = dados_dict.get(chave_logica)
            if not valor_a_preencher:
                print(f"❌ Valor não encontrado para '{chave_logica}' em dados.py")
                continue

            elemento = form_control.query_selector("div[role='combobox']")
            if not elemento:
                print(f"❌ Dropdown não encontrado para '{texto_label_limpo}'")
                continue

            try:
                elemento.click()
                page.wait_for_selector("ul[role='listbox']", timeout=5000)
                page.click(f"li[role='option']:has-text('{valor_a_preencher}')")
                print(f"✅ Dropdown '{texto_label_limpo}' preenchido com '{valor_a_preencher}'")
            except Exception as e:
                print(f"⚠️ Erro ao preencher dropdown '{texto_label_limpo}': {e}")

def preencher_formulario_ifood(vaga_url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(vaga_url, timeout=60000)

        page.wait_for_selector("button:has-text('Aplicar-se à Vaga')", timeout=10000)
        page.click("button:has-text('Aplicar-se à Vaga')")
        page.wait_for_selector("form", timeout=10000)

        ids_presentes = page.eval_on_selector_all("[id]", "els => els.map(e => e.id)")

        for label_visivel, ids_possiveis in labels_agrupados.items():
            tipo = TIPO_CAMPO.get(label_visivel)
            valor = SEU_NOME.get(label_visivel)

            if not valor:
                print(f"❌ Valor não encontrado para '{label_visivel}'")
                continue

            if tipo == "dropdown":
                continue  # será tratado separadamente

            if tipo == "upload":
                if not Path(valor).exists():
                    print(f"❌ Arquivo não encontrado: '{valor}'")
                    continue
                try:
                    input_selector = "label[for='resume'] >> xpath=../..//input[@type='file']"
                    page.set_input_files(input_selector, valor)
                    print(f"📎 Currículo enviado com sucesso: '{valor}'")
                except Exception as e:
                    print(f"⚠️ Erro ao enviar currículo: {e}")
                continue

            id_encontrado = next((i for i in ids_possiveis if i in ids_presentes), None)

            try:
                if id_encontrado:
                    seletor = f'#{escapar_css_id(id_encontrado)}'
                    page.fill(seletor, valor)
                    print(f"✅ Preenchido '{label_visivel}' em '{id_encontrado}' com '{valor}'")
                else:
                    print(f"❌ Nenhum ID encontrado no DOM para '{label_visivel}'")
            except Exception as e:
                print(f"⚠️ Erro ao preencher '{label_visivel}': {e}")

        preencher_dropdowns_dinamicamente(page, labels_agrupados, SEU_NOME)

        # Verifica se já existe candidatura com o mesmo e-mail
        try:
            email_container = page.query_selector("label[for='email'] >> xpath=ancestor::div[contains(@class, 'MuiFormControl-root')]")
            if email_container:
                erro_element = email_container.query_selector("p.MuiFormHelperText-root.Mui-error")
                if erro_element:
                    texto_erro = erro_element.inner_text().strip()
                    if "Já existe uma candidatura nesta vaga com este e-mail" in texto_erro:
                        print("⚠️ Já existe uma candidatura nesta vaga com este e-mail.")
                        browser.close()
                        return "candidatura_existente"
        except Exception as e:
            print(f"Erro ao verificar duplicidade de e-mail: {e}")

        # Envia candidatura se ainda não enviada
        try:
            page.wait_for_selector("button[type='submit']:has-text('Enviar Candidatura'):not([disabled])", timeout=10000)
            page.click("button[type='submit']:has-text('Enviar Candidatura')")

            # Espera a mensagem de sucesso visual após o envio
            page.wait_for_selector("text=Recebemos sua candidatura!", timeout=10000)

            print("🚀 Candidatura enviada com sucesso.")
            browser.close()
            return "candidatura_enviada"
        except Exception as e:
            print(f"❌ Erro ao tentar clicar no botão de envio: {e}")
            browser.close()
            return "erro"

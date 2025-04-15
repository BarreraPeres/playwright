from playwright.sync_api import sync_playwright, expect

import pandas as pd
import re
import time

class GoogleMapsScraper:
    def __init__(self):
        self.page = None

    def coletar_dados_google_maps(self, palavra_chave, localizacao):
        dados = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                self.page = browser.new_page()

                self.page.goto("https://www.google.com.br/maps")
                expect(self.page).to_have_title(re.compile("Google Maps"))
                print("processando...")

                self.page.wait_for_selector('input[name="q"]')
                self.page.fill('input[name="q"]', f"{palavra_chave} em {localizacao}")
                self.page.press('input[name="q"]', 'Enter')
                self.page.get_by_role('feed').wait_for()
                print("carregou os feed")

                for _ in range(5):
                    self.page.evaluate("document.querySelector('div[role=\\'feed\\']').scrollTop += 500;")
                    time.sleep(2)

                # self.page.wait_for_selector('.hfpxzc')
                cards = self.page.locator('.hfpxzc').all()
                print(f"resultados encontrados: {len(cards)}")

                for i in range(0, len(cards)):
                    try:
                        card = cards[i]
                        card.click()

                        nome =  self.page.locator("h1.DUwDvf.lfPIob").inner_text()
                        endereco = self.page.locator("div.Io6YTe.fontBodyMedium.kR99db.fdkmkc").first.inner_text()
                        status = self.page.locator("span.ZDu9vd").last.inner_text()
                    
                        dados.append({
                            'Nome': nome,
                            'Endereço': endereco,
                            "Status": status
                        })

                        time.sleep(1)

                    except Exception as e:
                        print(f"Erro ao processar resultado {i+1}: {e}")
                        try:
                            self.page.go_back()
                            self.page.wait_for_selector('.hfpxzc', timeout=5000)
                            time.sleep(1)
                        except:
                            pass
                        continue

                browser.close()

        except Exception as e:
            print(f"Erro interno {e}")

        return pd.DataFrame(dados)

if __name__ == '__main__':
    palavra = "restaurantes"
    local = "Jacareí, SP"

    scraper = GoogleMapsScraper()
    df_dados = scraper.coletar_dados_google_maps(palavra, local)

    if not df_dados.empty:
        print("\nDados coletados:")
        df_dados.to_csv(f'dados_google_maps_{palavra.replace(" ", "_")}_{local.replace(" ", "_")}.csv',
                        index=False,
                        encoding='utf-8'
        )
        print("\nDados salvos em arquivo CSV.")
    else:
        print("\nNenhum dado foi coletado.")

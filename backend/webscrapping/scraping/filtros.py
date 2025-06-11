from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def aplicar_filtros(driver, tipo_operacao="", tipo_imovel="", localizacao="", cidade="", bairro="", quartos="", preco_medio="", palavra_chave=""):
    wait = WebDriverWait(driver, 10)
    driver.get("https://dfimoveis.com.br")

    # Aceitar cookies
    try:
        botao_cookies = wait.until(EC.element_to_be_clickable((By.ID, "btn-lgpd")))
        botao_cookies.click()
        sleep(1)
    except:
        pass

    def selecionar_opcao(indice, texto):
        # Alvo: elementos que abrem o combo
        combos = driver.find_elements(By.CSS_SELECTOR, "span.select2-selection__rendered")
        if len(combos) > indice:
            combos[indice].click()
            campo = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-search__field")))
            campo.send_keys(texto)
            campo.send_keys(Keys.ENTER)
            sleep(1)
        else:
            print(f"⚠️ Combo index {indice} fora do range [{len(combos)}]")

    if tipo_operacao:
        selecionar_opcao(0, tipo_operacao)
    if tipo_imovel:
        selecionar_opcao(1, tipo_imovel)
    if localizacao:
        selecionar_opcao(2, localizacao)
    if cidade:
        selecionar_opcao(3, cidade)
    if bairro:
        selecionar_opcao(4, bairro)

    if quartos:
        driver.find_elements(By.CLASS_NAME, "select2-selection--single")[5].click()
        sleep(1)
        opcoes = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "select2-results__option")))
        for opcao in opcoes:
            if opcao.text.strip().startswith(quartos):
                opcao.click()
                break
        sleep(1)

    if preco_medio:
        campo = wait.until(EC.element_to_be_clickable((By.ID, "valorMedio")))
        campo.clear()
        campo.send_keys(preco_medio)
        sleep(1)

    if palavra_chave:
        campo = wait.until(EC.element_to_be_clickable((By.ID, "palavraChave")))
        campo.clear()
        campo.send_keys(palavra_chave)
        sleep(1)

    # Botão de busca
    botao_buscar = wait.until(EC.element_to_be_clickable((By.ID, "botaoDeBusca")))
    botao_buscar.click()
    sleep(5)


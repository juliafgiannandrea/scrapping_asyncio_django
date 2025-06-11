from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def iniciar_navegador(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver





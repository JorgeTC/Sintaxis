import time
import webbrowser

import requests
from selenium import webdriver

from src.aux_res_directory import get_res_folder

# Variable para saber si estoy intentando resolver el captcha
stopped = False
# XPath donde está el botón
XPATH_PASS_BUTTON = "/html/body/div[1]/div[2]/form/div[2]/input"
# Opciones para el driver de Chrome
DRIVER_OPTION = webdriver.ChromeOptions()
DRIVER_OPTION.add_experimental_option('excludeSwitches', ['enable-logging'])
# Path donde se encuentra el driver
DRIVER_PATH = get_res_folder("driver", "chromedriver")


def safe_get_url(url):
    # open with GET method
    resp = requests.get(url)
    # Caso 429: too many requests
    if resp.status_code == 429:
        return PassCaptcha(url)
    else:  # No está contemplado el caso 404: not found
        return resp


def PassCaptcha(url):
    global stopped
    if not stopped:

        # Impido tratar de pasar el captcha más de una vez
        stopped = True

        # Intento pasar el Captcha de forma automática
        automatically_pass_captcha(url)

        if requests.get(url).status_code != 200:
            # No he conseguido pasar el Captcha, necesito ayuda del usuario
            # abro un navegador para poder pasar el Captcha
            webbrowser.open(url)
            print("\nPor favor, entra en FilmAffinity y pasa el captcha por mí.")

    resp = requests.get(url)
    # Controlo que se haya pasado el Captcha
    while resp.status_code != 200:
        time.sleep(3)  # intento recargar la página cada 3 segundos
        resp = requests.get(url)
    stopped = False
    return resp


def automatically_pass_captcha(url):
    try:
        # Abro una instancia de Chrome
        # Lo creo con un conjunto de opciones para no emitir errores por consola
        driver = webdriver.Chrome(DRIVER_PATH,
                                  options=DRIVER_OPTION)
        # Entro a la dirección que ha dado error
        driver.get(url)
        # Espero a que se haya cargado el botón que quiero clicar
        time.sleep(1)

        # Accedo al botón que permite pasar el captcha
        button = driver.find_element_by_xpath(XPATH_PASS_BUTTON)
        # Clico sobre él
        button.click()
        # Espero a que me redirija a la página a la que quería acceder
        time.sleep(1)

        # Cierro la instancia de Chrome
        driver.close()
    except:
        pass

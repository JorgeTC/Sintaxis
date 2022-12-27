import time
import webbrowser

import requests
from requests.models import Response
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.safe_url.chrome_driver import get_chrome_instance

# Variable para saber si estoy intentando resolver el captcha
stopped = False


def PassCaptcha(url: str) -> Response:
    global stopped
    if not stopped:
        stopped = True

        # Intento pasar el Captcha de forma automática
        automatically_pass_captcha(url)

        if requests.get(url).status_code == 429:
            # No he conseguido pasar el Captcha, necesito ayuda del usuario
            # abro un navegador para poder pasar el Captcha
            webbrowser.open(url)
            print("\nPor favor, entra en FilmAffinity y pasa el captcha por mí.")

    resp = requests.get(url)
    # Controlo que se haya pasado el Captcha
    while resp.status_code == 429:
        time.sleep(3)  # intento recargar la página cada 3 segundos
        resp = requests.get(url)
    stopped = False
    return resp


def automatically_pass_captcha(url: str) -> None:
    driver = get_chrome_instance()
    # Entro a la dirección que ha dado error
    driver.get(url)
    # Espero a que se haya cargado el botón que quiero clicar
    time.sleep(1)

    # Accedo al botón que permite pasar el captcha
    # XPath donde está el botón
    XPATH_PASS_BUTTON = "/html/body/div[1]/div[2]/form/div[2]/input"
    try:
        button = driver.find_element(By.XPATH, XPATH_PASS_BUTTON)
    except NoSuchElementException:
        driver.close()
        return
    # Clico sobre él
    button.click()
    # Espero a que me redirija a la página a la que quería acceder
    time.sleep(1)
    driver.get(url)

    # Cierro la instancia de Chrome
    driver.close()

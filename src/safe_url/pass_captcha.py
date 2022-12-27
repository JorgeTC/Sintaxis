import time
import webbrowser

import requests
from requests.models import Response
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from multiprocessing import Lock

from src.safe_url.chrome_driver import get_chrome_instance

# Variable para saber si estoy intentando resolver el captcha
stopped = Lock()


def PassCaptcha(url: str) -> Response:
    while True:
        # Hago la petición y la devuelvo si no ha saltado el captcha
        resp = requests.get(url)
        if resp.status_code != 429:
            return resp

        # Bloqueo el acceso a la función para pasar el captcha
        if stopped.acquire(block=False):
            # Estoy en el hilo responsable de pasar el captcha
            solve_captcha(url)
            stopped.release()
        else:
            # Me quedo esperando a que un hilo haya terminado el captcha
            with stopped:
                pass


def solve_captcha(url: str) -> None:
    # Intento pasar el Captcha de forma automática
    automatically_solve_captcha(url)

    if requests.get(url).status_code == 429:
        # No he conseguido pasar el Captcha, necesito ayuda del usuario
        manually_solve_captcha(url)

    # No quiero salir de la función hasta que haya resuelto el captcha
    while requests.get(url).status_code == 429:
        pass


def automatically_solve_captcha(url: str) -> None:
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


def manually_solve_captcha(url: str) -> None:
    # Abro un navegador para poder pasar el Captcha
    webbrowser.open(url)
    print("\nPor favor, entra en FilmAffinity y pasa el captcha por mí.")

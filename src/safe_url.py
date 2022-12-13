import os
import time
import webbrowser
from pathlib import Path

import chromedriver_autoinstaller
import requests
from requests.models import Response
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from src.aux_res_directory import get_res_folder

# Variable para saber si estoy intentando resolver el captcha
stopped = False
# Opciones para el driver de Chrome
DRIVER_OPTION = webdriver.ChromeOptions()
DRIVER_OPTION.add_argument('--headless')
DRIVER_OPTION.add_experimental_option('excludeSwitches', ['enable-logging'])
# Path donde se encuentra el driver
DRIVER_PATH = get_res_folder("Readdata", "driver", "chromedriver.exe")


def safe_get_url(url: str) -> Response:
    # open with GET method
    resp = requests.get(url)
    # Caso 429: too many requests
    if resp.status_code == 429:
        return PassCaptcha(url)
    else:
        return resp


def PassCaptcha(url: str) -> Response:
    global stopped
    if not stopped:

        # Impido tratar de pasar el captcha más de una vez
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


def create_chrome_instance() -> Chrome:
    # Abro una instancia de Chrome
    # Lo creo con un conjunto de opciones para no emitir errores por consola
    return webdriver.Chrome(DRIVER_PATH,
                            options=DRIVER_OPTION)


def automatically_pass_captcha(url: str) -> None:
    try:
        driver = create_chrome_instance()
    except WebDriverException:
        update_chrome_driver()
        driver = create_chrome_instance()
        if not driver:
            print("Por favor, actualiza el driver de Chrome.")
            return
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


def update_chrome_driver():
    # Descargo el nuevo driver
    str_path_new_driver = chromedriver_autoinstaller.install(
        path=DRIVER_PATH.parent)
    # Si no he descargado nada, salgo
    if not str_path_new_driver:
        return

    # Elimino el antiguo driver
    if os.path.isfile(DRIVER_PATH):
        os.remove(DRIVER_PATH)
    # Coloco el nuevo en la ruta que le corresponde
    os.rename(src=str_path_new_driver, dst=DRIVER_PATH)

    # Elimino la carpeta que ha creado
    path_new_driver = Path(str_path_new_driver).parent
    if DRIVER_PATH.parent == path_new_driver.parent:
        os.rmdir(path_new_driver)

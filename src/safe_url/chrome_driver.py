import os
from pathlib import Path

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException

from src.aux_res_directory import get_res_folder

DRIVER_PATH = get_res_folder("Readdata", "driver", "chromedriver.exe")


def create_chrome_instance() -> Chrome:
    # Abro una instancia de Chrome
    # Lo creo con un conjunto de opciones para no emitir errores por consola
    return webdriver.Chrome(DRIVER_PATH,
                            options=get_driver_option())


def get_chrome_instance() -> Chrome:
    try:
        return create_chrome_instance()
    except WebDriverException as driver_error:
        update_chrome_driver()
        driver = create_chrome_instance()
        if not driver:
            print("Por favor, actualiza el driver de Chrome.")
            raise driver_error
        else:
            return driver


def get_driver_option() -> webdriver.ChromeOptions:
    # Opciones para el driver de Chrome
    driver_option = webdriver.ChromeOptions()
    driver_option.add_argument('--headless')
    driver_option.add_experimental_option(
        'excludeSwitches', ['enable-logging'])

    return driver_option


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

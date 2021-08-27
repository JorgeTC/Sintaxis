import requests
import webbrowser
import time

stopped = False

def safe_get_url(url):
    #open with GET method
    resp = requests.get(url)
    # Caso 429: too many requests
    if resp.status_code == 429:
        return PassCaptcha(url)
    else: # No está contemplado el caso 404: not found
        return resp

def PassCaptcha(url):
    global stopped
    if not stopped:
        stopped = True
        # abro un navegador para poder pasar el Captcha
        webbrowser.open(url)
        print("\nPor favor, entra en FilmAffinity y pasa el captcha por mí.")
    resp = requests.get(url)
    # Controlo que se haya pasado el Captcha
    while resp.status_code != 200:
        time.sleep(3) # intento recargar la página cada 3 segundos
        resp = requests.get(url)
    stopped = False
    return resp

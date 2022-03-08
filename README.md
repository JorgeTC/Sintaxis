# Sintaxis

A program to scrap your votes from FilmAffinity.
The data will be stored in an Excel file.
You will see some statistics about your votes.

The available users are in `res/usuarios.json`.
The user will be prompted at the beginning of the program.
You can scroll through them with the arrow keys.

FilmAffinity might launch its captcha to verify that we are not robots.
I will try to fool it by opening a Chrome instance.
If the Captcha is smarter than me, the scraping stops until a human passes the Captcha.

The code uses the `win32api` library.
This implies that it will run only in Windows.

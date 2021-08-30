# Sintaxis

The user whose movies are to be read must be entered. By default those of "Jorge" are read.
To choose another user, simply enter the desired name.
Those available are: 'Sasha', 'Jorge', 'Guillermo', 'Daniel Gallego', 'Luminador', 'Will_llermo', 'Roger Peris', 'Javi', 'El Feo', 'coleto'.
The reading is slow and the program is not able to avoid the captcha.
When FilmAffinity launches the captcha, a window will open in the browser for the user to pass the captcha. When it is done, scraping will continue.
When finished, an excel will be generated with the data read.
---
# Add a new user
First you need to know your id in FilmAffinity.
To do so, go to your votations page.
Your profile page.
Look the url, it will end with ```user_id=```.
The number after that, is your id.

To add your profile to the program, go to ```src\Readdata\usuarios.json```.
Just write your name (different from the others) and your number.
Remember adding a comma at the end of the line before yours.

Execute ```main.py``` when the program asks you to press enter, write your name as you have written it in the json file.
Press enter and the reading will start.

# WalmartBot
This is a bot that will buy anything through Walmart.ca and break their captcha. It's written in python and uses selenium to interact with web pages. It's a very simple program and there's no promise it'll work. It's your job to see what happens if the website crash and during a few edge cases ex. survey.

# Why
I was inspired after seeing a few articles on breaking the Google reCAPTCHA and I wanted to try to break a captcha by myself. It eventually evolved into something else.

# Installation

* [Python](https://www.python.org/)
* [Selenium](https://selenium-python.readthedocs.io/installation.html) (I use v4.0)
* [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

You need to add chromedriver to your PATH

# Use
To keep the number of requests to walmart.ca low, the code is separated in 2, client and server.

## Server (walmart_bot_server.py)
The server periodically checks the stocks for all clients. Return a json with a list of sku-bool indicating the availability of the product.

### Args

* -i The stock update interval (sec)
* -a The server ip address
* -p The server port
* -c The maximum number of connections
* -t Time until client timeout (sec)

## Client (walmart_bot_client.py)
The client receives information from the server and checkout if there is any stocks. It takes sku(s) as an entry (the number at the end of a walmart product url). Fill your info in customer.json.

### Args

* -i The stock update interval (sec)
* -a The server ip address
* -s The walmart skus to watch

# Hey @bersekee the code SUCKS
Well.. I've never used python or selenium and I did this in 2 evening between games of League of Legends. Draw the conclusion you want.

# Contribution
I am no longer actively working this project so merge requests are very welcome. I might try to make chrome headless at some point.
You can also add me on discord Bersekee#7545 if you have any questions

## Disclaimer
This project is meant for "educational" purposes hence there will never be any release versions. Do NOT use for reselling. Try to keep your number of requests to low so you don't harm walmart.ca.

## LICENSE

GNU General Public License v3.0
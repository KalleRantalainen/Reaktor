"""
File: keep_alive.py
Programmer: Kalle Rantalainen
Email: kalle.rantalainen@tuni.fi
Date: 13.01.2023

This file creates the web application and calls the
update_web_page function from the scraping.py file
to update the html template of the web page.
"""
from flask import Flask, render_template
from threading import Thread

from scraping import update_web_page

app = Flask('')
app.config.update(TEMPLATES_AUTO_RELOAD=True)

@app.route('/')
def home():
    """
    Defining the home page of the web page. This function
    renders the updated html template for the web page.
    :return: html template for the web page
    """
    update_web_page()
    return render_template("information.html")

def run():
    """
    This function is only called at the start of the program
    to run the web server.
    """
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """
    Starts a separate thread for the web server
    at the beginning of the program.
    """
    t = Thread(target=run)
    t.start()

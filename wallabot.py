#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import pickle
import os
import config as cfg
import smtplib
from email.message import EmailMessage

OFFERS_URL ='https://es.wallapop.com/search?time_filter=lastWeek&keywords=rx%205700%20xt&max_sale_price=1000&order_by=price_high_to_low&latitude=40.4893538&longitude=-3.6827461&filters_source=quick_filters'

def enviarmail(to, msg):
    """Funcion que envia un mensaje"""
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(cfg.username,cfg.password)

    em = EmailMessage()
    em.set_content(msg)
    em['To'] = to
    em['From'] = cfg.username
    em['Subject'] = 'Ofertas de ' + OFFERS_URL

    server.send_message(em)

    server.quit()


def scrappeOffers(driver):
    accept_terms_button = driver.find_element_by_id('didomi-notice-agree-button')
    if(accept_terms_button is not None):
        accept_terms_button.send_keys(Keys.RETURN)

    sleep(10)

    cards = driver.find_elements_by_class_name('card')
    if(cards is not None):
        print('Buenos dias Argonauta estas son tus ofertas para hoy:')
        new_cards = []
        for e in cards:
            try:
                precio = e.find_element_by_class_name('product-info-price').text
                titulo = e.find_element_by_class_name('product-info-title').text
                enlace = e.find_element_by_tag_name('a')
                #reservada
                reservada = False
                try:
                    reservada_element = e.find_element_by_class_name('reserved')
                    if(reservada_element is not None):
                        reservada = True
                except NoSuchElementException:
                    reservada = False
                item_id = e.get_attribute('data-item-id')
                print('- Tarjeta Gráfica: Id: {} titulo: {} precio: {} enlace: {} reservada: {}'.format(item_id,titulo,precio,enlace.get_attribute('href'),str(reservada)))
                new_cards.append({'item_id':item_id,'titulo': titulo, 'precio': precio, 'enlace': enlace.get_attribute('href'), 'reservada': reservada })
            except:
                pass
        return new_cards
if __name__=="__main__":
    email_candidate = []
    driver = webdriver.Chrome()
    driver.get(OFFERS_URL)

    offers = scrappeOffers(driver)
    ##recover offers
    if os.path.exists('offers.pickle'):
        with open('offers.pickle', 'rb') as f:
            data = pickle.load(f)
        for offer in offers:
            if offer not in data:
                data.append(offer)
                email_candidate.append(offer)
    else:
        with open('offers.pickle', 'wb') as f:
            pickle.dump(offers, f, pickle.HIGHEST_PROTOCOL)
        email_candidate = offers
    msg = ['- Tarjeta Gráfica: Id: {} titulo: {} precio: {} enlace: {} reservada: {}'.format(n['item_id'],n['titulo'],n['precio'],n['enlace'],n['reservada']) for n in email_candidate]
    enviarmail(cfg.username,'\n'.join(msg))
    driver.quit()
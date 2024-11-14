from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time
from main import WebScraping
import csv
import re
import logging




def toate_anunturile(url):
    # Liste pentru a stoca datele extrase
    lista_titluri = []
    lista_preturi = []
    lista_linkuri = []

    nume_csv = input('Ce nume doriti sa aiba csv-ul dvs?\n')
    with open(nume_csv + '.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        coloane_csv = input('Ce coloane doriti sa aibe fisierul dvs?\n').lower()
        header = [col.strip() for col in coloane_csv.split(',')]
        writer.writerow(header)

        # Initializează driver-ul
        driver = webdriver.Chrome()

        # Accesează pagina dorită
        driver.get(url)

        # Accept cookie-uri (dacă este necesar)
        # time.sleep(1)
        # accept = driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler")
        # accept.click()

        while True:
            # Așteaptă încărcarea completă a anunțurilor
            time.sleep(2)  # Ajustează timpul de așteptare

            # Extrage anunțurile de pe pagina curentă
            anunturi = driver.find_elements(By.CSS_SELECTOR, 'ol.row > li')  # Selector pentru fiecare anunț

            for anunt in anunturi:
                # Extrage titlul
                try:
                    title = anunt.find_element(By.CSS_SELECTOR, "h3 > a").text
                except NoSuchElementException:
                    title = "Titlu indisponibil"

                # Extrage prețul
                try:
                    price = anunt.find_element(By.CSS_SELECTOR, "p.price_color").text
                    if price:
                        pret_text = price.replace(' ', '')
                        pret_numeric = re.split(r'leiPretulnegociabil|lei|€|£|\$', pret_text)[0].replace(',', '.')
                        lista_preturi.append(price)  # Adaugă doar prețul numeric
                except NoSuchElementException:
                    price = "Preț indisponibil"

                # Extrage link-ul
                try:
                    link = anunt.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except NoSuchElementException:
                    link = "Link indisponibil"

                # Salvează datele în liste
                lista_titluri.append(title)
                lista_linkuri.append(link)

            # Verifică dacă există butonul de "Pagina următoare" și trece la următoarea pagină
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "div > ul > li.next > a")
                next_button.click()
                time.sleep(3)  # Așteaptă încărcarea paginii următoare
            except NoSuchElementException:
                print("Nu mai există o pagină următoare.")
                break  # Ieși din bucla while

        # Scrierea datelor în CSV după ce ai terminat de procesat toate paginile
        for t, p, l in zip(lista_titluri, lista_preturi, lista_linkuri):
            writer.writerow([t, p, l])

        logging.info(f'Fisierul {nume_csv} a fost creat cu succes!')
        driver.quit()  # Închide driver-ul după ce am terminat

toate_anunturile('https://books.toscrape.com/catalogue/category/books/mystery_3/index.html')

# driver = webdriver.Chrome()
# driver.get('https://books.toscrape.com/catalogue/category/books/mystery_3/index.html')
# anunturi = driver.find_elements(By.CSS_SELECTOR, 'ol.row > li')  # folosește selecția directă a articolelor
# for anunt in anunturi:
#     print(anunt.text)
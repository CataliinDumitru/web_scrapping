import time
import requests
from bs4 import BeautifulSoup
import lxml
import csv
import re
import logging
import sqlite3


# Importurile pentru Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, \
    StaleElementReferenceException

logging.basicConfig(
    filename='web_scaping.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)


conn = sqlite3.connect('Anunturi.db')
cursor = conn.cursor()

cursor.execute('''
                CREATE TABLE IF NOT EXISTS Anunturi(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titlu TEXT NOT NULL,
                pret INTEGER NOT NULL,
                link TEXT NOT NULL,
                status TEXT NOT NULL
                ) 
            ''')

conn.commit()
conn.close()




class WebScraping():

    def __init__(self, url):
        #Initiate the connexion with the server we want to get the data we want
        # and return a status code for the connexion

        '''This constructor takes a URL as an argument from wich is going to make the GET requests and look for the ads.'''
        self.url = url
        self.response = requests.get(self.url)
        self.lista_titluri_anunturi = []
        self.lista_preturi_anunturi = []
        self.lista_linkuri_anunturi = []

        if self.response.status_code == 200:
            logging.info("Am reusit sa extragem informatiile.")
        else:
            logging.error(f'A aparut o eroare: {self.response.status_code}')





    def titlu(self, tag):
        """Shows all the titles from the URL that the user choose."""

        self.soup = BeautifulSoup(self.response.content, 'lxml')
        self.titles = self.soup.select(tag)
        self.lista_titluri_anunturi = []
        for title in self.titles:
            if title:
                self.lista_titluri_anunturi.append(title.get_text())
        return self.lista_titluri_anunturi





    def pret(self, tag):
        """Shows all the prices from the URL that the user choose."""

        self.soup = BeautifulSoup(self.response.content, 'lxml')
        self.prices = self.soup.select(tag)
        self.lista_preturi_anunturi = []
        for price in self.prices:
            if price:
                pret_text = price.get_text().replace(' ', '')
                pret_numeric = re.split(r'leiPretulnegociabil|lei|€|\$', pret_text)[0].replace(',', '.')
                self.lista_preturi_anunturi.append(pret_numeric)
        return self.lista_preturi_anunturi

    #self.lista_preturi_anunturi.append(price.get_text().split(" lei")[0].replace(' ', ''))



    def link(self, tag):
        """Show all the links from the URL that the user choose."""

        self.soup = BeautifulSoup(self.response.content, 'lxml')
        self.links = self.soup.select(tag)
        self.lista_linkuri_anunturi = []
        for link in self.links:
            if link:
                linkul_final = link['href']
                if linkul_final.startswith('/d/oferta'):
                    linkul_final = 'https://www.olx.ro' + linkul_final
                    if linkul_final not in self.lista_linkuri_anunturi:
                        self.lista_linkuri_anunturi.append(linkul_final)
        return self.lista_linkuri_anunturi

    def toate_anunturile(self, url):
        # Liste pentru a stoca datele extrase
        lista_titluri = []
        lista_preturi = []
        lista_linkuri = []

        # Inițializează fișierul CSV
        nume_csv = input('Ce nume doriti sa aiba csv-ul dvs?\n')
        with open(nume_csv + '.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Citirea și scrierea antetului
            coloane_csv = input('Ce coloane doriti sa aibe fisierul dvs?\n').lower()
            header = [col.strip() for col in coloane_csv.split(',')]
            writer.writerow(header)

            # Initializează driver-ul
            driver = webdriver.Chrome()
            driver.get(url)

            # Accept cookie-uri (dacă este necesar)
            time.sleep(1)
            try:
                accept = driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler")
                accept.click()
            except NoSuchElementException:
                pass

            # Așteaptă încărcarea anunțurilor și extrage-le pagină cu pagină
            while True:
                time.sleep(2)  # Ajustează timpul de așteptare dacă e necesar

                # Extrage anunțurile de pe pagina curentă
                anunturi = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='l-card']")
                for anunt in anunturi:
                    try:
                        title = anunt.find_element(By.CSS_SELECTOR, ".css-1wxaaza").text
                    except NoSuchElementException:
                        title = "Titlu indisponibil"

                    try:
                        price = anunt.find_element(By.CSS_SELECTOR, "p.css-13afqrm").text
                        if price:
                            pret_text = price.replace(' ', '')
                            pret_numeric = re.split(r'leiPretulnegociabil|lei|€|£|\$', pret_text)[0].replace(',', '.')
                        else:
                            pret_numeric = "Preț indisponibil"
                    except NoSuchElementException:
                        pret_numeric = "Preț indisponibil"

                    try:
                        link = anunt.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    except NoSuchElementException:
                        link = "Link indisponibil"

                    lista_titluri.append(title)
                    lista_preturi.append(pret_numeric)
                    lista_linkuri.append(link)

                # Scrierea anunțurilor în fișierul CSV
                for t, p, l in zip(lista_titluri, lista_preturi, lista_linkuri):
                    writer.writerow([t, p, l])

                # Golește listele pentru a evita duplicarea
                lista_titluri.clear()
                lista_preturi.clear()
                lista_linkuri.clear()

                # Localizează și clic pe butonul "Pagina următoare"
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-cy='pagination-forward']"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(2)
                    next_button.click()
                    time.sleep(3)  # Așteaptă încărcarea noii pagini
                except (StaleElementReferenceException, TimeoutException):
                    print("Nu mai există o pagină următoare.")
                    break

            logging.info(f'Fisierul {nume_csv}.csv a fost creat cu succes!')
            driver.quit()


    def arata_anunturi(self):
        """Lists the pots in the console section."""

        titlu = self.lista_titluri_anunturi
        pret = self.lista_preturi_anunturi
        link = self.lista_linkuri_anunturi

        if not titlu or not pret or not link:
            logging.info("Nu sunt anunțuri de afișat.")
            return

        for t, p, l in zip(titlu, pret, link):
            print(f'Numele anuntului este: {t}\nPretul anuntului este: {p}\nLinkul catre anunt este: {l}\n{"-"*35}')


    def selection(self):

        """Take's a CSV file, open it, read it and ask what's the ammount of money you want to spend on the article you are looking for."""
        while True:
            alege_csv = input('Introduceti numele fisierului CSV.\n')
            try:
                with open(alege_csv + '.csv', mode='r', newline="", encoding='utf-8')as file:
                    reader = csv.reader(file)
                    try:
                        pret_tinta = int(input('Care este suma maxima pe care doriti sa o platiti?\n'))
                    except Exception as e:
                        logging.error(f'A aparut o eroare:{e}')

                    next(reader, None)
                    for row in reader:
                        try:
                            pret = float(row[1])
                            if pret <= pret_tinta:
                                print(f'Nume: {row[0]}\nPreț: {row[1]}\nLink: {row[2]}\n', '-'*35)

                        except ValueError:
                            logging.error("Unul dintre prețuri nu a putut fi convertit la întreg.")
                        except IndexError:
                            logging.error("Rândul nu conține suficiente coloane.")

            except FileNotFoundError:
                logging.error(f"Fisierul {alege_csv} nu a fost găsit.")
            except Exception as e:
                logging.error(f'A apărut o eroare: {e}')
            continuare = input("Doriți să căutați într-un alt fișier CSV? (da/nu): ").strip().lower()
            if continuare != 'da':
                break

    def store_in_db(self, file):

        '''This function storage data in a SQLite data base, giving info's about title, price, link's and status of the post'''


        with (open(file +'.csv', mode='r', newline='', encoding='utf-8') as document):
            reader = csv.DictReader(document)


            conn = sqlite3.connect('Anunturi.db')
            cursor = conn.cursor()
            for element in reader:
                titlul = element['titlu']
                pretul = element['pret']
                linkul = element['link']

                response = requests.get(linkul, timeout=5)
                if response.status_code == 200:
                    status = 'Activ'
                else:
                    status = 'Inactiv'

                cursor.execute('''
                        INSERT INTO Anunturi (titlu, pret, link, status)
                        VALUES(?, ?, ?, ?)
                ''',(titlul, pretul, linkul, status))

            conn.commit()
            conn.close()

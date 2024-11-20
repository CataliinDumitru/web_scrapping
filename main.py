import time
import requests
from bs4 import BeautifulSoup
import lxml
import csv
import re
import logging
import sqlite3


# Imports for Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, \
    StaleElementReferenceException

logging.basicConfig(
    filename='web_scraping.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)

class WebScraping:

    def __init__(self, url):
        #Initiate the connexion with the server we want to get the data we want
        # and return a status code for the connexion

        """This constructor takes a URL as an argument from wich is going to make the GET requests and look for the ads."""
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
        """Make a request with Selenium library, identify all the ads and extract the title, the price and the link of every ad. Create a CSV file with all the data thay had been extracted."""
        # List for the data's we're going to collect
        lista_titluri = []
        lista_preturi = []
        lista_linkuri = []

        # Initiating the CSV file
        nume_csv = input('Ce nume doriti sa aiba csv-ul dvs?\n')
        with open(nume_csv + '.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Reading and writting of the header
            coloane_csv = input('Ce coloane doriti sa aibe fisierul dvs?\n').lower()
            header = [col.strip() for col in coloane_csv.split(',')]
            writer.writerow(header)

            # Set up the drive
            driver = webdriver.Chrome()
            driver.get(url)

            # Accepting cookies (if needed)
            time.sleep(1)
            try:
                accept = driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler")
                accept.click()
            except NoSuchElementException:
                pass

            # Waits for the ads to load up and then extract the information page by page
            while True:
                time.sleep(2)  # Ajustează timpul de așteptare dacă e necesar

                # Extract the ads from the current page
                anunturi = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='l-card']")
                for anunt in anunturi:
                    try:
                        title = anunt.find_element(By.CSS_SELECTOR, "h4.css-1s3qyje").text
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

                # Writting the ads in the CSV file
                for t, p, l in zip(lista_titluri, lista_preturi, lista_linkuri):
                    writer.writerow([t, p, l])

                # Empty the lists to aviod a duplicate ad
                lista_titluri.clear()
                lista_preturi.clear()
                lista_linkuri.clear()

                # Locate and click the ''Next page'' button
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-cy='pagination-forward']"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(2)
                    next_button.click()
                    time.sleep(3)
                except (StaleElementReferenceException, TimeoutException):
                    print("Nu mai există o pagină următoare.")
                    break

            logging.info(f'Fisierul {nume_csv}.csv a fost creat cu succes!')
            driver.quit()


    def arata_anunturi(self):
        """Lists the ads from ONE SINGLE PAGE in the console section."""

        #Initiate the lists from the constructor so we can stoarge the data
        titlu = self.lista_titluri_anunturi
        pret = self.lista_preturi_anunturi
        link = self.lista_linkuri_anunturi

        #Checks if on the provided URL are title, prices or link's to extract
        if not titlu or not pret or not link:
            logging.info("Nu sunt anunțuri de afișat.")
            return

        for t, p, l in zip(titlu, pret, link):
            print(f'Numele anuntului este: {t}\nPretul anuntului este: {p}\nLinkul catre anunt este: {l}\n{"-"*35}')

    def selection(self):
        """Take's a CSV file, open it, read it and ask what's the amount of money you want to spend on the article you are looking for."""
        while True:
            alege_csv = input('Introduceți numele fișierului CSV fără extensie.\n')
            try:
                with open(alege_csv + '.csv', mode='r', newline="", encoding='utf-8') as file:
                    reader = csv.reader(file)
                    try:
                        pret_tinta = float(input('Care este suma maximă pe care doriți să o plătiți?\n'))
                    except ValueError:
                        logging.error('Valoarea introdusă pentru preț nu este validă. Introduceți un număr.')
                        continue

                    # Skip the header
                    next(reader, None)

                    # Gather all the ads
                    articole = []
                    for row in reader:
                        try:
                            pret = float(row[1])
                            if pret <= pret_tinta:
                                articole.append((row[0], pret, row[2]))
                        except ValueError:
                            logging.error("Unul dintre prețuri nu a putut fi convertit la număr.")
                        except IndexError:
                            logging.error("Rândul nu conține suficiente coloane.")

                    # Sort the ads by price
                    articole.sort(key=lambda x: x[1], reverse=True)

                    # Show the ads
                    if articole:
                        for articol in articole:
                            print(f'Nume: {articol[0]}\nPreț: {articol[1]}\nLink: {articol[2]}\n', '-' * 35)
                    else:
                        print("Nu s-au găsit articole în limita de preț specificată.")

            except FileNotFoundError:
                logging.error(f"Fișierul {alege_csv}.csv nu a fost găsit.")
            except Exception as e:
                logging.error(f'A apărut o eroare: {e}')

            continuare = input("Doriți să căutați într-un alt fișier CSV? (da/nu): ").strip().lower()
            if continuare != 'da':
                break


    def store_in_db(self, file):
        """This function stores data in a SQLite database, including title, price, link, and status of the post."""
        try:
            with open(file + '.csv', mode='r', newline='', encoding='utf-8') as document:
                reader = csv.DictReader(document)

                # Connect to the database
                conn = sqlite3.connect('Anunturi.db')
                cursor = conn.cursor()

                # Create the table if not exists
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Anunturi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titlu TEXT NOT NULL,
                        pret INTEGER NOT NULL,
                        link TEXT NOT NULL UNIQUE, 
                        status TEXT NOT NULL
                    )
                ''')
                conn.commit()

                # Iterate through the lists
                for element in reader:
                    titlul = element.get('titlu')
                    pretul = element.get('pret')
                    linkul = element.get('link')

                    # Checks data
                    if not titlul or not pretul or not linkul:
                        logging.warning("Rând ignorat din cauza datelor lipsă: %s", element)
                        continue

                    try:
                        pret_numeric = int(float(pretul))  # Conversie la întreg
                    except ValueError:
                        logging.error("Preț invalid: %s", pretul)
                        continue

                    # Checks the status of the link
                    try:
                        response = requests.get(linkul, timeout=10)
                        status = 'Activ' if response.status_code == 200 else 'Inactiv'
                    except requests.RequestException:
                        status = 'Inactiv'

                    # Insert the data into the database and checks if there are duplicates
                    cursor.execute('''
                        INSERT OR IGNORE INTO Anunturi (titlu, pret, link, status)
                        VALUES (?, ?, ?, ?)
                    ''', (titlul, pret_numeric, linkul, status))

                # Save and close
                conn.commit()
                conn.close()
        finally:
                logging.info(f"Datele au fost stocate cu succes în baza de date {file}.")
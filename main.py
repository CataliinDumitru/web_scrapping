import requests
from bs4 import BeautifulSoup
import lxml
import csv
import re
import logging


logging.basicConfig(
    filename='web_scaping.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)


class WebScraping():

    def __init__(self, url):
        #Initiate the connexion with the server we want to get the data we want
        # and return a status code for the connexion
        self.url = url
        self.response = requests.get(self.url)
        self.lista_titluri_anunturi = []
        self.lista_preturi_anunturi = []
        self.lista_linkuri_anuntrui = []
        self.lista_linkuri_finala = []
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
        self.lista_linkuri_anuntrui = []
        for link in self.links:
            if link:
                linkul_final = link['href']
                if linkul_final.startswith('/d/oferta'):
                    linkul_final = 'https://www.olx.ro' + linkul_final
                    self.lista_linkuri_anuntrui.append(linkul_final)

        #lista_linkuri_finala reprezinta lista in care functia link returneaza lista finala a linkurilor.
        #neavand bucata de cod de mai jos, functia ar returna o lista duplicata de linkuri.

        self.lista_linkuri_finala = [self.lista_linkuri_anuntrui[0]]
        for i in range(1, len(self.lista_linkuri_anuntrui)):
            if self.lista_linkuri_anuntrui[i] != self.lista_linkuri_anuntrui[i-1]:
                self.lista_linkuri_finala.append(self.lista_linkuri_anuntrui[i])
        return self.lista_linkuri_finala




    def arata_anunturi(self,titlu, pret, link):
        """Lists the pots in the console section."""

        titlu = titlu
        pret = pret
        link = link

        if not titlu or not pret or not link:
            logging.info("Nu sunt anunțuri de afișat.")
            return

        for t, p, l in zip(titlu, pret, link):
            logging.info(f'Numele anuntului este: {t}\nPretul anuntului este: {p}\nLinkul catre anunt este: {l}\n{"-"*35}')



    def create_csv(self):
        """Creates a CSV file as a way to organize and storage the data that just been scrapped."""
        nume_csv = input('Ce nume doriti sa aiba csv-ul dvs?\n')
        try:
            with open(nume_csv + '.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)


                coloane_csv = input('Ce coloane doriti sa aibe fisierul dvs?\n')
                header = [col.strip() for col in coloane_csv.split(',')]
                writer.writerow(header)

                for t, p, l in zip(self.lista_titluri_anunturi, self.lista_preturi_anunturi, self.lista_linkuri_finala):
                    writer.writerow([t, p, l])
                logging.info(f'Fisierul {nume_csv} a fost creat cu succes!')
        except Exception as e:
            logging.error(f'A aparut o eroare la crearea fisierului csv. {e}')


    def selection(self,):

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
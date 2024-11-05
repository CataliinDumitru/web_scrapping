import requests
from bs4 import BeautifulSoup
import lxml
import csv

class WebScraping():

    def __init__(self, url):
        #Initiaza conexiunea cu serverul de pe care vrem sa luam datele
        # si returneaza un status_code pentru a vedea in ce stadiu este conexiunea
        self.url = url
        self.response = requests.get(self.url)
        self.lista_titluri_anunturi = []
        self.lista_preturi_anunturi = []
        self.lista_linkuri_anuntrui = []
        self.lista_linkuri_finala = []
        if self.response.status_code == 200:
            print("Am reusit sa extragem informatiile.")
        else:
            print(f'A aparut o eroare: {self.response.status_code}')





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
                self.lista_preturi_anunturi.append(price.get_text())
        return self.lista_preturi_anunturi




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
            print("Nu sunt anunțuri de afișat.")
            return

        for t, p, l in zip(titlu, pret, link):
            print(f'Numele anuntului este: {t}\nPretul anuntului este: {p}\nLinkul catre anunt este: {l}\n{"-"*35}')



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
                print(f'Fisierul {nume_csv} a fost creat cu succes!')
        except Exception as e:
            print(f'A aparut o eroare la crearea fisierului csv. {e}')


    def selection(self,):

        alege_csv = input('Introduceti numele fisierului CSV.\n')
        try:
            with open(alege_csv + '.csv', mode='r', newline="", encoding='utf-8')as file:
                reader = csv.reader(file)
                try:
                    pret_tinta = int(input('Care este suma maxima pe care doriti sa o platiti?\n'))
                except Exception as e:
                    print(f'A aparut o eroare:{e}')

                next(reader, None)
                for row in reader:
                    try:
                        pret = int(row[1])
                        if pret <= pret_tinta:
                            print(f'Nume: {row[0]}, Preț: {row[1]}, Link: {row[2]}\n', '-'*35)
                    except ValueError:
                        print("Unul dintre prețuri nu a putut fi convertit la întreg.")
                    except IndexError:
                        print("Rândul nu conține suficiente coloane.")

        except FileNotFoundError:
            print(f"Fisierul {alege_csv} nu a fost găsit.")
        except Exception as e:
            print(f'A apărut o eroare: {e}')
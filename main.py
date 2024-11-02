import requests
from bs4 import BeautifulSoup
import lxml

class WebScraping():

    def __init__(self, url):
        #Initiaza conexiunea cu serverul de pe care vrem sa luam datele
        # si returneaza un status_code pentru a vedea in ce stadiu este conexiunea
        self.url = url
        self.response = requests.get(self.url)
        self.lista_titluri_anunturi = []
        self.lista_preturi_anunturi = []
        self.lista_linkuri_anuntrui = []
        if self.response.status_code == 200:
            print("Am reusit sa extragem informatiile.")
        else:
            print(f'A aparut o eroare: {self.response.status_code}')


    def titlu(self, tag):
        self.soup = BeautifulSoup(self.response.content, 'lxml')
        self.titles = self.soup.select(tag)
        self.lista_titluri_anunturi = []
        for title in self.titles:
            if title:
                self.lista_titluri_anunturi.append(title.get_text())
        return self.lista_titluri_anunturi

    def pret(self, tag):
        self.soup = BeautifulSoup(self.response.content, 'lxml')
        self.prices = self.soup.select(tag)
        self.lista_preturi_anunturi = []
        for price in self.prices:
            if price:
                self.lista_preturi_anunturi.append(price.get_text())
        return self.lista_preturi_anunturi

    def link(self, tag):
        self.soup = BeautifulSoup(self.response.content, 'lxml')
        self.links = self.soup.select(tag)
        self.lista_linkuri_anuntrui = []
        for link in self.links:
            if link:
                linkul_final = link['href']
                if linkul_final.startswith('/d/oferta'):
                    linkul_final = 'https://www.olx.ro' + linkul_final
                    self.lista_linkuri_anuntrui.append(linkul_final)
        return self.lista_linkuri_anuntrui

    def arata_anunturi(self,titlu, pret, link):
        titlu = titlu
        pret = pret
        link = link

        if not titlu or not pret or not link:
            print("Nu sunt anunțuri de afișat.")
            return

        for t, p, l in zip(titlu, pret, link):
            print(f'Numele anuntului este: {t}\nPretul anuntului este: {p}\nLinkul catre anunt este: {l}\n{"-"*35}')
The WebScraping class is used to extract, process, and store information from a web page containing advertisements, leveraging libraries such as requests, BeautifulSoup, Selenium, and sqlite3. Its main functionality includes extracting titles, prices, and links from web pages, saving them to CSV files or SQLite databases, and processing them based on user-specified criteria.


Initializes the class with a URL, performs an HTTP GET request to fetch the page's content, and logs the connection status.

def __init__(self, url):
    ...
    # Initialize lists to store titles, prices, and links
    self.lista_titluri_anunturi = []
    self.lista_preturi_anunturi = []
    self.lista_linkuri_anunturi = []

    # Check server response
    if self.response.status_code == 200:
        logging.info("Successfully fetched the information.")
    else:
        logging.error(f'An error occurred: {self.response.status_code}')



Method: titlu

Extracts advertisement titles using a specific CSS selector.

def titlu(self, tag):
    """Extracts all titles from the specified page."""
    ...
    for title in self.titles:
        if title:
            self.lista_titluri_anunturi.append(title.get_text())

Additional Comments:

Ensure the provided CSS selector is valid for the targeted page.
Handle cases where no titles are found.




Method: pret
Extracts and cleans advertisement prices by removing spaces and symbols.

def pret(self, tag):
    """Extracts all prices from the specified page."""
    ...
    for price in self.prices:
        if price:
            pret_text = price.get_text().replace(' ', '')
            pret_numeric = re.split(r'leiPretulnegociabil|lei|€|\$', pret_text)[0].replace(',', '.')
            self.lista_preturi_anunturi.append(pret_numeric)
Additional Comments:

The regular expression for removing symbols could be made more robust.
Add checks for missing or improperly formatted prices.





Method: link
Constructs absolute URLs for each advertisement and saves them to a list.

def link(self, tag):
    """Extracts all links from the specified page."""
    ...
    for link in self.links:
        if link:
            linkul_final = link['href']
            if linkul_final.startswith('/d/oferta'):
                linkul_final = 'https://www.olx.ro' + linkul_final
                if linkul_final not in self.lista_linkuri_anunturi:
                    self.lista_linkuri_anunturi.append(linkul_final)
Additional Comments:

Validate all links before adding them to the list.





Method: toate_anunturile
Uses Selenium to navigate through pages on a website, extracting and storing advertisements in a CSV file.

def toate_anunturile(self, url):
    """Extracts advertisements from all pages and stores them in a CSV file."""
    ...
    while True:
        # Extract advertisements from the current page
        anunturi = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='l-card']")
        ...
        # Locate and click the "Next Page" button
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-cy='pagination-forward']"))
            )
            next_button.click()
        except (StaleElementReferenceException, TimeoutException):
            print("No more pages available.")
            break
Additional Comments:

Handle cases where elements fail to load completely.
Add a timeout check for page loading.






Method: arata_anunturi
Lists all extracted advertisements from a single page in the console.

def arata_anunturi(self):
    """Displays extracted advertisements in the console."""
    ...
    for t, p, l in zip(titlu, pret, link):
        print(f'Ad title: {t}\nAd price: {p}\nAd link: {l}\n{"-"*35}')





Method: selection
Allows the user to filter advertisements from a CSV file based on a maximum price.

def selection(self):
    """Filters advertisements from a CSV file based on a target price."""
    ...
    articole.sort(key=lambda x: x[1], reverse=True)
    ...
    print("No items found within the specified price range.")
Additional Comments:

Add validations for missing or invalid data in the CSV file.






Method: store_in_db
Stores advertisements in a SQLite database and checks if the links are active.

def store_in_db(self, file):
    """Stores advertisement data in a SQLite database."""
    ...
    for element in reader:
        ...
        # Insert into database, ignoring duplicates
        cursor.execute('''
            INSERT OR IGNORE INTO Anunturi (titlu, pret, link, status)
            VALUES (?, ?, ?, ?)
        ''', (titlul, pret_numeric, linkul, status))
Additional Comments:

Add extra validation for CSV fields before storing them in the database.
Improve error handling for HTTP connections.
















            

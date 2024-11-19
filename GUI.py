from tkinter import Tk, Label, Entry, Button, Text, Scrollbar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper GUI")

        # URL input
        Label(root, text="Enter URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_entry = Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        # Preț maxim input
        Label(root, text="Maximum Price (optional):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.price_entry = Entry(root, width=20)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Butoane principale
        Button(root, text="Scrape Ads", command=self.scrape_ads_selenium).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        Button(root, text="Show All Ads", command=self.show_all_ads).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        Button(root, text="Show Filtered Ads", command=self.show_filtered_ads).grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Text area pentru afișare
        self.text_area = Text(root, wrap="word", height=20, width=70)
        self.text_area.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        # Scrollbar pentru text area
        scrollbar = Scrollbar(root, command=self.text_area.yview)
        scrollbar.grid(row=3, column=3, sticky="ns")
        self.text_area.configure(yscrollcommand=scrollbar.set)

        # Variabile pentru date
        self.ads_data = []

    def scroll_to_bottom(self, driver):
        """Derulează pagina până jos pentru încărcarea completă."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Derulează până jos
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Așteaptă pentru încărcarea elementelor

            # Verifică dacă s-a ajuns la capăt
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def navigate_and_scrape(self, driver, ads_data):
        """Navighează între pagini și colectează anunțurile."""
        while True:
            # Derulează pagina curentă
            self.scroll_to_bottom(driver)

            # Adună anunțurile din pagina curentă
            ads = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='l-card']")
            for ad in ads:
                try:
                    title = ad.find_element(By.CSS_SELECTOR, "h4.css-1s3qyje").text
                except NoSuchElementException:
                    title = "Title unavailable"

                try:
                    price = ad.find_element(By.CSS_SELECTOR, "p.css-13afqrm").text
                    price = price.replace(' ', '').split("lei")[0]
                except NoSuchElementException:
                    price = "Price unavailable"

                try:
                    link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except NoSuchElementException:
                    link = "Link unavailable"

                ads_data.append({"title": title, "price": price, "link": link})

            # Încearcă să navighezi la pagina următoare
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
                next_button.click()
                time.sleep(3)  # Așteaptă încărcarea noii pagini
            except NoSuchElementException:
                break  # Ieși din buclă dacă nu mai există butonul "Next"

    def scrape_ads_selenium(self):
        """Scrape ads using Selenium, navigating through multiple pages."""
        url = self.url_entry.get().strip()
        if not url:
            self.text_area.insert("end", "Please enter a valid URL.\n")
            return

        # Configure Selenium WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        try:
            driver.get(url)

            # Accept cookies if necessary
            try:
                accept_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#onetrust-accept-btn-handler"))
                )
                accept_button.click()
            except TimeoutException:
                pass  # Ignore if no cookies banner

            # Initialize storage for ads data
            self.ads_data = []

            while True:  # Loop through pages
                time.sleep(2)  # Adjust time if necessary

                # Scroll the page to ensure all ads are loaded
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Extract ads from the current page
                ads = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='l-card']")
                if not ads:
                    self.text_area.insert("end", "No ads found on the page.\n")
                    break

                for ad in ads:
                    try:
                        title = ad.find_element(By.CSS_SELECTOR, "h4.css-1s3qyje").text
                    except NoSuchElementException:
                        title = "Title unavailable"

                    try:
                        price = ad.find_element(By.CSS_SELECTOR, "p.css-13afqrm").text
                        price = price.replace(' ', '').split("lei")[0] if "lei" in price else price
                    except NoSuchElementException:
                        price = "Price unavailable"

                    try:
                        link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    except NoSuchElementException:
                        link = "Link unavailable"

                    self.ads_data.append({"title": title, "price": price, "link": link})

                # Attempt to click the "Next Page" button
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-cy='pagination-forward']"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(2)
                    next_button.click()
                except TimeoutException:
                    self.text_area.insert("end", "No more pages available.\n")
                    break

            # Display the number of ads scraped
            self.text_area.insert("end", f"Scraped {len(self.ads_data)} ads successfully.\n")

        except Exception as e:
            self.text_area.insert("end", f"An error occurred: {e}\n")
        finally:
            driver.quit()

    def show_all_ads(self):
        """Display all scraped ads."""
        if not self.ads_data:
            self.text_area.insert("end", "No ads available to display. Please scrape first.\n")
            return

        self.text_area.delete("1.0", "end")  # Golește zona de text
        for ad in self.ads_data:
            self.text_area.insert(
                "end",
                f"Title: {ad['title']}\nPrice: {ad['price']}\nLink: {ad['link']}\n{'-' * 40}\n"
            )

    def show_filtered_ads(self):
        """Display ads filtered by maximum price."""
        if not self.ads_data:
            self.text_area.insert("end", "No ads available to filter. Please scrape first.\n")
            return

        try:
            max_price = float(self.price_entry.get().strip())
        except ValueError:
            self.text_area.insert("end", "Please enter a valid maximum price.\n")
            return

        # Filtrare anunțuri după preț
        filtered_ads = [
            ad for ad in self.ads_data if
            ad["price"].replace(" ", "").replace(",", "").replace("lei", "").isdigit() and float(
                ad["price"].replace(",", ".")) <= max_price
        ]

        if not filtered_ads:
            self.text_area.insert("end", f"No ads found under the price {max_price}.\n")
            return

        self.text_area.delete("1.0", "end")  # Golește zona de text
        for ad in filtered_ads:
            self.text_area.insert(
                "end",
                f"Title: {ad['title']}\nPrice: {ad['price']}\nLink: {ad['link']}\n{'-' * 40}\n"
            )

# Pornirea aplicației
if __name__ == "__main__":
    root = Tk()
    gui = WebScraperGUI(root)
    root.mainloop()
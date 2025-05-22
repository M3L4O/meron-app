from dataclasses import dataclass
from random import uniform
from time import sleep
from uuid import uuid4

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scraper.models import Volatile


@dataclass
class KabumScraper:
    url_base = "https://www.kabum.com.br/hardware/{}?page_number={}&page_size={}"
    path_component = {
        "cpu": "processadores",
        "gpu": "placa-de-video-vga",
        "motherboard": "placas-mae",
        "ram": "memoria-ram",
        "storage": ["disco-rigido-hd", "ssd-2-5"],
        "psu": "fontes",
    }
    page_size = 100

    def __post_init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(service=Service(), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.driver.set_page_load_timeout(60)

    def get_pages(self):
        try:
            pages = self.driver.find_elements(By.CSS_SELECTOR, ".page")
            return max(
                (int(page.text) for page in pages if page.text.isdigit()), default=1
            )
        except:
            return 1

    def get_page_info(self, kind: str):
        components = []
        products = self.driver.find_elements(By.CSS_SELECTOR, ".productCard")
        for product in products:
            try:
                model = product.find_element(By.CSS_SELECTOR, ".nameCard").text
                price_text = (
                    product.find_element(By.CSS_SELECTOR, ".priceCard")
                    .text.replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                    .strip()
                )
                price = float(price_text)
                components.append(
                    {"model": model, "price": price, "kind": kind, "availability": True}
                )
            except Exception as e:
                print(f"Erro ao processar produto: {e}")
        return components

    def scrape_category(self, category: str, kind: str, retries=3):
        components = []
        url = self.url_base.format(category, 1, self.page_size)

        attempt = 0
        while attempt < retries:
            try:
                self.driver.get(url)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".productCard")))
                max_page = self.get_pages()
                break
            except TimeoutException:
                attempt += 1
                print(f"Timeout na página inicial {category}, tentativa {attempt}/{retries}")
                sleep(uniform(5, 7))
                if attempt == retries:
                    print(f"Falha ao carregar categoria {category} após {retries} tentativas. Pulando.")
                    return []

        for page_number in range(1, max_page + 1):
            url = self.url_base.format(category, page_number, self.page_size)
            attempt = 0
            while attempt < retries:
                try:
                    print(f"Raspando a Url: {url}")
                    self.driver.get(url)
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".productCard")))
                    components.extend(self.get_page_info(kind))
                    break
                except TimeoutException:
                    attempt += 1
                    print(f"Timeout na página {page_number} da categoria {category}, tentativa {attempt}/{retries}")
                    sleep(uniform(5, 7))
                    if attempt == retries:
                        print(f"Pulando página {page_number} da categoria {category} após {retries} tentativas.")
            sleep(uniform(5, 7))

        return components

    def scraping(self):
        all_components = []
        for kind, categories in self.path_component.items():
            print(f"Raspando {kind.upper()}............")
            categories = categories if isinstance(categories, list) else [categories]
            for category in categories:
                all_components.extend(self.scrape_category(category, kind))

            sleep(uniform(10, 30))

        volatile_objects = [
            Volatile(
                id=uuid4(),
                model=comp["model"],
                price=comp["price"],
                availability=comp["availability"],
                kind=comp["kind"],
            )
            for comp in all_components
        ]
        Volatile.objects.bulk_create(volatile_objects, batch_size=100)

        self.driver.quit()
        return all_components

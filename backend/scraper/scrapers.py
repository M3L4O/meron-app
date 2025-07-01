import shutil
from dataclasses import dataclass, field
from random import uniform
from time import sleep

from django.utils import timezone
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth


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
    source_name = "Kabum"

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
        components_data = []
        products = self.driver.find_elements(By.CSS_SELECTOR, ".productCard")
        for product in products:
            try:
                product_name = product.find_element(By.CSS_SELECTOR, ".nameCard").text
                try:
                    url_element = product.find_element(By.CSS_SELECTOR, "a.productLink")
                except NoSuchElementException:
                    url_element = product.find_element(By.CSS_SELECTOR, ".nameCard a")

                product_url = url_element.get_attribute("href")

                price_element = product.find_element(By.CSS_SELECTOR, ".priceCard")
                price_text = (
                    price_element.text.replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                    .strip()
                )
                price = float(price_text)
                availability = True

                components_data.append(
                    {
                        "product_name_on_source": product_name,
                        "price": price,
                        "availability": availability,
                        "url": product_url,
                        "kind": kind,
                        "source_name": self.source_name,
                    }
                )
            except NoSuchElementException:
                try:
                    product_name_on_source = product.find_element(
                        By.CSS_SELECTOR, ".nameCard"
                    ).text
                    product_url = product.find_element(
                        By.CSS_SELECTOR, ".productCard a"
                    ).get_attribute("href")
                    components_data.append(
                        {
                            "product_name_on_source": product_name_on_source,
                            "price": 0.0,
                            "availability": False,
                            "url": product_url,
                            "kind": kind,
                            "source_name": self.source_name,
                        }
                    )
                    print(
                        f"Produto '{product_name_on_source}' detectado como indisponível/sem preço na Kabum."
                    )
                except Exception as e_inner:
                    print(
                        f"Erro ao processar produto (provavelmente indisponível) e capturar nome/URL: {e_inner}"
                    )
            except Exception as e:
                print(f"Erro inesperado ao processar produto no card: {e}")

        return components_data

    def scrape_category(self, category: str, kind: str, retries=3):
        components = []
        url = self.url_base.format(category, 1, self.page_size)

        attempt = 0
        while attempt < retries:
            try:
                self.driver.get(url)
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".productCard"))
                )
                max_page = self.get_pages()
                break
            except TimeoutException:
                attempt += 1
                print(
                    f"Timeout na página inicial {category}, tentativa {attempt}/{retries}"
                )
                sleep(uniform(5, 7))
                if attempt == retries:
                    print(
                        f"Falha ao carregar categoria {category} após {retries} tentativas. Pulando."
                    )
                    return []

        for page_number in range(1, max_page + 1):
            url = self.url_base.format(category, page_number, self.page_size)
            attempt = 0
            while attempt < retries:
                try:
                    print(f"Raspando a Url: {url}")
                    self.driver.get(url)
                    self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".productCard")
                        )
                    )
                    components.extend(self.get_page_info(kind))
                    break
                except TimeoutException:
                    attempt += 1
                    print(
                        f"Timeout na página {page_number} da categoria {category}, tentativa {attempt}/{retries}"
                    )
                    sleep(uniform(5, 7))
                    if attempt == retries:
                        print(
                            f"Pulando página {page_number} da categoria {category} após {retries} tentativas."
                        )
            sleep(uniform(5, 7))

        return components

    def scraping(self):
        all_scraped_data = []
        for kind, categories in self.path_component.items():
            print(f"Raspando {kind.upper()}............")
            categories = categories if isinstance(categories, list) else [categories]
            for category in categories:
                scraped_category_data = self.scrape_category(category, kind)
                all_scraped_data.extend(scraped_category_data)

            sleep(uniform(10, 30))

        self.driver.quit()
        return all_scraped_data


# @dataclass
# class PichauScraper:
#     url_base = "https://www.pichau.com.br/hardware/{}?page={}"
#     path_component = {
#         "cpu": "processadores",
#         "gpu": "placa-de-video",
#         "motherboard": "placa-m-e",
#         "ram": "memorias",
#         "storage": ["hard-disk-e-ssd", "ssd"],
#         "psu": "fonte",
#     }
#     source_name = "Pichau"

#     def __post_init__(self):
#         chrome_options = Options()
#         # chrome_options.add_argument("--disable-dev-shm-usage")
#         # chrome_options.add_argument("--headless=new")
#         # chrome_options.add_argument("--disable-gpu")
#         # chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument(
#             "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/124.0.0.0 Safari/537.36"
#         )

#         self.driver = webdriver.Chrome(service=Service(), options=chrome_options)
#         self.wait = WebDriverWait(self.driver, 30)
#         self.driver.set_page_load_timeout(60)

#     def get_pages(self):
#         try:
#             pages = self.driver.find_elements(By.CSS_SELECTOR, ".MuiPaginationItem-page")
#             return max(
#                 (int(page.text) for page in pages if page.text.isdigit()), default=1
#             )
#         except:
#             return 1

#     def get_page_info(self, kind: str):
#         components_data = []
#         products = self.driver.find_elements(By.CSS_SELECTOR, ".mui-p3mq1s")
#         for product in products:
#             try:
#                 product_name = product.find_element(By.CSS_SELECTOR, ".mui-1jecgbd-product_info_title-noMarginBottom").text
#                 url_element = product.find_element(By.CSS_SELECTOR, ".mui-p3mq1s a")

#                 product_url = url_element.get_attribute("href")

#                 price_element = product.find_element(By.CSS_SELECTOR, ".mui-1q2ojdg-price_vista")
#                 price_text = (
#                     price_element.text.replace("R$ ", "")
#                     .replace(".", "")
#                     .replace(",", ".")
#                     .strip()
#                 )
#                 price = float(price_text)
#                 availability = True

#                 components_data.append(
#                     {
#                         "product_name_on_source": product_name,
#                         "price": price,
#                         "availability": availability,
#                         "url": product_url,
#                         "kind": kind,
#                         "source_name": self.source_name,
#                     }
#                 )
#             except NoSuchElementException:
#                 try:
#                     product_name_on_source = product.find_element(
#                         By.CSS_SELECTOR, ".nameCard"
#                     ).text
#                     product_url = product.find_element(
#                         By.CSS_SELECTOR, ".productCard a"
#                     ).get_attribute("href")
#                     components_data.append(
#                         {
#                             "product_name_on_source": product_name_on_source,
#                             "price": 0.0,
#                             "availability": False,
#                             "url": product_url,
#                             "kind": kind,
#                             "source_name": self.source_name,
#                         }
#                     )
#                     print(
#                         f"Produto '{product_name_on_source}' detectado como indisponível/sem preço na Pichau."
#                     )
#                 except Exception as e_inner:
#                     print(
#                         f"Erro ao processar produto (provavelmente indisponível) e capturar nome/URL: {e_inner}"
#                     )
#             except Exception as e:
#                 print(f"Erro inesperado ao processar produto no card: {e}")

#         return components_data

#     def scrape_category(self, category: str, kind: str, retries=3):
#         components = []
#         url = self.url_base.format(category, 1)

#         attempt = 0
#         while attempt < retries:
#             try:
#                 self.driver.get(url)
#                 self.wait.until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, ".mui-p3mq1s"))
#                 )
#                 max_page = self.get_pages()
#                 break
#             except TimeoutException:
#                 attempt += 1
#                 print(
#                     f"Timeout na página inicial {category}, tentativa {attempt}/{retries}"
#                 )
#                 sleep(uniform(15, 20))
#                 if attempt == retries:
#                     print(
#                         f"Falha ao carregar categoria {category} após {retries} tentativas. Pulando."
#                     )
#                     return []

#         sleep(uniform(15, 20))

#         for page_number in range(1, max_page + 1):
#             url = self.url_base.format(category, page_number)
#             attempt = 0
#             while attempt < retries:
#                 try:
#                     print(f"Raspando a Url: {url}")
#                     self.driver.get(url)
#                     self.wait.until(
#                         EC.presence_of_element_located(
#                             (By.CSS_SELECTOR, ".mui-p3mq1s")
#                         )
#                     )
#                     components.extend(self.get_page_info(kind))
#                     print(components)
#                     break
#                 except TimeoutException:
#                     attempt += 1
#                     print(
#                         f"Timeout na página {page_number} da categoria {category}, tentativa {attempt}/{retries}"
#                     )
#                     sleep(uniform(15, 20))
#                     if attempt == retries:
#                         print(
#                             f"Pulando página {page_number} da categoria {category} após {retries} tentativas."
#                         )
#             sleep(uniform(15,25))

#         return components


#     def scraping(self):
#         all_scraped_data = []
#         for kind, categories in self.path_component.items():
#             print(f"Raspando {kind.upper()}............")
#             categories = categories if isinstance(categories, list) else [categories]
#             for category in categories:
#                 scraped_category_data = self.scrape_category(category, kind)
#                 all_scraped_data.extend(scraped_category_data)

#             sleep(uniform(10, 30))


#         self.driver.quit()
#         return all_scraped_data
@dataclass
class PichauScraper:
    url_base: str = "https://www.pichau.com.br/hardware/{}?page={}"
    path_component: dict = field(
        default_factory=lambda: {
            "cpu": "processadores",
            "gpu": "placa-de-video",
            "motherboard": "placa-m-e",
            "ram": "memorias",
            "storage": ["hard-disk-e-ssd", "ssd"],
            "psu": "fonte",
        }
    )
    source_name: str = "Pichau"

    def __post_init__(self):
        print(
            "Instância do PichauScraper criada. O driver será gerenciado pelo método scraping."
        )

    def _initialize_driver(self):
        """
        Método auxiliar privado para criar e configurar uma nova instância do driver.
        """
        print(f"\n[{timezone.now()}] Inicializando uma nova instância do navegador...")

        chrome_options = Options()
        ua = UserAgent()
        user_agent = ua.random

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(service=Service(), options=chrome_options)

        stealth(
            driver,
            languages=["pt-BR", "pt"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        print(f"[{timezone.now()}] Nova instância do navegador pronta.")
        return driver

    def cleanup(self):
        """
        Método de limpeza para fechar o driver do Chrome e apagar a pasta
        do perfil temporário. Deve ser chamado no final de cada tarefa.
        """
        print(f"[{timezone.now()}] Iniciando limpeza dos recursos do scraper...")

        if hasattr(self, "driver") and self.driver:
            self.driver.quit()
            print(f"[{timezone.now()}] Driver do Chrome fechado.")

        if hasattr(self, "profile_path") and self.profile_path:
            try:
                shutil.rmtree(self.profile_path)
                print(
                    f"[{timezone.now()}] Pasta de perfil temporário removida: {self.profile_path}"
                )
            except OSError as e:
                print(
                    f"[{timezone.now()}] Erro ao remover a pasta de perfil {self.profile_path}: {e}"
                )

    def scrape_category(self, driver, wait, category: str, kind: str, retries=3):
        """
        Versão corrigida que aceita 'driver' e 'wait' como argumentos.
        """
        components = []
        url = self.url_base.format(category, 1)
        print(f"Iniciando raspagem da categoria '{category}' em: {url}")

        attempt = 0
        while attempt < retries:
            try:
                driver.get(url)
                wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".mui-p3mq1s")
                    )
                )
                break
            except TimeoutException:
                attempt += 1
                print(
                    f"Timeout na página inicial {category}, tentativa {attempt}/{retries}"
                )
                if attempt == retries:
                    print(f"Falha ao carregar categoria {category}. Pulando.")
                    return []

        page_count = 1

        while True:
            print(f"Raspando dados da página {page_count}...")
            page_data = self.get_page_info(driver, kind)
            if page_data:
                components.extend(page_data)
                print(f"Encontrados {len(page_data)} componentes.")
            else:
                print(f"Nenhum componente encontrado na página {page_count}.")

            sleep(uniform(8, 15))

            try:
                next_button = driver.find_element(
                    By.CSS_SELECTOR, 'button[aria-label="Go to next page"]'
                )
                if not next_button.is_enabled():
                    print("Botão 'próxima página' desabilitado. Fim da categoria.")
                    break

                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                sleep(uniform(1, 2))
                driver.execute_script("arguments[0].click();", next_button)

                print("Clicado no botão 'próxima página'.")
                page_count += 1
                sleep(uniform(10, 15))
            except NoSuchElementException:
                print("Não foi encontrado o botão 'próxima página'. Fim da categoria.")
                break
            except Exception as e:
                print(f"Ocorreu um erro ao tentar ir para a próxima página: {e}")
                break

        return components

    def get_pages(self, driver, wait):
        """
        Versão corrigida que aceita 'driver' e 'wait' como argumentos.
        """
        try:
            wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, ".MuiPaginationItem-page")
                )
            )
            pages = driver.find_elements(By.CSS_SELECTOR, ".MuiPaginationItem-page")
            return max(
                (int(page.text) for page in pages if page.text.isdigit()), default=1
            )
        except TimeoutException:
            return 1
        except Exception:
            return 1

    def get_page_info(self, driver, kind: str):
        """
        Versão corrigida que aceita 'driver' como argumento.
        """
        components_data = []
        try:
            products = driver.find_elements(By.CSS_SELECTOR, ".mui-p3mq1s")
            for product in products:
                try:
                    product_name = product.find_element(
                        By.CSS_SELECTOR,
                        ".mui-1jecgbd-product_info_title-noMarginBottom",
                    ).text
                    url_element = product.find_element(By.CSS_SELECTOR, ".mui-p3mq1s a")
                    product_url = url_element.get_attribute("href")
                    price_element = product.find_element(
                        By.CSS_SELECTOR, ".mui-1q2ojdg-price_vista"
                    )
                    price_text = (
                        price_element.text.replace("R$ ", "")
                        .replace(".", "")
                        .replace(",", ".")
                        .strip()
                    )
                    price = float(price_text)
                    availability = True
                except NoSuchElementException:
                    availability = False
                    price = 0.0
                except Exception:
                    pass

                components_data.append(
                    {
                        "product_name_on_source": product_name,
                        "price": price,
                        "availability": availability,
                        "url": product_url,
                        "kind": kind,
                        "source_name": self.source_name,
                    }
                )
        except Exception as e:
            print(f"Erro ao buscar a lista de produtos na página: {e}")

        return components_data

    def scraping(self):
        """
        Orquestra o processo de scraping, criando e destruindo uma instância
        completa do navegador para cada categoria.
        """
        all_scraped_data = []
        component_items = list(self.path_component.items())

        for i, (kind, categories) in enumerate(component_items):
            print(
                f"\n{'=' * 30}\nIniciando sessão de scraping para: {kind.upper()} ({i + 1}/{len(component_items)})\n{'=' * 30}"
            )

            driver = None
            try:
                driver = self._initialize_driver()
                wait = WebDriverWait(driver, 30)
                driver.set_page_load_timeout(60)

                categories = (
                    categories if isinstance(categories, list) else [categories]
                )

                for category in categories:
                    scraped_category_data = self.scrape_category(
                        driver, wait, category, kind
                    )
                    all_scraped_data.extend(scraped_category_data)

            except Exception as e:
                print(
                    f"[{timezone.now()}] ERRO GRAVE na sessão de '{kind.upper()}': {e}"
                )

            finally:
                if driver:
                    driver.quit()
                    print(
                        f"[{timezone.now()}] Instância do navegador para '{kind.upper()}' foi destruída."
                    )

            print(f"Finalizada a sessão de {kind.upper()}. Pausando...")
            sleep(uniform(5, 10))

        return all_scraped_data

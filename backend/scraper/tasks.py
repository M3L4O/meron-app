from celery import shared_task
from scraper.scrapers import KabumScraper


@shared_task
def scrape_kabum_task():
    scraper = KabumScraper()
    scraper.scraping()

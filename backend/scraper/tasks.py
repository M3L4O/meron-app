from celery import shared_task
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import uuid  # Continua importado caso seja útil para outros contextos ou futuras modificações

# Importe a classe KabumScraper do seu arquivo scrapers.py
from scraper.scrapers import KabumScraper  # AGORA SÓ AQUI!

from .models import (
    CPU,
    GPU,
    Motherboard,
    RAM,
    Storage,
    PSU,  # Todos os seus modelos de componentes
    CurrentVolatileData,
    VolatileDataHistory,
)


@shared_task
def scrape_kabum_task():
    """
    Tarefa Celery principal para iniciar o processo de raspagem da Kabum.
    Instancia o KabumScraper, executa seu método scraping() para obter os dados,
    e então envia cada item raspado para a tarefa de processamento volátil.
    """
    print("Iniciando tarefa de scraping da Kabum...")
    scraper = KabumScraper()
    all_scraped_data = scraper.scraping()  # KabumScraper agora retorna os dados
    print(
        f"Scraping da Kabum concluído. Total de {len(all_scraped_data)} itens raspados."
    )

    print("Enviando itens raspados para a fila de processamento volátil...")
    for item_data in all_scraped_data:
        try:
            record_and_update_volatile_data.delay(
                product_name_on_source=item_data["product_name_on_source"],
                price=item_data["price"],
                availability=item_data["availability"],
                url=item_data["url"],
                source_name=item_data["source_name"],
                component_type_name=item_data["kind"],
                component_uuid=None,
            )
        except Exception as e:
            print(
                f"Erro ao enviar tarefa Celery para {item_data.get('product_name_on_source', 'N/A')}: {e}"
            )
    print(
        "Todos os itens raspados foram enviados para a fila de processamento volátil."
    )


@shared_task
def record_and_update_volatile_data(
    product_name_on_source: str,
    price: float,
    availability: bool,
    url: str,
    source_name: str,
    component_type_name: str,
    component_uuid: str = None,
):
    """
    Tarefa Celery para registrar dados voláteis no histórico e atualizar/criar
    o registro atual para um item de produto específico (URL + Fonte).
    Utiliza o 'component_type_name' para definir o ContentType,
    mas a GenericForeignKey para o componente principal (object_id)
    será deixada como None por enquanto.
    """
    print(f"Processando dados voláteis para URL: {url} da fonte: {source_name}")

    component_obj_id = None
    component_content_type = None

    if component_type_name:
        try:
            component_content_type = ContentType.objects.get(
                app_label="scraper", model=component_type_name.lower()
            )
            print(f"ContentType encontrado para '{component_type_name}'.")
        except ContentType.DoesNotExist:
            print(
                f"Erro: ContentType para '{component_type_name}' (app_label='scraper') não encontrado. O dado volátil será salvo sem tipo."
            )
            component_content_type = None
    else:
        print(
            "Aviso: 'component_type_name' não fornecido. O dado volátil será salvo sem tipo."
        )

    current_data_item, created = CurrentVolatileData.objects.get_or_create(
        url=url,
        source=source_name,
        defaults={
            "content_type": component_content_type,  # Pode ser o ContentType ou None
            "object_id": component_obj_id,  # Será None
            "product_name_on_source": product_name_on_source,
            "current_price": price,
            "current_availability": availability,
            "last_checked": timezone.now(),
        },
    )

    if (
        not created
        and component_content_type
        and (current_data_item.content_type is None)
    ):
        current_data_item.content_type = component_content_type
        current_data_item.save(update_fields=["content_type"])
        print(f"CurrentVolatileData atualizado com ContentType: {component_type_name}")

    if created:
        print(
            f"Novo item de CurrentVolatileData criado: '{product_name_on_source}' ({source_name})"
        )
    else:
        print(
            f"Item de CurrentVolatileData existente encontrado: '{current_data_item.product_name_on_source}' ({source_name})"
        )

    VolatileDataHistory.objects.create(
        current_data_item=current_data_item,  # Vincula ao item CurrentVolatileData
        product_name_on_source=product_name_on_source,
        price=price,
        availability=availability,
        recorded_at=timezone.now(),
    )
    print(f"Registro de histórico salvo para '{product_name_on_source}' (${price})")

    if (
        current_data_item.current_price != price
        or current_data_item.current_availability != availability
        or current_data_item.product_name_on_source != product_name_on_source
    ):
        current_data_item.product_name_on_source = product_name_on_source
        current_data_item.current_price = price
        current_data_item.current_availability = availability
        current_data_item.last_checked = timezone.now()
        current_data_item.save()
        print(
            f"CurrentVolatileData atualizado para '{product_name_on_source}' (${price})"
        )
    else:
        current_data_item.last_checked = timezone.now()
        current_data_item.save()
        print(
            f"CurrentVolatileData verificado (sem mudanças de preço/disponibilidade) para '{product_name_on_source}'"
        )

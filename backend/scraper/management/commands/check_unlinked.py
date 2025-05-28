import string

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from scraper.models import CPU, GPU, PSU, RAM, CurrentVolatileData, Motherboard, Storage


class Command(BaseCommand):
    help = "Verifica dados pendentes de vinculação e mostra termos e candidatos encontrados."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            help="Tipo de componente a verificar (cpu, gpu, motherboard, ram, storage, psu)",
            required=True,
        )
        parser.add_argument(
            "--limit", type=int, help="Número máximo de itens a verificar"
        )

    def handle(self, *args, **options):
        component_type_arg = options["type"].lower()

        model_map = {
            "cpu": CPU,
            "gpu": GPU,
            "motherboard": Motherboard,
            "ram": RAM,
            "psu": PSU,
            "storage": Storage,
        }

        if component_type_arg not in model_map:
            self.stdout.write(
                self.style.ERROR(f"Tipo '{component_type_arg}' não suportado.")
            )
            return

        SpecModel = model_map[component_type_arg]
        content_type = ContentType.objects.get(
            app_label="scraper", model=component_type_arg
        )

        unlinked_qs = CurrentVolatileData.objects.filter(
            object_id__isnull=True, content_type=content_type
        )
        limit = options.get("limit")
        if limit:
            unlinked_qs = unlinked_qs[:limit]

        count = unlinked_qs.count()
        self.stdout.write(
            f"Total de itens pendentes para '{component_type_arg.upper()}': {count}"
        )

        if count == 0:
            self.stdout.write("Nada para vincular, tudo atualizado!")
            return

        exclude_terms = {
            "placa",
            "de",
            "video",
            "processador",
            "memoria",
            "ram",
            "fonte",
            "alimentacao",
            "armazenamento",
            "hd",
            "ssd",
            "gabinete",
            "placa-mae",
            "mae",
        }

        for i, item in enumerate(unlinked_qs):
            self.stdout.write(f"\n[{i + 1}] Produto: '{item.product_name_on_source}'")

            # dentro do loop for item in unlinked_qs:
            translator = str.maketrans("", "", string.punctuation)

            terms = [
                term.lower().translate(translator)
                for term in item.product_name_on_source.split()
                if len(term) > 2 and term.lower() not in exclude_terms
            ]
            terms = [t for t in terms if t]  #
            print(f"  Termos para busca: {terms}")

            query = Q()
            for term in terms:
                query &= Q(model__icontains=term)

            candidates = list(SpecModel.objects.filter(query))
            self.stdout.write(f"  Candidatos encontrados: {len(candidates)}")
            for c in candidates[:3]:
                self.stdout.write(f"    -> {c.model}")

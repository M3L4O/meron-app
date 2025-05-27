# backend/scraper/management/commands/clear_links.py
from django.core.management.base import BaseCommand
from scraper.models import CurrentVolatileData
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Limpa os vínculos (object_id e content_type) nos registos CurrentVolatileData.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            help='Opcional: Limpa vínculos apenas para este tipo de componente (ex: cpu, gpu). Se não especificado, limpa todos.',
            required=False
        )

    def handle(self, *args, **options):
        component_type_arg = options['type']

        qs = CurrentVolatileData.objects.all()

        if component_type_arg:
            try:
                target_content_type = ContentType.objects.get(app_label='scraper', model=component_type_arg.lower())
                qs = qs.filter(content_type=target_content_type)
                self.stdout.write(self.style.WARNING(f"A limpar vínculos apenas para o tipo: {component_type_arg.upper()}"))
            except ContentType.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Tipo de componente '{component_type_arg}' não encontrado."))
                return
        else:
            self.stdout.write(self.style.WARNING("A limpar TODOS os vínculos em CurrentVolatileData..."))

        updated_count = qs.update(object_id=None)

        self.stdout.write(self.style.SUCCESS(f"{updated_count} registos tiveram os seus vínculos limpos."))
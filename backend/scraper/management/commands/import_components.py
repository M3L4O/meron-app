from django.core.management.base import BaseCommand
from scraper.serializers import (
    CPUSerializer,
    GPUSerializer,
    MotherboardSerializer,
    RAMSerializer,
    StorageSerializer,
    PSUSerializer,
)
import json
import os


class Command(BaseCommand):
    help = "Importa componentes a partir de arquivos JSON internos"

    def handle(self, *args, **kwargs):
        componentes = [
            ("data/cpus.json", CPUSerializer, "CPUs"),
            ("data/gpus.json", GPUSerializer, "GPUs"),
            ("data/motherboards.json", MotherboardSerializer, "Motherboards"),
            ("data/rams.json", RAMSerializer, "RAMs"),
            ("data/storages.json", StorageSerializer, "Storages"),
            ("data/psus.json", PSUSerializer, "PSUs"),
        ]

        for arquivo, serializer_class, nome in componentes:
            if not os.path.exists(arquivo):
                self.stdout.write(
                    self.style.WARNING(f"{arquivo} não encontrado, pulando {nome}.")
                )
                continue

            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            inseridos = 0
            ignorados = 0

            for dado in dados:
                item_serializer = serializer_class(data=dado)
                if item_serializer.is_valid():
                    item_serializer.save()
                    inseridos += 1
                else:
                    ignorados += 1
                    self.stderr.write(
                        self.style.WARNING(
                            f"Ignorado: Erros: {item_serializer.errors}"
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(f"{nome} — {inseridos} adicionados, {ignorados} ignorados.")
            )

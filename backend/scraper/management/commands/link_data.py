# backend/scraper/management/commands/link_data.py (com descrições específicas por categoria)

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from scraper.models import (
    CPU,
    GPU,
    Motherboard,
    RAM,
    PSU,
    Storage,
    CurrentVolatileData,
)  #
from django.db.models import Q
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import time

# --- Módulo de IA (Lógica do "Read-and-Select") ---

print("A carregar o modelo Cross-Encoder...")
try:
    cross_encoder_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    cross_encoder_tokenizer = AutoTokenizer.from_pretrained(cross_encoder_model_name)
    cross_encoder_model = AutoModelForSequenceClassification.from_pretrained(
        cross_encoder_model_name
    )
    print("Modelo carregado com sucesso.")
except Exception as e:
    print(f"Erro ao carregar o modelo de IA: {e}")
    cross_encoder_model = None


# ATUALIZAÇÃO: Adicionamos 'component_type' como argumento
def rank_and_select(mention_name, candidates, component_type):
    """Usa um Cross-Encoder para pontuar e selecionar o melhor candidato."""
    if not candidates or not cross_encoder_model:
        return None

    pairs = []
    for candidate in candidates:
        # --- INÍCIO DA LÓGICA DE DESCRIÇÃO ESPECÍFICA DA CATEGORIA ---
        model_name = getattr(candidate, "model", "").strip()

        description_parts = [model_name]

        if component_type == "cpu":
            if hasattr(candidate, "n_cores") and candidate.n_cores:
                description_parts.append(f"{candidate.n_cores} cores")
            if hasattr(candidate, "base_clock_speed") and candidate.base_clock_speed:
                description_parts.append(f"{candidate.base_clock_speed}GHz base")
            if (
                hasattr(candidate, "boost_clock_speed")
                and candidate.boost_clock_speed
                and candidate.boost_clock_speed > 0
            ):  # Boost pode ser 0
                description_parts.append(f"{candidate.boost_clock_speed}GHz turbo")
            if hasattr(candidate, "socket") and candidate.socket:
                description_parts.append(f"{candidate.socket}")

        elif component_type == "gpu":
            if hasattr(candidate, "vram") and candidate.vram:
                description_parts.append(f"{int(candidate.vram)}GB VRAM")
            if hasattr(candidate, "vram_speed") and candidate.vram_speed:
                description_parts.append(f"{int(candidate.vram_speed)}MHz VRAM speed")
            if hasattr(candidate, "consumption") and candidate.consumption:
                description_parts.append(f"{candidate.consumption}W consumption")
            if candidate.integrated_gpu:
                description_parts.append("Video Integrado")
            else:
                description_parts.append("Sem Video")

        elif component_type == "motherboard":
            if hasattr(candidate, "socket") and candidate.socket:
                description_parts.append(f"socket {candidate.socket}")
            if hasattr(candidate, "board_size") and candidate.board_size:
                description_parts.append(f"form_factor {candidate.board_size}")
            if hasattr(candidate, "memory_gen") and candidate.memory_gen:
                description_parts.append(f"{candidate.memory_gen}")
            if hasattr(candidate, "memory_max") and candidate.memory_max:
                description_parts.append(f"{candidate.memory_max}GB max_memory")

        elif component_type == "ram":
            if hasattr(candidate, "size") and candidate.size:
                description_parts.append(f"{candidate.size}GB")
            if hasattr(candidate, "generation") and candidate.generation:
                description_parts.append(candidate.generation)
            if hasattr(candidate, "speed") and candidate.speed:
                description_parts.append(f"{int(candidate.speed)}MHz")

        elif component_type == "storage":
            if hasattr(candidate, "capacity") and candidate.capacity:
                description_parts.append(
                    f"{candidate.capacity}GB"
                )  # Pode precisar converter para TB se for o caso
            if hasattr(candidate, "io") and candidate.io:
                description_parts.append(candidate.io)
            if hasattr(candidate, "is_hdd"):
                storage_type = "HDD" if candidate.is_hdd else "SSD"
                description_parts.append(storage_type)
            if (
                hasattr(candidate, "rpm") and candidate.is_hdd and candidate.rpm > 0
            ):  # RPM só para HDDs
                description_parts.append(f"{candidate.rpm} RPM")

        elif component_type == "psu":
            if hasattr(candidate, "power") and candidate.power:
                description_parts.append(f"{candidate.power}W")
            if hasattr(candidate, "rate") and candidate.rate:
                description_parts.append(candidate.rate)

        else:  # Fallback se o tipo não for reconhecido
            description_parts.append(model_name)

        # Junta as partes da descrição, removendo strings vazias e espaços extras
        description = ", ".join(filter(None, description_parts))

        pairs.append([mention_name, description.strip()])

    with torch.no_grad():
        inputs = cross_encoder_tokenizer(
            pairs, padding=True, truncation=True, return_tensors="pt", max_length=256
        )
        scores = cross_encoder_model(**inputs).logits.squeeze()

    if scores.dim() == 0:  # Lida com o caso de apenas um candidato
        scores = torch.tensor([scores.item()])

    best_candidate_index = torch.argmax(scores).item()
    best_candidate = candidates[best_candidate_index]
    best_score = scores[best_candidate_index].item()

    CONFIDENCE_THRESHOLD = 2
    if best_score < CONFIDENCE_THRESHOLD:
        print(
            f"  -> Melhor candidato '{best_candidate.model}' com pontuação baixa ({best_score:.2f}). A descartar."
        )
        return None

    print(
        f"  -> Selecionado: '{best_candidate.model}' (Descrição usada: '{pairs[best_candidate_index][1]}') com pontuação: {best_score:.2f}"
    )
    return best_candidate


# --- Lógica do Comando Django ---


class Command(BaseCommand):
    help = "Vincula registos de CurrentVolatileData às especificações de componentes usando IA."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            help="Tipo de componente a processar (cpu, gpu, motherboard, ram, storage, psu)",
            required=True,
        )
        parser.add_argument(
            "--limit", type=int, help="Número máximo de itens a processar"
        )

    def handle(self, *args, **options):
        if not cross_encoder_model:
            self.stdout.write(
                self.style.ERROR("O modelo de IA não foi carregado. A abortar.")
            )
            return

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
                self.style.ERROR(
                    f"Tipo de componente '{component_type_arg}' não é suportado."
                )
            )
            return

        SpecModel = model_map[component_type_arg]
        component_content_type = ContentType.objects.get(
            app_label="scraper", model=component_type_arg.lower()
        )

        unlinked_items = CurrentVolatileData.objects.filter(
            object_id__isnull=True, content_type=component_content_type
        )

        limit = options.get("limit")
        if limit:
            unlinked_items = unlinked_items[:limit]

        if not unlinked_items.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Nenhum dado de '{component_type_arg.upper()}' por vincular. Tudo atualizado!"
                )
            )
            return

        self.stdout.write(
            f"Encontrados {unlinked_items.count()} registos de '{component_type_arg.upper()}' por vincular."
        )

        processed_count = 0
        start_time = time.time()

        for item in unlinked_items:
            self.stdout.write(f"\nProcessando: '{item.product_name_on_source}'...")

            search_terms = item.product_name_on_source.split()
            query = Q()
            for term in search_terms:
                if len(term) > 2 and term.lower() not in [
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
                ]:
                    query |= Q(model__icontains=term)  # Procura no campo 'model'

            candidates = list(SpecModel.objects.filter(query))

            if not candidates:
                self.stdout.write("  -> Nenhum candidato encontrado na base de dados.")
                continue

            self.stdout.write(
                f"  -> Encontrados {len(candidates)} candidatos. A iniciar o ranking..."
            )

            # ATUALIZAÇÃO: Passar 'component_type_arg' para a função de ranking
            best_match = rank_and_select(
                item.product_name_on_source, candidates, component_type_arg
            )

            if best_match:
                item.component = best_match
                item.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  -> Vínculo criado: '{item.product_name_on_source}' -> '{best_match.model}'"
                    )
                )
                processed_count += 1

        end_time = time.time()
        self.stdout.write("\n-------------------------------------------------")
        self.stdout.write(
            self.style.SUCCESS(
                f"Processo concluído em {end_time - start_time:.2f} segundos."
            )
        )
        self.stdout.write(
            f"Total de {processed_count} novos vínculos foram criados para '{component_type_arg.upper()}'."
        )

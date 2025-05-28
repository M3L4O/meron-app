import re
import time

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from scraper.management.ml_matcher import get_scores_for_all_candidates
from scraper.management.ml_matcher import model as cross_encoder_model
from scraper.models import CPU, GPU, PSU, RAM, CurrentVolatileData, Motherboard, Storage

# Palavras removidas da lista de JUNK_WORDS pois podem ser importantes para
# diferenciar versões de produtos (ex: com ou sem cooler, versão de varejo ou não).
JUNK_WORDS = {
    "processador",
    "placa",
    "mae",
    "video",
    "memoria",
    "fonte",
    "gabinete",
    "armazenamento",
    "com",
    "sem",
    "de",
    "para",
    "pc",
    "gamer",
    "caixa",
    "box",
    "cooler",
    "original",
    "lacrado",
    "oferta",
    "promocao",
    "soquete",
    "socket",
    "oem",
    "wof",
    "pn",
    "tray",
    "bulk",
    "cores",
    "core",
    "núcleos",
    "threads",
    "cache",
    "turbo",
    "max",
    "boost",
    "clock",
    "base",
    "integrado",
    "grafico",
    "gráficos",
    "geração",
    "gen",
    "geracao",
    "series",
    "serie",
    "alimentacao",
    "potencia",
    "velocidade",
    "desbloqueado",
    "comet",
    "lake",
    "amd",
    "intel",
    "nvidia",
    "gabinete",
    "placa-mae",
    "entry",
    "level",
    "edition",
    "collectors",
    "dual",
    "quad",
    "hexa",
    "sqt",
    "10ª",
    "11ª",
    "12ª",
    "13ª",
    "14ª",
    "7º",
    "8ª",
    "9ª",
    "lga",
    "1151",
    "1155",
    "1200",
    "1700",
    "am4",
    "am5",
    "lga1700",
    "lga1200",
    "1151p",
    "ghz",
    "mhz",
    "mb",
    "gb",
    "w",
    "tb",
    "rpm",
    "k",
    "tdp",
    "mpki",
    "cbx",
    "woz",
    "fclga",
    "sk1200",
    "sr2he",
    "slbmd",
}


def calculate_mismatch_penalty(
    query_terms: set[str], candidate_terms: set[str], penalty_per_mismatch: float = 0.5
) -> float:
    """
    Calcula uma penalidade baseada na diferença simétrica entre os termos da consulta e do candidato.
    Penaliza termos que existem em um conjunto mas não no outro.
    """
    mismatched_terms = query_terms.symmetric_difference(candidate_terms)
    significant_mismatched_terms = [term for term in mismatched_terms if len(term) > 1]
    return len(significant_mismatched_terms) * penalty_per_mismatch


def get_essential_terms(product_name: str) -> set[str]:
    """Limpa o nome do produto e extrai termos essenciais como um conjunto (set)."""

    clean_name = product_name.lower().replace("-", " ")

    clean_name = re.sub(r"\([^)]*\)", " ", clean_name)
    clean_name = re.sub(r"[^\w\s]", " ", clean_name)

    terms = {
        term for term in clean_name.split() if len(term) >= 2 and term not in JUNK_WORDS
    }
    return terms


class Command(BaseCommand):
    help = "Vincula registos de CurrentVolatileData com desambiguação por IA e lógica de penalização."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            required=True,
            help="Tipo de componente (cpu, gpu, motherboard, ram, storage, psu)",
        )
        parser.add_argument("--limit", type=int, help="Limite de itens a processar")

    def handle(self, *args, **options):
        CONFIDENCE_THRESHOLD = 0.3
        AMBIGUITY_THRESHOLD = 0.3

        if not cross_encoder_model:
            self.stdout.write(
                self.style.ERROR("O modelo de IA não foi carregado. A abortar.")
            )
            return

        component_type = options["type"].lower()
        model_map = {
            "cpu": CPU,
            "gpu": GPU,
            "motherboard": Motherboard,
            "ram": RAM,
            "psu": PSU,
            "storage": Storage,
        }
        if component_type not in model_map:
            self.stdout.write(
                self.style.ERROR(
                    f"Tipo de componente '{component_type}' não suportado."
                )
            )
            return

        SpecModel = model_map[component_type]
        content_type = ContentType.objects.get(
            app_label="scraper", model=component_type
        )

        items = CurrentVolatileData.objects.filter(
            object_id__isnull=True, content_type=content_type
        )
        if limit := options.get("limit"):
            items = items[:limit]

        if not items.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Nenhum dado de '{component_type.upper()}' por vincular."
                )
            )
            return

        self.stdout.write(
            f"Encontrados {items.count()} registros de '{component_type.upper()}' por vincular."
        )
        items_to_update, start_time = [], time.time()

        for item in items:
            self.stdout.write(f"\nProcessando: '{item.product_name_on_source}'...")
            query_essential_terms = get_essential_terms(item.product_name_on_source)

            if not query_essential_terms:
                self.stdout.write(
                    self.style.WARNING(
                        "  -> Nenhum termo essencial encontrado. Ignorando."
                    )
                )
                continue

            self.stdout.write(
                f"  -> Termos essenciais da consulta: {query_essential_terms}"
            )

            # Ordena os termos por tamanho para usar nas buscas mais restritivas
            sorted_terms = sorted(list(query_essential_terms), key=len, reverse=True)
            candidates = []

            # ==============================================================================
            # LÓGICA DE BUSCA DE CANDIDATOS EM MÚLTIPLAS ETAPAS
            # ==============================================================================

            # Tentativa 1: Busca restrita com todos os termos (AND)
            query = Q()
            for term in sorted_terms:
                query &= Q(model__icontains=term)
            candidates = list(SpecModel.objects.filter(query))
            self.stdout.write(
                f"  -> [Tentativa 1] {len(candidates)} candidatos encontrados."
            )

            # Tentativa 1.5: Com os dois termos mais específicos
            if not candidates and len(sorted_terms) >= 2:
                query = Q()
                for term in sorted_terms[:2]:
                    query &= Q(model__icontains=term)
                candidates = list(SpecModel.objects.filter(query))
                self.stdout.write(
                    f"  -> [Tentativa 1.5] {len(candidates)} candidatos com '{sorted_terms[:2]}'."
                )

            # Tentativa 2: Termo a termo, parando no primeiro resultado
            if not candidates:
                for term in sorted_terms:
                    query = Q(model__icontains=term)
                    subset = list(SpecModel.objects.filter(query))
                    self.stdout.write(
                        f"    - Termo '{term}': {len(subset)} candidatos."
                    )
                    if subset:
                        candidates = subset
                        break

            # Tentativa 3: Busca aberta com qualquer um dos termos (OR)
            if not candidates:
                query = Q()
                for term in sorted_terms:
                    query |= Q(model__icontains=term)
                candidates = list(SpecModel.objects.filter(query))
                self.stdout.write(
                    self.style.WARNING(
                        f"  -> [Tentativa 3] {len(candidates)} candidatos encontrados (busca aberta)."
                    )
                )

            # ==============================================================================

            if not candidates:
                self.stdout.write(
                    self.style.ERROR(
                        "  -> Nenhum candidato encontrado após todas as tentativas."
                    )
                )
                continue

            if len(candidates) > 32:
                self.stdout.write(f"  -> Limitando candidatos a 32.")
                candidates = candidates[:32]

            self.stdout.write("  -> Iniciando ranking dos candidatos...")
            scored = get_scores_for_all_candidates(
                item.product_name_on_source.lower(), candidates, component_type
            )

            if not scored:
                self.stdout.write(
                    self.style.WARNING("  -> A IA não retornou pontuações.")
                )
                continue

            # Lógica de ajuste de score com penalização generalizada
            adjusted_scored = []
            self.stdout.write(
                "  -> Ajustando scores com base na divergência de termos..."
            )
            for candidate, original_score in scored:
                candidate_essential_terms = get_essential_terms(candidate.model)
                penalty = calculate_mismatch_penalty(
                    query_essential_terms, candidate_essential_terms
                )
                adjusted_score = original_score - penalty
                adjusted_scored.append((candidate, adjusted_score))
                if penalty > 0:
                    self.stdout.write(
                        f"    - Candidato '{candidate.model}' penalizado em {penalty:.2f}. Score: {original_score:.2f} -> {adjusted_score:.2f}"
                    )
            scored = sorted(adjusted_scored, key=lambda x: x[1], reverse=True)

            best, best_score = scored[0]
            second_score = scored[1][1] if len(scored) > 1 else -100

            if best_score < CONFIDENCE_THRESHOLD:
                self.stdout.write(
                    f"  -> Melhor candidato '{best.model}' com score baixo ({best_score:.2f}). Ignorado."
                )
                continue

            if (best_score - second_score) < AMBIGUITY_THRESHOLD:
                self.stdout.write(
                    self.style.WARNING(
                        f"  -> CASO AMBÍGUO: '{best.model}' ({best_score:.2f}) vs próximo ({second_score:.2f}). Ignorado."
                    )
                )
                continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"  -> SELEÇÃO CONFIANTE: '{best.model}' (Score: {best_score:.2f}, Diferença: {best_score - second_score:.2f})"
                )
            )
            item.component = best
            items_to_update.append(item)

        if items_to_update:
            CurrentVolatileData.objects.bulk_update(
                items_to_update, ["content_type", "object_id"]
            )

        total = len(items_to_update)
        self.stdout.write("\n" + "-" * 50)
        self.stdout.write(
            self.style.SUCCESS(f"Processo concluído em {time.time() - start_time:.2f}s")
        )
        self.stdout.write(
            f"Total de {total} vínculos criados para '{component_type.upper()}'."
        )

import logging  # Importa o módulo de logging
import re
import time
from typing import Any, Dict, List

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from scraper.management.ml_matcher import (
    get_scores_for_all_candidates,
    get_component_description,
)
from scraper.models import CPU, GPU, PSU, RAM, CurrentVolatileData, Motherboard, Storage

logger = logging.getLogger(__name__)

JUNK_WORDS = {
    "processador",
    "placa",
    "mae",
    "video",
    "vídeo",
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
    "oem",
    "wof",
    "pn",
    "tray",
    "bulk",
    "cores",
    "núcleos",
    "threads",
    "cache",
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
    "gabinete",
    "placa-mae",
    "entry",
    "level",
    "dual",
    "quad",
    "hexa",
}


def calculate_mismatch_penalty(
    query_terms: set[str], candidate_terms: set[str]
) -> float:
    mismatched_terms = query_terms.symmetric_difference(candidate_terms)
    significant_mismatched_terms = [term for term in mismatched_terms if len(term) > 1]
    return len(significant_mismatched_terms) * 0.5


def calculate_proportional_penalty(
    query_terms: set[str], candidate_terms: set[str]
) -> float:
    mismatched_terms = query_terms.symmetric_difference(candidate_terms)
    union_terms = query_terms.union(candidate_terms)
    if not union_terms:
        return 0.0
    penalty_ratio = len(mismatched_terms) / len(union_terms)
    return penalty_ratio * 5.0


PENALTY_FUNCTIONS = {
    "hard": calculate_mismatch_penalty,
    "soft": calculate_proportional_penalty,
}


def get_essential_terms(product_name: str) -> set[str]:
    clean_name = product_name.lower()
    clean_name = re.sub(r"\([^)]*\)", " ", clean_name)
    clean_name = re.sub(r"[^\w\s.]", " ", clean_name)
    terms = {
        term for term in clean_name.split() if len(term) >= 2 and term not in JUNK_WORDS
    }
    return terms


class Command(BaseCommand):
    help = "Vincula registos em duas rodadas: uma restrita e uma flexível."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            required=True,
            help="Tipo de componente (cpu, gpu, etc.)",
        )
        parser.add_argument(
            "--limit", type=int, help="Limite total de itens a processar"
        )
        parser.add_argument(
            "--log-level",
            type=str,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Define o nível do log para o console.",
        )

    def _find_best_candidates(self, spec_model, sorted_terms):
        query_or = Q()
        for term in sorted_terms:
            query_or |= Q(model__icontains=term)
        candidates = list(spec_model.objects.filter(query_or))
        logger.info(f"  -> [Busca Ampla] {len(candidates)} candidatos encontrados.")

        return candidates

    def _process_linking_round(
        self,
        items_to_process: List[CurrentVolatileData],
        component_type: str,
        spec_model: Any,
        config: Dict,
    ) -> List[CurrentVolatileData]:
        items_linked_in_this_round = []

        for item in items_to_process:
            logger.info(f"Processando: '{item.product_name_on_source}'...")
            query_essential_terms = get_essential_terms(item.product_name_on_source)

            if not query_essential_terms:
                logger.warning("  -> Nenhum termo essencial. Ignorando.")
                continue

            sorted_terms = sorted(list(query_essential_terms), key=len, reverse=True)
            candidates = self._find_best_candidates(spec_model, sorted_terms)

            if not candidates:
                logger.error("  -> Nenhum candidato encontrado.")
                continue

            scored = get_scores_for_all_candidates(
                item.product_name_on_source.lower(), candidates, component_type
            )

            if not scored:
                logger.warning("  -> A IA não retornou pontuações.")
                continue

            adjusted_scored = []
            penalty_function = PENALTY_FUNCTIONS[config["penalty_function"]]

            for candidate, original_score in scored:
                candidate_essential_terms = get_essential_terms(
                    get_component_description(candidate, component_type)
                )
                penalty = penalty_function(
                    query_essential_terms, candidate_essential_terms
                )
                adjusted_score = original_score - penalty
                adjusted_scored.append((candidate, adjusted_score))
                if penalty > 0:
                    logger.debug(
                        f"    - Candidato '{get_component_description(candidate, component_type)}' penalizado em {penalty:.2f}. Score: {original_score:.2f} -> {adjusted_score:.2f}"
                    )

            scored = sorted(adjusted_scored, key=lambda x: x[1], reverse=True)
            best, best_score = scored[0]
            second, second_score = scored[1] if len(scored) > 1 else ("", -100)

            if best_score < config["CONFIDENCE_THRESHOLD"]:
                logger.info(
                    f"  -> Melhor candidato '{get_component_description(best, component_type)}' com score baixo ({best_score:.2f}). Ignorado."
                )
                continue

            if (best_score - second_score) < config["AMBIGUITY_THRESHOLD"]:
                logger.warning(
                    f"  -> CASO AMBÍGUO: '{best.model}' ({best_score:.2f}) vs '{second.model}' ({second_score:.2f}). Ignorado."
                )
                continue

            logger.info(
                f"  -> SELEÇÃO CONFIANTE: '{get_component_description(best, component_type)}' (Score: {best_score:.2f})"
            )
            item.component = best
            items_linked_in_this_round.append(item)

        return items_linked_in_this_round

    def handle(self, *args, **options):
        log_level = options["log_level"].upper()

        logger.handlers = []

        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(f"linking_{options['type']}.log", mode="w")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        start_time = time.time()

        STRICT_CONFIG = {
            "name": "Rodada 1: Alta Confiança",
            "penalty_function": "hard",
            "CONFIDENCE_THRESHOLD": 0.3,
            "AMBIGUITY_THRESHOLD": 0.3,
        }
        LENIENT_CONFIG = {
            "name": "Rodada 2: Busca Ampla",
            "penalty_function": "soft",
            "CONFIDENCE_THRESHOLD": 0.7,
            "AMBIGUITY_THRESHOLD": 0.3,
        }

        component_type = options["type"].lower()
        model_map = {
            "cpu": CPU,
            "gpu": GPU,
            "motherboard": Motherboard,
            "ram": RAM,
            "psu": PSU,
            "storage": Storage,
        }
        spec_model = model_map.get(component_type)
        content_type = ContentType.objects.get(
            app_label="scraper", model=component_type
        )

        initial_items = CurrentVolatileData.objects.filter(
            object_id__isnull=True, content_type=content_type
        )
        if limit := options.get("limit"):
            initial_items = initial_items[:limit]

        if not initial_items.exists():
            logger.info(f"Nenhum dado de '{component_type.upper()}' por vincular.")
            return

        logger.info(f"Total de {initial_items.count()} itens para processar.")

        logger.info("\n" + "=" * 50)
        logger.info(STRICT_CONFIG["name"])
        logger.info("=" * 50)

        linked_in_round_1 = self._process_linking_round(
            list(initial_items), component_type, spec_model, STRICT_CONFIG
        )

        # linked_ids_round_1 = {item.id for item in linked_in_round_1}
        # items_for_round_2 = [
        #     item for item in initial_items if item.id not in linked_ids_round_1
        # ]

        # linked_in_round_2 = []
        # if items_for_round_2:
        #     logger.info("\n" + "=" * 50)
        #     logger.info(LENIENT_CONFIG["name"])
        #     logger.info(f"Processando {len(items_for_round_2)} itens restantes...")
        #     logger.info("=" * 50)

        #     linked_in_round_2 = self._process_linking_round(
        #         items_for_round_2, component_type, spec_model, LENIENT_CONFIG
        #     )
        # else:
        #     logger.warning("\nNenhum item restante para a segunda rodada.")

        all_items_to_update = linked_in_round_1
        if all_items_to_update:
            CurrentVolatileData.objects.bulk_update(
                all_items_to_update, ["content_type", "object_id"]
            )

        logger.info("\n" + "-" * 50)
        logger.info("RELATÓRIO FINAL DO PROCESSO")
        logger.info(f"Processo concluído em {time.time() - start_time:.2f}s")
        logger.info(f"  - Vínculos na Rodada 1 (Estrrita): {len(linked_in_round_1)}")
        # logger.info(f"  - Vínculos na Rodada 2 (Flexível): {len(linked_in_round_2)}")
        logger.info(
            f"Total de {len(all_items_to_update)} vínculos criados para '{component_type.upper()}'."
        )

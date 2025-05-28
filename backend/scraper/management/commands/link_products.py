import re
import time

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q

# Alterado para importar a nova função que retorna todas as pontuações
from scraper.management.ml_matcher import (  # Importa a nossa nova função de desempate
    get_scores_for_all_candidates,
)
from scraper.management.ml_matcher import (
    model as cross_encoder_model,
)
from scraper.models import (
    CPU,
    GPU,
    PSU,
    RAM,
    CurrentVolatileData,
    Motherboard,
    Storage,
)

# VERSÃO FINAL DA LISTA DE JUNK WORDS
# A mais completa possível, baseada em todos os logs.
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


# VERSÃO FINAL DA FUNÇÃO DE EXTRAÇÃO - SIMPLES E EFICAZ
def get_essential_terms(product_name: str) -> list[str]:
    """
    DOCUMENTAÇÃO: Limpa o nome do produto e extrai uma lista de termos essenciais.
    Esta versão é mais simples e confia na JUNK_WORDS para a filtragem.
    """
    clean_name = product_name.lower()
    clean_name = re.sub(r"\([^)]*\)", " ", clean_name)
    clean_name = re.sub(
        r"[^\w\s-]", " ", clean_name
    )  # Mantém letras, números, espaços e hífens

    # Usa um set para evitar duplicados, e depois converte para lista
    terms = {
        term for term in clean_name.split() if len(term) >= 2 and term not in JUNK_WORDS
    }
    # Ordena por comprimento para que o termo mais específico (ex: "i7-10700k") venha primeiro
    return sorted(list(terms), key=len, reverse=True)


class Command(BaseCommand):
    help = "Vincula registos de CurrentVolatileData com lógica de desambiguação inspirada em ReS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            required=True,
            help="Tipo de componente a processar (cpu, gpu, motherboard, ram, storage, psu)",
        )
        parser.add_argument(
            "--limit", type=int, help="Número máximo de itens a processar"
        )

    def handle(self, *args, **options):
        CONFIDENCE_THRESHOLD = 0.5
        AMBIGUITY_THRESHOLD = 0.15
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
            app_label="scraper", model=component_type_arg
        )

        unlinked_items = CurrentVolatileData.objects.filter(
            object_id__isnull=True, content_type=component_content_type
        )
        if limit := options.get("limit"):
            unlinked_items = unlinked_items[:limit]

        if not unlinked_items.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Nenhum dado de '{component_type_arg.upper()}' por vincular."
                )
            )
            return

        self.stdout.write(
            f"Encontrados {unlinked_items.count()} registos de '{component_type_arg.upper()}' por vincular."
        )

        items_to_update = []
        start_time = time.time()

        for item in unlinked_items:
            self.stdout.write(f"\nProcessando: '{item.product_name_on_source}'...")

            essential_terms = get_essential_terms(item.product_name_on_source)
            if not essential_terms:
                self.stdout.write(self.style.WARNING("  -> Nenhum termo essencial encontrado. A ignorar."))
                continue

            self.stdout.write(f"  -> Termos essenciais encontrados: {essential_terms}")
            candidates = []

            # --- INÍCIO DA LÓGICA DE BUSCA MELHORADA (AGORA COM MAIS CAMADAS) ---

            # Tentativa 1: Ouro Total (AND com todos os termos)
            if essential_terms: # Garante que há termos para usar
                query_gold_total = Q()
                for term in essential_terms:
                    query_gold_total &= Q(model__icontains=term)
                candidates = list(SpecModel.objects.filter(query_gold_total))
                self.stdout.write(f"  -> [Tentativa 1: Ouro Total] Encontrados {len(candidates)} candidatos.")

            # Tentativa 1.5: Ouro Parcial (AND com os N termos mais específicos)
            # Vamos tentar com os 2 mais específicos, se a anterior falhou e há pelo menos 2 termos.
            if not candidates and len(essential_terms) >= 2:
                # Pega os N termos mais específicos (ex: os 2 primeiros, pois a lista está ordenada)
                # Você pode ajustar o número de termos (aqui, 2)
                num_top_terms = min(len(essential_terms), 2) # Pega até 2 termos
                top_terms = essential_terms[:num_top_terms]
                
                query_gold_partial = Q()
                for term in top_terms:
                    query_gold_partial &= Q(model__icontains=term)
                candidates = list(SpecModel.objects.filter(query_gold_partial))
                self.stdout.write(f"  -> [Tentativa 1.5: Ouro Parcial com '{top_terms}'] Encontrados {len(candidates)} candidatos.")

            # Tentativa 2: Modelo Iterativo (AND com cada termo essencial, do mais específico para o menos)
            if not candidates and essential_terms:
                self.stdout.write("  -> [Tentativa 2: Modelo Iterativo] A procurar termo a termo...")
                for i, term_candidate in enumerate(essential_terms):
                    # Não vamos usar termos muito curtos ou potencialmente problemáticos sozinhos
                    # Ex: 'i3', 'i5', 'i7', 'i9', 'am4', 'am5' sozinhos podem ser muito genéricos
                    # Esta é uma heurística, pode precisar de ajuste.
                    # Vamos focar em termos que provavelmente são números de modelo (contêm dígitos)
                    # ou termos mais longos.
                    if len(term_candidate) < 3 or term_candidate in ['am4', 'am5', 'lga']: # Evita termos muito curtos ou genéricos sozinhos
                         if i < len(essential_terms) -1 : # Se não for o último termo, pula para o próximo.
                            continue 
                         # Se for o último, permite a tentativa.

                    query_model_iterative = Q(model__icontains=term_candidate)
                    current_candidates = list(SpecModel.objects.filter(query_model_iterative))
                    self.stdout.write(f"    - Usando termo '{term_candidate}': {len(current_candidates)} candidatos.")
                    if current_candidates:
                        candidates = current_candidates
                        self.stdout.write(f"  -> [Tentativa 2: Modelo Iterativo] Sucesso com termo '{term_candidate}'.")
                        break # Encontrou candidatos, para de iterar
            
            # Tentativa 3: Busca Aberta (OR com todos os termos) - Nossa rede de segurança
            if not candidates and essential_terms: # Apenas se ainda não encontrou e há termos
                self.stdout.write(self.style.WARNING("  -> [Tentativa 3: Aberta] Nenhuma das buscas precisas funcionou. A usar busca aberta..."))
                query_open = Q()
                for term in essential_terms:
                    query_open |= Q(model__icontains=term)
                candidates = list(SpecModel.objects.filter(query_open))
                self.stdout.write(f"  -> [Tentativa 3: Aberta] Encontrados {len(candidates)} candidatos.")
            
            # --- FIM DA LÓGICA DE BUSCA MELHORADA ---

            if not candidates:
                self.stdout.write(
                    self.style.ERROR(
                        "  -> Nenhum candidato encontrado em nenhuma das buscas."
                    )
                )
                continue

            CANDIDATE_LIMIT = 32
            if len(candidates) > CANDIDATE_LIMIT:
                self.stdout.write(
                    f"  -> Encontrados {len(candidates)} candidatos. A limitar a {CANDIDATE_LIMIT} para ranking."
                )
                candidates = candidates[:CANDIDATE_LIMIT]
            else:
                self.stdout.write(
                    f"  -> Encontrados {len(candidates)} candidatos. A iniciar o ranking..."
                )

            # --- INÍCIO DA LÓGICA DE DECISÃO INSPIRADA NO ReS ---
            scored_candidates = get_scores_for_all_candidates(
                item.product_name_on_source.lower(), candidates, component_type_arg
            )

            if not scored_candidates:
                self.stdout.write(
                    self.style.WARNING("  -> A IA não retornou pontuações.")
                )
                continue

            best_candidate, best_score = scored_candidates[0]
            second_best_candidate, second_best_score = (None, -100)
            if len(scored_candidates) > 1:
                second_best_candidate, second_best_score = scored_candidates[1]

            if best_score < CONFIDENCE_THRESHOLD:
                self.stdout.write(
                    f"  -> Melhor candidato '{best_candidate.model}' com pontuação baixa ({best_score:.2f}). A descartar."
                )
                continue

            score_difference = best_score - second_best_score
            if second_best_candidate and score_difference < AMBIGUITY_THRESHOLD:
                self.stdout.write(
                    self.style.WARNING(
                        f"  -> CASO AMBÍGUO: '{best_candidate.model}' (score: {best_score:.2f}) "
                        f"muito próximo de '{second_best_candidate.model}' (score: {second_best_score:.2f}). "
                        f"Diferença: {score_difference:.2f}. A descartar."
                    )
                )
                continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"  -> SELEÇÃO CONFIANTE: '{best_candidate.model}' (Score: {best_score:.2f}, "
                    f"Diferença para o próximo: {score_difference:.2f})"
                )
            )
            item.component = best_candidate
            items_to_update.append(item)
            # --- FIM DA LÓGICA DE DECISÃO ---

        if items_to_update:
            CurrentVolatileData.objects.bulk_update(
                items_to_update, ["content_type", "object_id"]
            )
            processed_count = len(items_to_update)
        else:
            processed_count = 0

        end_time = time.time()
        self.stdout.write("\n" + "-" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Processo concluído em {end_time - start_time:.2f} segundos."
            )
        )
        self.stdout.write(
            f"Total de {processed_count} novos vínculos foram criados para '{component_type_arg.upper()}'."
        )

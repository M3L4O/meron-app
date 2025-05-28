from typing import Any, List, Optional, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

CONFIDENCE_THRESHOLD = 1.5
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-12-v2"

print("A carregar o modelo Cross-Encoder...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    print("Modelo carregado com sucesso.")
except Exception as e:
    print(f"Erro fatal ao carregar o modelo de IA: {e}")
    model = None

COMPONENT_ATTRS = {
    "cpu": [
        ("n_cores", "{value} cores"),
        ("base_clock_speed", "{value}GHz"),
        ("boost_clock_speed", "{value}GHz turbo"),
        ("socket", "{value}"),
        ("integrated_gpu", "{value}")
    ],
    "gpu": [
        ("vram", "{value}GB VRAM"),
        ("vram_speed", "{value}MHz VRAM speed"),
        ("consumption", "{value}W consumption"),
    ],
    "motherboard": [
        ("socket", "socket {value}"),
        ("board_size", "form_factor {value}"),
        ("memory_gen", "{value}"),
        ("memory_max", "{value}GB max_memory"),
    ],
    "ram": [
        ("size", "{value}GB"),
        ("generation", "{value}"),
        ("speed", "{value}MHz"),
    ],
    "storage": [
        ("capacity", "{value}GB"),
        ("io", "{value}"),
        (
            "is_hdd",
            lambda c: "HDD" if c.is_hdd else "SSD",
        ),  # Função para lógica condicional
        (
            "rpm",
            "{value} RPM",
            lambda c: c.is_hdd and c.rpm > 0,
        ),  # Só adiciona se for HDD com RPM
    ],
    "psu": [
        ("power", "{value}W"),
        ("rate", "{value}"),
    ],
}


def get_component_description(candidate: Any, component_type: str) -> str:
    """
    DOCUMENTAÇÃO: Gera uma descrição textual rica para um candidato a componente.
    Usa o dicionário COMPONENT_ATTRS para saber quais atributos são importantes
    para cada tipo de componente.

    Args:
        candidate: A instância do modelo do componente (ex: um objeto CPU).
        component_type: A string que identifica o tipo ('cpu', 'gpu', etc.).

    Returns:
        Uma string com a descrição formatada.
    """
    model_name = getattr(candidate, "model", "").strip()
    description_parts = [model_name]

    # Procura os atributos para o tipo de componente especificado
    attrs_to_check = COMPONENT_ATTRS.get(component_type, [])

    for attr_info in attrs_to_check:
        # Lógica para suportar condicionais na formatação
        if len(attr_info) == 3:
            attr_name, format_str, condition = attr_info
            if not condition(candidate):
                continue
        else:
            attr_name, format_str = attr_info

        value = getattr(candidate, attr_name, None)

        if value is not None and value != "" and value != 0:
            # Lógica para formatação condicional (ex: is_hdd)
            if callable(format_str):
                description_parts.append(format_str(candidate))
            else:
                description_parts.append(format_str.format(value=value))

    return ", ".join(filter(None, description_parts))


def get_scores_for_all_candidates(
    query_name: str, candidates: List[Any], component_type: str
) -> Optional[List[Tuple[Any, float]]]:
    """
    DOCUMENTAÇÃO: Usa o Cross-Encoder para pontuar TODOS os candidatos.

    Args:
        query_name: O nome do produto que estamos a tentar encontrar.
        candidates: Uma lista de objetos da base de dados que são candidatos.
        component_type: A string que identifica o tipo ('cpu', 'gpu', etc.).

    Returns:
        Uma lista de tuplos (candidato, pontuação), ordenada da maior para a menor pontuação,
        ou None se não houver candidatos ou modelo.
    """
    if not candidates or not model:
        return None

    pairs = [
        [query_name, get_component_description(c, component_type).lower()] for c in candidates
    ]

    with torch.no_grad():
        inputs = tokenizer(
            pairs, padding=True, truncation=True, return_tensors="pt", max_length=256
        )
        scores = model(**inputs).logits.squeeze()

    if scores.dim() == 0:
        scores = torch.tensor([scores.item()])

    scored_candidates = []
    for i, candidate in enumerate(candidates):
        scored_candidates.append((candidate, scores[i].item()))

    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    return scored_candidates


def rank_and_select_best_match(
    query_name: str, candidates: List[Any], component_type: str
) -> Optional[Any]:
    """
    DOCUMENTAÇÃO: Usa o Cross-Encoder para pontuar e selecionar o melhor candidato.

    Args:
        query_name: O nome do produto que estamos a tentar encontrar (ex: "Ryzen 5 5600G").
        candidates: Uma lista de objetos da base de dados que são candidatos.
        component_type: A string que identifica o tipo ('cpu', 'gpu', etc.).

    Returns:
        O objeto candidato com a maior pontuação, ou None se nenhum for bom o suficiente.
    """
    if not candidates or not model:
        return None

    # Cria pares de [query, descrição_do_candidato] para o modelo avaliar
    pairs = [
        [query_name, get_component_description(c, component_type)] for c in candidates
    ]

    with torch.no_grad():
        inputs = tokenizer(
            pairs, padding=True, truncation=True, return_tensors="pt", max_length=256
        )
        scores = model(**inputs).logits.squeeze()

    # Garante que 'scores' é sempre uma lista, mesmo com um só candidato
    if scores.dim() == 0:
        scores = torch.tensor([scores.item()])

    best_candidate_index = torch.argmax(scores).item()
    best_candidate = candidates[best_candidate_index]
    best_score = scores[best_candidate_index].item()

    # Verifica se a pontuação do melhor candidato atinge o nosso limiar de confiança
    if best_score < CONFIDENCE_THRESHOLD:
        print(
            f"  -> Melhor candidato '{best_candidate.model}' com pontuação baixa ({best_score:.2f}). A descartar."
        )
        return None

    best_description = pairs[best_candidate_index][1]
    print(
        f"  -> Selecionado: '{best_candidate.model}' (Descrição usada: '{best_description}') com pontuação: {best_score:.2f}"
    )
    return best_candidate

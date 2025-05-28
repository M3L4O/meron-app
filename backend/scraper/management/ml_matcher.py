from typing import Any, List, Optional, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

CONFIDENCE_THRESHOLD = 1.5
# MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-12-v2"
MODEL_NAME = "cross-encoder/ms-marco-TinyBERT-L-2-v2"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("A carregar o modelo Cross-Encoder...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.to(DEVICE)
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
        ("integrated_gpu", "{value}"),

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
        ("is_hdd", lambda c: "HDD" if c.is_hdd else "SSD"),
        ("rpm", "{value} RPM", lambda c: c.is_hdd and c.rpm > 0),
    ],
    "psu": [
        ("power", "{value}W"),
        ("rate", "{value}"),
    ],
}


def get_component_description(candidate: Any, component_type: str) -> str:
    model_name = getattr(candidate, "model", "").strip()
    description_parts = [model_name]

    attrs_to_check = COMPONENT_ATTRS.get(component_type, [])

    for attr_info in attrs_to_check:
        if len(attr_info) == 3:
            attr_name, format_str, condition = attr_info
            if not condition(candidate):
                continue
        else:
            attr_name, format_str = attr_info

        value = getattr(candidate, attr_name, None)

        if value not in (None, "", 0):
            description_parts.append(
                format_str(candidate)
                if callable(format_str)
                else format_str.format(value=value)
            )

    return ", ".join(filter(None, description_parts))


def get_scores_for_all_candidates(
    query_name: str, candidates: List[Any], component_type: str
) -> Optional[List[Tuple[Any, float]]]:
    if not candidates or not model:
        return None

    pairs = [
        [query_name, get_component_description(c, component_type).lower()]
        for c in candidates
    ]

    with torch.no_grad():
        inputs = tokenizer(
            pairs, padding=True, truncation=True, return_tensors="pt", max_length=256
        ).to(DEVICE)
        scores = model(**inputs).logits.squeeze()

    if scores.dim() == 0:
        scores = torch.tensor([scores.item()])

    scored_candidates = [
        (candidates[i], scores[i].item()) for i in range(len(candidates))
    ]
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    return scored_candidates


def rank_and_select_best_match(
    query_name: str,
    candidates: List[Any],
    component_type: str,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> Optional[Any]:
    if not candidates or not model:
        return None

    pairs = [
        [query_name, get_component_description(c, component_type)] for c in candidates
    ]

    with torch.no_grad():
        inputs = tokenizer(
            pairs, padding=True, truncation=True, return_tensors="pt", max_length=256
        ).to(DEVICE)
        scores = model(**inputs).logits.squeeze()

    if scores.dim() == 0:
        scores = torch.tensor([scores.item()])

    best_index = torch.argmax(scores).item()
    best_candidate = candidates[best_index]
    best_score = scores[best_index].item()

    if best_score < confidence_threshold:
        print(
            f"  -> Melhor candidato '{best_candidate.model}' com pontuação baixa ({best_score:.2f}). A descartar."
        )
        return None

    print(
        f"  -> Selecionado: '{best_candidate.model}' (Descrição usada: '{pairs[best_index][1]}') com pontuação: {best_score:.2f}"
    )
    return best_candidate

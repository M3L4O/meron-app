import json

import numpy as np
from sentence_transformers import SentenceTransformer, util

with open("data/cpus.json", "r") as spec_file:
    specs = json.load(spec_file)

with open("data/cpu_volatile.json", "r") as volatile_file:
    volatile_data = json.load(volatile_file)

model = SentenceTransformer("all-MiniLM-L6-v2")

spec_names = [item["model"] for item in specs]
spec_embeddings = model.encode(spec_names, convert_to_tensor=True)


def read_and_select(mention, spec_embeddings, specs, model, threshold=0.75):
    mention_emb = model.encode(mention, convert_to_tensor=True)
    cosine_scores = util.cos_sim(mention_emb, spec_embeddings)[0]
    top_idx = np.argmax(cosine_scores.cpu().numpy())
    top_score = cosine_scores[top_idx].item()
    if top_score >= threshold:
        return specs[top_idx], top_score
    else:
        return None, top_score


for produto in volatile_data:
    nome_volatil = produto["model"]
    entidade, score = read_and_select(nome_volatil, spec_embeddings, specs, model)
    if entidade:
        # print(f"'{nome_volatil}' ligado a '{entidade['model']}' (score {score:.3f})")
        ...
    else:
        print(
            f"'{nome_volatil}' não ligado a nenhuma entidade confiável (score {score:.3f})"
        )

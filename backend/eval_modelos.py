import json, os, time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELOS = [
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
    "allam-2-7b",
    "groq/compound-mini",
]
PROMPT_TEMPLATE = """Es um assistente especializado em retalho de luxo.
Analisa esta conversa e extrai informacao para CRM.

CONVERSA:
TRANSCRIPT_PLACEHOLDER

Responde APENAS com JSON valido, sem markdown:
{
    "client_profile": {
        "gender": null,
        "age_range": null,
        "residence": null,
        "client_tier": null,
        "style_preferences": [],
        "fabric_preferences": [],
        "sizes": {"clothing": null, "shoes": null, "other": null}
    },
    "purchase_history": {
        "products_owned": [],
        "estimated_spend": null,
        "purchase_frequency": null
    },
    "family_relations": [],
    "memories": [],
    "current_visit": {
        "products_mentioned": [],
        "purchase_intent": "high/medium/low",
        "budget_range": null,
        "occasion": null
    },
    "follow_up_actions": [],
    "summary": null
}

REGRAS: usa null para campos sem info, tamanhos em numeros, follow_up_actions lista de strings simples, SEM markdown"""


def extract_crm(segments, model):
    lines = []
    for s in segments:
        lines.append(s["speaker"] + ": " + s["text"])
    transcript = "\n".join(lines)
    prompt = PROMPT_TEMPLATE.replace("TRANSCRIPT_PLACEHOLDER", transcript)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip()), None
    except json.JSONDecodeError as e:
        return None, "JSON invalido: " + str(e)
    except Exception as e:
        return None, "Erro: " + str(e)


def avaliar(resultado, ground_truth):
    score = 0
    total = 0
    erros = []

    # gender
    total += 1
    gt_val = (ground_truth.get("client_profile") or {}).get("gender") or ""
    res_val = (resultado.get("client_profile") or {}).get("gender") or ""
    if not gt_val:
        score += 1
    elif gt_val.lower() in res_val.lower():
        score += 1
    else:
        erros.append("gender: esperado='" + gt_val + "' obtido='" + res_val + "'")

    # residence
    total += 1
    gt_val = (ground_truth.get("client_profile") or {}).get("residence") or ""
    res_val = (resultado.get("client_profile") or {}).get("residence") or ""
    if not gt_val:
        score += 1
    elif gt_val.lower() in res_val.lower():
        score += 1
    else:
        erros.append("residence: esperado='" + gt_val + "' obtido='" + res_val + "'")

    # clothing size
    total += 1
    gt_val = str((ground_truth.get("client_profile") or {}).get("sizes", {}).get("clothing") or "")
    res_sizes = (resultado.get("client_profile") or {}).get("sizes") or {}
    res_val = str(res_sizes.get("clothing") or "")
    if not gt_val:
        score += 1
    elif gt_val in res_val:
        score += 1
    else:
        erros.append("clothing_size: esperado='" + gt_val + "' obtido='" + res_val + "'")

    # purchase_intent
    total += 1
    gt_val = (ground_truth.get("current_visit") or {}).get("purchase_intent") or ""
    res_val = (resultado.get("current_visit") or {}).get("purchase_intent") or ""
    if not gt_val:
        score += 1
    elif gt_val.lower() in res_val.lower():
        score += 1
    else:
        erros.append("purchase_intent: esperado='" + gt_val + "' obtido='" + res_val + "'")

    # follow_up_actions
    total += 1
    actions = resultado.get("follow_up_actions") or []
    if actions and isinstance(actions[0], str):
        score += 1
    elif not actions:
        erros.append("follow_up_actions: vazio")
    else:
        erros.append("follow_up_actions: devia ser lista de strings")

    # summary
    total += 1
    if resultado.get("summary"):
        score += 1
    else:
        erros.append("summary: em falta")

    # family_relations schema
    total += 1
    gt_fam = ground_truth.get("family_relations") or []
    res_fam = resultado.get("family_relations") or []
    if not gt_fam:
        score += 1
    elif res_fam and isinstance(res_fam[0], dict):
        score += 1
    else:
        erros.append("family_relations: schema errado — " + str(res_fam[:1]))

    return score, total, erros


with open("dataset_eval_voicecrm.json") as f:
    dataset = json.load(f)

resultados_finais = {}

for model in MODELOS:
    print("\n" + "="*60)
    print("MODELO: " + model)
    print("="*60)
    total_score = 0
    total_max = 0

    for conv in dataset["conversations"]:
        print("  " + conv["title"])
        resultado, erro = extract_crm(conv["segments"], model)
        if erro:
            print("  ERRO: " + erro)
            continue
        score, maximo, erros = avaliar(resultado, conv["ground_truth"])
        total_score += score
        total_max += maximo
        pct = round(score / maximo * 100)
        print("  Score: " + str(score) + "/" + str(maximo) + " (" + str(pct) + "%)")
        for e in erros:
            print("    ! " + e)
        time.sleep(1)

    pct_total = round(total_score / total_max * 100) if total_max > 0 else 0
    resultados_finais[model] = pct_total
    print("  TOTAL: " + str(total_score) + "/" + str(total_max) + " (" + str(pct_total) + "%)")

print("\n" + "="*60)
print("RANKING FINAL")
print("="*60)
for model, pct in sorted(resultados_finais.items(), key=lambda x: -x[1]):
    print("  " + str(pct) + "%  " + model)
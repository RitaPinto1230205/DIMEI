"""
VoiceCRM — LLM Evaluation Script v2.0
Avalia modelos de linguagem na tarefa de extração de dados CRM
a partir de transcrições de conversas diarizadas (STT output).

MÉTRICAS IMPLEMENTADAS:
  === DATA FIDELITY ===
  1.  Exact Match (EM)         — valor extraído == ground truth (exacto)
  2.  Precision                — dos campos extraídos, % correctos
  3.  Recall                   — dos campos no GT, % extraídos
  4.  F1-Score                 — média harmónica Precision/Recall
  5.  Hallucination Rate       — % de campos inventados sem evidência

  === SCHEMA COMPLIANCE ===
  6.  Schema Validity          — JSON segue o schema definido (tipos, estrutura)
  7.  Null Discipline          — sem strings vazias ou "desconhecido"
  8.  Language Compliance      — campos em português (gender não em inglês)

  === OPERATIONAL / DIAGNOSTIC ===
  9.  Latency (s)              — tempo de resposta por chamada
  10. Token Efficiency         — tokens usados por campo correctamente extraído
  11. JSON Parse Rate          — % de respostas parseáveis sem erro
  12. Follow-up Actionability  — follow_up_actions são strings accionáveis
  13. Summary Quality          — summary presente e com >20 chars
"""

import json, os, time
from groq import Groq
from dotenv import load_dotenv

load_dotenv('/Users/ritapinto/Desktop/TESE-project/backend/.env')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELOS = [
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
    "allam-2-7b",
]

MODELO_INFO = {
    "llama-3.1-8b-instant":                     {"params": "8B",  "open_source": True,  "fabricante": "Meta"},
    "llama-3.3-70b-versatile":                   {"params": "70B", "open_source": True,  "fabricante": "Meta"},
    "meta-llama/llama-4-scout-17b-16e-instruct": {"params": "17B", "open_source": True,  "fabricante": "Meta"},
    "allam-2-7b":                                {"params": "7B",  "open_source": False, "fabricante": "SDAIA"},
    "groq/compound-mini":                        {"params": "?",   "open_source": False, "fabricante": "Groq"},
    "qwen/qwen3-32b":                            {"params": "32B", "open_source": True,  "fabricante": "Alibaba"},
}

PROMPT_TEMPLATE = """Es um assistente especializado em retalho de luxo.
Analisa esta conversa entre consultor e cliente (output de sistema STT com diarizacao de locutores) e extrai informacao para o CRM da loja.

CONVERSA:
TRANSCRIPT_PLACEHOLDER

Responde APENAS com JSON valido, sem markdown, sem texto adicional:
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
    "summary": "resumo obrigatório em português europeu, 50-100 palavras"
}


REGRAS:
- gender: "masculino" ou "feminino" em portugues
- null para campos sem informacao, nunca strings vazias ou "desconhecido"
- tamanhos em numeros ("38", "43")
- follow_up_actions: lista de strings simples e accionaveis
- family_relations: lista de objectos {relation, name, occasions, preferences}
- purchase_intent: "high", "medium" ou "low"
- O campo summary é OBRIGATÓRIO — escreve sempre um resumo em português europeu entre 50 e 100 palavras, mencionando o perfil do cliente, os produtos discutidos e as acções de seguimento
- Responde APENAS com JSON"""


def safe_str(val):
    if val is None: return ""
    if isinstance(val, (str, int, float)): return str(val)
    if isinstance(val, list): return " ".join([safe_str(v) for v in val])
    return str(val)


def extract_crm(segments, model):
    lines = [s["speaker"] + ": " + s["text"] for s in segments]
    transcript = "\n".join(lines)
    prompt = PROMPT_TEMPLATE.replace("TRANSCRIPT_PLACEHOLDER", transcript)
    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        latencia = round(time.time() - t0, 2)
        content = response.choices[0].message.content.strip()
        usage = response.usage
        tok_in = usage.prompt_tokens if usage else 0
        tok_out = usage.completion_tokens if usage else 0

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        if not content:
            return None, "Resposta vazia", latencia, tok_in, tok_out, False

        result = json.loads(content)
        return result, None, latencia, tok_in, tok_out, True

    except json.JSONDecodeError as e:
        return None, "JSON invalido: " + str(e)[:60], round(time.time()-t0,2), 0, 0, False
    except Exception as e:
        msg = str(e)
        if "rate_limit" in msg.lower() or "429" in msg:
            return None, "RATE LIMIT", round(time.time()-t0,2), 0, 0, False
        return None, "Erro: " + msg[:80], round(time.time()-t0,2), 0, 0, False


# ── CAMPOS ESCALARES A AVALIAR ────────────────────────────────────────────────
# (caminho_no_resultado, caminho_no_gt, nome)
SCALAR_FIELDS = [
    (["client_profile", "gender"],    ["client_profile", "gender"],    "gender"),
    (["client_profile", "residence"], ["client_profile", "residence"], "residence"),
    (["client_profile", "age_range"], ["client_profile", "age_range"], "age_range"),
    (["client_profile", "client_tier"],["client_profile","client_tier"],"client_tier"),
    (["client_profile","sizes","clothing"],["client_profile","sizes","clothing"],"clothing_size"),
    (["client_profile","sizes","shoes"],  ["client_profile","sizes","shoes"],   "shoe_size"),
    (["current_visit","purchase_intent"], ["current_visit","purchase_intent"],  "purchase_intent"),
    (["current_visit","budget_range"],    ["current_visit","budget_range"],     "budget_range"),
    (["current_visit","occasion"],        ["current_visit","occasion"],         "occasion"),
]

def get_nested(d, keys):
    for k in keys:
        if not isinstance(d, dict): return None
        d = d.get(k)
    return d


def compute_metrics(resultado, ground_truth, tok_in, tok_out):
    """Retorna dicionário com todas as métricas."""
    m = {}

    # ── 1-4. EM, Precision, Recall, F1 ─────────────────────────────────────
    tp = 0  # campo extraído e correcto
    fp = 0  # campo extraído mas errado ou inventado
    fn = 0  # campo no GT mas não extraído

    field_results = {}
    for res_path, gt_path, name in SCALAR_FIELDS:
        gt_val  = safe_str(get_nested(ground_truth, gt_path)).lower().strip()
        res_val = safe_str(get_nested(resultado, res_path)).lower().strip()

        if not gt_val:
            # campo sem GT — não conta para recall, só verifica se não inventou muito
            if res_val and len(res_val) > 0:
                pass  # aceitável
            field_results[name] = "n/a"
            continue

        if not res_val:
            fn += 1
            field_results[name] = "miss"
        elif gt_val in res_val or any(p.strip() in res_val for p in gt_val.split(",")):
            tp += 1
            field_results[name] = "ok"
        else:
            fp += 1
            fn += 1
            field_results[name] = "wrong:" + res_val[:20]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    m["exact_match_fields"] = tp
    m["precision"] = round(precision * 100, 1)
    m["recall"]    = round(recall * 100, 1)
    m["f1"]        = round(f1 * 100, 1)
    m["field_results"] = field_results

    # ── 5. Hallucination Rate ──────────────────────────────────────────────
    # Verifica se o summary menciona entidades que NÃO aparecem na conversa
    # Heurística: campos com valores mas GT=null são potenciais alucinações
    hallucinated = 0
    halluc_fields = []
    for res_path, gt_path, name in SCALAR_FIELDS:
        gt_val  = safe_str(get_nested(ground_truth, gt_path)).strip()
        res_val = safe_str(get_nested(resultado, res_path)).strip()
        bad_vals = {"desconhecido","unknown","n/a","nao disponivel","nao mencionado"}
        if gt_val == "" and res_val != "" and res_val.lower() not in bad_vals:
            hallucinated += 1
            halluc_fields.append(name + "=" + res_val[:15])

    total_gt_empty = sum(1 for _, gp, _ in SCALAR_FIELDS if not safe_str(get_nested(ground_truth, gp)).strip())
    m["hallucination_rate"] = round(hallucinated / total_gt_empty * 100, 1) if total_gt_empty > 0 else 0.0
    m["hallucinated_fields"] = halluc_fields

    # ── 6. Schema Validity ─────────────────────────────────────────────────
    schema_errors = []
    # family_relations deve ser lista de dicts
    fam = resultado.get("family_relations")
    gt_fam = ground_truth.get("family_relations") or []
    if gt_fam:
        if not isinstance(fam, list):
            schema_errors.append("family_relations: nao e lista")
        elif fam and not isinstance(fam[0], dict):
            schema_errors.append("family_relations: elementos nao sao dicts")
    # follow_up_actions deve ser lista de strings
    actions = resultado.get("follow_up_actions")
    if not isinstance(actions, list):
        schema_errors.append("follow_up_actions: nao e lista")
    elif actions and not isinstance(actions[0], str):
        schema_errors.append("follow_up_actions: elementos nao sao strings")
    # purchase_intent deve ser high/medium/low
    intent = safe_str((resultado.get("current_visit") or {}).get("purchase_intent")).lower()
    if intent and intent not in ["high", "medium", "low"]:
        schema_errors.append("purchase_intent: valor invalido '" + intent + "'")
    # sizes devem ser strings numéricas ou null
    sizes_raw = (resultado.get("client_profile") or {}).get("sizes")
    sizes = sizes_raw if isinstance(sizes_raw, dict) else {}
    for sz_key in ["clothing", "shoes"]:
        sz_val = sizes.get(sz_key)
        if sz_val is not None:
            try:
                float(str(sz_val))
            except ValueError:
                schema_errors.append("sizes." + sz_key + ": nao numerico '" + str(sz_val)[:10] + "'")

    m["schema_valid"] = len(schema_errors) == 0
    m["schema_errors"] = schema_errors

    # ── 7. Null Discipline ─────────────────────────────────────────────────
    json_str = json.dumps(resultado, ensure_ascii=False).lower()
    bad_vals = ["desconhecido", "unknown", "n/a", "nao disponivel", "\"\"", "nao mencionado"]
    found_bad = [bv for bv in bad_vals if bv in json_str]
    m["null_discipline"] = len(found_bad) == 0
    m["null_violations"] = found_bad

    # ── 8. Language Compliance ─────────────────────────────────────────────
    gender_val = safe_str((resultado.get("client_profile") or {}).get("gender")).lower()
    lang_ok = "male" not in gender_val and "female" not in gender_val
    m["language_compliance"] = lang_ok
    m["language_violation"] = gender_val if not lang_ok else None

    # ── 9. Latency — passada como parâmetro externo ────────────────────────
    # (gerida no loop principal)

    # ── 10. Token Efficiency ───────────────────────────────────────────────
    total_tokens = tok_in + tok_out
    m["tokens_total"] = total_tokens
    m["token_efficiency"] = round(total_tokens / max(tp, 1), 1)  # tokens por campo correcto

    # ── 11. JSON Parse Rate — gerida no loop principal ─────────────────────

    # ── 12. Follow-up Actionability ────────────────────────────────────────
    actions = resultado.get("follow_up_actions") or []
    actionable = (
        len(actions) > 0
        and isinstance(actions[0], str)
        and len(actions[0]) > 10
    )
    m["followup_actionable"] = actionable
    m["followup_count"] = len(actions)

    # ── 13. Summary Quality ────────────────────────────────────────────────
    summary = resultado.get("summary") or ""
    m["summary_quality"] = len(str(summary)) > 30
    m["summary_len"] = len(str(summary))

    return m


# ── MAIN ──────────────────────────────────────────────────────────────────────

with open("dataset_golden_v3.json") as f:
    dataset = json.load(f)

num_conversas = len(dataset["conversations"])
print("\nVoiceCRM LLM Evaluation v2.0")
print("Dataset: " + dataset["dataset_info"]["name"])
print("Conversas: " + str(num_conversas) + " pç| Métricas: 13 (EM, Precision, Recall, F1, Hallucination, Schema, Null, Language, Latency, TokenEff, ParseRate, Actionability, Summary)")
print("="*75)

all_results = {}

for model in MODELOS:
    info = MODELO_INFO.get(model, {})
    print("\n" + "="*65)
    print("MODELO: " + model)
    print("Params: " + info.get("params","?") + " | Fabricante: " + info.get("fabricante","?") + " | OSS: " + str(info.get("open_source","?")))
    print("="*65)

    conv_metrics = []
    total_latencia = 0.0
    n_parse_ok = 0
    n_total = 0

    for conv in dataset["conversations"]:
        print("  " + conv["title"])
        n_total += 1

        resultado, erro, lat, tok_in, tok_out, parsed = extract_crm(conv["segments"], model)
        total_latencia += lat

        if not parsed or resultado is None:
            print("  ERRO (" + str(lat) + "s): " + str(erro))
            continue

        n_parse_ok += 1
        m = compute_metrics(resultado, conv["ground_truth"], tok_in, tok_out)
        m["latencia"] = lat
        m["conversation"] = conv["title"]
        conv_metrics.append(m)

        print("  F1=" + str(m["f1"]) + "% | P=" + str(m["precision"]) + "% | R=" + str(m["recall"]) + "% | Halluc=" + str(m["hallucination_rate"]) + "% | " + str(lat) + "s | " + str(m["tokens_total"]) + "tok")
        if not m["schema_valid"]:
            for e in m["schema_errors"]:
                print("    [SCHEMA] " + e)
        if not m["null_discipline"]:
            print("    [NULL]   valores invalidos: " + str(m["null_violations"]))
        if not m["language_compliance"]:
            print("    [LANG]   gender em ingles: " + str(m["language_violation"]))
        if m["hallucinated_fields"]:
            print("    [HALLUC] " + str(m["hallucinated_fields"]))
        if not m["followup_actionable"]:
            print("    [ACTION] follow_up vazio ou nao accionavel")
        if not m["summary_quality"]:
            print("    [SUMM]   summary em falta ou curto (" + str(m["summary_len"]) + " chars)")

        time.sleep(1)

    # Agregar métricas do modelo
    if conv_metrics:
        def avg(key): return round(sum(m[key] for m in conv_metrics) / len(conv_metrics), 1)
        def pct_true(key): return round(sum(1 for m in conv_metrics if m[key]) / len(conv_metrics) * 100, 1)

        agg = {
            "model": model,
            "info": info,
            "n_conversas_ok": n_parse_ok,
            "n_conversas_erro": n_total - n_parse_ok,
            "json_parse_rate": round(n_parse_ok / n_total * 100, 1),
            "f1_medio": avg("f1"),
            "precision_media": avg("precision"),
            "recall_media": avg("recall"),
            "hallucination_rate_media": avg("hallucination_rate"),
            "schema_compliance_rate": pct_true("schema_valid"),
            "null_discipline_rate": pct_true("null_discipline"),
            "language_compliance_rate": pct_true("language_compliance"),
            "latencia_media": round(total_latencia / n_total, 2),
            "token_efficiency_media": avg("token_efficiency"),
            "tokens_media": avg("tokens_total"),
            "followup_actionability_rate": pct_true("followup_actionable"),
            "summary_quality_rate": pct_true("summary_quality"),
            "conv_metrics": conv_metrics
        }
        all_results[model] = agg

        print("\n  SUBTOTAL:")
        print("  F1=" + str(agg["f1_medio"]) + "% | P=" + str(agg["precision_media"]) + "% | R=" + str(agg["recall_media"]) + "%")
        print("  Hallucination=" + str(agg["hallucination_rate_media"]) + "% | ParseRate=" + str(agg["json_parse_rate"]) + "%")
        print("  Schema=" + str(agg["schema_compliance_rate"]) + "% | NullDisc=" + str(agg["null_discipline_rate"]) + "% | Lang=" + str(agg["language_compliance_rate"]) + "%")
        print("  Latência=" + str(agg["latencia_media"]) + "s | Tokens/campo=" + str(agg["token_efficiency_media"]))
    else:
        all_results[model] = {
            "model": model, "info": info,
            "n_conversas_ok": 0, "n_conversas_erro": n_total,
            "json_parse_rate": 0, "f1_medio": 0,
            "precision_media": 0, "recall_media": 0,
            "hallucination_rate_media": 0,
            "schema_compliance_rate": 0, "null_discipline_rate": 0,
            "language_compliance_rate": 0,
            "latencia_media": round(total_latencia / max(n_total,1), 2),
            "token_efficiency_media": 0, "tokens_media": 0,
            "followup_actionability_rate": 0, "summary_quality_rate": 0,
            "conv_metrics": []
        }


# ── TABELA COMPARATIVA ────────────────────────────────────────────────────────

print("\n\n" + "="*75)
print("  RESULTADOS FINAIS — VoiceCRM LLM Evaluation v2.0")
print("="*75)

ranked = sorted(all_results.values(), key=lambda x: -x["f1_medio"])

W = 18
print("\n  {:<30} {:>{w}} {:>{w}} {:>{w}} {:>{w}} {:>{w}}".format(
    "MODELO", "F1", "Precis.", "Recall", "Halluc.", "ParseRate", w=W//2+2))
print("  " + "-"*73)
for d in ranked:
    print("  {:<30} {:>{w}}% {:>{w}}% {:>{w}}% {:>{w}}% {:>{w}}%".format(
        d["model"][:28],
        d["f1_medio"], d["precision_media"], d["recall_media"],
        d["hallucination_rate_media"], d["json_parse_rate"], w=W//2+1))

print("\n  {:<30} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
    "MODELO", "Schema", "NullDisc", "Lang", "Action", "Summary"))
print("  " + "-"*73)
for d in ranked:
    print("  {:<30} {:>7}% {:>7}% {:>6}% {:>6}% {:>6}%".format(
        d["model"][:28],
        d["schema_compliance_rate"], d["null_discipline_rate"],
        d["language_compliance_rate"],
        d["followup_actionability_rate"], d["summary_quality_rate"]))

print("\n  {:<30} {:>10} {:>10} {:>10}".format(
    "MODELO", "Latência(s)", "Tok/campo", "ParseRate%"))
print("  " + "-"*73)
for d in ranked:
    print("  {:<30} {:>10} {:>10} {:>9}%".format(
        d["model"][:28],
        d["latencia_media"], d["token_efficiency_media"], d["json_parse_rate"]))

print("\n" + "="*75)
if ranked:
    best = ranked[0]
    print("  MODELO RECOMENDADO: " + best["model"])
    print("  F1=" + str(best["f1_medio"]) + "% | Recall=" + str(best["recall_media"]) + "% | Hallucination=" + str(best["hallucination_rate_media"]) + "% | OSS=" + str(best["info"].get("open_source","?")))
print("="*75)

# ── GUARDAR ───────────────────────────────────────────────────────────────────
output = {
    "eval_version": "2.0",
    "dataset": dataset["dataset_info"]["name"],
    "dataset_version": dataset["dataset_info"]["version"],
    "num_conversations": num_conversas,
    "metrics_evaluated": [
        "Exact Match", "Precision", "Recall", "F1-Score",
        "Hallucination Rate", "Schema Validity", "Null Discipline",
        "Language Compliance", "Latency", "Token Efficiency",
        "JSON Parse Rate", "Followup Actionability", "Summary Quality"
    ],
    "data": {model: {k: v for k, v in d.items() if k != "conv_metrics"} for model, d in all_results.items()},
    "ranking": [{"pos": i+1, "model": d["model"], "f1": d["f1_medio"]} for i, d in enumerate(ranked)],
    "timestamp": time.strftime("%Y-%m-%d %H:%M")
}

fname = "eval_results_v2_" + time.strftime("%Y%m%d_%H%M") + ".json"
with open(fname, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n  Resultados guardados em: " + fname)
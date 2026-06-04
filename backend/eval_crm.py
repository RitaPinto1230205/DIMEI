"""
eval_crm.py — Avaliação de qualidade da extração CRM a partir de transcrições STT
===================================================================================
STT (Speech-to-Text): converte áudio em texto. Neste sistema, o SFSpeechRecognizer
do iOS transcreve a conversa e o FluidAudio/pyannote diariza os locutores.
Este script avalia a qualidade da extração de campos CRM pelo LLM a partir
dessas transcrições diarizadas.

Métricas avaliadas:
  - Field Extraction Rate (FER): % de campos preenchidos quando há informação
  - Schema Compliance (SC): % de campos com o tipo de dados correcto
  - Semantic Accuracy (SA): % de campos com conteúdo semanticamente correcto
  - Hallucination Rate (HR): % de campos inventados sem base na conversa
  - JSON Parse Rate (JPR): % de respostas que são JSON válido
  - Score Global: média ponderada de todas as métricas
"""

import json
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv("/Users/ritapinto/Desktop/TESE-project/backend/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Modelos a avaliar ─────────────────────────────────────────────────────────

MODELOS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "allam-2-7b",
    "groq/compound-mini",
]

# ── Golden Dataset ────────────────────────────────────────────────────────────
# Conversas sintéticas com ground truth anotado manualmente.
# Cobrem 5 perfis distintos de clientes de retalho de luxo.
# Cada campo do ground_truth representa o valor ESPERADO após extracção correcta.
# Campos null no ground_truth = informação não mencionada na conversa (modelo NÃO deve inventar).

GOLDEN_DATASET = [
    {
        "id": "conv_001",
        "title": "Cliente habitual — aniversário do marido",
        "segments": [
            {"speaker": "Consultor", "text": "Bom dia, Dra. Mariana! Que bom vê-la por cá.", "timestamp": "10:02:15"},
            {"speaker": "Cliente", "text": "Bom dia! Vim em março comprar o casaco tweed. Adoro-o.", "timestamp": "10:02:22"},
            {"speaker": "Consultor", "text": "Veio sozinha hoje?", "timestamp": "10:02:30"},
            {"speaker": "Cliente", "text": "Sim, trabalho aqui perto, no Porto, na Avenida da Boavista.", "timestamp": "10:02:38"},
            {"speaker": "Cliente", "text": "É o aniversário do meu marido, ele faz cinquenta anos. Quero estar impecável.", "timestamp": "10:02:58"},
            {"speaker": "Cliente", "text": "Prefiro algo clássico. Adoro tweed e seda. Uso o trinta e oito na roupa e trinta e seis em sapatos.", "timestamp": "10:03:20"},
            {"speaker": "Cliente", "text": "O meu filho mais novo faz dezoito anos em Julho, queria oferecer-lhe algo da Chanel.", "timestamp": "10:03:50"},
            {"speaker": "Cliente", "text": "Ele usa médio ou quarenta e dois. Gosta de streetwear com classe.", "timestamp": "10:04:10"},
            {"speaker": "Cliente", "text": "Para mim dois a três mil euros. Para o filho talvez oitocentos a mil.", "timestamp": "10:04:35"},
            {"speaker": "Cliente", "text": "Pode chamar-me pelo número no sistema. Chamo-me Mariana Ferreira.", "timestamp": "10:05:02"},
        ],
        "ground_truth": {
            "client_profile": {
                "gender": "feminino",
                "age_range": None,
                "residence": "Porto",
                "client_tier": None,
                "style_preferences": ["clássico"],
                "fabric_preferences": ["tweed", "seda"],
                "sizes": {"clothing": "38", "shoes": "36", "other": None}
            },
            "purchase_history": {
                "products_owned": ["casaco tweed"],
                "estimated_spend": None,
                "purchase_frequency": None
            },
            "family_relations": [
                {"relation": "marido", "name": None, "occasions": ["aniversário 50 anos"], "preferences": []},
                {"relation": "filho", "name": None, "occasions": ["aniversário 18 anos Julho"], "preferences": ["streetwear"]}
            ],
            "current_visit": {
                "products_mentioned": ["conjunto seda azul-marinho"],
                "purchase_intent": "high",
                "budget_range": "2000-3000",
                "occasion": "aniversário marido"
            },
            "follow_up_actions": ["contactar para opções filho Julho"],
            "summary": "Cliente habitual Porto, tweed/seda, aniversário marido e filho"
        },
        "hallucination_traps": ["país", "email", "número de telefone", "profissão"]
    },
    {
        "id": "conv_002",
        "title": "Nova cliente — turista brasileira",
        "segments": [
            {"speaker": "Consultor", "text": "Boa tarde! Bem-vinda à Chanel. É a primeira vez?", "timestamp": "15:10:05"},
            {"speaker": "Cliente", "text": "Sim, vim de São Paulo especialmente para fazer compras.", "timestamp": "15:10:12"},
            {"speaker": "Consultor", "text": "Que viagem especial! Está de férias?", "timestamp": "15:10:20"},
            {"speaker": "Cliente", "text": "Sim, duas semanas. Já vim três vezes a Portugal. Tenho família em Lisboa.", "timestamp": "15:10:28"},
            {"speaker": "Cliente", "text": "Quero uma bolsa clássica. Tenho o Boy Bag em preto que comprei há dois anos em Paris.", "timestamp": "15:10:45"},
            {"speaker": "Cliente", "text": "Beige ou camel. Em couro de novilho, não gosto de verniz.", "timestamp": "15:11:08"},
            {"speaker": "Cliente", "text": "Uso muito casual chic. Tenho uns quarenta e dois anos.", "timestamp": "15:11:28"},
            {"speaker": "Cliente", "text": "Não tenho limite. Já gastei cerca de cinco mil em Lisboa. Para a bolsa aceito até seis ou sete mil.", "timestamp": "15:11:50"},
            {"speaker": "Cliente", "text": "Chamo-me Beatriz Santos.", "timestamp": "15:12:38"},
        ],
        "ground_truth": {
            "client_profile": {
                "gender": "feminino",
                "age_range": "42",
                "residence": "São Paulo",
                "client_tier": None,
                "style_preferences": ["casual chic"],
                "fabric_preferences": ["couro de novilho"],
                "sizes": {"clothing": None, "shoes": None, "other": None}
            },
            "purchase_history": {
                "products_owned": ["Boy Bag preto"],
                "estimated_spend": "5000",
                "purchase_frequency": None
            },
            "family_relations": [],
            "current_visit": {
                "products_mentioned": ["Classic Flap", "19 Bag"],
                "purchase_intent": "high",
                "budget_range": "6000-7000",
                "occasion": "férias"
            },
            "follow_up_actions": ["registar Beatriz Santos para próximas visitas"],
            "summary": "Nova cliente brasileira São Paulo, casual chic, couro de novilho, alto poder de compra"
        },
        "hallucination_traps": ["profissão", "morada exacta", "número de telefone"]
    },
    {
        "id": "conv_003",
        "title": "Cliente jovem — oferta para mãe",
        "segments": [
            {"speaker": "Consultor", "text": "Bom dia! Em que posso ajudar?", "timestamp": "11:30:00"},
            {"speaker": "Cliente", "text": "Queria um presente para a minha mãe. É o aniversário dela daqui a duas semanas.", "timestamp": "11:30:08"},
            {"speaker": "Cliente", "text": "Ela tem uns sessenta anos, é muito elegante. Usa preto e bege, adora flores e pérolas.", "timestamp": "11:30:25"},
            {"speaker": "Cliente", "text": "Trabalha numa empresa de advocacia, veste-se sempre muito formal.", "timestamp": "11:30:45"},
            {"speaker": "Cliente", "text": "Tenho à volta de quinhentos euros. Somos três irmãos a oferecer juntos.", "timestamp": "11:31:05"},
            {"speaker": "Cliente", "text": "Ela usa as coisas, não gosta de guardar.", "timestamp": "11:31:28"},
            {"speaker": "Cliente", "text": "Oh, o broche de camélia é lindo! Ela ficava maluca.", "timestamp": "11:31:50"},
            {"speaker": "Cliente", "text": "Sou o Miguel Rodrigues. Tenho vinte e oito anos, é a primeira vez que venho à Chanel.", "timestamp": "11:32:10"},
        ],
        "ground_truth": {
            "client_profile": {
                "gender": "masculino",
                "age_range": "28",
                "residence": None,
                "client_tier": None,
                "style_preferences": [],
                "fabric_preferences": [],
                "sizes": {"clothing": None, "shoes": None, "other": None}
            },
            "purchase_history": {
                "products_owned": [],
                "estimated_spend": None,
                "purchase_frequency": None
            },
            "family_relations": [
                {"relation": "mãe", "name": None, "occasions": ["aniversário 2 semanas"], "preferences": ["clássico", "preto", "bege", "flores", "pérolas"]}
            ],
            "current_visit": {
                "products_mentioned": ["broche camélia", "foulard seda", "brincos pérola"],
                "purchase_intent": "high",
                "budget_range": "500",
                "occasion": "aniversário mãe"
            },
            "follow_up_actions": ["embalar para oferta", "registar Miguel Rodrigues"],
            "summary": "Jovem 28 anos, primeira visita, presente para mãe ~60 anos aniversário, orçamento 500€"
        },
        "hallucination_traps": ["tamanho mãe", "nome mãe", "morada"]
    },
    {
        "id": "conv_004",
        "title": "Cliente regular masculino — eventos formais",
        "segments": [
            {"speaker": "Consultor", "text": "Boa tarde, Dr. Ricardo! Muito prazer em recebê-lo.", "timestamp": "16:45:00"},
            {"speaker": "Cliente", "text": "Tenho um jantar de gala, uma conferência em Genebra e uma inauguração de galeria.", "timestamp": "16:45:28"},
            {"speaker": "Cliente", "text": "Tenho dois fatos que comprei aqui há três anos. O preto de lã e o cinzento.", "timestamp": "16:45:52"},
            {"speaker": "Cliente", "text": "Cinquenta em fatos, quarenta e três em sapatos.", "timestamp": "16:46:15"},
            {"speaker": "Cliente", "text": "Prefiro cortes clássicos com um detalhe diferente. Lã e cashmere sobretudo.", "timestamp": "16:46:42"},
            {"speaker": "Cliente", "text": "Orçamento não é factor principal. Diria até quatro ou cinco mil por peça.", "timestamp": "16:47:15"},
            {"speaker": "Cliente", "text": "Moro em Cascais. O ambiente é conservador mas apreciativo de qualidade.", "timestamp": "16:47:45"},
            {"speaker": "Cliente", "text": "Prefiro manhãs, terça ou quarta para a sessão de prova.", "timestamp": "16:48:10"},
        ],
        "ground_truth": {
            "client_profile": {
                "gender": "masculino",
                "age_range": None,
                "residence": "Cascais",
                "client_tier": None,
                "style_preferences": ["clássico"],
                "fabric_preferences": ["lã", "cashmere"],
                "sizes": {"clothing": "50", "shoes": "43", "other": None}
            },
            "purchase_history": {
                "products_owned": ["fato preto lã", "fato cinzento"],
                "estimated_spend": "4000-5000",
                "purchase_frequency": None
            },
            "family_relations": [],
            "current_visit": {
                "products_mentioned": ["blazer cashmere", "fato lã"],
                "purchase_intent": "high",
                "budget_range": "4000-5000",
                "occasion": "jantar gala, conferência Genebra, inauguração galeria"
            },
            "follow_up_actions": ["agendar prova terça ou quarta manhã"],
            "summary": "Cliente regular Cascais, lã/cashmere, 3 eventos formais, sessão prova terça/quarta"
        },
        "hallucination_traps": ["empresa", "email", "número telefone", "nome completo"]
    },
    {
        "id": "conv_005",
        "title": "Primeira compra — ligação emocional",
        "segments": [
            {"speaker": "Consultor", "text": "Boa tarde! Posso ajudá-la?", "timestamp": "14:20:00"},
            {"speaker": "Cliente", "text": "Tenho estado a poupar para comprar uma bolsa Chanel há dois anos.", "timestamp": "14:20:32"},
            {"speaker": "Cliente", "text": "A minha avó tinha uma e eu adorava desde pequena.", "timestamp": "14:20:42"},
            {"speaker": "Cliente", "text": "Quero algo que dure e que possa passar para a minha filha. Ela tem seis anos.", "timestamp": "14:20:55"},
            {"speaker": "Cliente", "text": "Principalmente para ocasiões especiais. Sou professora.", "timestamp": "14:21:22"},
            {"speaker": "Cliente", "text": "Preto. Quero algo que não saia de moda. Tenho trinta e cinco anos.", "timestamp": "14:21:45"},
            {"speaker": "Cliente", "text": "Quanto custa o Classic Flap médio em pele de cordeiro?", "timestamp": "14:22:08"},
            {"speaker": "Cliente", "text": "Tenho exactamente esse valor poupado. Moro em Braga, vim especialmente ao Porto.", "timestamp": "14:22:28"},
            {"speaker": "Cliente", "text": "Chamo-me Ana Sousa.", "timestamp": "14:22:48"},
        ],
        "ground_truth": {
            "client_profile": {
                "gender": "feminino",
                "age_range": "35",
                "residence": "Braga",
                "client_tier": None,
                "style_preferences": ["clássico", "atemporal"],
                "fabric_preferences": ["pele de cordeiro"],
                "sizes": {"clothing": None, "shoes": None, "other": None}
            },
            "purchase_history": {
                "products_owned": [],
                "estimated_spend": None,
                "purchase_frequency": None
            },
            "family_relations": [
                {"relation": "filha", "name": None, "occasions": ["herança futura"], "preferences": []},
                {"relation": "avó", "name": None, "occasions": [], "preferences": ["Chanel"]}
            ],
            "current_visit": {
                "products_mentioned": ["Classic Flap médio preto pele cordeiro"],
                "purchase_intent": "high",
                "budget_range": "6400",
                "occasion": "primeira compra pessoal"
            },
            "follow_up_actions": ["registar Ana Sousa, enviar info manutenção pele cordeiro"],
            "summary": "Professora 35 anos Braga, primeira compra, ligação emocional avó, Classic Flap preto"
        },
        "hallucination_traps": ["escola", "número telefone", "tamanho roupa"]
    }
]

# ── Prompt ────────────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """Es um assistente especializado em retalho de luxo.
Analisa esta conversa entre consultor e cliente e extrai informacao para CRM.

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
    "summary": null
}

REGRAS:
- Usa null para campos sem informacao na conversa, NUNCA inventes
- Tamanhos em numeros (38, 43)
- family_relations e lista de objectos com chaves: relation, name, occasions, preferences
- follow_up_actions e lista de strings simples
- Responde APENAS com JSON"""


# ── Funções de extracção ──────────────────────────────────────────────────────

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
        parsed = json.loads(content.strip())
        return parsed, None, True  # result, erro, json_ok
    except json.JSONDecodeError as e:
        return None, "JSON invalido: " + str(e), False
    except Exception as e:
        return None, "Erro API: " + str(e), False


# ── Métricas ──────────────────────────────────────────────────────────────────

def calcular_metricas(resultado, conv):
    gt = conv["ground_truth"]
    traps = conv.get("hallucination_traps", [])

    # ── 1. Field Extraction Rate (FER) ────────────────────────────────────────
    # % de campos preenchidos quando a informação existe no ground_truth
    campos_esperados = 0
    campos_extraidos = 0

    def check_field(gt_val, res_val):
        nonlocal campos_esperados, campos_extraidos
        if gt_val is not None and gt_val != [] and gt_val != "":
            campos_esperados += 1
            if res_val is not None and res_val != [] and res_val != "":
                campos_extraidos += 1

    cp_gt = gt.get("client_profile", {})
    cp_res = (resultado.get("client_profile") or {})
    check_field(cp_gt.get("gender"), cp_res.get("gender"))
    check_field(cp_gt.get("age_range"), cp_res.get("age_range"))
    check_field(cp_gt.get("residence"), cp_res.get("residence"))
    check_field(cp_gt.get("style_preferences"), cp_res.get("style_preferences"))
    check_field(cp_gt.get("fabric_preferences"), cp_res.get("fabric_preferences"))
    check_field((cp_gt.get("sizes") or {}).get("clothing"), (cp_res.get("sizes") or {}).get("clothing"))
    check_field((cp_gt.get("sizes") or {}).get("shoes"), (cp_res.get("sizes") or {}).get("shoes"))

    ph_gt = gt.get("purchase_history", {})
    ph_res = (resultado.get("purchase_history") or {})
    check_field(ph_gt.get("products_owned"), ph_res.get("products_owned"))
    check_field(ph_gt.get("estimated_spend"), ph_res.get("estimated_spend"))

    cv_gt = gt.get("current_visit", {})
    cv_res = (resultado.get("current_visit") or {})
    check_field(cv_gt.get("products_mentioned"), cv_res.get("products_mentioned"))
    check_field(cv_gt.get("purchase_intent"), cv_res.get("purchase_intent"))
    check_field(cv_gt.get("budget_range"), cv_res.get("budget_range"))
    check_field(cv_gt.get("occasion"), cv_res.get("occasion"))

    check_field(gt.get("follow_up_actions"), resultado.get("follow_up_actions"))
    check_field(gt.get("summary"), resultado.get("summary"))

    fer = round(campos_extraidos / campos_esperados * 100) if campos_esperados > 0 else 0

    # ── 2. Schema Compliance (SC) ─────────────────────────────────────────────
    # % de campos com o tipo de dados correcto
    sc_checks = 0
    sc_ok = 0

    def check_type(val, expected_type):
        nonlocal sc_checks, sc_ok
        sc_checks += 1
        if val is None:
            sc_ok += 1  # null é sempre aceitável
        elif isinstance(val, expected_type):
            sc_ok += 1

    check_type(cp_res.get("gender"), str)
    check_type(cp_res.get("residence"), str)
    check_type(cp_res.get("style_preferences"), list)
    check_type(cp_res.get("fabric_preferences"), list)
    check_type(resultado.get("family_relations"), list)
    check_type(resultado.get("follow_up_actions"), list)
    check_type(resultado.get("summary"), str)

    # family_relations deve ser lista de dicts
    fam = resultado.get("family_relations") or []
    sc_checks += 1
    if not fam or isinstance(fam[0], dict):
        sc_ok += 1

    # follow_up_actions deve ser lista de strings
    actions = resultado.get("follow_up_actions") or []
    sc_checks += 1
    if not actions or isinstance(actions[0], str):
        sc_ok += 1

    sc = round(sc_ok / sc_checks * 100) if sc_checks > 0 else 0

    # ── 3. Semantic Accuracy (SA) ─────────────────────────────────────────────
    # % de campos semanticamente correctos vs ground truth
    sa_checks = 0
    sa_ok = 0

    def check_semantic(gt_val, res_val, partial=False):
        nonlocal sa_checks, sa_ok
        if gt_val is None:
            return
        sa_checks += 1
        if res_val is None:
            return
        gt_str = str(gt_val).lower()
        res_str = str(res_val).lower()
        if partial:
            if any(part.strip() in res_str for part in gt_str.split(",")):
                sa_ok += 1
        else:
            if gt_str in res_str or res_str in gt_str:
                sa_ok += 1

    check_semantic(cp_gt.get("gender"), cp_res.get("gender"))
    check_semantic(cp_gt.get("residence"), cp_res.get("residence"), partial=True)
    check_semantic(cp_gt.get("age_range"), cp_res.get("age_range"), partial=True)
    check_semantic(cv_gt.get("purchase_intent"), cv_res.get("purchase_intent"))
    check_semantic(cv_gt.get("budget_range"), cv_res.get("budget_range"), partial=True)

    sa = round(sa_ok / sa_checks * 100) if sa_checks > 0 else 0

    # ── 4. Hallucination Rate (HR) ────────────────────────────────────────────
    # % de campos null no GT que foram inventados pelo modelo
    null_gt = 0
    null_invented = 0
    result_str = json.dumps(resultado, ensure_ascii=False).lower()
    for trap in traps:
        null_gt += 1
        if trap.lower() in result_str:
            null_invented += 1

    hr = round(null_invented / null_gt * 100) if null_gt > 0 else 0

    return {
        "fer": fer,
        "sc": sc,
        "sa": sa,
        "hr": hr,
        "global": round((fer * 0.30 + sc * 0.25 + sa * 0.30 + (100 - hr) * 0.15))
    }


# ── Main ──────────────────────────────────────────────────────────────────────

print("\n" + "="*70)
print("  VoiceCRM — EVAL de Extracção CRM a partir de transcrições STT")
print("="*70)
print("\nMétricas:")
print("  FER  = Field Extraction Rate   — % campos extraídos quando existem")
print("  SC   = Schema Compliance       — % campos com tipo de dados correcto")
print("  SA   = Semantic Accuracy       — % campos semanticamente correctos")
print("  HR   = Hallucination Rate      — % campos inventados (menos é melhor)")
print("  GLB  = Score Global            — média ponderada (30%FER+25%SC+30%SA+15%anti-HR)")

todos_resultados = {}

for model in MODELOS:
    print("\n" + "-"*70)
    print("MODELO: " + model)
    print("-"*70)

    model_metrics = []
    json_parse_ok = 0

    for conv in GOLDEN_DATASET:
        resultado, erro, json_ok = extract_crm(conv["segments"], model)

        if json_ok:
            json_parse_ok += 1

        if erro or not resultado:
            print("  [" + conv["id"] + "] ERRO: " + str(erro))
            model_metrics.append({"fer": 0, "sc": 0, "sa": 0, "hr": 100, "global": 0})
            time.sleep(0.5)
            continue

        metrics = calcular_metricas(resultado, conv)
        model_metrics.append(metrics)

        print("  [" + conv["id"] + "] " + conv["title"])
        print("    FER=" + str(metrics["fer"]) + "%  SC=" + str(metrics["sc"]) + "%  SA=" + str(metrics["sa"]) + "%  HR=" + str(metrics["hr"]) + "%  GLB=" + str(metrics["global"]) + "%")
        time.sleep(1)

    jpr = round(json_parse_ok / len(GOLDEN_DATASET) * 100)
    avg_fer = round(sum(m["fer"] for m in model_metrics) / len(model_metrics))
    avg_sc = round(sum(m["sc"] for m in model_metrics) / len(model_metrics))
    avg_sa = round(sum(m["sa"] for m in model_metrics) / len(model_metrics))
    avg_hr = round(sum(m["hr"] for m in model_metrics) / len(model_metrics))
    avg_glb = round(sum(m["global"] for m in model_metrics) / len(model_metrics))

    todos_resultados[model] = {
        "jpr": jpr, "fer": avg_fer, "sc": avg_sc,
        "sa": avg_sa, "hr": avg_hr, "global": avg_glb
    }

    print("  MÉDIA — FER=" + str(avg_fer) + "%  SC=" + str(avg_sc) + "%  SA=" + str(avg_sa) + "%  HR=" + str(avg_hr) + "%  JPR=" + str(jpr) + "%  GLB=" + str(avg_glb) + "%")

print("\n" + "="*70)
print("RANKING FINAL")
print("="*70)
print("  {:<45} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}".format("Modelo", "FER", "SC", "SA", "HR", "JPR", "GLB"))
print("  " + "-"*65)
for model, m in sorted(todos_resultados.items(), key=lambda x: -x[1]["global"]):
    print("  {:<45} {:>4}% {:>4}% {:>4}% {:>4}% {:>4}% {:>4}%".format(
        model[:45], m["fer"], m["sc"], m["sa"], m["hr"], m["jpr"], m["global"]))

# Guarda resultados em JSON para usar no Miro/visualização
with open("eval_results.json", "w") as f:
    json.dump({
        "modelos": todos_resultados,
        "dataset": [{"id": c["id"], "title": c["title"]} for c in GOLDEN_DATASET]
    }, f, ensure_ascii=False, indent=2)

print("\nResultados guardados em eval_results.json")

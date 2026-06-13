"""
VoiceCRM — Cálculo DER todas as sessões R01 a R12
Pré-requisito: servidor backend em execução em localhost:5003
Execução: uv run python3 calc_der_todas.py

VoiceCRM — Resultados DER R01 a R12
=================================================================
Sessão   Ambiente                        DER   RNF2
-----------------------------------------------------------------
R01      Doméstico                     9.9%     OK
R02      Doméstico                    13.1%     OK
R03      Escritório                    9.4%     OK
R04      Escritório                    4.5%     OK
R05      Doméstico c/ ruído           18.7%     OK
R06      Escritório                    6.3%     OK
R07      Doméstico                     6.5%     OK
R08      Escritório                    5.4%     OK
R09      Doméstico                     9.7%     OK
R10      Escritório                    6.7%     OK
R11      Público c/ muito ruído       17.1%     OK
R12      Público c/ muito ruído       16.3%     OK
-----------------------------------------------------------------
Média R01-R12                         10.3%

Cada linha comentada com ← ERRO é um segmento mal atribuído.
"""

import requests

BACKEND = "http://localhost:5003/der"

SESSOES = {
    "R01": {
    "ambiente": "Doméstico",
    "reference": [
        {"start": 0.0,  "end": 3.5,  "speaker": "Consultor"},  # Bom dia bem-vinda...
        {"start": 4.0,  "end": 9.1,  "speaker": "Cliente"},    # Bom dia estou à procura...
        {"start": 9.6,  "end": 18.0, "speaker": "Consultor"},  # Claro temos peças lindas...
        {"start": 18.5, "end": 26.0, "speaker": "Cliente"},    # Prefiro cores neutras...
        {"start": 26.5, "end": 30.0, "speaker": "Consultor"},  # Posso perguntar...
        {"start": 30.5, "end": 34.0, "speaker": "Cliente"},    # Sou um 36...
        {"start": 34.5, "end": 42.0, "speaker": "Consultor"},  # Temos um tweed creme...
        {"start": 42.5, "end": 48.0, "speaker": "Cliente"},    # Sim com certeza...
        {"start": 48.5, "end": 57.0, "speaker": "Consultor"},  # Este tweed está a 3200...
        {"start": 57.5, "end": 68.0, "speaker": "Cliente"},    # Ótimo o meu marido...
        {"start": 68.5, "end": 75.0, "speaker": "Consultor"},  # Para homem temos...
        {"start": 75.5, "end": 82.0, "speaker": "Cliente"},    # Perfumaria talvez...
        {"start": 82.5, "end": 86.0, "speaker": "Consultor"},  # Perfeito o Bleu de Chanel...
        {"start": 86.5, "end": 93.0, "speaker": "Cliente"},    # Muito bem vamos então...
    ],
    "hypothesis": [
        {"start": 0.0,  "end": 3.5,  "speaker": "Consultor"},
        {"start": 4.0,  "end": 9.1,  "speaker": "Consultor"},  # ← ERRO (era Cliente)
        {"start": 9.6,  "end": 18.0, "speaker": "Consultor"},
        {"start": 18.5, "end": 26.0, "speaker": "Cliente"},
        {"start": 26.5, "end": 30.0, "speaker": "Consultor"},
        {"start": 30.5, "end": 34.0, "speaker": "Cliente"},
        {"start": 34.5, "end": 42.0, "speaker": "Consultor"},
        {"start": 42.5, "end": 48.0, "speaker": "Cliente"},
        {"start": 48.5, "end": 57.0, "speaker": "Consultor"},
        {"start": 57.5, "end": 68.0, "speaker": "Cliente"},
        {"start": 68.5, "end": 75.0, "speaker": "Consultor"},
        {"start": 75.5, "end": 82.0, "speaker": "Cliente"},
        {"start": 82.5, "end": 86.0, "speaker": "Cliente"},    # ← ERRO (era Consultor)
        {"start": 86.5, "end": 93.0, "speaker": "Cliente"},
    ],
},
    "R02": {
        "ambiente": "Doméstico",
        "reference": [
            {"start": 0.0,   "end": 5.0,   "speaker": "Consultor"},
            {"start": 6.0,   "end": 16.0,  "speaker": "Cliente"},
            {"start": 17.0,  "end": 28.4,  "speaker": "Consultor"},
            {"start": 29.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 47.0,  "speaker": "Consultor"},
            {"start": 48.0,  "end": 57.0,  "speaker": "Cliente"},
            {"start": 58.0,  "end": 70.0,  "speaker": "Consultor"},
            {"start": 71.0,  "end": 83.0,  "speaker": "Cliente"},
            {"start": 84.0,  "end": 97.0,  "speaker": "Consultor"},
            {"start": 98.0,  "end": 107.0, "speaker": "Cliente"},
            {"start": 108.0, "end": 118.0, "speaker": "Consultor"},
            {"start": 119.0, "end": 127.0, "speaker": "Cliente"},
            {"start": 128.0, "end": 135.0, "speaker": "Consultor"},
            {"start": 136.0, "end": 143.0, "speaker": "Cliente"},
            {"start": 144.0, "end": 151.0, "speaker": "Consultor"},
            {"start": 152.0, "end": 157.0, "speaker": "Cliente"},
            {"start": 158.0, "end": 163.0, "speaker": "Consultor"},
            {"start": 164.0, "end": 169.0, "speaker": "Cliente"},
            {"start": 170.0, "end": 181.0, "speaker": "Consultor"},
            {"start": 182.0, "end": 187.0, "speaker": "Cliente"},
            {"start": 188.0, "end": 190.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,   "end": 5.0,   "speaker": "Consultor"},
            {"start": 6.0,   "end": 16.0,  "speaker": "Cliente"},
            {"start": 17.0,  "end": 28.4,  "speaker": "Cliente"},   # erro 11.4s
            {"start": 29.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 47.0,  "speaker": "Consultor"},
            {"start": 48.0,  "end": 57.0,  "speaker": "Cliente"},
            {"start": 58.0,  "end": 70.0,  "speaker": "Consultor"},
            {"start": 71.0,  "end": 83.0,  "speaker": "Cliente"},
            {"start": 84.0,  "end": 97.0,  "speaker": "Consultor"},
            {"start": 98.0,  "end": 107.0, "speaker": "Cliente"},
            {"start": 108.0, "end": 118.0, "speaker": "Consultor"},
            {"start": 119.0, "end": 127.0, "speaker": "Cliente"},
            {"start": 128.0, "end": 135.0, "speaker": "Consultor"},
            {"start": 136.0, "end": 143.0, "speaker": "Cliente"},
            {"start": 144.0, "end": 151.0, "speaker": "Consultor"},
            {"start": 152.0, "end": 157.0, "speaker": "Cliente"},
            {"start": 158.0, "end": 163.0, "speaker": "Consultor"},
            {"start": 164.0, "end": 169.0, "speaker": "Cliente"},
            {"start": 170.0, "end": 181.0, "speaker": "Cliente"},   # erro 11s
            {"start": 182.0, "end": 187.0, "speaker": "Cliente"},
            {"start": 188.0, "end": 190.0, "speaker": "Consultor"},
        ],
    },
    "R03": {
        "ambiente": "Escritório",
        "reference": [
            {"start": 0.0,   "end": 5.0,   "speaker": "Consultor"},
            {"start": 6.0,   "end": 17.0,  "speaker": "Cliente"},
            {"start": 18.0,  "end": 26.0,  "speaker": "Consultor"},
            {"start": 27.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 47.0,  "speaker": "Consultor"},
            {"start": 48.0,  "end": 58.0,  "speaker": "Cliente"},
            {"start": 59.0,  "end": 67.0,  "speaker": "Consultor"},
            {"start": 68.0,  "end": 77.0,  "speaker": "Cliente"},
            {"start": 78.0,  "end": 90.0,  "speaker": "Consultor"},
            {"start": 91.0,  "end": 102.0, "speaker": "Cliente"},
            {"start": 103.0, "end": 112.0, "speaker": "Consultor"},
            {"start": 113.0, "end": 120.0, "speaker": "Cliente"},
            {"start": 121.0, "end": 130.0, "speaker": "Consultor"},
            {"start": 131.0, "end": 140.0, "speaker": "Cliente"},
            {"start": 141.0, "end": 151.9, "speaker": "Consultor"},
            {"start": 152.4, "end": 160.0, "speaker": "Cliente"},
            {"start": 161.0, "end": 168.0, "speaker": "Consultor"},
            {"start": 169.0, "end": 175.0, "speaker": "Cliente"},
            {"start": 176.0, "end": 183.0, "speaker": "Consultor"},
            {"start": 184.0, "end": 187.0, "speaker": "Cliente"},
        ],
        "hypothesis": [
            {"start": 0.0,   "end": 5.0,   "speaker": "Cliente"},   # erro 5s
            {"start": 6.0,   "end": 17.0,  "speaker": "Cliente"},
            {"start": 18.0,  "end": 26.0,  "speaker": "Consultor"},
            {"start": 27.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 47.0,  "speaker": "Consultor"},
            {"start": 48.0,  "end": 58.0,  "speaker": "Cliente"},
            {"start": 59.0,  "end": 67.0,  "speaker": "Consultor"},
            {"start": 68.0,  "end": 77.0,  "speaker": "Cliente"},
            {"start": 78.0,  "end": 90.0,  "speaker": "Consultor"},
            {"start": 91.0,  "end": 102.0, "speaker": "Cliente"},
            {"start": 103.0, "end": 112.0, "speaker": "Consultor"},
            {"start": 113.0, "end": 120.0, "speaker": "Cliente"},
            {"start": 121.0, "end": 130.0, "speaker": "Consultor"},
            {"start": 131.0, "end": 140.0, "speaker": "Cliente"},
            {"start": 141.0, "end": 151.9, "speaker": "Cliente"},   # erro 10.9s
            {"start": 152.4, "end": 160.0, "speaker": "Cliente"},
            {"start": 161.0, "end": 168.0, "speaker": "Consultor"},
            {"start": 169.0, "end": 175.0, "speaker": "Cliente"},
            {"start": 176.0, "end": 183.0, "speaker": "Consultor"},
            {"start": 184.0, "end": 187.0, "speaker": "Cliente"},
        ],
    },
    "R04": {
        "ambiente": "Escritório",
        "reference": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 14.0, "speaker": "Cliente"},
            {"start": 15.0, "end": 22.0, "speaker": "Consultor"},
            {"start": 23.0, "end": 30.0, "speaker": "Cliente"},
            {"start": 31.0, "end": 38.0, "speaker": "Consultor"},
            {"start": 39.0, "end": 44.0, "speaker": "Cliente"},
            {"start": 45.0, "end": 48.1, "speaker": "Consultor"},
            {"start": 48.6, "end": 58.0, "speaker": "Cliente"},
            {"start": 59.0, "end": 64.0, "speaker": "Consultor"},
            {"start": 65.0, "end": 72.0, "speaker": "Cliente"},
            {"start": 73.0, "end": 78.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 14.0, "speaker": "Cliente"},
            {"start": 15.0, "end": 22.0, "speaker": "Consultor"},
            {"start": 23.0, "end": 30.0, "speaker": "Cliente"},
            {"start": 31.0, "end": 38.0, "speaker": "Consultor"},
            {"start": 39.0, "end": 44.0, "speaker": "Cliente"},
            {"start": 45.0, "end": 48.1, "speaker": "Cliente"},    # erro 3.1s
            {"start": 48.6, "end": 58.0, "speaker": "Cliente"},
            {"start": 59.0, "end": 64.0, "speaker": "Consultor"},
            {"start": 65.0, "end": 72.0, "speaker": "Cliente"},
            {"start": 73.0, "end": 78.0, "speaker": "Consultor"},
        ],
    },
    "R05": {
        "ambiente": "Doméstico c/ ruído",
        "reference": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 15.0, "speaker": "Cliente"},
            {"start": 16.0, "end": 22.0, "speaker": "Consultor"},
            {"start": 23.0, "end": 30.0, "speaker": "Cliente"},
            {"start": 31.0, "end": 39.0, "speaker": "Consultor"},
            {"start": 40.0, "end": 50.0, "speaker": "Cliente"},
            {"start": 51.0, "end": 57.0, "speaker": "Consultor"},
            {"start": 58.0, "end": 65.0, "speaker": "Cliente"},
            {"start": 66.0, "end": 74.9, "speaker": "Consultor"},
            {"start": 75.4, "end": 80.0, "speaker": "Cliente"},
            {"start": 81.0, "end": 85.0, "speaker": "Cliente"},
            {"start": 86.0, "end": 90.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 15.0, "speaker": "Cliente"},
            {"start": 16.0, "end": 22.0, "speaker": "Cliente"},    # erro 6s
            {"start": 23.0, "end": 30.0, "speaker": "Cliente"},
            {"start": 31.0, "end": 39.0, "speaker": "Consultor"},
            {"start": 40.0, "end": 50.0, "speaker": "Cliente"},
            {"start": 51.0, "end": 57.0, "speaker": "Consultor"},
            {"start": 58.0, "end": 65.0, "speaker": "Cliente"},
            {"start": 66.0, "end": 74.9, "speaker": "Cliente"},    # erro 8.9s
            {"start": 75.4, "end": 80.0, "speaker": "Cliente"},
            {"start": 81.0, "end": 85.0, "speaker": "Cliente"},
            {"start": 86.0, "end": 90.0, "speaker": "Consultor"},
        ],
    },
    "R06": {
        "ambiente": "Escritório",
        "reference": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 20.0,  "speaker": "Cliente"},
            {"start": 21.0,  "end": 27.0,  "speaker": "Consultor"},
            {"start": 28.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 44.0,  "speaker": "Consultor"},
            {"start": 45.0,  "end": 60.0,  "speaker": "Cliente"},
            {"start": 61.0,  "end": 67.0,  "speaker": "Consultor"},
            {"start": 68.0,  "end": 80.0,  "speaker": "Cliente"},
            {"start": 81.0,  "end": 92.0,  "speaker": "Consultor"},
            {"start": 93.0,  "end": 106.0, "speaker": "Cliente"},
            {"start": 107.0, "end": 116.0, "speaker": "Consultor"},
            {"start": 117.0, "end": 133.0, "speaker": "Cliente"},
            {"start": 134.0, "end": 143.0, "speaker": "Consultor"},
            {"start": 144.0, "end": 160.0, "speaker": "Cliente"},
            {"start": 161.0, "end": 172.0, "speaker": "Consultor"},
            {"start": 173.0, "end": 182.0, "speaker": "Cliente"},
            {"start": 183.0, "end": 188.0, "speaker": "Consultor"},
            {"start": 189.0, "end": 210.0, "speaker": "Cliente"},
            {"start": 211.0, "end": 218.0, "speaker": "Consultor"},
            {"start": 219.0, "end": 224.0, "speaker": "Cliente"},
        ],
        "hypothesis": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 20.0,  "speaker": "Cliente"},
            {"start": 21.0,  "end": 27.0,  "speaker": "Consultor"},
            {"start": 28.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 44.0,  "speaker": "Consultor"},
            {"start": 45.0,  "end": 60.0,  "speaker": "Cliente"},
            {"start": 61.0,  "end": 67.0,  "speaker": "Consultor"},
            {"start": 68.0,  "end": 80.0,  "speaker": "Cliente"},
            {"start": 81.0,  "end": 92.0,  "speaker": "Consultor"},
            {"start": 93.0,  "end": 106.0, "speaker": "Consultor"}, # erro 13s
            {"start": 107.0, "end": 116.0, "speaker": "Consultor"},
            {"start": 117.0, "end": 133.0, "speaker": "Cliente"},
            {"start": 134.0, "end": 143.0, "speaker": "Consultor"},
            {"start": 144.0, "end": 160.0, "speaker": "Cliente"},
            {"start": 161.0, "end": 172.0, "speaker": "Consultor"},
            {"start": 173.0, "end": 182.0, "speaker": "Cliente"},
            {"start": 183.0, "end": 188.0, "speaker": "Consultor"},
            {"start": 189.0, "end": 210.0, "speaker": "Cliente"},
            {"start": 211.0, "end": 218.0, "speaker": "Consultor"},
            {"start": 219.0, "end": 224.0, "speaker": "Cliente"},
        ],
    },
    "R07": {
        "ambiente": "Doméstico",
        "reference": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 15.0,  "speaker": "Cliente"},
            {"start": 16.0,  "end": 21.0,  "speaker": "Consultor"},
            {"start": 22.0,  "end": 32.0,  "speaker": "Cliente"},
            {"start": 33.0,  "end": 39.7,  "speaker": "Consultor"},
            {"start": 40.2,  "end": 50.0,  "speaker": "Cliente"},
            {"start": 51.0,  "end": 62.0,  "speaker": "Consultor"},
            {"start": 63.0,  "end": 70.0,  "speaker": "Cliente"},
            {"start": 71.0,  "end": 77.0,  "speaker": "Consultor"},
            {"start": 78.0,  "end": 90.0,  "speaker": "Cliente"},
            {"start": 91.0,  "end": 98.0,  "speaker": "Consultor"},
            {"start": 99.0,  "end": 108.0, "speaker": "Cliente"},
            {"start": 109.0, "end": 114.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 15.0,  "speaker": "Cliente"},
            {"start": 16.0,  "end": 21.0,  "speaker": "Consultor"},
            {"start": 22.0,  "end": 32.0,  "speaker": "Cliente"},
            {"start": 33.0,  "end": 39.7,  "speaker": "Cliente"},   # erro 6.7s
            {"start": 40.2,  "end": 50.0,  "speaker": "Cliente"},
            {"start": 51.0,  "end": 62.0,  "speaker": "Consultor"},
            {"start": 63.0,  "end": 70.0,  "speaker": "Cliente"},
            {"start": 71.0,  "end": 77.0,  "speaker": "Consultor"},
            {"start": 78.0,  "end": 90.0,  "speaker": "Cliente"},
            {"start": 91.0,  "end": 98.0,  "speaker": "Consultor"},
            {"start": 99.0,  "end": 108.0, "speaker": "Cliente"},
            {"start": 109.0, "end": 114.0, "speaker": "Consultor"},
        ],
    },
    "R08": {
        "ambiente": "Escritório",
        "reference": [
            {"start": 0.0,  "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,  "end": 15.0,  "speaker": "Cliente"},
            {"start": 16.0, "end": 21.0,  "speaker": "Consultor"},
            {"start": 22.0, "end": 30.0,  "speaker": "Cliente"},
            {"start": 31.0, "end": 37.0,  "speaker": "Consultor"},
            {"start": 38.0, "end": 44.0,  "speaker": "Cliente"},
            {"start": 45.0, "end": 55.0,  "speaker": "Consultor"},
            {"start": 56.0, "end": 61.0,  "speaker": "Cliente"},
            {"start": 62.0, "end": 74.0,  "speaker": "Consultor"},
            {"start": 75.0, "end": 80.0,  "speaker": "Cliente"},
            {"start": 81.0, "end": 87.0,  "speaker": "Consultor"},
            {"start": 88.0, "end": 98.0,  "speaker": "Cliente"},
            {"start": 99.0, "end": 104.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,  "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,  "end": 15.0,  "speaker": "Cliente"},
            {"start": 16.0, "end": 21.0,  "speaker": "Consultor"},
            {"start": 22.0, "end": 30.0,  "speaker": "Cliente"},
            {"start": 31.0, "end": 37.0,  "speaker": "Consultor"},
            {"start": 38.0, "end": 44.0,  "speaker": "Cliente"},
            {"start": 45.0, "end": 55.0,  "speaker": "Consultor"},
            {"start": 56.0, "end": 61.0,  "speaker": "Consultor"}, # erro 5s
            {"start": 62.0, "end": 74.0,  "speaker": "Consultor"},
            {"start": 75.0, "end": 80.0,  "speaker": "Cliente"},
            {"start": 81.0, "end": 87.0,  "speaker": "Consultor"},
            {"start": 88.0, "end": 98.0,  "speaker": "Cliente"},
            {"start": 99.0, "end": 104.0, "speaker": "Consultor"},
        ],
    },
    "R09": {
        "ambiente": "Doméstico",
        "reference": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 16.0,  "speaker": "Cliente"},
            {"start": 17.0,  "end": 23.0,  "speaker": "Consultor"},
            {"start": 24.0,  "end": 35.0,  "speaker": "Cliente"},
            {"start": 36.0,  "end": 46.0,  "speaker": "Consultor"},
            {"start": 47.0,  "end": 56.0,  "speaker": "Cliente"},
            {"start": 57.0,  "end": 63.0,  "speaker": "Consultor"},
            {"start": 64.0,  "end": 74.0,  "speaker": "Cliente"},
            {"start": 75.0,  "end": 81.0,  "speaker": "Consultor"},
            {"start": 82.0,  "end": 94.0,  "speaker": "Cliente"},
            {"start": 95.0,  "end": 100.0, "speaker": "Consultor"},
            {"start": 101.0, "end": 104.0, "speaker": "Cliente"},
        ],
        "hypothesis": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 16.0,  "speaker": "Cliente"},
            {"start": 17.0,  "end": 23.0,  "speaker": "Consultor"},
            {"start": 24.0,  "end": 35.0,  "speaker": "Cliente"},
            {"start": 36.0,  "end": 46.0,  "speaker": "Consultor"},
            {"start": 47.0,  "end": 56.0,  "speaker": "Consultor"}, # erro 9s
            {"start": 57.0,  "end": 63.0,  "speaker": "Consultor"},
            {"start": 64.0,  "end": 74.0,  "speaker": "Cliente"},
            {"start": 75.0,  "end": 81.0,  "speaker": "Consultor"},
            {"start": 82.0,  "end": 94.0,  "speaker": "Cliente"},
            {"start": 95.0,  "end": 100.0, "speaker": "Consultor"},
            {"start": 101.0, "end": 104.0, "speaker": "Cliente"},
        ],
    },
    "R10": {
        "ambiente": "Escritório",
        "reference": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 14.0, "speaker": "Cliente"},
            {"start": 15.0, "end": 21.0, "speaker": "Consultor"},
            {"start": 22.0, "end": 32.0, "speaker": "Cliente"},
            {"start": 33.0, "end": 43.0, "speaker": "Consultor"},
            {"start": 44.0, "end": 50.0, "speaker": "Cliente"},
            {"start": 51.0, "end": 59.0, "speaker": "Consultor"},
            {"start": 60.0, "end": 66.0, "speaker": "Cliente"},
            {"start": 67.0, "end": 76.0, "speaker": "Consultor"},
            {"start": 77.0, "end": 88.0, "speaker": "Cliente"},
            {"start": 89.0, "end": 99.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 14.0, "speaker": "Cliente"},
            {"start": 15.0, "end": 21.0, "speaker": "Consultor"},
            {"start": 22.0, "end": 32.0, "speaker": "Cliente"},
            {"start": 33.0, "end": 43.0, "speaker": "Consultor"},
            {"start": 44.0, "end": 50.0, "speaker": "Cliente"},
            {"start": 51.0, "end": 59.0, "speaker": "Consultor"},
            {"start": 60.0, "end": 66.0, "speaker": "Consultor"}, # erro 6s
            {"start": 67.0, "end": 76.0, "speaker": "Consultor"},
            {"start": 77.0, "end": 88.0, "speaker": "Cliente"},
            {"start": 89.0, "end": 99.0, "speaker": "Consultor"},
        ],
    },
    "R11": {
        "ambiente": "Público c/ muito ruído",
        "reference": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 11.0, "speaker": "Cliente"},
            {"start": 12.0, "end": 19.0, "speaker": "Consultor"},
            {"start": 20.0, "end": 30.0, "speaker": "Cliente"},
            {"start": 31.0, "end": 40.0, "speaker": "Consultor"},
            {"start": 41.0, "end": 47.0, "speaker": "Cliente"},
            {"start": 48.0, "end": 58.0, "speaker": "Consultor"},
            {"start": 59.0, "end": 69.0, "speaker": "Cliente"},
            {"start": 70.0, "end": 78.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
            {"start": 0.0,  "end": 4.0,  "speaker": "Consultor"},
            {"start": 5.0,  "end": 11.0, "speaker": "Consultor"}, # erro 6s
            {"start": 12.0, "end": 19.0, "speaker": "Consultor"},
            {"start": 20.0, "end": 30.0, "speaker": "Cliente"},
            {"start": 31.0, "end": 40.0, "speaker": "Consultor"},
            {"start": 41.0, "end": 47.0, "speaker": "Consultor"}, # erro 6s
            {"start": 48.0, "end": 58.0, "speaker": "Consultor"},
            {"start": 59.0, "end": 69.0, "speaker": "Cliente"},
            {"start": 70.0, "end": 78.0, "speaker": "Consultor"},
        ],
    },
    "R12": {
        "ambiente": "Público c/ muito ruído",
        "reference": [
            {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 18.0,  "speaker": "Cliente"},
            {"start": 19.0,  "end": 26.0,  "speaker": "Consultor"},
            {"start": 27.0,  "end": 38.0,  "speaker": "Cliente"},
            {"start": 39.0,  "end": 48.0,  "speaker": "Consultor"},
            {"start": 49.0,  "end": 57.0,  "speaker": "Cliente"},
            {"start": 58.0,  "end": 66.0,  "speaker": "Consultor"},
            {"start": 67.0,  "end": 73.0,  "speaker": "Cliente"},
            {"start": 74.0,  "end": 81.0,  "speaker": "Consultor"},
            {"start": 82.0,  "end": 90.0,  "speaker": "Cliente"},
            {"start": 91.0,  "end": 100.0, "speaker": "Consultor"},
            {"start": 101.0, "end": 110.0, "speaker": "Cliente"},
            {"start": 111.0, "end": 116.0, "speaker": "Consultor"},
        ],
        "hypothesis": [
           {"start": 0.0,   "end": 4.0,   "speaker": "Consultor"},
            {"start": 5.0,   "end": 18.0,  "speaker": "Cliente"},
            {"start": 19.0,  "end": 26.0,  "speaker": "Consultor"},
            {"start": 27.0,  "end": 38.0,  "speaker": "Consultor"}, # erro 11s ← muda para Consultor
            {"start": 39.0,  "end": 48.0,  "speaker": "Consultor"},
            {"start": 49.0,  "end": 57.0,  "speaker": "Cliente"},
            {"start": 58.0,  "end": 66.0,  "speaker": "Consultor"},
            {"start": 67.0,  "end": 73.0,  "speaker": "Consultor"}, # erro 6s
            {"start": 74.0,  "end": 81.0,  "speaker": "Consultor"},
            {"start": 82.0,  "end": 90.0,  "speaker": "Cliente"},
            {"start": 91.0,  "end": 100.0, "speaker": "Consultor"},
            {"start": 101.0, "end": 110.0, "speaker": "Cliente"},
            {"start": 111.0, "end": 116.0, "speaker": "Consultor"},
        ],
    },
}

print("\nVoiceCRM — Resultados DER R01 a R12")
print("=" * 65)
print(f"{'Sessão':<8} {'Ambiente':<26} {'DER':>8} {'RNF2':>6}")
print("-" * 65)

resultados = []
for sessao, dados in SESSOES.items():
    try:
        resp = requests.post(BACKEND, json={
            "reference": dados["reference"],
            "hypothesis": dados["hypothesis"]
        }, timeout=15)
        der_val = resp.json()["der"]
        der_pct = resp.json()["der_percent"]
        rnf2 = "OK" if der_val < 0.20 else "FALHOU"
        resultados.append(der_val)
        print(f"{sessao:<8} {dados['ambiente']:<26} {der_pct:>7} {rnf2:>6}")
    except Exception as e:
        print(f"{sessao:<8} ERRO: {str(e)[:40]}")

if resultados:
    media = round(sum(resultados) / len(resultados) * 100, 1)
    print("-" * 65)
    print(f"{'Média R01-R12':<34} {media:>7}%")
    
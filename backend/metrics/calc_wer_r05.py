"""
VoiceCRM — Cálculo WER sessão R05
Execução: uv run python3 calc_wer_r05.py
"""

def wer(ref, hyp):
    r = ref.lower().split()
    h = hyp.lower().split()
    if not r: return 0.0
    d = [[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): d[i][0] = i
    for j in range(len(h)+1): d[0][j] = j
    for i in range(1,len(r)+1):
        for j in range(1,len(h)+1):
            if r[i-1]==h[j-1]: d[i][j]=d[i-1][j-1]
            else: d[i][j]=1+min(d[i-1][j],d[i][j-1],d[i-1][j-1])
    return round(d[len(r)][len(h)]/len(r)*100,1)

ref = "bom dia bem vinda é um prazer recebê-la em que posso ajudá-la hoje bom dia preciso de renovar o meu guarda-roupa de trabalho comecei um novo emprego numa consultora de gestão em lisboa e quero ter um visual mais profissional e sofisticado parabéns pelo novo emprego para um ambiente de consultora temos peças excelentes prefere um visual mais clássico ou algo mais moderno com cortes contemporâneos prefiro clássico mas com personalidade gosto muito de azul marinho e cinzento uso tamanho trinta e seis em roupa e calço o trinta e sete perfeito com esse perfil temos opções magníficas temos blazers estruturados em lã merino que são absolutamente versáteis também acabaram de chegar calças de corte clássico que combinam na perfeição adoro blazers estruturados tenho um casamento em junho e gostava de ter algo que pudesse usar tanto no trabalho como na cerimónia o meu orçamento total é cerca de dois mil euros para o conjunto completo com dois mil euros conseguimos criar um conjunto muito completo e versátil um blazer duas calças e duas blusas já cobrem várias combinações quer começar por ver os blazers sim por favor prefiro tecidos naturais lã seda ou algodão tenho alergia a sintéticos e fico muito desconfortável todas as nossas peças são em tecidos naturais por isso não terá qualquer problema este blazer azul marinho em lã merino italiano é uma das peças mais procuradas esta temporada quer experimentar com todo o prazer moro em lisboa no marquês de pombal venho ao porto regularmente por causa do trabalho pode ficar com o meu contacto claro nome completo por favor ana lopes o email é ana ponto lopes arroba consultora ponto pt prefiro contacto por email"

hyp = "bom dia bem vinda é um prazer recebê-la em que posso ajudá-la hoje bom dia preciso de renovar o meu guarda-roupa de trabalho comecei um novo emprego gestão em lisboa e quero ter um visual mais profissional e sofisticado novo emprego para um ambiente de consultora temos peças excelentes refere um visual mais clássico ou algo mais moderno com cortes contemporâneos prefiro clássico mas com personalidade azul marinho e cinzento uso tamanho trinta e seis em roupa e calço o trinta e sete perfeito com esse perfil temos opções magníficas temos blazers estruturados em lã absolutamente versáteis também acabaram de chegar calças de corte clássico que combinam na perfeição adoro blazers estruturados tenho um casamento em junho e gostava de ter algo que pudesse usar tanto no trabalho como na cerimónia o meu orçamento total é cerca de dois mil euros para o conjunto completo com 2000 conseguimos criar um conjunto muito completo e versátil um blazer duas calças e duas blusas já cobrem várias combinações quer começar por ver os blazers sim por favor prefiro tecidos naturais lã seda ou algodão tenho alergia a sintéticos e fico muito desconfortável cirurgia tecidos naturais por isso não terá qualquer problema este blazer azul marinho em lã merino italiano é uma das peças mais procuradas esta temporada com todo o prazer moro em lisboa no marquês de pombal venho ao porto regularmente por causa do trabalho ode ficar com o meu contacto claro nome completo por favor ana lopes o email é ana.lopes arroba consultora ponto pt prefiro contacto por email"

resultado = wer(ref, hyp)
print(f"WER R05: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")
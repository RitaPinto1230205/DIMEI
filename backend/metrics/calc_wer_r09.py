"""
VoiceCRM — Cálculo WER sessão R09
Execução: uv run python3 calc_wer_r09.py
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

ref = "bom dia bem vinda em que posso ajudá-la hoje bom dia preciso de um fato completo para a minha filha ela termina a licenciatura em junho e vai ter uma cerimónia de graduação muito formal quer estar impecável que momento especial a formatura para uma cerimónia de graduação formal temos opções lindas a sua filha tem alguma preferência de cor ou estilo ela gosta de cores sóbrias preto bordeaux ou verde escuro é muito moderna mas gosta de peças com classe usa tamanho trinta e quatro em roupa e calça o trinta e seis tem vinte e dois anos perfeito para o perfil que descreveu temos um fato de calças em bordeaux com casaco estruturado que é absolutamente deslumbrante para uma cerimónia o tecido é em lã mista muito confortável bordeaux é perfeito ela vai adorar quanto custa o conjunto o conjunto completo casaco e calças está a oitocentos e cinquenta euros temos também a opção de saia em vez de calças pelo mesmo preço prefiro as calças é mais ela posso trazer a minha filha para experimentar na próxima semana moro em braga mas venho ao porto com frequência claro que sim reservo o conjunto no tamanho trinta e quatro quando pretende vir na próxima quinta-feira de manhã seria ideal o meu nome é conceição martins o telemóvel é noventa e um seis sete oito novecentos e onze perfeito conceição fico a aguardar a sua visita na próxima quinta-feira com a sofia muito obrigada até quinta"

hyp = "bom dia bem vinda em que posso ajudá-la hoje bom dia preciso de um fato completo para a minha filha ela termina a licenciatura em junho e vai ter uma cerimónia de graduação muito formal quer estar impecável que momento especial a formatura para uma cerimónia de graduação formal temos opções lindas a sua filha tem alguma preferência de cor ou estilo ela gosta de cores sóbrias preto bordeaux ou verde escuro é muito moderna mas gosta de peças com classe usa tamanho 34 em roupa e calça o trinta e seis tem vinte e dois anos perfeito para o perfil que descreveu temos um fato de calças em bordeaux com casaco estruturado que é absolutamente deslumbrante para uma cerimónia o tecido é em lã mista muito confortável bordeaux é perfeito ela vai adorar quanto custa o conjunto o conjunto completo casaco e calças está a oitocentos e cinquenta euros temos também a opção de saia em vez de calças pelo mesmo preço prefiro as calças é mais ela posso trazer a minha filha para experimentar na próxima semana moro em braga mas venho ao porto com frequência claro que sim reservo o conjunto no tamanho trinta e quatro quando pretende vir na próxima quinta-feira de manhã seria ideal o meu nome é conceição martins o telemóvel é noventa e um seis sete oito novecentos e onze perfeito conceição fico a aguardar a sua visita na próxima quinta-feira com a sofia muito obrigada até quinta"

resultado = wer(ref, hyp)
print(f"WER R09: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")
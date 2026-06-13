"""
VoiceCRM — Cálculo WER sessão R08
Execução: uv run python3 calc_wer_r08.py
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

ref = "boa tarde bem vindo em que posso ajudá-lo hoje boa tarde estou à procura de um presente para a minha esposa fazemos dez anos de casados no próximo mês e quero fazer algo especial que ocasião linda dez anos de casamento é uma data muito especial tem alguma ideia do que ela gostaria ela adora perfumes e joias é muito elegante usa sempre peças discretas e clássicas tem quarenta e dois anos e trabalha como médica em coimbra que perfil sofisticado para uma médica que aprecia elegância discreta temos opções magníficas prefere um perfume ou um acessório como ponto de partida talvez um perfume primeiro ela gosta de fragrâncias florais com um toque amadeirado o orçamento é até trezentos euros temos o número cinco l eau que é uma interpretação moderna e leve do clássico chanel número cinco é floral com base amadeirada e tem sido muito procurado está a cento e oitenta euros perfeito e tem algo para complementar uma vela perfumada ou um gel de duche da mesma linha temos um conjunto com gel de duche e loção corporal da mesma fragrância por mais noventa euros o conjunto completo ficaria a duzentos e setenta euros dentro do seu orçamento óptimo fico com o conjunto pode fazer embrulho de casamento com laço dourado com todo o prazer fazemos embrulho especial para aniversários o seu nome para registar pedro carvalho moro em coimbra no bairro norton de matos o telemóvel é nove um três dois dois três quatro cinco seis muito obrigada pedro ficou registado parabéns pela data especial"

hyp = "boa tarde bem vindo em que posso ajudá-lo hoje boa tarde estou à procura de um presente para a minha esposa fazemos dez anos de casados no próximo mês e quero fazer algo especial que ocasião linda dez anos de casamento é uma data muito especial tem alguma ideia do que ela gostaria ela adora perfumes e joias é muito elegante usa sempre peças discretas e clássicas tem quarenta e dois anos e trabalha como médica em coimbra que perfil sofisticado para uma médica que aprecia elegância discreta temos opções magníficas prefere um perfume ou um acessório como ponto de partida primeiro ela gosta de fragrâncias florais com um toque amadeirado o orçamento é até trezentos euros temos o número cinco l eau que é uma interpretação moderna e leve do clássico chanel número cinco é floral com base amadeirada e tem sido muito procurado está a 180 perfeito e tem algo para complementar uma vela perfumada ou um gel de duche da mesma linha com gel de duche e loção corporal da mesma fragrância por mais 92 conjunto completo ficaria a duzentos e setenta euros dentro do seu orçamento óptimo fico com o conjunto pode fazer embrulho de casamento com laço dourado com todo o prazer fazemos embrulho especial para aniversários o seu nome para registar pedro carvalho moro em coimbra no bairro norton de matos o telemóvel é nove um três dois dois três quatro cinco seis muito obrigada pedro ficou registado parabéns pela data especial"

resultado = wer(ref, hyp)
print(f"WER R08: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")
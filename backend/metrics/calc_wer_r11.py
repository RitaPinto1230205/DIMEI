"""
VoiceCRM — Cálculo WER sessão R11
Execução: uv run python3 calc_wer_r11.py
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

ref = "boa tarde bem vindo em que posso ajudá-lo boa tarde sou estudante de mestrado e vou defender a minha tese em julho a minha orientadora sugeriu que investisse num fato adequado para a apresentação nunca usei um fato de marca que ocasião importante a defesa de tese é um momento muito especial para uma primeira peça de marca recomendo algo versátil que possa usar depois em entrevistas de emprego e outras ocasiões formais que tamanho usa uso tamanho quarenta e oito em fatos e quarenta e dois de calçado prefiro cores sóbrias cinzento ou azul marinho o meu orçamento é limitado talvez até seiscentos euros com seiscentos euros conseguimos um fato de excelente qualidade temos um modelo em cinzento mescla com corte clássico que é perfeito para uma primeira peça muito versátil e atemporal está a quinhentos e cinquenta euros inclui calças e tenho de comprar camisa separada inclui casaco e calças para camisa temos modelos brancos de fio egípcio a partir de cento e vinte euros mas pode usar camisas que já tenha para a defesa de tese uma camisa branca simples com o fato cinzento fica perfeito então fico só com o fato por agora moro em porto na boavista chamo-me nuno ferreira o telemóvel é noventa e dois três quatro cinco seiscentos e setenta e oito muito obrigada nuno fico a registar boa sorte na defesa de tese em julho"

hyp = "boa tarde bem vindo em que posso ajudá-lo boa tarde mestrado e vou defender a minha tese em julho a minha orientadora sugeriu que investisse num fato adequado para a apresentação nunca usei um fato de marca que ocasião importante a defesa de tese é um momento muito especial para uma primeira peça de marca recomendo algo versátil que possa usar depois em entrevistas de emprego e outras ocasiões formais que tamanho usa uso tamanho quarenta e oito em fatos e quarenta e dois de calçado prefiro cores sóbrias cinzento ou azul marinho o meu orçamento é limitado talvez até 600 com seiscentos euros conseguimos um fato de excelente qualidade temos um modelo em cinzento mescla com corte clássico que é perfeito para uma primeira peça muito versátil e atemporal está a 550 euros inclui calças e tenho de comprar camisa separada inclui casaco e calças para camisa temos modelos brancos de fio egípcio a partir de cento e vinte euros mas pode usar camisas que já tenha para a defesa de tese uma camisa branca simples com o fato cinzento fica perfeito então fico só com o fato por agora moro em porto na boavista chamo-me nuno ferreira o telemóvel é noventa e dois três quatro cinco seiscentos e setenta e oito muito obrigada nuno fico a registar boa sorte na defesa de tese em julho"

resultado = wer(ref, hyp)
print(f"WER R11: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")
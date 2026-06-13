"""
VoiceCRM — Cálculo WER sessão R04
Execução: uv run python3 calc_wer_r04.py


ritapinto@NULL backend % uv run python3 calc_wer_r04.py
WER R04: 7.4%
Palavras referência: 269
Palavras hipótese: 253

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

ref = "boa tarde bem vindo em que posso ajudá-lo hoje temos peças novas que chegaram esta semana e ficaria feliz de lhe mostrar boa tarde estou à procura de um relógio para oferta é para o meu pai que faz setenta anos no próximo mês quero algo especial que ele possa usar todos os dias mas que seja elegante que ocasião linda para um aniversário tão especial temos opções excelentes o seu pai tem algum estilo preferido prefere algo mais clássico e discreto ou algo com mais presença ele é um homem muito clássico usa sempre fato ao trabalho é advogado em lisboa gosta de coisas simples mas de qualidade o orçamento é até mil euros perfeito com esse perfil temos um modelo em aço com mostrador branco e bracelete em pele castanha que seria ideal é elegante atemporal e muito versátil posso mostrar lhe sim com certeza qual é o tamanho do mostrador o meu pai tem o pulso fino por isso prefiro algo não muito grande este modelo tem trinta e oito milímetros de diâmetro que é um tamanho clássico e discreto fica muito bem em pulsos finos o preço é oitocentos e cinquenta euros dentro do seu orçamento é exactamente o que procurava pode fazer embrulho para presente e tem caixa especial claro que sim todos os relógios vêm com caixa da marca e fazemos embrulho especial posso registar os seus dados sim chamo me miguel santos moro no porto na foz o telemóvel é nove três dois um dois três quatro cinco seis muito obrigada miguel fico a registar o seu pai vai adorar a prenda"

hyp = "boa tarde bem vindo em que posso ajudá-lo hoje temos peças novas que chegaram esta semana e ficaria feliz de lhe mostrar boa tarde estou à procura de um relógio para oferta é para o meu pai que faz setenta anos no próximo mês se algo que possa usar todos os dias mas que seja elegante que ocasião linda para um aniversário tão especial temos opções excelentes o seu pai tem algum estilo preferido prefere algo mais clássico e discreto ou algo com mais presença ele é um homem muito clássico usa sempre fato ao trabalho é advogado em lisboa gosta de coisas simples mas de qualidade o orçamento é até 1000 perfeito com esse perfil temos um modelo em aço com mostrador branco e bracelete em pele castanha que seria ideal é elegante atemporal e muito versátil posso mostrar lhe sim com certeza qual é o tamanho do mostrador o meu pai tem o pulso fino por isso prefiro algo não muito grande este modelo tem trinta e oito milímetros de diâmetro que é um tamanho clássico e discreto fica muito bem em pulsos finos o preço é oitocentos e cinquenta euros dentro do seu orçamento é exactamente o que procurava ode fazer embrulho para presente claro que sim todos os relógios vêm com caixa da marca e fazemos embrulho especial posso registar os seus dados sim chamo me miguel santos moro no porto na foz o telemóvel é 932123456 muito obrigada miguel fico a registar seu pai vai adorar a prenda"

resultado = wer(ref, hyp)
print(f"WER R04: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")

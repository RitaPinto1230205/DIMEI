"""
VoiceCRM — Cálculo WER sessão R07
Execução: uv run python3 calc_wer_r07.py
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

ref = "boa tarde bem vindo em que posso ajudá-lo hoje boa tarde estou à procura de um presente para a minha namorada fazemos dois anos juntos na próxima semana e quero surpreendê-la com algo especial que ocasião romântica tem alguma ideia do que ela gostaria conhece as preferências dela em termos de estilo e acessórios ela adora malas e perfumes é muito feminina e elegante usa tamanho trinta e seis em roupa e calça o trinta e oito tem vinte e oito anos e trabalha como advogada no porto gosta muito de tons dourados e bege que perfil elegante para uma advogada que gosta de tons dourados e bege temos opções magníficas tem algum orçamento em mente estou disposto a gastar até quinhentos euros é o nosso segundo aniversário por isso quero algo memorável já lhe ofereci um lenço no primeiro aniversário e ela usa-o com frequência que atencioso para este aniversário temos uma mala de mão em pele bege com fecho dourado que combina perfeitamente com o lenço que já tem é uma peça muito versátil serve para o trabalho e para saídas está a quatrocentos e cinquenta euros é perfeita ela vai adorar a combinação com o lenço pode fazer embrulho especial ela gosta muito de detalhes cuidados nas prendas claro que sim fazemos embrulho com fita e cartão personalizado quer acrescentar alguma mensagem no cartão sim quero escrever eu próprio preciso também de um cinto para mim uso tamanho noventa e dois de cinto e quarenta e dois de fato trabalho numa empresa de arquitectura em braga mas vivo no porto temos cintos em pele genuína em vários tamanhos este modelo em pele castanha com fivela discreta é muito versátil para o dia a dia profissional está a cento e vinte euros óptimo fico com os dois então o meu nome é tomás oliveira o telemóvel é nove seis cinco quatro três dois um zero nove muito obrigada tomás fico a registar a sua namorada vai ter uma surpresa maravilhosa"

hyp = "boa tarde bem vindo em que posso ajudá-lo hoje boa tarde estou à procura de um presente para a minha namorada fazemos dois anos juntos na próxima semana e quero surpreendê-la com algo especial que ocasião romântica tem alguma ideia do que ela gostaria conhece as preferências dela em termos de especially acessórios ela adora malas e perfumes é muito feminina e elegante usa tamanho 36 em roupa e calça o 38 tem 28 anos e trabalha como advogada no porto gosta muito de tons dourados e bege que perfil elegante para uma advogada que gosta de tons dourados e bege temos opções magníficas tem algum orçamento em mente estou disposto a gastar até 500 aniversário por isso quero algo memorável no primeiro aniversário e ela usa-o com frequência ansioso para este aniversário temos uma mala de mão em pele bege com fecho dourado que combina perfeitamente com o lenço que já tem é uma peça muito versátil serve para o trabalho e para saídas está a 400 a 500 é perfeita ela vai adorar a combinação com o lenço pode fazer embrulho especial ela gosta muito de detalhes cuidados nas prendas claro que sim fazemos embrulho com fita e cartão personalizado quer acrescentar alguma mensagem no cartão próprio preciso também de um cinto para mim uso tamanho 92 de cinto e 42 de fato trabalho numa empresa de arquitectura em braga mas vivo no porto temos cintos em pele genuína em vários tamanhos este modelo em pele castanha com fivela discreta é muito versátil para o dia a dia profissional está a cento e vinte euros óptimo ico com os dois então o meu nome é tomás oliveira o telemóvel é 965432019 muito obrigada tomás fico a registar a sua namorada vai ter uma surpresa maravilhosa"

resultado = wer(ref, hyp)
print(f"WER R07: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")
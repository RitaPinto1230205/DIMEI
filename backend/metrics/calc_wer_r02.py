"""
VoiceCRM — Cálculo WER sessão R02
Execução: uv run python3 calc_wer_r02.py
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

ref = (
    "boa tarde bem vinda à nossa loja é um prazer recebê-la em que posso ajudá-la hoje "
    "temos novidades na coleção de primavera que acabaram de chegar esta semana "
    "boa tarde obrigada estou à procura de um presente especial para o aniversário da minha mãe "
    "ela faz anos para a semana e ainda não comprei nada ela gosta muito de acessórios "
    "principalmente malas e lenços que ocasião especial temos uma seleção maravilhosa de malas "
    "e lenços que seriam perfeitos para oferta tem alguma preferência de cor ou estilo "
    "a sua mãe prefere algo mais clássico ou mais moderno e arrojado ela é uma mulher muito elegante "
    "gosta de coisas clássicas e atemporais prefere cores neutras como o bege o preto e o castanho "
    "mora no porto e trabalha numa empresa de advocacia por isso usa muito roupa formal "
    "perfeito com esse perfil temos opções excelentes para malas a linha clássica em pele genuína "
    "nas cores que referiu seria ideal temos também lenços em seda com padrões geométricos muito elegantes "
    "qual é o orçamento que tem em mente para esta prenda estou a pensar gastar entre trezentos e quinhentos euros "
    "quero algo de qualidade que ela possa usar durante muitos anos ela já tem algumas peças da marca "
    "e adora por isso sei que vai gostar óptimo dentro desse orçamento temos várias opções muito bonitas "
    "deixe me mostrar lhe esta mala de mão em pele de vitela bege é uma peça atemporal "
    "com forro em tecido e fecho dourado cabe o essencial para o dia a dia o preço é trezentos e oitenta euros "
    "é lindíssima adoro o acabamento dourado a minha mãe usa tamanho trinta e oito na roupa "
    "e calça o trinta e oito também mas para a mala não interessa o tamanho pois não "
    "posso ver também os lenços que mencionou claro que sim os lenços são em seda cem por cento "
    "e têm noventa por noventa centímetros este modelo em bege com padrão geométrico dourado "
    "combina perfeitamente com a mala o conjunto fica muito harmonioso o lenço custa cento e vinte euros "
    "juntos ficam em quinhentos euros exatamente dentro do seu orçamento são perfeitos "
    "acho que vou levar os dois a minha mãe vai adorar pode fazer embrulho para presente "
    "e tem cartão de oferta para eu escrever uma mensagem com todo o prazer fazemos embrulho especial "
    "para presente com papel de seda e fita também temos cartões de oferta muito elegantes "
    "posso registar os seus dados para o nosso programa de clientes assim fica com acesso "
    "a novidades e eventos exclusivos da loja sim claro o meu nome é sofia rodrigues "
    "moro em lisboa no chiado o meu email é sofia ponto rodrigues arroba gmail ponto com "
    "venho ao porto com frequência por causa do trabalho muito obrigada sofia ficou registada "
    "vou preparar o embrulho agora a sua mãe vai ter uma surpresa maravilhosa "
    "tem mais alguma coisa em que a possa ajudar hoje não por hoje está bem obrigada "
    "foi um prazer ser atendida por si até à próxima "
    "o prazer foi todo nosso sofia esperamos vê-la em breve bom resto de dia"
)

hyp = (
    "boa tarde bem vinda à nossa loja é um prazer recebê-la em que posso ajudá-la hoje "
    "temos novidades na coleção de primavera que acabaram de chegar esta semana "
    "boa tarde obrigada estou à procura de um presente especial para o aniversário da minha mãe "
    "não comprei nada ela gosta muito de acessórios principalmente malas e lenços "
    "que ocasião especial temos uma seleção maravilhosa de malas e lenços que seriam perfeitos para oferta "
    "a sua mãe prefere algo mais clássico ou mais moderno e arrojado ela é uma mulher muito elegante "
    "gosta de coisas clássicas e atemporais preto e o castanho mora no porto "
    "e trabalha numa empresa de advocacia por isso usa muito roupa formal "
    "perfeito com esse perfil temos opções excelentes para malas a linha clássica em pele genuína "
    "nas cores que referiu seria ideal com padrões geométricos muito elegantes "
    "qual é o orçamento que tem em mente para esta prenda estou a pensar gastar entre trezentos e quinhentos euros "
    "quero algo de qualidade que ela possa usar durante muitos anos ela já tem algumas peças da marca "
    "e adora por isso sei que vai gostar óptimo dentro desse orçamento temos várias opções muito bonitas "
    "deixe me mostrar lhe esta mala de mão em pele de vitela bege o em tecido e fecho dourado "
    "cabe o essencial para o dia a dia o preço é trezentos e oitenta euros "
    "é lindíssima dourado a minha mãe usa tamanho trinta e oito na roupa "
    "e calça o trinta e oito também mas para a mala não interessa o tamanho pois não mencionou "
    "claro que sim os lenços são em seda cem por cento e têm noventa por noventa centímetros "
    "este modelo em bege com padrão geométrico dourado combina perfeitamente com a mala "
    "o conjunto fica muito harmonioso o lenço custa cento e vinte euros "
    "juntos ficam em quinhentos euros exatamente dentro do seu orçamento são perfeitos "
    "acho que vou levar os dois a minha mãe vai adorar pode fazer embrulho para presente "
    "para eu escrever uma mensagem com todo o prazer fazemos embrulho especial "
    "para presente com papel de seda e fita ta posso registar os seus dados "
    "para o nosso programa de clientes assim fica com acesso a novidades e eventos exclusivos da loja "
    "sim claro o meu nome é sofia rodrigues moro em lisboa no chiado "
    "o meu email é sofia ponto rodrigues arroba gmail ponto com "
    "venho ao porto com frequência por causa do trabalho muito obrigada sofia ficou registada "
    "agora a sua mãe vai ter uma surpresa maravilhosa "
    "tem mais alguma coisa em que a possa ajudar hoje não por hoje está bem obrigada "
    "fpor si até à próxima "
    "o prazer foi todo nosso sofia esperamos vê-la em breve bom resto de dia"
)

resultado = wer(ref, hyp)
print(f"WER Sessão R02: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese:   {len(hyp.split())}")
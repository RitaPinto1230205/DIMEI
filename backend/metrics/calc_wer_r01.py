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

ref = "bom dia bem vinda à zara em que posso ajudá-la hoje claro temos peças lindas para essa ocasião tem alguma preferência de cor preto creme talvez um bege prefiro cores neutras o preto é sempre seguro mas já tenho dois pretos no armário talvez o creme ou um bege escuro posso perguntar que tamanho usa normalmente sou um 36 em roupa europeia às vezes 38 dependendo do corte temos um tweed creme que chegou esta semana da coleção outono inverno que acho que vai adorar é estruturado mas muito confortável posso mostrar lhe sim com certeza qual é o preço aproximado tenho um orçamento de uns três mil euros para esta peça este tweed está a três mil e duzentos mas temos também opções a partir de dois mil e quatrocentos deixe me buscar os dois para comparar ótimo o meu marido faz anos em dezembro e ele adora a linha masculina da chanel tem alguma sugestão para homem temos carteiras cintos e perfumes o bleu de chanel é o mais pedido prefere algo mais pessoal como acessórios ou perfumaria perfumaria talvez ele já tem a carteira o orçamento para o presente é à volta de duzentos euros perfeito o bleu de chanel eau de parfum em cento e cinquenta mililitros está dentro desse orçamento é uma escolha excelente muito bem vamos então ver o casaco primeiro"

hyp = "bom dia bem vinda à zara em que posso ajudá-la hoje não muito chamativo mas que sem claro temos peças lindas para essa ocasião tem alguma preferência de cor preto creme ou talvez um bege o preto é sempre seguro mas já tenho pretos no armário talvez o creme posso perguntar que tamanho usa normalmente som 36 em roupa europeia às vezes 38 temos um tweed creme que chegou esta semana da coleção outono inverno que acho que vai adorar é estruturado mas muito confortável posso mostrar lhe com certeza qual é o preço aproximado 3000 este tweed está a três mil e duzentos mas temos também opções a partir de dois mil e quatrocentos deixe me buscar os dois para comparar ótimo o meu marido faz anos em dezembro e ele adora a linha masculina da chanel tem alguma sugestão para homem temos carteiras cintos e perfumes o bleu de chanel é o mais pedido prefere algo mais pessoal como acessórios ou perfumaria perfumaria talvez eu já tenha a carteira o orçamento para o presente é à volta 200 perfeito o bleu de chanel eau de parfum em cento e cinquenta mililitros está dentro desse orçamento é uma escolha excelente muito bem vamos então ver o casaco primeiro"

print("WER Sessão R01:", wer(ref, hyp), "%")

"""
VoiceCRM — Cálculo WER sessão R10
Execução: uv run python3 calc_wer_r10.py
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

ref = "boa tarde bem vinda já nos conhecemos certo que bom vê-la por cá boa tarde sim vim cá em janeiro comprar um casaco ainda o uso muito foi uma excelente escolha hoje venho porque preciso de acessórios para completar o look de uma gala que tenho em março que bom fico feliz que ainda use o casaco para uma gala em março que tipo de acessórios tem em mente mala lenços joias principalmente uma mala de mão elegante e uns brincos discretos se tiverem o vestido que vou usar é preto com detalhes dourados então preciso de acessórios que complementem sem competir com detalhes dourados no vestido uma mala em pele preta com fecho dourado seria perfeito temos um modelo clutch muito elegante que combina na perfeição e para brincos temos argolas pequenas em banhado a ouro muito discretas posso ver os dois o meu orçamento para os acessórios é de cerca de setecentos euros no total a mala clutch está a trezentos e cinquenta euros e os brincos a cento e vinte ficaria em quatrocentos e setenta euros bem dentro do orçamento são lindos fico com os dois a minha filha sofia faz quinze anos em abril tem alguma sugestão para um presente dentro de cento e cinquenta euros para uma jovem de quinze anos temos um mini perfume da linha chance muito popular entre jovens está a noventa euros ou um porta-moedas em pele colorida que está muito na moda a cento e trinta euros o porta-moedas é uma ideia fantástica fico com os três então o meu nome é isabel rodrigues moro em lisboa no restelo o email é isabel ponto rodrigues arroba gmail ponto com obrigada isabel ficou tudo registado a gala em março e o aniversário da sofia em abril entramos em contacto quando chegarem as novidades de primavera"

hyp = "boa tarde bem vinda já nos conhecemos certo que bom vê-la por cá boa tarde comprar um casaco ainda o uso muito uma excelente escolha hoje venho porque preciso de acessórios para completar o look de uma gala que tenho em março que bom fico feliz que ainda use o casaco para uma gala em março que tipo de acessórios tem em mente mala lenços joias principalmente não elegante e uns brincos secretos se tiverem o vestido que vou usar é preto preciso de acessórios que complementem sem competir com detalhes dourados no vestido uma mala em pele preta com fecho dourado seria perfeito temos um modelo clutch muito elegante que combina na perfeição e para brincos temos argolas pequenas em banhado a ouro muito discretas posso ver os dois setecentos euros no total a mala clutch está a trezentos e cinquenta euros e os brincos a cento e vinte ficaria em quatrocentos e setenta euros bem dentro do orçamento são lindos fico com os dois a minha filha sofia faz quinze anos em abril tem alguma sugestão para um presente dentro de cento e cinquenta euros para uma jovem de quinze anos temos um mini perfume da linha chance muito popular entre jovens está a 90 ou um porta-moedas em pele colorida que está muito na moda a 130 fico com os três então o meu nome é isabel rodrigues moro em lisboa no restelo o email é isabel rodrigues arroba gmail ponto com obrigada isabel ficou tudo registado a gala em março e o aniversário da sofia em abril entramos em contacto quando chegarem as novidades de primavera"

resultado = wer(ref, hyp)
print(f"WER R10: {resultado}%")
print(f"Palavras referência: {len(ref.split())}")
print(f"Palavras hipótese: {len(hyp.split())}")
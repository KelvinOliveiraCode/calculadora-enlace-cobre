# Como ler uma ficha tecnica de cabo de rede

Este documento nao e sobre programar. E sobre ler o que o fabricante escreveu,
saber o que ele **nao** escreveu, e perceber quando as duas historias nao fecham.

## O que voce precisa extrair, em ordem

### 1. Categoria

Procure `Category 6A`, `Cat 6A`, `CAT6A`, `Category 6`. Se a ficha nao tem
categoria, e porque o cabo nao e certificado - e apenas "cabo de rede".

Verifique contra a **norma**, nao contra a propaganda:

| Categoria | 100 MHz | 250 MHz | 500 MHz |
|---|---|---|---|
| Cat5e | sim | nao | nao |
| Cat6 | sim | sim | nao |
| Cat6A | sim | sim | sim |

Se o vendedor escreve "Cat6" numa linha e "500 MHz" em outra, alguma coisa nao
esta certa. Cat6 para em 250 MHz.

### 2. NVP (Velocity of Propagation)

A fracao da velocidade da luz que o sinal propaga no material. O cobre puro
propaga a cerca de 0,66; um cabo decente fica entre **0,66 e 0,78**.

Por que importa: NVP e o que permite calcular atraso de propagacao, que e o
que causa *delay skew* entre pares. Pares com NVP muito diferente um do outro
nao se sincronizam, e a taxa de erro sobe mesmo que cada par esteja "dentro do
especificado".

Se a ficha nao traz NVP, ela nao foi feita por quem mediu. Peca.

### 3. Diametro do condutor

AWG e milimetro. Condutor mais grosso tem menos resistencia, e menos perda. O
diametro sozinho nao diz a categoria, mas duas cabecas com o mesmo AWG e
frequencias declaradas diferentes significam que uma delas esta inflando o
numero.

### 4. Loss a 100, 250, 500 MHz

E aqui que a ficha costuma ser enganosa. **Verifique se o valor e do cabo ou do
canal.**

- Se a ficha fala em **"insertion loss"** por 100 m, e do cabo.
- Se fala em **"channel loss"**, ja inclui conectores.

Misturar as duas e a forma mais comum de orcamento errado. Um cabo com perda de
19,0 dB/100 m em 100 MHz parece otimo contra o limite de 20,7 dB do Cat6 - mas
se voce ainda tem 5,8 dB de componentes, o total passa de 20,7 e o enlace
reprova.

### 5. NEXT e PS-NEXT

NEXT e quanto um par vaza para o vizinho. PS-NEXT e quanto sobrevive depois
de passar pelo ruido do vizinho. Os dois sao **pisos** (maior e melhor).

Gabarito rapido para 100 MHz:

| Categoria | NEXT min | PS-NEXT min |
|---|---|---|
| Cat5e | 32,4 dB | 27,4 dB |
| Cat6 | 41,8 dB | 39,1 dB |
| Cat6A | 44,4 dB | 42,4 dB |

Se a ficha traz so NEXT e nao traz PS-NEXT, e uma ficha incompleta. Ou e
cabo blindado (STP) e a norma e outra, e entao a ficha deveria dizer.

### 6. Blindagem

- **UTP** - sem blindagem. Exige aterramento correto da canaleta.
- **FTP/STP** - com blindagem. Reduz ruido, mas so funciona se a blindagem for
  aterrada nas duas pontas e continuar pelo caminho todo. Blindagem sem aterramento
  piora o problema.

### 7. Chama e material

- PVC: mais rigido, ate ~70 °C, uso interno.
- LSZH (Low Smoke Zero Halogen): obrigatorio em Predio/Telecom, recomendado em
  qualquer prdio com muito gente.

Se a obra exige LSZH e a ficha nao diz, o cabo esta errado.

## O que o vendedor omite, sempre

| Omitted | Como descobrir |
|---|---|
| Se e cabo ou canal | Leia "insertion loss" vs "channel loss" |
| NVP | Se nao tem, nao mediram |
| Emendas / reparos | Peça fotos da Drummond antes de comprar |
| Se foi certificado ou so testado | Certificado tem numero de certificado rastreavel |
| Condutor real | AWG as vezes e "nominal" |

Vale levar essas perguntas para a reuniao. Nenhuma e ofensiva, e todas
economizam retrabalho depois.

## Cinco perguntas para o fornecedor

1. A loss informada e por 100 m de cabo ou do canal completo?
2. Qual e o NVP deste cabo especifico?
3. Tem numero de certificado rastreavel, e qual o dia do teste?
4. O material da cha e PVC ou LSZH?
5. Qual a temperatura maxima de instalacao em caixa de passagem fechada?

Se o fornecedor responde as cinco sem gaguejar, o cabo presta. Se enrola na
primeira, o resto da conversa e perda de tempo.

## Leitura de laudo de medicao

Quando vier um laudo de equipamento, confira nesta ordem:

1. **O canal passou em todas as frequencias?** Reprovacao em uma so frequencia
   reprova o enlace.
2. **NEXT e PS-NEXT tem numero?** Laudo sem acoplamento medido nao e laudo
   completo, por mais que passe em perda.
3. **O comprimento bate?** 90,4 m ja e violacao de limite fisico, por melhor
   que seja o resultado.
4. **Qual equipamento?** Modelos diferentes tem limites de teste diferentes.
   Um laudo de um aparelho que so mede NEXT a 100 MHz nao cobre 250.
5. **Tem data?** Medicao de ano anterior nao descreve o cabo que esta la hoje.
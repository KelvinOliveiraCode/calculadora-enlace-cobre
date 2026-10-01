# Tabela de perdas e como o orcamento e montado

Este documento explica de onde vem cada numero no `caboclink` e, principalmente,
**por que o limite da norma se aplica ao canal inteiro** e nao so ao cabo. Esse
detalhe e a origem do erro mais comum em planilha de orcamento de perda.

## O limite e do canal, nao do cabo

O limite de perda de insercao da ISO/IEC 11801 (e da TIA-568) vale para o
**canal completo**: 90 m de cabo horizontal mais os conectores e o patch panel
das duas pontas. A tabela nao da um limite separado para o cabo.

Duas consequencias praticas:

1. Voce **nao pode** comparar so a perda do cabo com o limite da norma. Tem de
   somar os componentes e comparar o total.
2. Se voce compra Cat7A achando que "1 par a mais = folga de sobra", voce esta
   errado: o limite do canal ja foi definido com os componentes dentro.
   O que a categoria superior melhora e a **margem**, nao o teto.

## As tres numeros que importam

| Parametro | Tipo | Direcao | Pergunta que responde |
|---|---|---|---|
| Insertion Loss (IL) | teto (max) | menor e melhor | Quanto o sinal perde no caminho? |
| NEXT | piso (min) | maior e melhor | Quanto um par vaza para o vizinho? |
| PS-NEXT | piso (min) | maior e melhor | Quanto o vazamento sobrevive ao ruido do par vizinho? |

Perda de insercao e um **teto**: passar significa ficar abaixo. NEXT e PS-NEXT sao
**pisos**: passar significa ficar acima. Confundir as duas direcoes e o erro que
faz um laudo reprovar um enlace bom.

## Tabela usada pelo codigo

Valores de perda de insercao maxima por 100 m de cabo:

| Categoria | 100 MHz | 250 MHz | 500 MHz |
|---|---|---|---|
| Cat5e | 20,0 dB | - | - |
| Cat6 | 20,7 dB | 26,6 dB | - |
| Cat6A | 21,0 dB | 26,0 dB | 32,0 dB |

Perdas de componente (praticamente independentes do comprimento):

| Componente | 100 MHz | 250 MHz | 500 MHz |
|---|---|---|---|
| Patch panel | 1,0 dB | 1,3 dB | 1,8 dB |
| Conector RJ45 | 1,1 dB | 1,5 dB | 2,0 dB |
| Patch cord | 1,2 dB | 1,6 dB | 2,2 dB |
| Divisor | 1,4 dB | 1,8 dB | 2,4 dB |

Pisos de NEXT:

| Categoria | 100 MHz | 250 MHz | 500 MHz |
|---|---|---|---|
| Cat5e | 32,4 dB | - | - |
| Cat6 | 41,8 dB | 38,6 dB | - |
| Cat6A | 44,4 dB | 41,4 dB | 39,1 dB |

Note que NEXT cai com a frequencia: um par que isola bem em 100 MHz pode vazar
mais em 250 MHz. E por isso que o `caboclink` avalia todas as frequencias da
categoria, e nao so 100 MHz.

## A conta, linha a linha

Para o exemplo de `dados/exemplo-enlace.yaml` (Cat6, 45 m, 2 patch cords,
2 conectores, 1 patch panel):

**100 MHz**

```
cabo        20,7 dB/100 m x 0,45 =  9,31 dB
patch cords  2 x 1,2 dB         =  2,40 dB
conectores   2 x 1,1 dB         =  2,20 dB
patch panel  1 x 1,0 dB         =  1,00 dB
                                  --------
total                             14,91 dB
limite Cat6 em 100 MHz            20,70 dB
margem                             5,79 dB   APROVADO
```

**250 MHz**

```
cabo        26,6 dB/100 m x 0,45 = 11,97 dB
patch cords  2 x 1,6 dB         =  3,20 dB
conectores   2 x 1,5 dB         =  3,00 dB
patch panel  1 x 1,3 dB         =  1,30 dB
                                  --------
total                             19,47 dB
limite Cat6 em 250 MHz            26,60 dB
margem                             7,13 dB   APROVADO
```

## Modelo simplificado - leia antes de confiar

Este codigo **nao e um certificador**. O que ele faz e somar valores de tabela
com um modelo linear de comprimento. As limitacoes concretas:

- **NEXT e PS-NEXT sao mostrados como piso de referencia, nao calculados.**
  O codigo lista o piso aplicavel por frequencia para contexto do laudo. Ele
  **nao** estima acoplamento a partir do comprimento, do diametro ou do layout
  dos pares, porque isso exigiria um modelo de ICR que depende de geometria que
  a ferramenta nao tem. Um laudo real mede.
- **Nao ha correcao de temperatura.** Cabo instalado em ambiente quente tem
 atenuacao maior. A norma compensa isso em ensaio de laboratorio.
- **Nao ha degradacao por curvatura, grampeamento ou emenda.** Um cabo prensado
  dentro de uma canaleta pode perder mais que um divisor inteiro.
- **A perda escala linearmente com o comprimento.** Em baixa frequencia isso e
  razoavelmente verdade; perto do limite da categoria a curva real acelera.

Se o laudo deste codigo Reprovar, vale medir. Se ele Aprovar com ressalva, ainda
vale medir antes de passar o cabo. O que a ferramenta entrega e **antecipacao**:
descobrir o problema na planilha, e nao depois de puxar 88 m de cabo.

## Limites fisicos

| Limite | Valor | Origem |
|---|---|---|
| Cabo no canal | 90 m | ISO/IEC 11801 |
| Enlace total | 100 m | 90 m de cabo + patch cords e conectores |

Acima de 90 m de canal nao existe categoria que salve o enlace: o sinal ja
saiu do que a norma cobre. O `caboclink` reprova antes de fazer conta de perda,
porque o resultado seria enganoso.
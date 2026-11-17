# Experimento A-0 — Célula MTJ individual (macrospin STT)

## Objetivo científico

Estabelecer o modelo físico de referência da célula magnética do MHM-1: uma p-MTJ
CoFeB/MgO com anisotropia perpendicular, respondendo às perguntas:

1. Qual a resistência dos estados P e AP? (leitura)
2. Quanta corrente (densidade de corrente) comuta a célula, e em quanto tempo? (escrita)
3. A célula retém o estado a 300 K? (retenção — Δ)
4. Quanta energia custa um pulso de escrita? (célula, sem periféricos)
5. Onde estão os conflitos físicos (retenção × corrente de escrita × velocidade)?

## Ferramenta

Solver LLGS de macrospin escrito pelo projeto (Python/NumPy, sem dependências pagas):
`llgs_macrospin.py`. Equação: Landau-Lifshitz-Gilbert + torque de Slonczewski +
campo térmico de Brown, integrada por RK4.

## Execução (PC local)

```
pip install numpy matplotlib
cd C:\Users\edval\Desktop\MHM-1\exp_A0_macrospin
python experimento_a0.py
```

Tempo: ~1 min no i3-10105F. Saídas em `resultados/` (CSV + PNG + console.txt).

## Resultados obtidos (execução REAL de 16/11/2026 — ver resultados/console.txt)

| Grandeza | Valor |
|---|---|
| Δ (barreira térmica, 300 K) | **59,2 k_B·T** (critério 10 anos: Δ ≳ 43 ✔ com folga) |
| R(P) / R(AP) | 7,96 / 19,9 kΩ (RA = 10 Ω·µm², TMR = 150%) |
| J_c0 macrospin (0 K, analítico) | 5,54 MA/cm² (I_c0 ≈ 70 µA) |
| Limiar de comutação a 0 K em pulso de 5 ns | **entre 9,5 e 10 MA/cm²** |
| Comutação a 0 K | 3,74 ns @ 10 MA/cm²; 2,91 ns @ 12; 2,02 ns @ 16 |
| Comutação a 300 K (P ≥ 97,5%) | J = 8 MA/cm² com 5 ns (t_med 3,6 ns); J = 12 com 2 ns (só 17,5% a 2 ns) |
| Pulso de 1 ns | **0% de comutação até 12 MA/cm²** |
| Retenção (J=0, 300 K, 5 ns, 40 trajetórias) | 0 comutações espontâneas ✔ |
| Energia de escrita (célula) | 0,28 pJ @ (8 MA/cm², 2 ns); 0,63 pJ @ (12, 2 ns); 1,1 pJ @ (10, 5 ns) |

## Interpretação (o que os números ensinam)

1. **Limiar de instabilidade ≠ comutação em pulso.** A corrente crítica analítica
   (J_c0 = 5,5 MA/cm²) marca onde o torque STT vence o amortecimento, mas a comutação
   determinística a partir de uma inclinação mínima exige amplificar essa inclinação
   (regime logarítmico): a 0 K isso empurra o limiar *efetivo* para ~2× J_c0 no pulso de 5 ns.
2. **A temperatura ajuda e torna o processo probabilístico.** A 300 K o ruído térmico
   semeia a inclinação: J = 8 MA/cm² comuta em ~3,6 ns com P ≈ 98% (pulso 5 ns), mas
   **pulsos de 1 ns não comutam nem a 12 MA/cm²** com STT puro.
   → Conclusão de projeto: **a meta de 1–2 ns/célula exige assistência** (SOT com maior
   eficiência, pré-pulso VCMA reduzindo Δ, ou camada ferrimagnética) — exatamente o
   Experimento B.
3. **Conflito retenção × escrita quantificado.** Nossa célula tem Δ = 59 (retenção
   folgada) e isso eleva a corrente de escrita. Reduzir K_eff diminui J_c, mas destrói a
   retenção. O ponto de operação é uma escolha de projeto, e é ali que VCMA (Δ dinâmico)
   se torna interessante (hipótese H1).
4. **Energia de célula < 1 pJ é alcançável em regime, mas sem folga** no canto
   (2 ns, 12 MA/cm² = 0,63 pJ) — e o valor real do dispositivo incluirá acesso transistor,
   linhas e overhead de erro, que ainda não modelamos.
5. **Célula ≠ matriz:** os 2–4 ns medidos são só a dinâmica magnética. A meta de 20–30 ns
   de latência de matriz inclui seleção, sense amplifier e roteamento (FASES 5–6).

## Limitações do modelo (declaradas)

- Macrospin: ignora nucleação de domínios → dispositivos reais comutam com corrente
  MENOR. O A-1 (MuMax3, micromagnético) vai quantificar isso.
- RK4 com ruído congelado por passo; Heun estocástico seria preferível para estatística térmica fina.
- Sem termo "field-like" do STT; TMR sem dependência de bias; R média no cálculo de energia.
- 40 trajetórias/ponto dão resolução de probabilidade ~2,5%; mais trajetórias para P < 5%.

## Próximos incrementos (A-1, A-2)

- **A-1:** repetir a célula em MuMax3 (60×60×1,5 nm, template em `../exp_A1_mumax3/`) e
  comparar limiar/t_upload com o macrospin.
- **A-2:** extração de Δ por taxa de fuga térmica (tempo médio de dwell × N trajetórias
  longas ou barreira reduzida) para validar a retenção de 10 anos além da checagem analítica.

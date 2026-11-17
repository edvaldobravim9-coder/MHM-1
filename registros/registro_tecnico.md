# Registro Técnico — MHM-1 (diário de bordo oficial)

## Entrada 001 — 16/11/2026 — FASE 1 (e início da FASE 2)

### Verificado de fato (sites abertos hoje)
- Ubermag ✔ https://ubermag.github.io — Binder oficial ativo; backends OOMMF (CPU) e mumax3c (GPU).
- MuMax3 3.12 ✔ https://mumax.github.io — exige NVIDIA CC ≥ 5,0; **GT 1030 = CC 6,1 → compatível em princípio**; ~16 M células com 2 GB.
- OOMMF ✔ https://math.nist.gov/oommf/ — gratuito (NIST); opção online no nanoHUB (link oficial na página).
- Ramulator 2.1 ✔ https://github.com/CMU-SAFARI/ramulator2 — MIT; DDR3–DDR5, LPDDR5/6, GDDR6/7, HBM1–4; energia pJ/bit (plugin Ayna); integração gem5; **arquitetural, não físico**.
- numpy 2.5.3 e matplotlib 3.11.2 instalados no PC local (Python 3.15).

### Não verificado hoje (busca web indisponível — cota)
- Links do Spirit, Vampire, Fidimag, SunTzu/CEA-Leti (Verilog-A) e Xyce — marcar para revalidação.
- Números de patentes específicas (ver `docs/paisagem_ip.md`, consultas prontas).

### Executado de fato
- **Experimento A-0** (macrospin LLGS, STT + térmico, RK4) — célula p-MTJ 40 nm × 1,5 nm,
  Ms = 6e5 A/m, K_eff = 1,3e5 J/m³ (Δ = 59), α = 0,01, TMR = 150%, RA = 10 Ω·µm².
  Resultados principais (arquivos em `exp_A0_macrospin/resultados/`):
  - J_c0 analítico 5,54 MA/cm²; limiar efetivo a 0 K em pulso de 5 ns: 9,5–10 MA/cm²
    (efeito logarítmico da amplificação de inclinação — física correta do macrospin).
  - 300 K: P(comutar) = 97,5% com (8 MA/cm², 5 ns), t_medio 3,58 ns; 17,5% com (12, 2 ns);
    **0% com pulsos de 1 ns até 12 MA/cm²** → STT puro não atinge a meta de 1–2 ns.
  - Retenção: 0 comutações espontâneas em 5 ns × 40 trajetórias (coerente com Δ = 59).
  - Energia de escrita (célula): 0,28 pJ (8 MA/cm², 2 ns) … 1,58 pJ (12, 5 ns).
- **Correção de modelo durante o experimento:** primeira execução usava varredura até
  8 MA/cm² e não observou comutação a 0 K; análise indicou que o regime determinístico
  rápido está acima de ~2×J_c0 → varredura estendida (10–16 MA/cm²) e reexecutada.
  Ambas as execuções estão no histórico desta entrada (console final em `console.txt`).

### Conclusões da entrada
1. O conflito Δ × J_c está quantificado: retenção folgada (Δ = 59) custa corrente de
   escrita; STT puro não entrega 1–2 ns com energia confortável → **motiva o Experimento B**
   (SOT, VCMA, ferrimagnéticos).
2. Macrospin serve para varreduras de projeto, mas superestima J_c (sem nucleação) →
   validar em MuMax3 (A-1) antes de qualquer conclusão forte.

### Próximo passo proposto (não executado)
- Baixar e instalar MuMax 3.12 (Windows, binário) e validar a GT 1030 com o template
  `exp_A1_mumax3/mtj_camada_livre.mx3` (60×60×1,5 nm).
- Executar as consultas de patentes do `docs/paisagem_ip.md` (Seção 3) e registrar números.
- A-2: extração de Δ por fuga térmica acelerada.

---

## Entrada 002 — 16/11/2026 — Disco recuperado, MuMax3 instalado e calibrado

### Infraestrutura
- **Disco recuperado: 0 → 13,17 GB livres.** Pip cache 3,37 GB; %TEMP% 0,16 GB;
  npm cache 2,80 GB; cleanmgr + cache do Windows Update + DISM /StartComponentCleanup
  0,90 GB (UAC aprovado pelo usuário; log em `registros/limpeza_admin.log`).
- **Mapeamento somente leitura** (nada apagado): maiores ocupantes —
  AppData\Local\Android 26,4 GB; C:\Windows 26,7 GB; C:\LDPlayer 20,1 GB;
  Downloads 19,4 GB (INTOCADO, por instrução do usuário); Roaming 7,3 GB;
  Programas 7,3 GB; Lixeira 4,15 GB; C:\modelos 3,8 GB; ms-playwright 2,5 GB; WSL 2,3 GB.
  Candidatos futuros (só com aprovação): LDPlayer + Android SDK (~46 GB).
- **Projeto movido** de `C:\Users\edval\MHM-1` para `C:\Users\edval\Desktop\MHM-1`
  (pasta antiga removida; caminhos nos READMEs atualizados).

### MuMax 3.12 na GT 1030 — instalado e calibrado
- Binários em `tools\` (mumax3.exe 26,3 MB, -convert, -server). GPU detectada:
  **GT 1030, 2047 MB, CUDA Driver 12.7, cc=6.1 (PTX ativo)** — funcional.
- Correções de API (3.12): `mz`/`E`/`Edens_exchange` não são globais →
  `mz := m.Comp(2)`, `Edens_total`, `Edens_exch`; série temporal com
  `TableAutoSave(δt)`; **`tablesave()` ao final é obrigatório** (buffer não
  descarrega na saída limpa — aprendido à custa de uma execução perdida).

### Lição central do dia: estabilidade de troca × passo de tempo
- Sintoma: solver adaptativo padrão (RK45) "travado" por 25+ min em grade 40×40×1
  com Temp=300 K; processo morto. Substituí por RK4 (solver 4) + FixDt=1e-12.
- **RK4+dt=1 ps explodiu**: E_exchange saturou em 6,5e7 J/m³ (teto de células
  antiparalelas) e m_z ficou preso no equador mesmo sob B=-1 T. Inicialmente
  suspeitei do RK4 com ruído (pump de energia); o diagnóstico C (**Temp=0**)
  reproduziu a explosão → não era o ruído.
- **Causa raiz**: com células de 1 nm, o campo de troca do modo de Nyquist é
  ~200–500 T → dt estável ≈ 20–60 fs. O adaptativo estava CORRETO (encolhia o
  passo para essa escala; a lentidão era física da malha rígida, não latência).
- Confirmação (diagnóstico E): Heun + FixDt=2e-14, Temp=0 → reversão limpa
  m_z: +1 → -0,23 em 1 ns, espiralando para -z. Teoria verificada.

### Malha A-1 recalibrada (smoke_test_v2.mx3) — números reais
- Célula 2,5×2,5×1,5 nm, grade 14×14×1 (35×35 nm — mesma área do círculo de
  40 nm do A-0), Ku1=335 kJ/m³, Heun + FixDt=1e-13 (margem 1,4× sobre o limite).
- Fase 1 (relax, B=0): Edens_demag = 201 901 J/m³ → **N_z = 0,8925** →
  **K_eff = 133,1 kJ/m³ → B_keff = 0,4437 T → Δ = 59,1** (A-0: 59,2 — desvio 0,2%).
- Fase 2 (B=-1 T, 300 K): comuta em ~3,2 ns; m_z(5 ns) = -0,46 convergindo para -1.
  E_exch ~ 9e6 J/m³ (~4 kT) = texturas térmicas físicas. A reversão 2D é ~3× mais
  lenta que a previsão macrospin (tanh dá -0,998 em 5 ns) — físico a medir no A-1a.

### Experimento A-2 — primeira execução (v1) e correção
- **v1 executado**: 0 flips em 80 trajetórias × 3 raios (Δ = 3,7/5,7/8,3).
- **A teoria do script estava errada, não o solver**: usei f₀ = γ·B_keff/2π
  sem o fator de amortecimento. Em LLG com α baixo, a fuga sobre a barreira é
  conduzida pelo amortecimento → f₀ ~ α·γ·B_keff/(2π)·√(Δ/π) (Brown 1963).
  Janela ~100× curta demais → 0 flips é o esperado. polyfit crashou (guarda ausente).
- **v2 em execução** (janelas com prefactor de Brown; captura quando notificar).
  O teste real da calibração do ruído é a INCLINAÇÃO ln(taxa) vs Δ (esperado -1);
  a prefactor só Fixa o intercepto.

### Próximo passo proposto (não executado)
- Registrar resultado do A-2 v2 (inclinação e f₀ efetivo) nesta entrada.
- A-1a: varredura de campo (B_sw) na malha calibrada; A-1b: varredura STT
  Slonczewski (DisableZhangLiTorque=true, J, Pol, FixedLayer, Lambda) para
  comparar nucleação vs macrospin do A-0.
- Revalidar links (Spirit/Vampire/Fidimag/SunTzu/Xyce) e patentes quando a
  busca web voltar (hoje: cota 402/429).

---

## Entrada 003 — 16/11/2026 — FASE 1 ENCERRADA; FASE 3 quase completa

### FASE 1 ENCERRADA (23:45) — revalidação final
- websearch segue fora (402); revalidação por webfetch/GitHub API:
  ✔ Vampire 7 (york.ac.uk) · ✔ Xyce 7.10 (sandia.gov) · ✔ Spirit (moveu-se para
  github.com/spirit-code/spirit, MIT — site antigo da TU Wien morto) ·
  ✔ Fidimag (github.com/computationalmodelling/fidimag, ativo 10/11/2026) ·
  ⚠ SunTzu não localizado publicamente (modelo CEA-Leti sob registro).
- Decisão: SunTzu não bloqueia nada — FASE 6 usará Verilog-A próprio do
  macrospin validado. Consultas de patentes RECLASSIFICADAS como pré-requisito
  da FASE 4 (são análise de novidade, não seleção de ferramentas).
- Ferramentas do stack foram validadas NA PRÁTICA (Fases 2–3) — critério mais
  forte que o levantamento de papel. Detalhes em `docs/fase1_ferramentas.md` §0.

## Entrada 003 — detalhes de execução (16/11/2026, dia)

### Correção de solver (supersede a lição 1 do README da pasta A-1)
- **Heun explícito (solver 2) + FixDt é incondicionalmente instável em precessão
  pura**: o esquema |1 + iθ + (iθ)²/2| = √(1 + θ⁴/4) > 1 para todo θ > 0 bombeia
  energia no modo de xadrez; o RK45 padrão é estável no eixo imaginário até θ ≈ 2,8.
- **A-1a v1 (13 campos 0,300–0,550 T, pulso 3 ns, Heun+FixDt=1e-13) está
  CONTAMINADA** — números RETRAÍDOS; artefatos preservados em
  `exp_A1_mumax3/v1_heun_contaminado/` (13 .mx3 + 13 .out).
- Regra adotada: runs determinísticos (Temp=0) usam o RK45 ADAPTATIVO padrão
  (sem SetSolver/FixDt). Evidência: `verif_rk45.mx3` (reversão por campo
  damping-limited, ~25–37 ns a 0,55 T — física, não bug).

### Experimento A-1a v2 — EXECUTADO (resultados em `exp_A1_mumax3/resultados_a1a/`)
- Protocolo: RK45 padrão, Temp=0, pulso 10 ns, 11 campos 0,50–1,00 T,
  malha calibrada 14×14×1 (2,5 nm), m₀ inclinado 0,01.
- **B_sw(10 ns) = 0,75 T** — transição limpa: 0,70 T → m_z = +0,859 (não comuta);
  0,75 T → −0,556 (comuta; meio da reversão no fim do pulso); 0,80 T → −0,999.
  B_sw/B_keff = 1,69 (B_keff = 0,4437 T).
- **Validação quantitativa da dinâmica**: o modelo damping-limited
  t_sw ≈ ln(1/θ₀)/(αγ·(B−B_keff)) prevê B_sw(10 ns) = 0,4437 + ln(100)/(αγ·10 ns)
  ≈ 0,70–0,71 T — dentro do intervalo medido (0,70–0,75 T; fatores O(1) no log).
- **Interpretação (rigor)**: B_sw > B_keff NÃO contradiz nucleação — com pulso de
  10 ns o regime é damping-limited. O teste de nucleação (B_sw ≤ B_keff) exige
  pulsos quase-estáticos de ~µs (custo ~100–200 min/run na GT 1030). Alternativa
  barata proposta: dump espacial de m_z durante a reversão (0,70–0,75 T) para
  distinguir nucleação por bordas de rotação coerente. O critério do README
  ("B_sw ~ B_keff") vale para o limite quase-estático; o de 10 ns valida a dinâmica.

### A-1b v2 — EXECUTADO (~21:20, resultados em `exp_A1_mumax3/resultados_a1b/`)
- Pulso 5 ns, 0 K, RK45, J<0 (magnitudes 6–16 MA/cm²):
  **J_sw = 8 MA/cm²** (bracket 6–8; a 6 m_z = +0,944; a 8 comuta com
  t(cruzou 0) = 4,08 ns). t(cruzou 0): 4,08 → 1,58 ns (8 → 16 MA/cm²), monotônico.
- **Razão MuMax3/A-0 = 0,82** — nucleação REDUZ o limiar (direção prevista).
  Normalizado por J_c0 (5,54): malha 1,44×; A-0 1,71–1,8×.
- Ressalvas registradas: A-0 comparador pende de reexecução (anisotropia);
  quadrado 35 nm vs círculo 40 nm (mesma área, nucleação por bordas difere).

### A-1b v1 — resultado nulo e diagnóstico do sinal (20:45–21:00)
- **Nenhuma das 8 correntes (6–16 MA/cm², pulso 5 ns, 0 K) comutou**; m_z final
  = +1,00000 exato em todas — o torque não anti-amortece a inclinação.
- Hipóteses: (a) sinal do STT invertido em relação ao A-0 (risco documentado no
  docstring — convenção de J do MuMax3 × FIXEDLAYER_TOP); (b) STT não aplicado.
  m_z = +1,00000 exato é compatível com ambas (torque restaurador ou nulo
  devolvem m ao polo).
- **Diagnóstico concluído** (`diag_stt_sinal.py`, evidência em `v1_jpositivo_nulo/`):
  J = −10 e −14 MA/cm² (5 ns) e −8 MA/cm² (10 ns) **COMUTARAM** (m_z final −1,00000)
  → STT ativo e mapeamento correto; o sinal de J do MuMax3 com FixedLayer=+z e
  FIXEDLAYER_TOP é OPOSTO ao do A-0 (J>0 estabiliza P; J<0 comuta P→AP).
- **A-1b v2 relançado (~21:00)** com J<0: mesma faixa de magnitude (6–16 MA/cm²),
  CSV com colunas J_mag e J_aplicado. Comparar J_sw com A-0 (9,5–10 MA/cm²; nota:
  números do A-0 pendentes de reexecução pós-correção da anisotropia).
  Resultados A-1b v1 mantidos em `resultados_a1b/` (evidência do nulo).

### A-2 v3 — concluído (~22:30): ruído no lugar, desvio quantificado
- Resultado bruto: Δ=3,70 → 80/80 (MFP 76,8 ns); Δ=5,69 → 80/80 (330,1 ns);
  Δ=8,32 → 59/80 (rate MLE 2,68e5/s). Contraste com v2 (0/80): a correção da
  anisotropia destravou a fuga.
- **Taxas 4–5,6× acima de f0_Brown·e^(−Δ)**; inclinação do script (−0,654) é
  ENVIESADA — usa o limite inferior nas linhas com 80/80. Reanálise com o tempo
  médio de primeira passagem: **inclinação ≈ −0,85, f0_eff ≈ 3,2e8 Hz**
  (Brown assintótico: −1 e 1,3–2e8 Hz).
- Significância: P(80/80 | taxa teórica) ≈ 10⁻³ em CADA ponto baixo → o desvio
  é real, não fluke estatístico.
- Interpretação provisória: (a) Brown (1963) é assintótico para Δ≫1 — em
  Δ = 3,7–8,3 a degradação da forma assintótica é esperada da literatura;
  (b) possível artefato de dt (RK4 com ruído congelado, dt = 1 ps).
  **Teste discriminatório em execução** (`diag_dt_convergencia.py`:
  Δ = 5,69 a dt = 0,5 ps + equipartição a dt = 0,25 ps; ~1,5 h).
- **Robustez da retenção** (não espera o teste): mesmo com a inclinação mais
  pessimista observada (−0,65), o dwell extrapolado para Δ = 59 dá ~25 anos
  (> meta de 10). Com inclinação −1: ~10¹⁰ anos. A conclusão qualitativa
  "Δ = 59 segura 10 anos" é robusta ao desvio.
- Decisão de método: para afirmações quantitativas térmicas, usar a CALIBRAÇÃO
  EMPÍRICA taxa(Δ) medida (com sua incerteza) em vez de extrapolar com a
  fórmula assintótica de Brown.
- **A-0 reexecução lançada (~22:40)** com o solver corrigido (0 K + 300 K +
  retenção + energia); saída viva em `resultados/`; execução v1 (campo
  constante) preservada em `resultados/v1_campo_constante/` (8 arquivos).

### A-0 v2 (reexecutado com anisotropia corrigida) — concluído ~23:00
- **Limiar 0 K (5 ns): 8 MA/cm² comuta (4,44 ns); 6 não comuta** — era 9,5–10 no
  v1 (campo constante). Direção prevista: o uniaxial acelera após o equador.
- **300 K REVISADO**: 2 ns @ 12 MA/cm² = **90%** (v1: 17,5%); 5 ns @ 8 = 100%
  (v1: 97,5%); **1 ns continua 0% até 12 MA/cm²**.
- Retenção: 0 flips ✓ (inalterada, como previsto — teste insensível ao bug).
- Energia: inalterada (não depende da dinâmica): 2 ns @ 12 = 0,63 pJ;
  5 ns @ 8 = 0,70 pJ.
- **Veredito de metas atualizado (macrospin, 300 K)**: 2 ns ✓ (90%, 0,63 pJ);
  <1 pJ ✓ nos pontos rápidos; 1 ns ✗ (motiva SOT/VCMA); Δ = 59 ✓.
### Refino J_sw — razão definitiva (~23:15, `exp_A1_mumax3/refino_jsw.py`)
- Malha: 6,5 → +0,786 ✗; 7,0 → +0,179 ✗ (quase); 7,5 → −0,762 ✓ (4,54 ns)
  → **J_sw(malha) ∈ (7,0–7,5] MA/cm²**.
- Macrospin v2: 6,5 → ✗; 7,0 → −0,928 ✓ (6,76 ns, cruzou no tail); 7,5 → ✓
  → **J_sw(macrospin) ∈ (6,5–7,0] MA/cm²**.
- **RAZÃO ≈ 1,07 (1,0–1,15) — nucleação NÃO reduz o limiar neste desenho**;
  malha ~7% pior que macrospin. RETRAÇÃO: o "0,82" anterior era vs o A-0 v1
  (campo constante, limiar 9,5–10) — não usar.
- **Explicação**: δ_w = √(A/K_eff) ≈ 10,6 nm → parede de Bloch ~33 nm vs amostra
  de 35 nm — a parede mal cabe; reversão quase-coerente, custo de troca na
  textura. Consistente com A-1a (nucleação não observada por campo também).
- **Implicação metodológica (para Fase 4+)**: nesta classe de célula (≥ ~30 nm,
  Δ ~ 60, parede ~ amostra), o MACROSPIN é aproximação excelente do limiar
  (desvio ~7%) → varreduras de arquitetura podem usar macrospin, com MuMax3
  como verificação pontual. Economia de ~100× em custo computacional.

### API do MuMax 3.12 — semente de ruído térmico (~23:30)
- `RNGSEED = n` NÃO existe (4 runs falharam com "undefined: RNGSEED").
- Correto (API oficial 3.12): **`ThermSeed(n)`** — semente do ruído térmico
  (`randSeed(n)` semeia rand/randExp/randNorm/randInt do script Go).
- Viabilidade térmica relançada com `ThermSeed`.

### Viabilidade térmica do MuMax3 — concluída (~00:30, `termico_viabilidade.py`)
- Protocolo: malha 14×14 (2,5 nm), 300 K, RK45, `ThermSeed` — 4 runs.
- **T1 ruído puro (J=0, 3 ns, seeds 1–2): 0 flips**; m_z mín = +0,925 → retenção
  sã no nível da malha (Δ = 59,1: reversão total esperada ≈ e^(−59), confirmado).
- **T2 assistência térmica (J = 6,5 MA/cm², 5 ns, seeds 1–2): 2/2 comutaram**
  (m_z final ≈ −0,955). Abaixo do limiar 0 K da malha (6,5 → m_z = +0,786),
  coerente com o A-0 macrospin a 300 K (5 ns @ 6 MA/cm² = 95%). Indicação n=2,
  não estatística — mas fisicamente consistente em ambos os modelos.
- **CUSTO (decisivo para a Fase 4+)**: wall ≈ 200 s / 3 ns (ruído puro) e
  **≈ 655 s / 5 ns com STT** (≈ 11 min/run) na GT 1030 → campanha de 100 runs
  ≈ 18–19 h = 1 noite local. **Não precisa Colab/Kaggle para n ~ 100.**
- ⚠ **Equipartição da malha: em aberto** — <1−m_z²> = 0,107 medido vs a
  referência "0,0085" impressa no script. A referência era a fórmula de
  MACROSPIN (1/(2Δ)), que NÃO se aplica a 196 células (~392 modos térmicos →
  valor esperado maior por construção). Discriminador lançado
  (`diag_equipart_1celula.py`): 2×2×2, Aex = 0 (células independentes),
  demag off, Ku = K_eff = 1,30e5 → Δ = 59,2 exato, fórmula macrospin válida.
  Se ≈ 0,008–0,02 → FDT por célula correto e 0,107 é contagem de modos;
  se ≈ 0,1 → amplitude térmica ~13× alta → investigar.
- **API descoberta no caminho**: `Temp > 0` exige número PAR de células por eixo
  (RNG térmico via FFT) — 1×1×1 panica com exit 2; usar 2×2×2 + Aex = 0.
- Os runs T2 (<1−m_z²> ≈ 0,39) incluem a rotação de comutação — não são
  referência de equilíbrio; usar só os runs T1.

### Equipartição por célula — discriminador concluído (~01:20, `diag_equipart_1celula.py`)
- Setup: 2×2×2 células, **Aex = 0** (8 macrospins independentes), demag off,
  Ku = K_eff = 1,30e5 → Δ = 59,2 exato; 10 ns, 300 K, ThermSeed(1).
- **MEDIDO: <1−m_z²> = 0,0200** (1002 amostras; m_z mín = +0,981, nunca saiu do poço).
- **CORREÇÃO DE CONVENÇÃO (minha)**: a teoria "1/(2Δ) = 0,00845" impressa em v1
  do teste usava a convenção errada. Equipartição correta para o macrospin:
  E ≈ KV(m_x² + m_y²), 2 DOF quadráticos → **<1−m_z²> = kT/(K_eff·V) = 1/Δ ≈
  0,0169** (o valor exato da integral de Boltzmann converge para 1/Δ a Δ alto;
  a mesmo fórmula usada no diag_ruido: em Δ=3,7 ela dá 0,3171 ✓).
  **Razão medido/teoria = 1,18** → FDT por célula do MuMax3 essencialmente
  correto; resíduo ~18% compatível com autocorrelação (1002 amostras
  correlacionadas em ~120 períodos de precessão) + viés de ruído congelado.
- **Veredito**: o 0,107 da malha 14×14 é CONTAGEM DE MODOS (~392 DOF térmicos
  em 196 células), não bug — o ruído térmico do MuMax3 está **APROVADO** para
  as campanhas térmicas da Fase 4+.
- Nota de método: para comparar equipartição malha vs macrospin no futuro,
  somar os modos (teoria de equilíbrio discretizado) em vez de usar a fórmula
  macrospin direta.


### dt-convergência — desvio do A-2 é FÍSICA (~01:50, `diag_dt_convergencia.py`)
- Δ = 5,69, 80 trajetórias, janela 4,52 µs:
  - dt = 1,0 ps (A-2 v3): MFP 330,1 ns → 3,03e6/s
  - **dt = 0,5 ps: MFP 381,6 ns → 2,62e6/s** (queda de só −14%)
- Se fosse artefato de ruído congelado, a taxa convergiria para a teoria de
  Brown ao refinar dt — mas permanece **~4,7–5,5× acima** (teoria: 5,55e5/s).
  → **Desvio vs Brown é FÍSICA de Δ baixo** (degradação da forma assintótica),
  com resíduo sistemático menor de dt declarado como incerteza (~−14% por
  half-dt; extrapolação dt→0: ~2,4e6/s, ainda 4,3× acima de Brown).
- Equipartição a dt = 0,25 ps: **0,3197 vs 0,3171 → razão 1,008** — banho
  térmico do solver praticamente exato mesmo com passo 4× menor.
- **DECISÃO: A-2 v3 fica como calibração empírica definitiva** (inclinação
  ≈ −0,85, f₀ ≈ 3,2e8 Hz), sem reexecução a dt menor. Não havia artefato a
  corrigir — o A-2 fino seria custo de ~6 h sem mudança de conclusão.

### FASE 3 ENCERRADA (~01:55) — veredito consolidado
- Campo (A-1a): B_sw = 0,75 T @ 10 ns — validação quantitativa (prev. 0,70–0,71).
- Corrente (A-1b + refino): J_sw malha ≈ 1,07× macrospin; reversão
  quase-coerente (δ_w ≈ 10,6 nm); **macrospin validado para varreduras (Fase 4+,
  ~100× mais barato)**.
- Macrospin corrigido (A-0 v2): limiar 0 K 5 ns = 8 MA/cm²; 300 K: 2 ns ✓ (90%
  @ 12, 0,63 pJ); 1 ns ✗ (motiva SOT/VCMA); <1 pJ ✓; Δ = 59,2 ✓.
- Térmico macrospin (A-2 v3): calibração empírica taxa(Δ) com incerteza; desvio
  vs Brown explicado (física de Δ baixo + resíduo dt).
- Térmico micromagnético (viabilidade + discriminador): wall ≈ 11 min/run;
  FDT por célula correto (0,0200 vs 0,0169, razão 1,18; malha 0,107 = contagem
  de modos).
- **Metas da célula: 2 ns ✓ · <1 pJ ✓ · Δ ≥ 42 ✓ · 1 ns ✗ (→ SOT/VCMA, Fase 4).**
- Progresso do projeto: **~36%** (Fases 1–3 fechadas = 37,5 de 100).


### GitHub — publicado (00:57–01:05)
- Repo: **github.com/edvaldobravim9-coder/MHM-1** (público, licença MIT).
- Push completo: código, resultados, diários, docs (336 arquivos) + ferramentas
  MuMax3/DLLs CUDA (**618 MB via Git LFS**, 3 objetos, 12 MB/s).
- Commits: `d4031ff` (projeto), `ed90209` (MIT), `313d034` (tools via LFS).
- `.gitignore`: `__pycache__`, `*.pyc`, `*.ovf` (dumps espaciais); tools/ versionado
  a pedido do autor ("tudo no GitHub"). MuMax3 é GPLv3 — nota de fonte no repo pendente.
- Conta limpa a pedido do autor: chatbox-ai, Zygisk-Il2CppDumper, robo-surebet e
  sure-bot EXCLUÍDOS pelo usuário via navegador (exclusão é só do dono);
  **backup mirror local pré-exclusão** em `C:\Users\edval\Desktop\github_backup_2026-11-17\`.
- Automação restante: atualizações futuras = commit + push (auth já cacheada no
  Git Credential Manager; sem novo login).

### Em execução neste momento (~01:00)
- `diag_dt_convergencia` (CPU): dt = 0,5 ps no Δ = 5,69 — física de Δ baixo vs
  artefato de dt no desvio do A-2.
- `diag_equipart_1celula` (GPU): discriminador de equipartição (acima).

### ACHADO MAJOR — bug estrutural no solver A-0 (20:00–20:30)
- **A-2 v2 concluiu com 0/80 flips nos três raios** — impossível por estatística
  (janelas corretas: esperava ~2,5 flips/trajetória em Δ=3,7 e ~19 no Δ=8,3 cap;
  p < 10⁻⁸⁰). Não era janela: era o MODELO.
- **Causa raiz** (`llgs_macrospin.py::deriv`): o campo aplicado era
  **B_keff·ẑ CONSTANTE**, não anisotropia uniaxial B_anis = B_keff·m_z·ẑ.
  Campo constante não tem barreira de Néel (um único poço +z) → fuga para
  m_z = −0,9 escala ~e^(−2Δ), não e^(−Δ) → taxas ~10⁵× menores que o alvo.
  O MuMax3 (anisU/Ku1) sempre teve anisotropia verdadeira.
- **Diagnóstico** (`exp_A2_termico/diag_ruido.py`, mantido como evidência):
  - D1 equipartição: ANTES razão 0,737 vs Boltzmann; DEPOIS **0,994** (<1−m_z²>
    medido 0,3151 vs teoria 0,3171; 576 000 amostras) — FDT essencialmente exata;
    viés residual 0,6% atribuído ao RK4 com ruído congelado (limitação já
    documentada no solver).
  - D1 pós-fix: 13,3% das amostras com m_z<0, mín −1,0 → dois poços populados ✓.
  - D2 (3000 K, Δ_eff=0,37): 158/160 → 160/160 cruzamentos em 20 ns ✓.
  - D3 (0 K): desvio de m_z=1 = 0,0 ✓.
- **Correção aplicada**: `B[:, 2] = self.B_keff * m[:, 2]` + comentário no código.
- **Impacto nos resultados anteriores (rigor)**:
  - A-0 térmico/retenção (0 flips): conclusão MANTIDA (com barreira real, Δ=59,
    0 flips em 5 ns é o esperado com folga), mas o teste era insensível ao bug.
  - **A-0 limiar 0 K (9,5–10 MA/cm²) e P(comutar) 300 K: REEXECUTAR** — a
    restauração perto de +z é a mesma (curvatura idêntica), mas a dinâmica além
    do equador muda (uniaxial ACELERA após 90°; campo constante resistia).
    Não citar os números antigos até reexecutar.
  - A-1 (MuMax3): NÃO afetado (anisotropia verdadeira desde sempre).
- **A-2 v3 relançado 20:30** com o solver corrigido (mesmo protocolo); capturar
  inclinação ln(taxa) vs Δ (esperado −1) e f₀ efetivo.

### Próximo passo proposto (não executado)
- Registrar J_sw do A-1b e a razão vs A-0 (9,5–10 MA/cm²); < 1 → nucleação,
  ≥ 1 → investigar malha/parâmetros/mapeamento de sinal STT.
- Registrar A-2 v2: inclinação ln(taxa) vs Δ (esperado −1) e f₀ efetivo.
- Testar viabilidade de runs térmicos no MuMax3 (Temp>0, RK45, malha 2,5 nm) antes
  de campanhas estatísticas.


---

## Entrada 004 — 17/11/2026 — FASE 4: arquiteturas

### A-4a aberto: VCMA + STT (~02:10, `exp_A4_arquiteturas/`)
- Alvo direto: a meta **1 ns** (0% até 12 MA/cm² no A-0 v2 com STT puro).
- Ideia: reduzir a barreira **apenas durante o pulso** (K_eff' = f_K·K_eff),
  mantendo Δ = 59,2 estático — retenção preservada por construção (comutação é
  absorvente: no tail a barreira integral prende em −z).
- Implementação no solver: `k_mult` (atributo) + `k_mult_pulse` em `run_pulse`
  — retrocompatível (f_K = 1,0 replica o A-0 v2 exato).
- Grid: f_K ∈ {1.0, 0.9, 0.75, 0.5, 0.25} × J ∈ {8, 10, 12, 15} MA/cm²;
  0 K determinístico + 300 K (40 traj/ponto), pulso 1 ns.
- ⚠ **β (VCMA) SEM FONTE ainda**: busca web bloqueada (402). Mapeamento
  V_b = (1−f_K)·K_eff·t_FL·t_MgO/β declarado como **ILUSTRATIVO** (β = 100
  fJ/(V·m) projeto; 50 pessimista; faixa relatada 20–300). A varredura em f_K é
  autocontida (física pura); a tradução em volts exige a fonte. Pendência
  registrada: consultar literatura quando a busca voltar (ou manual).
- E_VCMA ≈ ½·C·V² com C ≈ 100 aF (MgO 1 nm, εr = 9) → 5–100 aJ: desprezível
  vs STT (0,3–1 pJ) — o ganho do VCMA é REDUZIR J, não custo próprio.

### A-4a concluído (~02:20): NEGATIVO para 1 ns — e a lição de design
- Resultado: 0 K — NADA comuta em 1 ns (nem J = 15, nem f_K = 0,25);
  300 K — P ≈ 0% no grid todo, exceto 12,5–15% @ J = 15, **independente de f_K**.
- **Diagnóstico (por que é física real, não bug)**: o gargalo do 1 ns é TORQUE,
  não barreira. B_stt(J = 15 MA/cm²) ≈ 0,022 T — 5× menor que B_keff' = 0,108 T
  mesmo com f_K = 0,25. A comutação determinística em <1 ns exigiria B_stt ~ B_keff
  (J >> 15 — energia explode). E a via térmica: Δ' = 14,8 (f_K = 0,25) →
  P(fuga em 1 ns) ≈ e^(−14,8)·f0·1 ns ≈ 10⁻⁷ — desprezível.
- **Consequências para a Fase 4**:
  1. H1 REESCRITA: VCMA não é alavanca de VELOCIDADE; é alavanca de ENERGIA
     (reduz J do alvo 2 ns) — teste no A-4a2 (lançado).
  2. O caminho físico para 1 ns com baixa corrente é TORQUE/CORRENTE:
     SOT (via dedicada, J_density alta sem passar pela MTJ) e/ou
     **ferrimagnético (H2)**: B_stt ∝ 1/M_s — no ponto de compensação o torque
     por corrente dispara. Nota: J_c0 vs M_s com Δ fixo tem mínimo em
     M_s* = √(4K_eff/μ0) ≈ 6,4e5 A/m — o CoFeB (6,0e5) JÁ está perto do ótimo
     para STT ferromagnético convencional; o ganho ferrimagnético vem da
     compensação de momento angular (dinâmica diferente, modelo 2 sub-redes
     — Spirit/Vampire validados na Fase 1 são os instrumentos certos).
  3. A-4b (varredura de espaço de designs com Δ = 59 fixo) quantifica o
     "impossível 1 ns por STT puro" — pendente.

### A-4a2 concluído (~02:35): VCMA corta ~30% de energia no 2 ns
- Mínimo: **0,44 pJ @ f_K = 0,75, J = 10 MA/cm² (P = 90%)** vs 0,63 pJ do
  A-0 v2 (f_K = 1, J = 12). E_VCMA ≈ 12 aJ — desprezível (ganho vem do J²).
- f_K = 0,25 não melhora sobre 0,75 → **saturação**: perto do limiar de torque,
  a barreira deixa de ser o fator limitante. V_b ≈ 0,5 V (β = 100, ilustrativo).
- Baseline replicado dentro do erro (97,5% vs 90% ± 4,7% binomial, 1,6σ) ✓.
- **Veredito VCMA (H1 reescrita)**: alavanca de energia moderada (−30% no 2 ns),
  não de velocidade. Pendência: fonte de β (busca 402).

### A-4d aberto: margem de leitura (~03:40, `experimento_a4d.py`)
- Problema (declarado desde o A-0): leitura por TMR com sinal pequeno —
  TMR = 150% de projeto, degradação com viés (TMR(V) = TMR_0/cosh(V/V_c),
  V_c sem fonte — pendência 402), série do seletor, C_BL, kT/C + offset de SA.
- Ataques quantificados no grid: designs {40 baseline, 30 doce, 20 rápido} ×
  TMR_0 {150, 300, 600}% × V_read {0,1–0,3} V × R_on {1, 3} kΩ ×
  C_BL {50, 500} fF × esquema {SE, PAR}.
- **PAR = H3-lite** (par diferencial, estados opostos): sinal ×2, offset comum
  cancelado; custo: 2× energia de escrita por bit (aceitável: 0,13–0,15 pJ →
  ~0,3 pJ/bit útil — ainda 2× melhor que o baseline single-ended).
- Veredito por config: ΔV > 10 mV, t_read < 5 ns, I_read ≤ I_c0/5.
- Observação já visível: nos designs vencedores I_c0 ~ 40–70 µA vs I_read
  ~ 3–14 µA → disturb não deve ser o killer; o jogo é sinal × variância.
- Pré-SPICE: a Fase 6 refina com ngspice/Xyce + Verilog-A do macrospin.


### A-4b concluído (~03:15): **1 ns É VIÁVEL — o design de 40 nm era o gargalo**
- RETRAÇÃO (da minha própria conclusão do A-4a): "1 ns é torque-limited nesta
  classe" — FALSO como afirmação geral. Vale para o design de 40 nm
  (B_keff = 0,33–0,98 T, precessão lenta). Com Δ = 59,2 FIXO e célula menor,
  K_eff sobe (2,3–7,8e5 J/m³) → B_keff = 1,7–3,9 T → f₀ ~ 40–100 GHz → a
  dinâmica acelera e o STT puro fecha 1 ns.
- **Q1 (mínimo de energia @2 ns, P ≥ 90%): 0,130 pJ** — d = 30 nm, t = 1,0 nm,
  Ms = 4e5, J = 7,2 MA/cm² (1,2×J_c0). ~5× melhor que o baseline (0,63 pJ) e
  melhor que o caminho VCMA (0,44 pJ).
- **Q2 (1 ns, P ≥ 90%): 7 designs** — destaque: **d = 30 nm, t = 1,0 nm,
  Ms = 4e5 → 1 ns a 0,15 pJ**; d = 20 nm/t = 1,0 nm → 0,28 pJ (J = 22,7 MA/cm²).
- **Tendência de material**: o ótimo corre para Ms BAIXO (4e5) — consistente
  com a H2 (ferrimagnético/low-Ms), agora por TRÊS vias: torque/corrente ↑,
  J_c0 ↓ e energia ↓.
- **Ressalva em verificação (lançada)**: δ_w ≈ 4,4–5,9 nm << d nos designs
  vencedores → reversão pode ser por NUCLEAÇÃO (não quase-coerente) → a razão
  malha/macrospin 1,07 (medida em K_eff = 1,3e5) pode mudar.
  `verifica_a4b_mumax3.py` compara malha vs macrospin nos designs de 30 e
  20 nm (12 runs, 0 K). Se a malha comutar a J ≤ macrospin → A-4b conservador.
- Ressalvas declaradas (cabeçalho do A-4b): R_A fixo (túnel de condutância em
  t = 1 nm ignorado); K_eff até 7,8e5 J/m³ exige material anisotrópico forte
  (fonte pendente — buscas 402); J = 22,7 MA/cm² no design de 20 nm pede
  verificação de breakdown/eletromigração (Fase 7).
- Leitura de conjuntura: o ganho de energia vinda de d menor + anisotropia alta
  NÃO estava no grid original do projeto (40 nm herdado do A-0) — a Fase 4 já
  pagou o próprio custo.


### A-4b lançado (~02:40): espaço de designs com Δ = 59,2 FIXO
- K_eff recalculado por design (K_eff = Δ·kT/V) → retenção garantida por
  construção em todo o grid.
- Grid: d ∈ {20, 30, 40} nm × t_FL ∈ {1,0; 1,5} nm × Ms ∈ {4, 6, 8}e5 × α = 0,01;
  J = {1,2; 1,8}×J_c0(Sun); pulso 2 ns + 1 ns; 300 K, 40 traj; 0 K a 1,8×J_c0.
- Q1: mínimo de energia no 2 ns (P ≥ 90%). Q2: algum design atinge 1 ns?
  (d menor → K_eff ↑ → B_keff ↑ → precessão acelera; mas J_c0 ↑ e R = R_A/A ↑ —
  o trade é medido, não assumido.)
- Limitações declaradas no cabeçalho: macrospin; R_A fixo; K_eff até ~5e5 J/m³
  exige material forte (fonte pendente); α fixo 0,01.

### A-4d concluído (~03:55): leitura single-ended MORTA — par diferencial (H3) é REQUISITO
- Matriz de viabilidade (ΔV > 10 mV, t < 5 ns, I_read ≤ I_c0/5):
  - **SE (referência clássica): 0/12 em praticamente tudo** — nem com TMR 600%
    (só o baseline 40 nm passa 1/12 a 600%). O "sense amplifier difícil"
    está CONFIRMADO quantitativamente.
  - **PAR (par diferencial, estados opostos): salva TODOS os designs** —
    40 nm e 20 nm vivem até com TMR 150%; 30 nm (R_P = 14,1 kΩ, I_c0 = 42,7 µA)
    fica apertado entre sinal e disturb a 150% → **quer TMR ≥ 300%**
    (CoFeB/MgO recozido: 600% demonstrado — Ikeda 2008, APL 92, 082508,
    604% RT; confirmação formal pendente 402).
- **H3 promovida de hipótese a REQUISITO de design**: leitura diferencial não
  é opcional no MHM-1 — é o que torna o array legível. Custo: 2× escrita por
  bit útil (0,13 → ~0,26 pJ/bit — ainda metade do baseline single-ended).
- O design de 20 nm lê até a 150% (ΔR absoluto maior: R_P = 31,8 kΩ) — mas com
  t_read = 2,7 ns se C_BL = 500 fF (no array grande o trade aperta; a Fase 5
  mede o C_BL real).
- Fase 6 (ngspice) refina o SA (carga-transferência) com o Verilog-A do
  macrospin; o A-4d é a análise de rede que dimensiona o problema.

### Verificação MuMax3 do A-4b (~04:10): CONFIRMADA — malha ≤ macrospin
- Design 30 nm (B_keff = 1,73 T): malha comuta a 1,58 ns vs macrospin 1,68 ns
  a 1,8×J_c0 (0 K) → razão **0,94**.
- Design 20 nm (B_keff = 3,90 T): malha 1,20 ns vs 1,24 ns (1,5×) e 0,80 ns vs
  0,85 ns (1,8×) → razões **0,97 e 0,94**.
- Em todos os pontos: malha comuta a J ≤ macrospin → **nucleação ajuda um
  pouco; os números do A-4b são CONSERVADORES, não otimistas.** O teste térmico
  (300 K, 40 traj) do macrospin segue como estimativa central; a malha térmica
  fica para a Fase 5/7 (custo 11 min/run).
- **Destaque final (última linha do console)**: design de 20 nm @ 1 ns @
  1,8×J_c0 (22,7 MA/cm²): **MALHA COMUTOU em 0,80 ns** (m_z = −0,996) —
  o 1 ns é confirmado EM MALHA, não só no macrospin. Para o design de 30 nm,
  o 1 ns depende de assistência térmica (300 K: 92,5% no macrospin; a 0 K
  malha e macrospin não fecham em 1 ns — coerente).
### Programa "atacar os pontos fracos vs mercado" (pedido do usuário, 17/11) + A-4e concluído
- Inventário dos pontos fracos vs mercado e plano: (1) leitura/SA difícil →
  F6.1 antecipada (ngspice + modelos PTM grátis, SA real); (2) breakdown/
  endurance de escrita → **A-4e (feito abaixo)**; (3) densidade → H5 avaliar/
  arquivar com justificativa; (4) velocidade de sistema → Fases 5–6;
  (5) fontes de material → buscas manuais do usuário; (6) P de escrita 90% →
  write-verify na controladora (Fase 6).

### A-4e (~05:20): o ponto fraco "endurance" era REAL — e o conserto é um prêmio duplo
- **Achado**: com R_A = 10 Ω·µm² (herdado do A-0), TODOS os designs excedem o
  breakdown pessimista na escrita: V_write = 0,93–1,92 V vs V_bd = 0,5–1,2 V
  (MgO 1 nm; E_bd ∈ {5, 8, 12} MV/cm — SEM FONTE, pendência).
- **Conserto (janela de R_A)**: R_A ∈ {1,25–2,5} Ω·µm² fecha escrita + leitura
  em todos os casos razoáveis — e como E ∝ R (I é fixo pelo torque), a energia
  CAI 4–8× junto:
  - doce30 @ R_A = 2,5: **0,035 pJ/célula (2 ns)** → 0,07 pJ/bit útil (par H3),
    leitura PAR 20,7 mV ok
  - rapido20 @ R_A = 1,25: **1 ns @ 0,018 pJ/célula** → 0,036 pJ/bit útil,
    leitura ok (20 mV)
  - baseline40 @ R_A = 2,5: 0,133 pJ (2 ns)
- **Números agora em fJ (18–35 fJ/célula)**: ~2–7× a energia de escrita de
  célula DRAM — com não-volatilidade. Atualiza as manchetes do dossiê (A-4c/d
  foram calculados em R_A = 10; a janela viável os refaz em fJ).
- Janela existe em TODOS os combos (design × TMR0 × E_bd) testados, mas afina
  no caso pessimista (E_bd = 5 MV/cm → R_A ≤ 2,5). R_A ≤ 2,5 Ω·µm² exige
  controle de fabricação — pendência de fonte +2: E_bd real do MgO e R_A
  típico de produtos comerciais (suspeita: 2–10 Ω·µm², a confirmar).
- Honestidade: endurance em ciclos NÃO é simulável aqui (fadiga = milhões de
  ciclos); o que se auditou é o estresse de tensão por escrita vs breakdown.

### A-4c concluído (~04:35): J_90 cravado — dobrar a velocidade custa ~0 energia por bit útil
- Com 60 traj/ponto (σ ~3–4% em P = 90%):
  - doce30 @ 2 ns: **J_90 = 8,0 MA/cm² → 0,158 pJ/célula** (par H3: 0,317 pJ/bit útil)
  - doce30 @ 1 ns: J_90 = 11,6 → 0,166 pJ (0,333 pJ/bit útil)
  - rapido20 @ 2 ns: J_90 = 13,5 → 0,200 pJ (0,401 pJ/bit útil)
  - rapido20 @ 1 ns: J_90 = 17,0 → 0,159 pJ (0,318 pJ/bit útil)
- **CORREÇÃO HONESTA do A-4b Q1**: o "mínimo 0,130 pJ @ 7,2 MA/cm²" ficava a
  88,3% ± 4,1 com n = 40 — ruído da amostra. Com n = 60, o J_90 honesto é
  8,0 MA/cm² → **0,158 pJ** (não 0,130). O CSV do A-4c é o número do dossiê.
- **Pareto energia × velocidade quase PLANO por bit útil**: doce30 @ 2 ns
  (0,317) ≈ rapido20 @ 1 ns (0,318). Dobrar a velocidade não custa energia —
  custa CORRENTE (8 → 17 MA/cm²; breakdown/eletromigração a verificar na Fase 7).
- Faixa final do dossiê: **0,32–0,40 pJ/bit útil** (par diferencial H3) —
  metade do baseline single-ended original (0,63 pJ/bit).
- t_sw médio em J_90 fica bem abaixo do pulso (1,54 ns @ pulso 2 ns) → há
  folga de timing; o pulso pode ser encurtado em design de controladora.

---

## Entrada 005 — 17/11/2026 — Buscas de anterioridade EXECUTADAS (Google Patents via XHR)

### Método
- websearch genérica segue bloqueada (402, retestado hoje). **Descoberta de rota**:
  o endpoint JSON do Google Patents (`https://patents.google.com/xhr/query?url=q%3D<consulta>&exp=`)
  responde via webfetch — título, titular (assignee), data de prioridade e snippet nos
  ~10 primeiros resultados, + sumários por assignee/ano.
- Consultas executadas (5): H4-bruta; VCMA+memory (consulta 2 da Seção 3 do
  `paisagem_ip.md`); janela R_A; ferrimagnética; H4-refinada.
- Nota de método: reexecução da consulta VCMA no fim da sessão retornou 503
  (rate-limit do endpoint) — os registros são das execuções bem-sucedidas do dia;
  números conferidos nos snippets. Consultas futuras: usar com moderação.

### Resultados por hipótese (detalhe; resumo em `docs/paisagem_ip.md` §0)
- **H1 — BLOQUEADA (campo denso)**: **US9646670B2** (Qualcomm, prioridade 2015)
  descreve SOT-MRAM 3T com campo elétrico reduzindo a anisotropia durante a escrita —
  a H1 em essência. Portfólio da **Inston Inc.** é inteiramente VCMA-MRAM
  ("VCMA AND memory": **1.176** resultados). Aparecem ainda US10600460B2 e JP5231528B2.
- **H2 — BLOQUEADA (campo denso)**: **US8102701B2** (Crocus, prioridade 2007) — liga
  ferrimagnética 3d-4f para célula magnética; **CN111312745B** (Samsung);
  **JP7251811B2** (Tohoku). Consulta ferrimagnética: **6.314** resultados.
- **H3 — BLOQUEADA**: **US10483457B1** (Qualcomm, prioridade 2018) — célula SOT-MRAM
  diferencial com 2 MTJs de polaridade oposta (a estrutura PAR do A-4d).
- **H4 — PARCIALMENTE VIVA**: busca refinada (`"parallel write" OR "simultaneous
  write" OR "shared write line" OR "multi-cell write"`): **18 resultados**.
  Adjacentes — nenhum cobre o pacote "escrita SOT paralela + seleção por porta VCMA":
  - **US11004490B2** (imec) — linhas compartilhadas em arranjo SOT;
  - **CN113160863A** (Antalis) — célula/arranjo SOT;
  - **CN122314039A** (青岛海存微电子, 2026) — "Storage arrays and parallel write methods".
- **Janela R_A (A-4e)**: **951** resultados sem cobrir o pacote; risco real é
  "óbvio para experimentar" (obviedade) → valor de patente provavelmente fino.

### Consequências para o projeto
1. Nenhuma das H1–H3 sustenta pedido de patente. O valor do dossiê é
   **científico/publicável** — a principal justificativa do congelo de publicação
   enfraqueceu.
2. H4 é a única com janela aparente (arquitetura de array, não física). Patente
   estreita exigiria parecer de agente de PI (custo real) e o valor dependeria de
   licenciamento — recomendação honesta: publicar; patente só se houver interessado
   comercial na H4.
3. **Decisão pendente do usuário**: manter congelo e tentar patente estreita (H4),
   ou descongelar e voltar à publicação aberta (recomendação técnica).
4. Fila técnica inalterada (independe da decisão): A-4c2 (solver 2 sub-redes, H2),
   F6.1 (ngspice/PTM), A-4f (SOT-write/H4), H5 arquivar com justificativa.





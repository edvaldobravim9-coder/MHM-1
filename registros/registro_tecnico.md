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

### Em execução neste momento (~23:40)
- Fila: reexecução do A-0 (limiar 0 K + P 300 K) com o solver corrigido;
  teste de runs térmicos no MuMax3 (Temp>0, RK45, malha 2,5 nm).

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


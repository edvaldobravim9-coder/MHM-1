# PROGRESS.md — MHM-1 (memória magnética híbrida)

## Objetivo atual
**Fase 4 — Arquiteturas** (corrente aberta): testar as hipóteses H1–H5 por simulação
e consolidar o veredito de design da célula MHM-1.

## Status geral do projeto (~40%)
- Fases 1–3 **ENCERRADAS**: ferramentas validadas (MuMax3 + solver FDT próprio,
  FDT 1,008, calibração térmica empírica), solver de macrospin validado, viabilidade
  térmica e de malha confirmadas.
- GitHub: github.com/edvaldobravim9-coder/MHM-1 (público, MIT) — push a cada marco.

## O que já foi concluído (Fase 4, até agora)
- **A-4a (VCMA × 1 ns): NEGATIVO** — gargalo do 1 ns é TORQUE, não barreira
  (B_stt ~ 0,022 T << B_keff). P(fuga térmica em 1 ns) ≈ 10⁻⁷ mesmo com f_K = 0,25.
- **A-4a2 (VCMA × 2 ns): −30% energia** — 0,44 pJ @ f_K = 0,75, J = 10 MA/cm²
  (V_b ≈ 0,5 V; E_VCMA ~ 12 aJ). VCMA = alavanca de energia, não de velocidade.
- **A-4b (espaço de designs, Δ = 59,2 fixo): 1 ns VIÁVEL por STT puro** —
  Q1 mínimo 0,130 pJ @ 2 ns (30 nm / 1,0 nm / Ms 4e5, J = 7,2 MA/cm²);
  Q2: 7 designs com P ≥ 90% @ 1 ns (ponto-doce 30 nm: 0,15 pJ).
  Ótimo corre para Ms baixo → H2 fortalecida (3 vias independentes).
- **Verificação MuMax3 do A-4b: CONFIRMADA** — malha comuta a J ≤ macrospin
  (razões 0,94–0,97 a 0 K) → números conservadores, nucleação ajuda.
- **A-4d (margem de leitura): leitura single-ended MORTA; par diferencial (H3)
  promovido a REQUISITO de design** — PAR salva todos os designs (40/20 nm vivem
  a TMR 150%; 30 nm quer TMR ≥ 300% — Ikeda 2008 demonstrou 604% RT). Custo:
  2× escrita/bit útil (~0,26 pJ — ainda metade do baseline original).

## Em andamento
- **A-4c rodando** (background, ~10–15 min): refino do bracket dos designs
  vencedores — curva P(J) fina (60 traj/ponto), J_90 e custo por bit ÚTIL
  (par diferencial H3 = 2×E) para doce30 e rapido20, nos alvos 2 ns e 1 ns.

## Próximos passos
1. A-4c: refinar bracket do ponto-doce (30 nm / 1,0 nm / 4e5, J ∈ 6,5–8 MA/cm²)
   + modelagem ferrimagnética 2 sub-redes (H2) — Spirit/Vampire (validados Fase 1).
2. H4 (escrita paralela SOT + seleção VCMA) e H5 (3D): avaliar ou arquivar com justificativa.
3. Fase 5 (matriz 16×16, C_BL real) e Fase 6 (controladora, ngspice, Verilog-A) em seguida.
4. Registro de novidade: buscas de patente (docs/paisagem_ip.md Seção 3) — pendem
   porque websearch está bloqueada (HTTP 402, retestado hoje). Consulta manual pelo
   usuário em patents.google.com é a alternativa (instruções dadas).

## Pendências de fonte (bloqueadas pela busca web 402)
- β do VCMA (faixa relatada ~20–300 fJ/(V·m)) — mapeamento V_b marcado como ILUSTRATIVO.
- TMR_0 = 300–600% (Ikeda 2008, APL 92, 082508: 604% RT) — confirmar.
- V_c do TMR(V) (~0,5 V típico, sem fonte).
- K_eff = 5–8e5 J/m³: material anisotrópico forte que sustente o valor.

## Arquivos principais (Fase 4)
- `exp_A4_arquiteturas/experimento_a4a.py`, `experimento_a4a2.py`, `experimento_a4b.py`,
  `experimento_a4d.py`, `consulta_a4d.py`, `verifica_a4b_mumax3.py` + pastas
  `resultados_a4*/` e consoles .txt.
- `exp_A0_macrospin/llgs_macrospin.py` (solver: RK45 adaptativo, anisotropia uniaxial
  real, `k_mult`/`k_mult_pulse` para VCMA), `parametros.py`.
- `registros/registro_tecnico.md` — Entrada 004 (Fase 4 completa, com retratações).
- `docs/paisagem_ip.md` — Seção 3 (consultas prontas), Seção 4 (H1–H5).

## Restrições do projeto
- Sem laboratório; só ferramentas gratuitas; rigor científico (nada fictício,
  retratações explícitas, fontes ou pendências declaradas).
- Tudo versionado no GitHub (binários MuMax3 via Git LFS).
- Exclusões de repos/arquivos só com aprovação explícita do usuário.

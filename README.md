# MHM-1 — Magnetic Hybrid Memory

Projeto de pesquisa para desenvolvimento de uma arquitetura física de memória magnética
híbrida (SOT/STT-MRAM + VCMA + materiais ferrimagnéticos), começando **sem laboratório físico**
e usando exclusivamente simulação computacional gratuita.

## Regras de rigor do projeto

1. Nenhum resultado apresentado como descoberta sem simulação/documentação real associada.
2. Parâmetros de materiais sempre com fonte (artigo, manual ou banco de dados). Lacunas são
   declaradas explicitamente.
3. Metas (1–2 ns de comutação, < 1 pJ/bit, Δ ≥ 42 para 10 anos, 10¹² ciclos) são **objetivos de
   pesquisa**, nunca resultados.
4. Sempre distinguir: **tempo de comutação da célula** (física, ~ns) ≠ **latência de acesso do
   dispositivo completo** (célula + seleção + sense amplifier + controlador, dezenas de ns).
5. Simulação micromagnética ≠ simulação de arquitetura. Cada nível responde a perguntas diferentes.

## Fases

| Fase | Descrição | Status |
|------|-----------|--------|
| 1 | Pesquisa científica e seleção de ferramentas | **CONCLUÍDA** (16/11: Vampire 7, Xyce 7.10, Spirit→spirit-code, Fidimag→computationalmodelling revalidados; SunTzu indisponível publicamente → Verilog-A próprio na Fase 6; ferramentas validadas na prática na Fases 2–3) |
| 2 | Modelagem matemática e física | **CONCLUÍDA** (solver macrospin validado: FDT 0,994 e 1,008 a dt=0,25 ps; anisotropia uniaxial corrigida; calibração térmica empírica taxa(Δ) com incerteza declarada — desvio vs Brown é física de Δ baixo, confirmado por convergência dt) |
| 3 | Simulação de células magnéticas | **CONCLUÍDA** (A-1a: B_sw = 0,75 T @ 10 ns; A-1b + refino: J_sw malha ≈ 1,07× macrospin — reversão quase-coerente; A-0 v2: 2 ns ✓ 90% @ 12 MA/cm² 0,63 pJ, 1 ns ✗; térmico MuMax3 viável: 11 min/run, FDT por célula aprovado; retenção Δ = 59 robusta ~25 anos) |
| 4 | Comparação de materiais e arquiteturas | Pendente (pré-requisito: consultas de patentes do `docs/paisagem_ip.md` — websearch bloqueado; alternativa: consulta manual) |
| 5 | Matriz magnética 16×16 | Pendente |
| 6 | Controladora e arquitetura de memória | Pendente (Ramulator 2 / ngspice / Xyce) |
| 7 | Validação dos resultados | Pendente |
| 8 | Planejamento de protótipo físico | Pendente |

Não avançamos de fase sem avaliar os resultados da anterior.

## Estrutura

```
MHM-1/
├── README.md                  <- este arquivo
├── docs/
│   ├── fase1_ferramentas.md   <- levantamento de ferramentas (verificado em 16/11/2026)
│   └── paisagem_ip.md         <- patentes, artigos e hipóteses de inovação
├── exp_A0_macrospin/          <- Experimento A-0: célula MTJ (macrospin LLGS, Python)
│   ├── parametros.py          <- parâmetros de material com fontes
│   ├── llgs_macrospin.py      <- solver LLGS (RK4, torque STT, campo térmico)
│   ├── experimento_a0.py      <- roteiro do experimento (gera CSVs e figuras)
│   ├── resultados/            <- saídas (CSV/PNG) — gerados pela execução
│   └── README.md              <- objetivo, passo a passo, interpretação
├── exp_A1_mumax3/             <- (FASE 3) micromagnetismo na GPU (MuMax 3.12)
│   ├── README.md              <- calibração da malha + lições de execução
│   ├── smoke_test_v2.mx3      <- teste de fumaça (PASS em 16/11/2026)
│   ├── diagnostico_{a..e}.mx3 <- saga de depuração (evidência)
│   ├── experimento_a1a.py     <- A-1a: varredura de campo (B_sw)
│   ├── experimento_a1b.py     <- A-1b: varredura STT (mapeamento exato A-0↔MuMax3)
│   └── mtj_camada_livre.mx3   <- template antigo (atualizar antes de usar)
├── exp_A2_termico/            <- A-2: calibração do campo térmico do solver A-0
│   └── experimento_a2.py      <- extração de Δ por fuga espontânea (300 K)
├── tools/                     <- MuMax 3.12 (mumax3.exe etc., Windows CUDA 12.6)
├── ferramentas/               <- scripts de limpeza/relatório de disco
└── registros/
    ├── registro_tecnico.md    <- diário de bordo oficial do projeto
    └── limpeza_admin.log      <- log da limpeza administrativa (16/11/2026)
```

## Como executar o Experimento A-0 (computador local)

Requisitos: Python 3.10+, numpy, matplotlib (`pip install numpy matplotlib`).

```
cd C:\Users\edval\Desktop\MHM-1\exp_A0_macrospin
python experimento_a0.py
```

Saídas em `exp_A0_macrospin/resultados/` (CSV + PNG) e resumo no console.
Tempo de execução estimado: 1–3 min no i3-10105F.

## Como executar os experimentos A-1 (MuMax3, GPU)

Requisitos: MuMax 3.12 (já instalado em `tools\`) e GPU NVIDIA CC ≥ 5,0.

```
cd C:\Users\edval\Desktop\MHM-1\exp_A1_mumax3
..\tools\mumax3.exe smoke_test_v2.mx3     :: teste de fumaça (~1 min)
python experimento_a1a.py                 :: varredura de campo (13 runs, ~10 min)
python experimento_a1b.py                 :: varredura STT (8 runs, ~10 min)
```

**Importante**: respeitar o limite de estabilidade do passo de tempo da malha
(`SetSolver(2)` + `FixDt = 1e-13` para células de 2,5 nm) e terminar scripts
com `tablesave()` — detalhes e justificativas em `exp_A1_mumax3/README.md`.

## Computador disponível

- Intel i3-10105F (4C/8T), 8 GB RAM, NVIDIA GT 1030 2 GB (**CUDA compute capability 6.1 →
  compatível com MuMax 3.12**, que exige CC ≥ 5.0), SSD 256 GB, Windows.
- Alternativas em nuvem gratuitas: Binder (Ubermag), nanoHUB (OOMMF no navegador),
  Google Colab (GPU T4 grátis, com limites de sessão).

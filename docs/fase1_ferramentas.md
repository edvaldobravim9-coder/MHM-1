# FASE 1 — Levantamento de ferramentas de simulação (MHM-1)

Data da verificação: **16/11/2026**. Sites oficiais acessados diretamente nesta data
(links marcados com ✔ foram abertos e conferidos hoje; itens marcados com ⚠ não puderam
ser re-verificados hoje porque a busca web esteja indisponível — verificar na próxima sessão).

## 0. REVALIDAÇÃO FINAL — 16/11/2026, noite (FASE 1 ENCERRADA)

- **websearch segue bloqueado** (HTTP 402) — revalidação feita por webfetch/GitHub API:
  - ✔ **Vampire 7** — https://vampire.york.ac.uk — ativo, open source; V7 com GPU beta,
    STT/SOT, dinâmica spin + Monte Carlo.
  - ✔ **Xyce 7.10** — https://xyce.sandia.gov — ativo, GPL, release 7.10 publicada.
  - ✔ **Spirit** — moveu-se: o antigo site spirit.tuwien.ac.at está morto; projeto vivo em
    https://github.com/spirit-code/spirit (MIT, push 02/11/2026; homepage spirit-code.github.io).
  - ✔ **Fidimag** — moveu-se: agora em https://github.com/computationalmodelling/fidimag
    (push 10/11/2026; 71 stars; licença "Other" — conferir antes de redistribuir).
  - ⚠ **SunTzu (CEA-Leti)** — NÃO localizado em repositório público (busca GitHub vazia);
    modelo distribuído sob registro pelo CEA-Leti. **Decisão**: não é bloqueio — na FASE 6
    escreveremos Verilog-A próprio do nosso macrospin já validado (mais transparente e
    sem dependência de registro).
- **Ferramentas selecionadas e VALIDADAS NA PRÁTICA** (mais forte que levantamento de
  papel): solver macrospin próprio (A-0 v2, FDT 0,994), MuMax 3.12 (GT 1030, 4
  experimentos executados), Python/NumPy/matplotlib, Ramulator 2.1 reservado à FASE 6.
- Consultas de patentes (paisagem IP) **reclassificadas** como pré-requisito da FASE 4
  (comparação de arquiteturas) — pertencem à análise de novidade, não à seleção de
  ferramentas. Ficam pendentes até a busca web voltar (ou consulta manual pelo usuário).

## 1. Classificação importante (nível de simulação)

| Nível | O que responde | Ferramentas |
|---|---|---|
| **Físico — micromagnético** (LLG contínuo, células finitas) | Dinâmica de magnetização, nucleação de domínios, efeitos de borda, SOT/STT espaciais | OOMMF, MuMax3, Ubermag, Fidimag |
| **Físico — atomístico** (estidos/sub-redes) | Ferrimagnéticos (GdFeCo), troca atômica, temp. ultra-rápidas | Spirit, Vampire |
| **Físico — macrospin / compacto** (equação de momento único) | Comutação de uma MTJ, probabilidade térmica, energia por pulso — rápido, ideal para varreduras de projeto | Nosso solver Python (A-0), modelos Verilog-A tipo SunTzu |
| **Elétrico — circuito** (SPICE) | Sense amplifier, linhas de bit/palavra, temporização elétrica, consumo da interface | ngspice, Xyce (Verilog-A) |
| **Arquitetura** (ciclo de clock) | Latência de matriz, bancos, canais, filas, controlador — **NÃO simula física magnética** | Ramulator 2.1, gem5 |

**Erro comum que evitaremos:** tratar uma simulação de DRAM/MRAM em Ramulator como se fosse
simulação física de comutação magnética. São níveis distintos e complementares.

## 2. Ferramentas principais (verificadas 16/11/2026)

### 2.1 Ubermag — ✔ https://ubermag.github.io
- **Gratuita:** sim (BSD-3-Clause).
- **Navegador:** sim — Binder oficial ("Try it in your browser"): https://mybinder.org/v2/gh/ubermag/tutorials/latest?urlpath=lab/tree/demo.ipynb
- **Instalação local:** opcional (`conda install -c conda-forge ubermag` ou pip; precisa do backend OOMMF e/ou mumax3).
- **CPU/GPU:** depende do backend — `oommfc` usa CPU; `mumax3c` usa GPU NVIDIA (CUDA).
- **Fenômenos:** equação de Landau-Lifshitz-Gilbert completa: troca, magnetostática, anisotropia, DMI, Zeeman, agitação térmica (Brown), torque STT (via backend), interface Jupyter para análise.
- **Não simula diretamente:** transporte de tunelamento pela barreira (I–V da MTJ), circuitos, arquitetura. VCMA via parâmetros dependentes de tempo/tensão (implementável, não nativo).
- **Uso no MHM-1:** ambiente principal das FASES 3–4 (Experimentos A/B/C). O backend mumax3c dá velocidade de GPU na GT 1030; o Binder serve para rodar sem instalar nada.

### 2.2 MuMax3 (v3.12) — ✔ https://mumax.github.io
- **Gratuita:** sim (GPLv3, código aberto).
- **Navegador:** não (binário Windows/Linux; tem GUI web local para acompanhar a simulação).
- **Instalação:** binário pronto para Windows; linha de comando.
- **CPU/GPU:** **exige GPU NVIDIA com compute capability ≥ 5.0**.
  - **Nosso hardware: GT 1030 = CC 6.1 ✔ COMPATÍVEL.** Documentação oficial: ~16 milhões de células de diferenças finitas com 2 GB de VRAM — folga para células MTJ individuais e matrizes pequenas.
- **Fenômenos:** LLG, magnetostática, troca, DMI, anisotropia uniaxial/cúbica, térmico (Brown), **torque STT (Slonczewski e Zhang-Li)**, tesselação de Voronoi, parâmetros dependentes de tempo/espaço (permite emular VCMA variando anisotropia com a tensão de porta).
- **Não simula diretamente:** transporte quântico pela barreira, multi-camadas completas tipo pilha MTJ real (prática padrão: simular a camada livre com termos efetivos), circuitos.
- **Uso no MHM-1:** FASE 3 — validar macrospin vs micromagnético (nucleação de domínios), efeito de borda, SOT em geometria real. Template já criado: `exp_A1_mumax3/mtj_camada_livre.mx3` (ainda não executado).

### 2.3 OOMMF 2.1 — ✔ https://math.nist.gov/oommf/
- **Gratuita:** sim (domínio público, NIST).
- **Navegador:** **sim, via nanoHUB** — link oficial na página do NIST: https://nanohub.org/tools/oommf/
- **Instalação local:** precisa de Java (JDK) + Tcl/Tk; instalador Windows disponível.
- **CPU:** sim (paraleliza em CPU; sem GPU).
- **Fenômenos:** LLG completo, térmico, STT (extensões Oxs), padrão de referência da comunidade micromagnética (problemas μMAG de validação).
- **Não simula diretamente:** idem MuMax3.
- **Uso no MHM-1:** referência de validação cruzada do MuMax3 (FASE 3) e alternativa quando a GPU estiver ocupada/indisponível.

### 2.4 Ramulator 2.1 — ✔ https://github.com/CMU-SAFARI/ramulator2
- **Gratuita:** sim (MIT).
- **Navegador:** não (C++20 + CMake; bindings Python; recomendo container/Docker ou Codespaces).
- **CPU:** sim.
- **O que é:** simulador **arquitetural** ciclo-a-ciclo de DRAM/controladores: DDR3/4/5, LPDDR5/6, GDDR6/7, HBM1–4, com modelos de energia (pJ/bit via plugin Ayna) e integração com gem5.
- **NÃO simula:** física magnética de célula alguma. É a ferramenta da **FASE 6**, onde estenderemos a interface (`spec` customizável) para modelar uma "canal de memória MHM-1" com temporizações derivadas dos nossos experimentos físicos.
- **Uso no MHM-1:** Experimento E — latência de matriz, bancos paralelos, comparação com DRAM real.

### 2.5 ngspice — ✔ (ferramenta padrão; site https://ngspice.sourceforge.io)
- **Gratuita:** sim (código aberto).
- **Navegador:** não; binários Windows disponíveis.
- **CPU:** sim.
- **Fenômenos:** circuitos não lineares transitoriamente. Não tem modelo de MTJ nativo — mas aceita fontes comportamentais (B-source) para representar R(P/AP) com comutação controlada; para modelos compactos Verilog-A de MTJ, o caminho é o **Xyce** (Sandia, gratuito, suporta Verilog-A) — link a revalidar na próxima sessão (⚠).
- **Uso no MHM-1:** FASES 5–6 — elétrica da matriz (seleção, sense, consumo) usando o modelo compacto que estivermos calibrando.

## 3. Ferramentas complementares (⚠ re-verificar links na próxima sessão)

| Ferramenta | Tipo | Por que interessa ao MHM-1 | Status |
|---|---|---|---|
| **Spirit** (spirit-code.github.io) | Atomístico LLG, C++/Python, GUI web | Duas sub-redes → **ferrimagnéticos (GdFeCo)**; demo no navegador | ⚠ verificar |
| **Vampire** (Univ. of York) | Atomístico, MPI | Ferrimagnetos, dinâmica térmica ultrarrápida | ⚠ verificar |
| **Fidimag** (github.com/computational-physics/fidimag) | Micromagnético+atomístico, Python | Alternativa em Python puro (CPU) | ⚠ verificar |
| **nanoHUB** (nanohub.org) | Nuvem gratuita | OOMMF e outras ferramentas de spintrônica no navegador | ✔ (link no site do OOMMF) |
| **Google Colab** (gratuito, GPU T4) | Nuvem | Rodar Ubermag/mumax3 sem usar nosso PC; limites de sessão; instalar mumax3 exige passo extra | ⚠ testar |
| **Modelo compacto SunTzu / CEA-Leti MTJ (Verilog-A)** | Compacto de MTJ | Integração SPICE na FASE 6 | ⚠ verificar licença/link |

## 4. Compatibilidade com o computador (i3-10105F, 8 GB, GT 1030 2 GB)

| Ferramenta | Roda localmente? | Observação |
|---|---|---|
| Solver Python A-0 (macrospin) | ✔ | Leve; já executado neste PC |
| Ubermag + OOMMF (CPU) | ✔ | 8 GB RAM suficiente para células MTJ pequenas |
| MuMax3 (GPU) | ✔ **compatível em princípio** (CC 6.1, 2 GB) | Validar instalação real na FASE 3; grids ≤ ~10⁶ células confortáveis |
| Ramulator 2.1 | ✔ (via WSL2/Docker recomendado) | FASE 6 |
| ngspice | ✔ | trivial |
| Binder/nanoHUB/Colab | ✔ (nuvem) | quando quiser poupar o PC local |

## 5. Stack escolhida para o MHM-1

1. **A-0 (agora):** nosso solver macrospin LLGS em Python/NumPy — rápido, transparente, controlável, roda no PC local. Serve de referência interna calibrável.
2. **A-1+ (FASE 3):** MuMax3 na GT 1030 (micromagnético, valida ou refuta o macrospin) + Ubermag/OOMMF como referência e para casos CPU.
3. **Ferrimagnetos (FASE 4):** Spirit (atomístico, duas sub-redes) — alternativa a validar.
4. **Matriz elétrica (FASES 5–6):** ngspice (e Xyce/Verilog-A se confirmado) + modelo compacto MTJ calibrado pelo A-0/A-1.
5. **Arquitetura (FASE 6):** Ramulator 2.1 com interface customizada do "canal MHM-1".

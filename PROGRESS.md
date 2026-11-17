# PROGRESS.md — MHM-1 (memória magnética híbrida)

## Objetivo atual
**Fase 4 — Arquiteturas** (corrente aberta): testar as hipóteses H1–H5 por simulação
e consolidar o veredito de design da célula MHM-1.
**Foco do autor (17/11): APLICAÇÃO DE JOGO primeiro, sem deixar trabalho/tarefas
pesadas de fora.** Consequência honesta: o que a física entrega de sobra (escrita
1–2 ns, persistência, fJ) serve o jogo via console/handheld ligar-na-hora, save/
resume instantâneo e bateria — NÃO serve banda de VRAM (território GDDR/HBM, fora
do escopo). O gargalo do lado jogo é LEITURA em rajada → F6.1 e Fase 5 (Perfil-B)
são o ataque.

## Status geral do projeto (~40–45%)
- Fases 1–3 **ENCERRADAS**: ferramentas validadas (MuMax3 + solver FDT próprio,
  FDT 1,008, calibração térmica empírica), solver de macrospin validado, viabilidade
  térmica e de malha confirmadas.
- **Buscas de anterioridade EXECUTADAS** (17/11, Google Patents via XHR): H1–H3
  bloqueadas por prior art denso; **H4 parcialmente viva** (18 resultados, adjacentes
  apenas). Veredito em `docs/paisagem_ip.md` §0.
- GitHub: github.com/edvaldobravim9-coder/MHM-1 (público, MIT) — **push suspenso
  (congelo)**; commits locais a cada marco.

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
- **CONGELO DE PUBLICAÇÃO ENCERRADO** (decisão do usuário, 17/11/2026): com as buscas
  de anterioridade executadas (H1–H3 bloqueadas por prior art denso; só H4 parcialmente
  viva, de valor fino), decidiu-se voltar à ciência aberta. Todos os commits pendentes
  enviados ao GitHub (`2779198..0e7f062`).
- **A-4c2 em execução** (solver LLGS de 2 sub-redes — H2 ferrimagnético): smoke PASSOU
  (V1 regressão EXATA vs A-0: 4,44 ns; V2 par AF estável, Δ = 59,2). Ponto de fumaça
  revelou física importante: com STT só na sub-rede TM, o limiar NÃO colapsa com r
  (Ms_net cancela: J_c ≈ 5,3 MA/cm² a 0 K, ~12% melhor que o ferro) — o colapso de
  corrente perto da compensação só aparece com torque no momento total (modo "ambos",
  caso SOT). Campanha completa (V0/V3/V4, ~60 traj/J, batch de J) rodando em background,
  ~40–60 min.
- **A-4c concluído (LOCAL)**: J_90 cravado — doce30 @ 2 ns: 8,0 MA/cm²;
  rapido20 @ 1 ns: 17,0. Pareto energia × velocidade quase PLANO por bit útil.
- **A-4e concluído (LOCAL)**: janela de R_A fecha breakdown + leitura com
  energia em fJ (18–35 fJ/célula): doce30 @ R_A 2,5 → 0,035 pJ (2 ns);
  rapido20 @ R_A 1,25 → 1 ns @ 0,018 pJ. O ponto fraco endurance era a escolha
  conservadora de R_A = 10 do A-0.
- **Programa de ataque aos pontos fracos** (pedido do usuário): F6.1 (SA real
  em ngspice + PTM grátis) e A-4f (SOT-write, H4) na fila; H5 avaliar/arquivar.

## Próximos passos
1. A-4c2: solver LLGS de 2 sub-redes (H2 ferrimagnético) — campanha em background
   (ver Em andamento).
2. **F6.1 (PRIORIDADE SUBIU — foco do autor é JOGO, com trabalho incluído)**:
   SA real em ngspice + modelos PTM grátis — a leitura em rajada é o gargalo do
   lado jogo.
3. **Fase 5 desenhar Perfil-B primeiro** (bancos paralelos; H4 = escrita em rajada),
   Perfil-P como fallback de valor garantido (trabalho/infra).
4. A-4f: célula SOT-write (H4) — escrita paralela = banda de escrita para jogo.
5. H5 (3D): arquivar com justificativa (recomendação registrada no paisagem_ip.md §4).
6. Fase 6 (controladora, Ramulator2): comparar os dois perfis como sistema.

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
- `registros/registro_tecnico.md` — Entradas 004 (Fase 4, com retratações) e
  005 (buscas de anterioridade).
- `docs/paisagem_ip.md` — veredito de anterioridade com patentes verificadas (§0).

## Restrições do projeto
- Sem laboratório; só ferramentas gratuitas; rigor científico (nada fictício,
  retratações explícitas, fontes ou pendências declaradas).
- Tudo versionado no GitHub (binários MuMax3 via Git LFS).
- Exclusões de repos/arquivos só com aprovação explícita do usuário.

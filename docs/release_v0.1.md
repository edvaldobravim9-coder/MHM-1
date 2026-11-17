# Notas da release v0.1 (copiar para o GitHub)

**Título:** v0.1 — Fases 1–3 concluídas · Fase 4 em andamento

---

## O que é o MHM-1

Projeto de pesquisa de uma arquitetura de memória magnética híbrida (STT/SOT-MRAM +
VCMA + materiais ferrimagnéticos), desenvolvida 100% por simulação computacional
gratuita (sem laboratório): solver LLGS de macrospin próprio (Python/numpy), MuMax
3.12 na GPU local, e elétrica de array/controladora planejada com ngspice +
Ramulator 2. Foco de aplicação: **jogos** (console/handheld que liga na hora, save/
resume instantâneo, energia de fJ) **sem deixar trabalho pesado de fora**
(persistência para infraestrutura).

## Nesta versão

- **Fases 1–3 concluídas** (~37,5% do projeto): ferramentas validadas na prática;
  solver macrospin com anisotropia uniaxial real e campo térmico (FDT verificada a
  1,008 vs Boltzmann); calibração térmica empírica taxa(Δ); malha MuMax3 calibrada
  (Δ = 59,1 vs 59,2 do macrospin — desvio 0,2%).
- **Célula base (A-0 v2)**: 40 nm, Δ = 59,2 (retenção ~25 anos); 2 ns @ 12 MA/cm² =
  90% a 300 K com 0,63 pJ; 1 ns inalcançável nesse design (motiva a Fase 4).
- **Fase 4 (~80%)**:
  - A-4b/A-4c: **1 ns viável por STT puro** em designs de 20–30 nm com Δ fixo
    (verificado em malha MuMax3: 0,80 ns no design de 20 nm); J_90 cravado com
    60 traj/ponto; Pareto energia × velocidade quase plano por bit útil.
  - A-4d: leitura single-ended inviável nas margens realistas → **par diferencial
    promovido a requisito de design** (quer TMR ≥ 300%; 604% demonstrado em lab).
  - A-4e: janela de R_A (1,25–2,5 Ω·µm²) conserta o estresse de breakdown e leva a
    energia de escrita a **18–35 fJ/célula**.
  - **Veredito de anterioridade** (buscas no Google Patents): H1–H3 bloqueadas por
    prior art denso; **H4 (escrita paralela SOT + seleção VCMA) parcialmente viva**.
    Documentado em `docs/paisagem_ip.md`.
  - A-4c2 (solver de 2 sub-redes para H2 ferrimagnética): em execução.
- **Publicação**: ciência aberta (decisão de descongelamento de 17/11/2026).

## Próximos passos (v0.2)

1. Fecho da H2 (A-4c2) e do veredito de design da célula.
2. F6.1: sense amplifier real em ngspice + modelos PTM (leitura em rajada —
   gargalo do lado jogo).
3. Fase 5: matriz 16×16, Perfil-B (banda/jogos) primeiro, Perfil-P
   (persistência/trabalho) como fallback.

## Aviso de escopo

Simulações de célula (macrospin + verificação de malha); sem array fabricado, sem
endurance medido, sem parecer legal de FTO. Metas de pesquisa, não resultados de
produto.

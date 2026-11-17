# MHM-1 — Progresso

## Objetivo atual
Fechar a Fase 3 (simulação da célula magnética) e consolidar o repositório público.

## Concluído
- **GitHub publicado**: github.com/edvaldobravim9-coder/MHM-1 (público, MIT).
  Push completo — código, resultados, diários, docs (336 arquivos) + ferramentas
  MuMax3/DLLs CUDA (618 MB via Git LFS). Commits d4031ff / ed90209 / 313d034.
  Conta limpa: 4 repos antigos excluídos pelo usuário (backup mirror local em
  `C:\Users\edval\Desktop\github_backup_2026-11-17\`).
- **Fase 1 ENCERRADA (23:45)** — ferramentas revalidadas (Vampire 7, Xyce 7.10,
  Spirit → spirit-code, Fidimag → computationalmodelling; SunTzu não público →
  Verilog-A próprio na Fase 6). Detalhes: `docs/fase1_ferramentas.md` §0.
- **Fase 2 (~90%)** — solver macrospin corrigido (anisotropia uniaxial real,
  RK45): FDT 0,994.
- **A-0 v2** — limiar 0 K 5 ns: comuta a 8 MA/cm² (4,44 ns), não a 6;
  300 K: 2 ns @ 12 = 90% (0,63 pJ); 1 ns 0% até 12; retenção 0 flips; Δ = 59,2.
- **A-1a** — B_sw = 0,75 T (10 ns, 0 K); validação damping-limited (prev. 0,70–0,71).
- **A-1b + refino** — J_sw malha ∈ (7,0–7,5]; macrospin ∈ (6,5–7,0] → razão ≈ 1,07;
  reversão quase-coerente (δ_w ≈ 10,6 nm); macrospin validado p/ varreduras (Fase 4+).
- **A-2 v3** — calibração térmica macrospin: inclinação MFP ≈ −0,85, f₀ ≈ 3,2e8 Hz;
  retenção Δ = 59 robusta (~25 anos mesmo com inclinação −0,65).
- **Viabilidade térmica MuMax3** — T1 (ruído puro): 0 flips, m_z mín +0,925 ✓;
  T2 (assistência, 6,5 MA/cm²): 2/2 comutaram (coerente c/ A-0 300 K);
  **wall ≈ 11 min / run de 5 ns → 100 runs = 1 noite local (não precisa Colab)**.

## Em andamento
- `diag_dt_convergencia` (CPU): desvio do A-2 é física de Δ baixo ou artefato de dt.
- `diag_equipart_1celula` (GPU): equipartição por célula do MuMax3 (0,107 na malha
  vs fórmula macrospin 0,0085 — referência errada p/ malha; discriminador 2×2×2,
  Aex = 0, demag off decide se FDT por célula está correto).

## Próximos passos
1. Fechar os 2 diagnósticos → encerrar Fase 3 (percentual ~35–38%).
2. Se dt for artefato → relançar A-2 a dt = 0,25 ps (overnight).
3. Nota GPLv3 do MuMax3 no README do repo (ferramentas versionadas).
4. Fase 4: consultas de patentes (websearch bloqueado 402; alternativa manual)
   + varreduras de arquitetura com macrospin validado.

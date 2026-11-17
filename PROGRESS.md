# MHM-1 — Progresso

## Objetivo atual
Fechar a Fase 3 (simulação da célula magnética) e publicar o projeto no GitHub.

## Concluído
- **Fase 1 ENCERRADA (23:45)** — ferramentas revalidadas por webfetch/GitHub API:
  Vampire 7 ✔, Xyce 7.10 ✔, Spirit → `spirit-code/spirit` (MIT) ✔, Fidimag →
  `computationalmodelling/fidimag` ✔, SunTzu ⚠ não público (Fase 6 usará
  Verilog-A próprio). Detalhes: `docs/fase1_ferramentas.md` §0.
- **Fase 2 (~90%)** — solver macrospin corrigido (anisotropia uniaxial real,
  RK45 adaptativo): `exp_A0_macrospin/llgs_macrospin.py`.
- **A-0 v2** — limiar 0 K 5 ns: comuta a 8 MA/cm² (4,44 ns), não a 6;
  300 K: 2 ns @ 12 MA/cm² = 90% (0,63 pJ); 1 ns 0% até 12; retenção 0 flips;
  Δ = 59,2. v1 (campo constante) preservado em `resultados/v1_campo_constante/`.
- **A-1a** — B_sw = 0,75 T (10 ns, 0 K); validação damping-limited (previsto 0,70–0,71).
- **A-1b + refino** — J_sw malha ∈ (7,0–7,5]; macrospin v2 ∈ (6,5–7,0] → razão ≈ 1,07.
  Reversão quase-coerente (δ_w ≈ 10,6 nm → parede ~33 nm mal cabe na célula de 35 nm).
  Macrospin validado para varreduras de arquitetura (Fase 4+). Retração do "0,82" registrada.
- **A-2 v3** — calibração térmica: inclinação MFP ≈ −0,85, f₀ ≈ 3,2e8 Hz
  (Brown assintótico degrada em Δ = 3,7–8,3); retenção Δ = 59 robusta (~25 anos
  mesmo com inclinação −0,65). Afirmações quantitativas térmicas usam calibração
  empírica, não extrapolação de Brown.
- **API MuMax 3.12** — semente térmica é `ThermSeed(n)` (não existe `RNGSEED`).
- Checagens GitHub: 642 MB total (tools\ = 639 MB); grep de segredos limpo.

## Em andamento
- `diag_dt_convergencia.py` (CPU, ~00:00) — separa física de Δ baixo vs artefato
  de dt no desvio do A-2.
- `termico_viabilidade.py` (GPU) — runs térmicos no MuMax3 (wall-clock +
  equipartição); última peça física da Fase 3.
- **Upload GitHub** — git pronto; falta: repo na conta do usuário (login único
  via navegador) + decisão público/privado e licença.

## Próximos passos
1. Concluir upload GitHub (repo, push — login único do usuário).
2. Fechar Entrada 003 e READMEs com os resultados dos jobs da madrugada;
   atualizar percentual (~35–38% pós-Fase 3).
3. Se o teste de dt indicar artefato → relançar A-2 com dt = 0,25 ps (overnight).
4. Fase 4 destrava com consultas de patentes (`docs/paisagem_ip.md` — websearch
   bloqueado HTTP 402; alternativa: consulta manual) + varreduras de arquitetura
   com macrospin validado.

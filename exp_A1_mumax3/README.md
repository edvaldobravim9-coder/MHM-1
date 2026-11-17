# Experimento A-1 — MuMax3 (micromagnetismo 2D/3D na GPU)

Validar em malha real (nucleação, bordas, demagnetização completa) o que o
A-0 assumiu como macrospin. Plataforma: MuMax 3.12 na GT 1030 (cc 6.1, PTX).

## Estado

| Item | Status |
|---|---|
| Instalação + GPU | ✔ MuMax 3.12, GT 1030 detectada (2047 MB, CUDA 12.7) |
| Smoke test v2 (malha calibrada) | ✔ PASS — ver abaixo |
| A-1a: varredura de campo (B_sw) | **CONCLUÍDO** — B_sw(10 ns) = 0,75 T; dinâmica validada (ver seção abaixo) |
| A-1b: varredura STT (J_c vs A-0) | **CONCLUÍDO** — J_sw(5 ns, 0 K) = 8 MA/cm² (razão 0,82 vs A-0; ver seção abaixo) |

## Malha calibrada (2026-11-16, smoke_test_v2.mx3)

- Amostra 35×35×1,5 nm em células de 2,5 nm (14×14×1) — mesma área do
  círculo de 40 nm do A-0 (V = 1,8375e-24 m³).
- Ku1 = 335 kJ/m³ → medido em relax (B=0): Edens_demag = 201 901 J/m³,
  **N_z = 0,8925, K_eff = 133,1 kJ/m³, B_keff = 0,4437 T, Δ = 59,1**
  (alvo do A-0: K_eff = 130 kJ/m³, Δ = 59,2 — desvio 0,2%).
- Materiais: Ms = 600 kA/m, Aex = 15 pJ/m, α = 0,01, Temp = 300 K.

## Lições de execução (não repetir)

1. **Passo de tempo × rigidez de troca**: com célula de 1 nm, o campo de troca
   do modo de Nyquist é ~200–500 T → dt estável 20–60 fs. Fixar dt maior
   (ex.: 1 ps) explode a energia de troca (células antiparalelas, E ~ 6,5e7 J/m³)
   e prende m_z no equador. Com célula de 2,5 nm o limite é ~145 fs.
   *(Atualização, lição 5: o par Heun+FixDt foi ABANDONADO nos runs determinísticos.)*
2. **O solver adaptativo padrão não estava "travado"** — encolhia o passo
   corretamente para a rigidez da malha. Malha grosseira > matar o solver.
3. **`tablesave()` ao final é obrigatório** — o buffer da tabela não descarrega
   na saída limpa do processo.
4. Série temporal: `TableAutoSave(δt)`; colunas custom: `mz := m.Comp(2)` +
   `tableadd(mz)` (`mz`/`E`/`Edens_exchange` não são globais; usar `Edens_total`,
   `Edens_exch`, etc.).
5. **Heun explícito + FixDt é incondicionalmente instável em precessão pura** —
   |1 + iθ + (iθ)²/2| = √(1 + θ⁴/4) > 1 para todo θ > 0: bombeia energia no modo
   de xadrez. A varredura A-1a v1 (Heun+FixDt=1e-13) foi contaminada; números
   RETRAÍDOS (artefatos em `v1_heun_contaminado/`). Runs determinísticos usam o
   RK45 ADAPTATIVO padrão (validação: `verif_rk45.mx3`).

## Resultado A-1a (16/11/2026, `resultados_a1a/`)

- Pulso 10 ns, Temp=0, RK45 padrão, 11 campos 0,50–1,00 T:
  **B_sw = 0,75 T** (0,70 T → m_z = +0,859; 0,75 T → −0,556; 0,80 T → −0,999).
- B_sw/B_keff = 1,69. **Não é contradição com nucleação**: com 10 ns o regime é
  damping-limited; o modelo t_sw ≈ ln(1/θ₀)/(αγ·(B−B_keff)) prevê
  B_sw(10 ns) ≈ 0,70–0,71 T — dentro do intervalo medido (dinâmica validada).
- Teste de nucleação (B_sw ≤ B_keff) exige pulsos quase-estáticos de ~µs
  (custo 100–200 min/run na GT 1030) — alternativamente, dump espacial de m_z
  durante a reversão para identificar o modo de nucleação.

## Resultado A-1b v2 (16/11/2026, `resultados_a1b/`)

- Pulso 5 ns, Temp=0, RK45 padrão, **J<0** (sinal: ver NOTA DE SINAL no script;
  evidência do nulo v1 em `v1_jpositivo_nulo/`).
- **J_sw(5 ns, 0 K) = 8 MA/cm²** (bracket 6–8: a 6 MA/cm² m_z fica em +0,944;
  a 8 comuta em t(cruzou 0) = 4,08 ns). t(cruzou 0): 4,08 ns (8) → 1,58 ns (16),
  monotônico ✓.
- **Razão MuMax3/A-0 = ≈1,07** (refino: malha 7,0–7,5; macrospin v2 6,5–7,0) —
  nucleação NÃO reduz o limiar nesta geometria: δ_w = √(A/K_eff) ≈ 10,6 nm →
  parede ~33 nm mal cabe na amostra de 35 nm → reversão quase-coerente.
  *(Retração: o "0,82" anterior era vs o A-0 v1 com campo constante — obsoleto.)*
- **Implicação**: nesta classe de célula o macrospin é excelente (desvio ~7%)
  → varreduras de arquitetura (Fase 4+) podem usar macrospin com verificação
  pontual no MuMax3.
- Ressalvas: (1) A-0 v2 e malha com bracket de 0,5 MA/cm² de resolução;
  (2) geometria quadrada 35×35 nm vs círculo 40 nm de mesma área.

## Arquivos

- `smoke_test_v2.mx3` — calibração N_z + pulso de reversão (fonte dos números acima).
  *Nota: a Fase 2 deste arquivo usou Heun+FixDt e está contaminada — retrair os
  números do platô m_z ≈ 0,46 (artefato de bombeio numérico, não física);
  a Fase 1 (N_z, K_eff, B_keff, Δ) permanece válida.*
- `verif_rk45.mx3` — evidência: reversão por campo é damping-limited
  (~25–37 ns a 0,55 T, RK45, Temp=0).
- `diagnostico_{a,b,c,d,e}.mx3` — saga de depuração (energias decompostas,
  Temp=0 vs Temp=300, dt=1 ps vs 20 fs); mantidos como evidência.
- `smoke_test.mx3` — v1 (malha 1 nm, obsoleto, mantido para histórico).
- `mtj_camada_livre.mx3` — template antigo (atualizar sintaxe antes de usar).
- Saídas: `*.out/` (table.txt, log.txt).

## Critérios de sucesso da campanha

- A-1a: B_sw(quase-estático) ≈ B_keff da malha (0,44 T) — valida coerência;
  desvio indica nucleação por bordas.
- A-1b: J_c(STT) no MuMax3 vs A-0 macrospin (5,54 MA/cm² analítico;
  9,5–10 MA/cm² efetivo a 5 ns, 0 K). Micromagnetismo deve REDUZIR J_c
  (nucleação), nunca aumentá-lo — se aumentar, suspeitar de malha/parâmetros.

# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4c2: solver de 2 sub-redes (H2 ferrimagnético) e validação.

Objetivo (da fila da Fase 4): quantificar o mecanismo FERRIMAGNÉTICO da H2 —
comutação perto do ponto de compensação — com validação contra o macrospin
ferromagnético já calibrado, e DISCRIMINAR os dois regimes de acoplamento do
torque de spin:

  MODO "tm" (interface): torque STT só na sub-rede TM (barreira MgO polariza a
     interface rica em Fe). Previsão analítica (limite rígido, derivada no
     registro): B_STT1 = α·2K_total/Ms1 → Ms_net CANCELA → J_c ≈ INDEPENDENTE de
     r (≈ 5,3 MA/cm² a 0 K vs 6,0 do ferro — ganho ~12% do termo μ0·M/2).
     Esperado: J_90 @ 300 K ≈ J_90 do doce30 ferromagnético (8,0/11,6).

  MODO "ambos" (momento total): cada sub-rede recebe o torque como se carregasse
     a corrente sozinha (quadro de spin current absorvido pelo momento total —
     o caso SOT/transversal da literatura). Previsão: B_stt_eff ∝ 1/Ms_net →
     perto da compensação o drive efetivo AMPLIFICA (20× em r = 0,95) →
     comutação MUITO mais rápida ao mesmo J; J_90 pode cair bem abaixo do ferro.

Protocolo:
  V1 REGRESSÃO (portão): ativo2=False + frac_K1=1.0 + dt=1e-12 replica o A-0 v2
     (40 nm): 0 K @ 5 ns → 6 não comuta, 8 comuta (4,44 ns); 300 K @ (12, 2 ns,
     40 traj) → ~90%. Smoke já executado: PASS exato (4,44 ns).
  V2 SANIDADE (portão): par AF estável/rígido (0 K, J=0, r=0,95, B_ex0=500 T):
     m1z = +1,000000, m2z = −1,000000, Δ = 59,2. Smoke: PASS.
  V3 GRID "tm": doce30 (d=30 nm, t=1 nm, Ms1=4e5, K_total = Δ·kT/V = 3,47e5 →
     Δ = 59,2); r ∈ {0,50; 0,85; 0,95} × B_ex0 = 500 T (ILUSTRATIVO, pendente de
     fonte); pulsos 2 ns e 1 ns (r=0,50 só 2 ns — controle); 300 K; 60 traj POR J;
     TODOS os J de cada pulso num ÚNICO batch (custo ~passo, não ~trajetória).
  V4 GRID "ambos": r ∈ {0,85; 0,95}, mesmos pulsos, J afinado (2–8 MA/cm²).
  V0 limiares 0 K pontuais para checar a previsão 5,3 MA/cm² (tm e ambos).

Energia: E = (J·A)²·R·t com R_A = 2,5 Ω·µm² (janela A-4e) e R_A = 10 Ω·µm²
(comparabilidade A-4c). Par H3: 2× por bit útil.

Custo estimado: ~10 batches × 3e5 passos × ~0,6–1 ms ≈ 40–60 min CPU.

Execução: python experimento_a4c2.py   (background)
"""
import csv
import io
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_ferrimagnetico import SimuladorFerrimagnetico

KB = 1.380649e-23
T = 300.0
DELTA = 59.2
N_TRAJ = 60          # por valor de J (mesmo do A-4c — σ ~4,1% em P=90%)
TAIL = 1e-9
DT_FERRO = 1e-12     # V1 (sem troca — mesmo dt do A-0)
DT_FERRI = 1e-14     # V3–V4 (troca forte — estabilidade RK4, nota 7 do solver)


class Tee:
    """Console + arquivo UTF-8 (evita o UTF-16 do Tee-Object do PowerShell)."""
    def __init__(self, caminho):
        self.arq = io.open(caminho, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, txt):
        self.arq.write(txt)
        self.stdout.write(txt)

    def flush(self):
        self.arq.flush()
        self.stdout.flush()


os.makedirs("resultados_a4c2", exist_ok=True)
sys.stdout = Tee("resultados_a4c2/console.txt")

linhas = []

# geometria doce30 (comparabilidade direta com o A-4c)
K_TOT = DELTA * KB * T / (np.pi * (15e-9) ** 2 * 1e-9)   # 3,47e5 J/m³
MS1 = 4.0e5
p_des = ParametrosMTJ(Ms=MS1, K_eff=K_TOT, alpha=0.01, t_FL=1e-9,
                      diametro=30e-9, T=T, RA=2.5e-12, TMR=1.5)
A_MJ = p_des.area_MJ
R_25 = 2.5e-12 / A_MJ          # Ω (janela A-4e)
R_10 = 10e-12 / A_MJ           # Ω (comparabilidade A-4c)

# previsão analítica do limiar 0 K (modo "tm", limite rígido): B_STT1 = α·2K/Ms1
Jc_prev = (2.0 * 1.602176634e-19 * MS1 * 1e-9 * 0.01 * (2.0 * K_TOT / MS1)) \
          / (1.054571817e-34 * 0.40)
print("=" * 78)
print("A-4c2 — H2 ferrimagnética: 2 sub-redes, discriminação de regimes de torque")
print(f"doce30 ferrimagnético: K_total = {K_TOT:.3e} J/m³, Δ = {DELTA}")
print(f"Previsão analítica (limite rígido, modo 'tm'): J_c(0 K) ≈ "
      f"{Jc_prev/1e10:.2f} MA/cm² (independente de r; ferro: 6,03)")
print("=" * 78)


def batch_J(Js, tp, r_ratio, bex, stt_mode, tag):
    """Roda todos os Js de um pulso num único batch (n = n_J × 60 traj)."""
    sim = SimuladorFerrimagnetico(Ms1=MS1, Ms2=r_ratio * MS1, K_total=K_TOT,
                                  t_FL=1e-9, diametro=30e-9, B_ex0=bex,
                                  seed=123, stt_mode=stt_mode)
    J_rep = np.repeat(np.asarray(Js, dtype=float), N_TRAJ)
    rr = sim.run_pulse(J_rep, t_pulse=tp, dt=DT_FERRI, T=T, n_runs=len(J_rep),
                       t_tail=TAIL)
    melhor = None
    for k, J in enumerate(Js):
        bloco = slice(k * N_TRAJ, (k + 1) * N_TRAJ)
        P = float(rr["comutou"][bloco].mean())
        sg = np.sqrt(max(P * (1 - P), 1 / N_TRAJ) / N_TRAJ)
        E25 = (J * A_MJ) ** 2 * R_25 * tp
        E10 = (J * A_MJ) ** 2 * R_10 * tp
        tsw = rr["t_sw"][bloco]
        t_med = float(np.nanmean(tsw[rr["comutou"][bloco]])) \
            if rr["comutou"][bloco].any() else np.nan
        linhas.append([tag, tp * 1e9, J / 1e10, P, sg, E25, E10, t_med])
        t_s = f"{t_med*1e9:5.2f}" if np.isfinite(t_med) else "   -"
        print(f"  J = {J/1e10:5.1f}: P = {P*100:5.1f}% ± {sg*100:4.1f} | "
              f"E(2,5) = {E25*1e12:7.4f} pJ | t_sw = {t_s} ns")
        if P >= 0.90 and (melhor is None or J < melhor[0]):
            melhor = (J, E25, E10)
    if melhor:
        print(f"    → J_90 = {melhor[0]/1e10:.1f} MA/cm² | "
              f"E(2,5) = {melhor[1]*1e12:.4f} pJ/célula → "
              f"{2*melhor[1]*1e12:.4f} pJ/bit útil")
    else:
        print("    → nenhum J do grid atingiu P ≥ 90%")
    return melhor


# ----------------------------------------------------------------- V0 + V3 tm
print("\nV0 — limiares 0 K (r = 0,95, B_ex0 = 500):")
for modo in ("tm", "ambos"):
    sim0 = SimuladorFerrimagnetico(Ms1=MS1, Ms2=0.95 * MS1, K_total=K_TOT,
                                   t_FL=1e-9, diametro=30e-9, B_ex0=500.0,
                                   seed=7, stt_mode=modo)
    for J in (2e10, 4e10, 6e10):
        rr = sim0.run_pulse(J, t_pulse=2e-9, dt=DT_FERRI, T=0.0, n_runs=1,
                            t_tail=1e-9)
        tsw = rr["t_sw"][0]
        t_s = f"{tsw*1e9:.2f} ns" if np.isfinite(tsw) else "não cruzou"
        print(f"  [{modo:5s}] 0 K: J = {J/1e10:.1f} MA/cm² → "
              f"comutou = {bool(rr['comutou'][0])} (t_sw = {t_s})")

print("\nV3 — modo 'tm' (STT só na sub-rede TM), 300 K, 60 traj/J, "
      "ref. ferro: 8,0/11,6")
J90_tm = {}
for r_ratio in (0.50, 0.85, 0.95):
    for tp, js in [(2e-9, [1e10, 2e10, 4e10, 6e10, 8e10]),
                   (1e-9, [2e10, 4e10, 6e10, 8e10, 12e10])]:
        if r_ratio == 0.50 and tp == 1e-9:
            continue   # controle só no pulso longo (economia)
        print(f"  r = {r_ratio:.2f} @ {tp*1e9:.0f} ns:")
        m = batch_J(js, tp, r_ratio, 500.0, "tm", f"tm_r{r_ratio:.2f}")
        if m:
            J90_tm[(r_ratio, tp)] = m

# ------------------------------------------------------------------- V4 ambos
print("\nV4 — modo 'ambos' (torque no momento total — caso SOT), 300 K, 60 traj/J")
J90_am = {}
for r_ratio in (0.85, 0.95):
    for tp, js in [(2e-9, [2e10, 3e10, 4e10, 5e10, 6e10]),
                   (1e-9, [2e10, 3e10, 4e10, 6e10, 8e10])]:
        print(f"  r = {r_ratio:.2f} @ {tp*1e9:.0f} ns:")
        m = batch_J(js, tp, r_ratio, 500.0, "ambos", f"ambos_r{r_ratio:.2f}")
        if m:
            J90_am[(r_ratio, tp)] = m

# -------------------------------------------------------------------- resumo
print()
print("=" * 78)
print("RESUMO — J_90 @ 300 K (referência ferromagnética doce30: 8,0 @ 2 ns / "
      "11,6 @ 1 ns)")
print("=" * 78)
for tag, d in [("tm", J90_tm), ("ambos", J90_am)]:
    for (r_ratio, tp), v in sorted(d.items()):
        ref = 8.0 if tp == 2e-9 else 11.6
        print(f"  [{tag:5s}] r = {r_ratio:.2f} @ {tp*1e9:.0f} ns: "
              f"J_90 = {v[0]/1e10:5.1f} MA/cm² (ferro: {ref:.1f}) → "
              f"ganho {ref/(v[0]/1e10):.2f}× | E(2,5) {v[1]*1e12:.4f} pJ/célula")

with open("resultados_a4c2/a4c2_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["caso", "pulso_ns", "J_MA_cm2", "P_comutar", "sigma_P",
                "E_J_RA2p5", "E_J_RA10", "t_sw_med_ns"])
    for l in linhas:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4c2/")

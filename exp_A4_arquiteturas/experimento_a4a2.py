# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4a2: VCMA para ENERGIA no alvo 2 ns (pós-negativo A-4a).

A-4a mostrou que VCMA NÃO resgata 1 ns (gargalo é TORQUE: B_stt ~ 0,02 T <<
B_keff; a redução de barreira não acelera a travessia). Resta a outra face do
VCMA: no alvo 2 ns (atingível: A-0 v2 = 90% @ 12 MA/cm², 0,63 pJ), reduzir a
barreira DURANTE o pulso pode baixar o J necessário → energia de escrita.

Grid: pulso 2 ns, f_K ∈ {1.0, 0.9, 0.75, 0.5, 0.25}, J ∈ {5,6,8,10,12} MA/cm²,
300 K, 40 traj/ponto; tail 3 ns (barreira integral → absorção).
Métrica: P ≥ 90% com E_total = E_STT + E_VCMA mínima.
Mapeamento V_b: ILUSTRATIVO (β = 100 fJ/(V·m) projeto / 50 pessimista —
fonte pendente, busca 402; ver A-4a).

Execução: python experimento_a4a2.py   (~3 min CPU)
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin

PULSO = 2e-9
TAIL = 3e-9
DT = 1e-12
N_TRAJ = 40
JS = [5e10, 6e10, 8e10, 10e10, 12e10]         # A/m²
FKS = [1.0, 0.9, 0.75, 0.5, 0.25]

T_MGO = 1.0e-9
BETA = 100e-15                                 # J/(V·m) — ILUSTRATIVO (pendente de fonte)
EPS0, EPS_MGO = 8.854e-12, 9.0

p = ParametrosMTJ(T=300.0)
V_B = {f: (1.0 - f) * p.K_eff * p.t_FL * T_MGO / BETA for f in FKS if f < 1.0}
C_CELL = EPS0 * EPS_MGO * p.area_MJ / T_MGO
R_MED = 0.5 * (p.R_P + p.R_AP)

os.makedirs("resultados_a4a2", exist_ok=True)

print("=" * 76)
print("A-4a2: VCMA p/ ENERGIA no alvo 2 ns — 300 K, 40 traj/ponto, tail 3 ns")
print("=" * 76)
print(f"  referência A-0 v2 (f_K=1): 2 ns @ 12 MA/cm² = 90% → E_STT = 0,63 pJ")
print("-" * 76)

head = f"  {'f_K':>5} | " + " | ".join(f"J = {j/1e10:4.1f}" for j in JS) + "   [P% ; E_total pJ]"
print(head)

linhas = []
melhor = None
for f in FKS:
    celulas = []
    for J in JS:
        sim = SimuladorMacrospin(p, seed=123)
        r = sim.run_pulse(J, t_pulse=PULSO, dt=DT, T=300.0, n_runs=N_TRAJ,
                          t_tail=TAIL, k_mult_pulse=f)
        P = float(r["comutou"].mean())
        E_STT = (J * p.area_MJ) ** 2 * R_MED * PULSO
        E_VC = 0.5 * C_CELL * V_B[f] ** 2 if f < 1.0 else 0.0
        E_tot = E_STT + E_VC
        celulas.append((P, E_tot, t_sw_med := (float(np.nanmean(r["t_sw"][r["comutou"]]))
                                               if r["comutou"].any() else np.nan)))
        linhas.append([f, J, P, E_STT, E_VC, E_tot, celulas[-1][2]])
        if P >= 0.90 and (melhor is None or E_tot < melhor[0]):
            melhor = (E_tot, f, J, P)
    print(f"  {f:5.2f} | " + " | ".join(f"{c[0]*100:5.1f}%" for c in celulas))

print("-" * 76)
print("  E_total pJ nos pontos com P ≥ 90% (E_STT + E_VCMA):")
for f in FKS:
    for (J, (P, E_tot, t_med)) in zip(JS, [(l[5], l[5], l[6]) for l in linhas if False]):
        pass  # (relatório abaixo via linha única)
for f in FKS:
    pts = [l for l in linhas if l[0] == f and l[2] >= 0.90]
    if pts:
        det = ", ".join(f"J={l[1]/1e10:.0f}: E={l[5]*1e12:.2f} pJ (E_VCMA {l[4]*1e12:.3f})"
                        for l in pts)
        print(f"    f_K = {f:4.2f}: {det}")

if melhor:
    E_tot, f, J, P = melhor
    print(f"\n  MÍNIMO: E = {E_tot*1e12:.2f} pJ em f_K = {f:.2f}, J = {J/1e10:.0f} MA/cm² "
          f"(P = {P*100:.0f}%) — vs 0,63 pJ do A-0 v2 (f_K=1, J=12)")
else:
    print("\n  Nenhum ponto com P ≥ 90% no grid — ampliar J ou pulso.")

with open("resultados_a4a2/a4a2_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["f_K", "J_A_por_m2", "P_comutar", "E_STT_J", "E_VCMA_J", "E_total_J",
                "t_sw_med_ns"])
    for l in linhas:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4a2/")

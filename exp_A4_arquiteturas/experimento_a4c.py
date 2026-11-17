# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4c: refino do bracket dos designs vencedores (macrospin).

A-4b achou os vencedores com grid grosso (J = 1,2/1,8×J_c0, 40 traj). Este
experimento refina a curva P(J) com passo fino e mais trajetórias para obter:

  1. J_90: a corrente mínima com P ≥ 90% (e seu intervalo: bracket P<90% → P≥90%)
  2. E de escrita em J_90, por pulso (2 ns e 1 ns)
  3. Custo por bit ÚTIL com o par diferencial (H3 requisito, A-4d): 2× E

Designs (A-4b + verificação MuMax3):
  doce30: d = 30 nm, t = 1,0 nm, Ms = 4e5  (J_c0 = 6,03 MA/cm²; 0 K: 1,58 ns @ 1,8×)
  rapido20: d = 20 nm, t = 1,0 nm, Ms = 4e5 (J_c0 = 12,62; 0 K em MALHA: 0,80 ns @ 1,8×)

J em valores ABSOLUTOS (MA/cm²) escolhidos para cruzar o limiar P = 90%
(brackets do A-4b): doce30 @2ns {6,0–8,0}; doce30 @1ns {9,5–12,5};
rapido20 @2ns {12,0–15,1}; rapido20 @1ns {17,0–22,7}.
300 K, 60 traj/ponto (σ binomial ~4,1% em P=90%), pulso + tail 3 ns.

Limitações: macrospin (razão malha/macrospin 0,94–0,97 na verificação →
os J_90 daqui tendem a ser levemente conservadores); R_A fixo; α = 0,01.

Execução: python experimento_a4c.py   (background; ~10–15 min CPU)
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin

KB = 1.380649e-23
T = 300.0
DELTA = 59.2
N_TRAJ = 60
TAIL = 3e-9
DT = 1e-12

DESIGNS = [
    ("doce30", 30e-9, 1.0e-9, 4.0e5, {2e-9: [6.0e10, 6.5e10, 7.2e10, 8.0e10],
                                      1e-9: [9.5e10, 10.2e10, 10.9e10, 11.6e10, 12.5e10]}),
    ("rapido20", 20e-9, 1.0e-9, 4.0e5, {2e-9: [12.0e10, 13.5e10, 15.1e10],
                                        1e-9: [17.0e10, 19.0e10, 21.0e10, 22.7e10]}),
]

os.makedirs("resultados_a4c", exist_ok=True)

print("=" * 78)
print("A-4c: refino do bracket — curva P(J) fina, J_90, E por bit útil (par H3)")
print("=" * 78)

linhas = []
resumo = {}
for (nome, d, t_fl, Ms, grid) in DESIGNS:
    V_cell = np.pi * (d / 2) ** 2 * t_fl
    K_eff = DELTA * KB * T / V_cell
    p = ParametrosMTJ(Ms=Ms, K_eff=K_eff, alpha=0.01, t_FL=t_fl, diametro=d, T=T)
    J_c0 = SimuladorMacrospin(p, seed=3).J_c0()
    R_med = 0.5 * (p.R_P + p.R_AP)
    print(f"\n{nome}: d = {d*1e9:.0f} nm, t = {t_fl*1e9:.1f} nm, Ms = {Ms/1e5:.0f}e5 | "
          f"J_c0 = {J_c0/1e10:.2f} MA/cm² | R_P = {p.R_P/1e3:.1f} kΩ")
    for tp, js in grid.items():
        print(f"  pulso {tp*1e9:.0f} ns:")
        melhor = None
        for J in js:
            sim = SimuladorMacrospin(p, seed=123)
            r = sim.run_pulse(J, t_pulse=tp, dt=DT, T=T, n_runs=N_TRAJ, t_tail=TAIL)
            P = float(r["comutou"].mean())
            sig = np.sqrt(max(P * (1 - P), 1 / N_TRAJ) / N_TRAJ)
            E = (J * p.area_MJ) ** 2 * R_med * tp
            t_med = (float(np.nanmean(r["t_sw"][r["comutou"]])) if r["comutou"].any()
                     else np.nan)
            linhas.append([nome, tp * 1e9, J / 1e10, P, sig, E, t_med])
            t_s = f"{t_med*1e9:5.2f}" if np.isfinite(t_med) else "   -"
            print(f"    J = {J/1e10:5.1f} MA/cm²: P = {P*100:5.1f}% ± {sig*100:4.1f} | "
                  f"E = {E*1e12:6.3f} pJ | t_sw médio = {t_s} ns")
            if P >= 0.90 and (melhor is None or J < melhor[0]):
                melhor = (J, P, E)
        if melhor:
            J90, P90, E90 = melhor
            print(f"    → J_90 = {J90/1e10:.1f} MA/cm² | E = {E90*1e12:.3f} pJ/célula | "
                  f"par H3 (bit útil): {2*E90*1e12:.3f} pJ/bit")
            resumo[(nome, tp)] = (J90, E90)
        else:
            print(f"    → nenhum J do grid atingiu P ≥ 90% (ampliar bracket).")
            resumo[(nome, tp)] = None

print("-" * 78)
print("RESUMO — custo por bit ÚTIL (par diferencial H3 = 2 células/bit):")
for (nome, tp), v in resumo.items():
    if v:
        print(f"  {nome} @ {tp*1e9:.0f} ns: J_90 = {v[0]/1e10:5.1f} MA/cm² → "
              f"{2*v[1]*1e12:.3f} pJ/bit útil")

with open("resultados_a4c/a4c_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["design", "pulso_ns", "J_MA_cm2", "P_comutar", "sigma_P",
                "E_STT_J", "t_sw_med_ns"])
    for l in linhas:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4c/")

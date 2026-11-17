# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4b: varredura de designs com Δ fixo = 59,2 (macrospin).

Contexto: A-4a/a2 fecharam o VCMA (energia −30% no 2 ns; 1 ns não responde).
Agora o mapa do espaço de designs: com Δ FIXO (retenção de 10 anos garantida
por construção), variar d, t_FL, Ms → K_eff é RECALCULADO por design
(K_eff = Δ·k_B·T/V) para manter a barreira. Perguntas:
  Q1. Qual design minimiza E de escrita no alvo 2 ns (P ≥ 90%)?
  Q2. Algum design atinge 1 ns? (células menores → K_eff ↑ → B_keff ↑ →
      precessão mais rápida — mas J_c0 ↑ e R ↑ também; o trade é medido)

Grid: d ∈ {20, 30, 40} nm × t_FL ∈ {1.0, 1.5} nm × Ms ∈ {4,6,8}e5 × α = 0,01.
J em múltiplos do J_c0 analítico (Sun): {1.2, 1.8}× — brackets P em torno de 90%.
300 K, 40 traj/ponto, pulso 2 ns + 1 ns, tail 3 ns. 0 K: t_sw a 1,8×J_c0 (1 run).

Limitações declaradas: macrospin (razão malha 1,07 — ok); R = R_A/Área com
R_A fixo (20 nm → R ~ 32 kΩ; efeito túnel de condutância em t_FL pequeno
ignorado); K_eff até ~5e5 J/m³ exige material anisotrópico forte (fonte
pendente — buscas bloqueadas). α fixo em 0,01 nesta primeira passada.

Execução: python experimento_a4b.py   (background; ~25–35 min CPU)
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin
import dataclasses

DELTA_ALVO = 59.2
KB = 1.380649e-23
T = 300.0
DS = [20e-9, 30e-9, 40e-9]
TFLS = [1.0e-9, 1.5e-9]
MSS = [4.0e5, 6.0e5, 8.0e5]
ALPHA = 0.01
N_TRAJ = 40
JS_MULT = [1.2, 1.8]
PULSOS = [2e-9, 1e-9]
TAIL = 3e-9
DT = 1e-12

os.makedirs("resultados_a4b", exist_ok=True)

print("=" * 78)
print("A-4b: espaço de designs com Δ = %.1f FIXO — busca mínimo de E e teste de 1 ns" % DELTA_ALVO)
print("=" * 78)
print(f"  {'d nm':>5} {'t nm':>5} {'Ms':>7} {'K_eff':>9} {'B_keff':>7} {'J_c0':>7} | "
      f"P% @2ns (1,2x/1,8x) | P% @1ns | t_sw 0K @1,8x")

linhas = []
melhor_2ns = None
algum_1ns = []

for d in DS:
    for t_fl in TFLS:
        V_cell = np.pi * (d / 2) ** 2 * t_fl
        K_eff = DELTA_ALVO * KB * T / V_cell
        for Ms in MSS:
            p = ParametrosMTJ(Ms=Ms, K_eff=K_eff, alpha=ALPHA, t_FL=t_fl,
                              diametro=d, T=T)
            sim0 = SimuladorMacrospin(p, seed=3)
            J_c0 = sim0.J_c0()

            # 0 K: t_sw determinístico a 1,8×J_c0 (pulso 2 ns)
            r0 = SimuladorMacrospin(p, seed=3).run_pulse(1.8 * J_c0, t_pulse=2e-9,
                                                         dt=0.5e-12, T=0.0,
                                                         t_tail=1e-9)
            tsw_0k = r0["t_sw"][0] if r0["comutou"][0] else np.nan

            res = {2e-9: [], 1e-9: []}
            for tp in PULSOS:
                for mult in JS_MULT:
                    J = mult * J_c0
                    sim = SimuladorMacrospin(p, seed=123)
                    r = sim.run_pulse(J, t_pulse=tp, dt=DT, T=T, n_runs=N_TRAJ,
                                      t_tail=TAIL)
                    P = float(r["comutou"].mean())
                    R_med = 0.5 * (p.R_P + p.R_AP)
                    E = (J * p.area_MJ) ** 2 * R_med * tp
                    res[tp].append((mult, P, E, J))
                    linhas.append([d * 1e9, t_fl * 1e9, Ms, K_eff, J_c0 / 1e10,
                                   tp * 1e9, mult, P, E])

            p2 = [f"{r[1]*100:5.1f}" for r in res[2e-9]]
            p1 = [f"{r[1]*100:5.1f}" for r in res[1e-9]]
            t0s = f"{tsw_0k*1e9:6.2f}" if np.isfinite(tsw_0k) else "   nao"
            print(f"  {d*1e9:5.0f} {t_fl*1e9:5.1f} {Ms/1e5:7.1f} {K_eff:9.2e} "
                  f"{p.B_keff:7.3f} {J_c0/1e10:7.2f} | {'/'.join(p2)} | "
                  f"{'/'.join(p1)} | {t0s}")

            # mínimo de energia no alvo 2 ns com P ≥ 90%
            for (mult, P, E, J) in res[2e-9]:
                if P >= 0.90 and (melhor_2ns is None or E < melhor_2ns[0]):
                    melhor_2ns = (E, d, t_fl, Ms, J, mult)
            for (mult, P, E, J) in res[1e-9]:
                if P >= 0.90:
                    algum_1ns.append((d, t_fl, Ms, J, mult, E))

print("-" * 78)
if melhor_2ns:
    E, d, t_fl, Ms, J, mult = melhor_2ns
    print(f"Q1 — MÍNIMO DE ENERGIA @2ns (P≥90%): {E*1e12:.3f} pJ | d = {d*1e9:.0f} nm, "
          f"t = {t_fl*1e9:.1f} nm, Ms = {Ms/1e5:.0f}e5, J = {J/1e10:.1f} MA/cm² "
          f"({mult:.1f}×J_c0)")
    print(f"        (baseline A-0/A-4a2: 0,63 pJ @ 40 nm; com VCMA: 0,44 pJ)")
if algum_1ns:
    print("Q2 — DESIGNS com P≥90% @1ns:")
    for (d, t_fl, Ms, J, mult, E) in algum_1ns:
        print(f"        d = {d*1e9:.0f} nm, t = {t_fl*1e9:.1f} nm, Ms = {Ms/1e5:.0f}e5, "
              f"J = {J/1e10:.1f} MA/cm² ({mult:.1f}×J_c0), E = {E*1e12:.2f} pJ")
else:
    print("Q2 — NENHUM design com P ≥ 90% @1 ns no grid: 1 ns é torque-limited "
          "por STT puro nesta classe (consistente com A-4a). → SOT/ferrimagnético.")

with open("resultados_a4b/a4b_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["d_nm", "t_FL_nm", "Ms_A_m", "K_eff_J_m3", "J_c0_MA_cm2",
                "pulso_ns", "mult_Jc0", "P_comutar", "E_STT_J"])
    for l in linhas:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4b/")

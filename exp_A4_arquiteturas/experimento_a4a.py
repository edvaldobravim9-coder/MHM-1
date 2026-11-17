# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4a: assistência VCMA à comutação STT (macrospin validado).

Pergunta: a meta "1 ns" (0% até 12 MA/cm² no A-0 v2, STT puro) se torna viável
se a barreira for reduzida APENAS durante o pulso (VCMA), mantendo Δ = 59,2 no
estado estático (retenção de 10 anos preservada por construção)?

Física do modelo (A-4a usa o macrospin VALIDADO: FDT 1,008; razão malha 1,07):
  durante o pulso: K_eff' = f_K·K_eff  (f_K = 1,0 = sem VCMA)
  no tail:         K_eff  (barreira integral — comutação é ABSORVENTE: quem
                   cruzar o equador cai no poço −z com Δ = 59 e não volta).

Mapeamento f_K ↔ tensão (efeito INTERFACIAL):
  ΔK_s = β·E, E = V_b/t_MgO, ΔK_vol = ΔK_s/t_FL
  → V_b(f_K) = (1−f_K)·K_eff·t_FL·t_MgO/β
  β pendente de FONTE (busca web bloqueada 402 em 17/11): faixa relatada na
  literatura aberta ~20–300 fJ/(V·m). Aqui: β = 100 fJ/(V·m) como caso de
  projeto e 50 como pessimista — MARCADOS COMO ILUSTRATIVOS até a fonte.
  C(MgO, 1 nm, A = 1,26 µm²) ≈ 100 aF → E_VCMA ≈ ½·C·V² ~ 5–100 aJ (desprezível
  vs STT ~0,3–1 pJ; o ganho do VCMA é REDUZIR J, não custo próprio).

Protocolo:
  0 K: t_sw determinístico, J ∈ {8,10,12,15} MA/cm², f_K ∈ {1.0,0.9,0.75,0.5,0.25}
  300 K: P(comutar), 40 traj/ponto, mesmo grid (pulso 1 ns, tail 2 ns)
  Retenção pós-pulso: inerente ao 'comutou' (m_z final < 0 com barreira cheia).

Execução: python experimento_a4a.py   (~2 min CPU)
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin

PULSO = 1e-9
TAIL = 2e-9
DT = 1e-12
N_TRAJ = 40
JS = [8e10, 10e10, 12e10, 15e10]              # A/m²
FKS = [1.0, 0.9, 0.75, 0.5, 0.25]             # fator de anisotropia durante o pulso

# Mapeamento VCMA (ILUSTRATIVO até fonte de β)
T_MGO = 1.0e-9
BETA = 100e-15                                 # J/(V·m) — caso de projeto (pendente de fonte)
EPS0, EPS_MGO = 8.854e-12, 9.0

p = ParametrosMTJ(T=300.0)
V_B = {f: (1.0 - f) * p.K_eff * p.t_FL * T_MGO / BETA for f in FKS if f < 1.0}
C_CELL = EPS0 * EPS_MGO * p.area_MJ / T_MGO
E_VCMA = {f: 0.5 * C_CELL * v**2 for f, v in V_B.items()}
R_MED = 0.5 * (p.R_P + p.R_AP)

os.makedirs("resultados_a4a", exist_ok=True)
linhas_csv = []

print("=" * 76)
print("A-4a: VCMA + STT — pulso 1 ns — alvo: tornar 1 ns viável mantendo retenção")
print("=" * 76)
print(f"  célula: d = 40 nm, t_FL = 1,5 nm, K_eff = 1,3e5 → Δ estático = {p.delta:.1f}")
print(f"  mapeamento β = {BETA*1e15:.0f} fJ/(V·m) [ILUSTRATIVO — fonte pendente]:")
for f in FKS:
    if f < 1.0:
        print(f"    f_K = {f:4.2f} → V_b = {V_B[f]:5.2f} V | "
              f"E_VCMA = {E_VCMA[f]*1e18:6.1f} aJ | Δ_durante_pulso = {p.delta*f:5.1f}")
print("-" * 76)

# ---------------------------------------------------------------- 0 K: t_sw
print("\n0 K — tempo de comutação determinístico (pulso 1 ns):")
print(f"  {'f_K':>5} | " + " | ".join(f"J = {j/1e10:4.1f}" for j in JS) + "   [MA/cm²]")
tsw_0k = {}
for f in FKS:
    linha = [f"{f:5.2f}"]
    for J in JS:
        sim = SimuladorMacrospin(p, seed=3)
        r = sim.run_pulse(J, t_pulse=PULSO, dt=0.5e-12, T=0.0, t_tail=TAIL,
                          k_mult_pulse=f)
        if r["comutou"][0]:
            tsw_0k[(f, J)] = r["t_sw"][0]
            linha.append(f"{r['t_sw'][0]*1e9:6.3f}")
        else:
            tsw_0k[(f, J)] = np.nan
            linha.append("   nao")
    linhas_csv.append([0.0, f, "", *[t for t in [tsw_0k[(f, J)] for J in JS]]])
    print("  " + " | ".join(linha))

# ---------------------------------------------------------------- 300 K: P
print("\n300 K — P(comutar) com 40 trajetórias/ponto (pulso 1 ns):")
print(f"  {'f_K':>5} | " + " | ".join(f"J = {j/1e10:4.1f}" for j in JS) + "   [MA/cm²]")
for f in FKS:
    linha = [f"{f:5.2f}"]
    for J in JS:
        sim = SimuladorMacrospin(p, seed=123)
        r = sim.run_pulse(J, t_pulse=PULSO, dt=DT, T=300.0, n_runs=N_TRAJ,
                          t_tail=TAIL, k_mult_pulse=f)
        P = r["comutou"].mean() * 100
        t_med = np.nanmean(r["t_sw"][r["comutou"]]) * 1e9 if r["comutou"].any() else np.nan
        t_str = f"{t_med:6.3f}" if np.isfinite(t_med) else "     -"
        E_J = (J * p.area_MJ) ** 2 * R_MED * PULSO
        linha.append(f"{P:5.1f}%")
        linhas_csv.append([300.0, f, J, P, t_med, E_J, E_VCMA.get(f, 0.0)])
    print("  " + " | ".join(linha))

print("-" * 76)
print("  células da tabela 300 K: P(comutar); t_sw médio nos demais CSV.")
print("  E_STT(pulso integral) = I²·R_med·t (convenção A-0); E_VCMA por carga do capacitor.")
print("  LEITURA: f_K que der P ≈ 90–100% a 1 ns com J ≤ 12 MA/cm² define a exigência")
print("           de VCMA (via β) para bater a meta 1 ns; f_K = 1.0 replica o A-0 v2.")

with open("resultados_a4a/a4a_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["T_K", "f_K", "J_A_por_m2", "P_comutar_pct", "t_sw_med_ns",
                "E_STT_J", "E_VCMA_J"])
    for l in linhas_csv:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4a/")

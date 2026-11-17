# -*- coding: utf-8 -*-
"""
MHM-1 — Verificação MuMax3 dos designs vencedores do A-4b (0 K).

A-4b (macrospin) encontrou designs de 20–30 nm com K_eff alto (Δ fixo = 59,2)
que comutam em 1–2 ns com P ≥ 90%. Ressalva declarada: δ_w = √(A/K_eff) ≈
4,4–5,9 nm << d → possível nucleação (a razão malha/macrospin 1,07 do A-1b foi
medida em K_eff = 1,3e5, δ_w ≈ d — regime quase-coerente). Este teste compara
malha vs macrospin nos designs de 30 nm e 20 nm:
  se a malha comutar a J ≤ macrospin → números do A-4b são CONSERVADORES (ok);
  se a malha precisar de J muito maior → A-4b otimista → reavaliar.

Setup MuMax3 (convenções A-1): célula 2,5 nm; Ku1 = K_eff + ½μ0·Ms² (N_z ≈ 1 —
mesma aproximação do A-1, deriva de B_keff ~2% declarada); J < 0 comuta P→AP;
Pol = 0,40, Lambda = 1; 0 K; pulso 2 ns e 1 ns; J = 1,2/1,5/1,8×J_c0(Sun).

Execução: python verifica_a4b_mumax3.py   (~2–3 min GPU)
"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin

MUMAX = r"C:\Users\edval\Desktop\MHM-1\tools\mumax3.exe"
KB = 1.380649e-23
T = 300.0
DELTA = 59.2
MU0 = 4.0e-7 * np.pi

# (d, t_FL, Ms) — os dois designs-chave do A-4b
DESIGNS = [(30e-9, 1.0e-9, 4.0e5), (20e-9, 1.0e-9, 4.0e5)]
MULTS = [1.2, 1.5, 1.8]
PULSOS = [2e-9, 1e-9]

TEMPLATE = """// verifica A-4b: d = {d_nm:.0f} nm, t = {t_nm:.1f} nm, Ms = {ms:.1f}e5
SetGridSize({nx}, {ny}, 1)
SetCellSize(2.5e-9, 2.5e-9, {t_m:.3e})
Msat  = {ms:.6e}
Aex   = 15e-12
alpha = 0.01
Ku1   = {ku1:.6e}
anisU = vector(0, 0, 1)
Temp  = 0

DisableZhangLiTorque = true
Pol = 0.40
Lambda = 1
EpsilonPrime = 0
FixedLayer = vector(0, 0, 1)
FixedLayerPosition = FIXEDLAYER_TOP
// SINAL: J negativo comuta P→AP (diag_stt_sinal.py)
J = vector(0, 0, {J_aplicado:.6e})

m = Uniform(0.01, 0, 0.99995)
mz := m.Comp(2)
tableadd(mz)
TableAutoSave(1e-11)
run({t_run:.1e})
tablesave()
"""

print("=" * 78)
print("VERIFICAÇÃO A-4b no MuMax3 — designs 30 nm e 20 nm (Δ = 59,2 fixo, 0 K)")
print("=" * 78)

for (d, t_fl, Ms) in DESIGNS:
    V_cell = np.pi * (d / 2) ** 2 * t_fl
    K_eff = DELTA * KB * T / V_cell
    Ku1 = K_eff + 0.5 * MU0 * Ms ** 2
    p = ParametrosMTJ(Ms=Ms, K_eff=K_eff, alpha=0.01, t_FL=t_fl, diametro=d, T=T)
    J_c0 = SimuladorMacrospin(p, seed=3).J_c0()
    nx = int(round(d / 2.5e-9))
    delta_w = np.sqrt(15e-12 / K_eff) * 1e9
    print(f"\nDESIGN d = {d*1e9:.0f} nm, t = {t_fl*1e9:.1f} nm, Ms = {Ms/1e5:.0f}e5 | "
          f"K_eff = {K_eff:.2e} | B_keff = {p.B_keff:.3f} T | J_c0 = {J_c0/1e10:.2f} "
          f"MA/cm² | δ_w ≈ {delta_w:.1f} nm (vs d = {d*1e9:.0f} nm)")
    for tp in PULSOS:
        for mult in MULTS:
            J = mult * J_c0
            nome = f"v4b_d{int(d*1e9)}_t{t_fl*1e9:.0f}_{int(mult*10):02d}_{int(tp*1e9)}ns"
            with open(f"{nome}.mx3", "w", encoding="utf-8") as fh:
                fh.write(TEMPLATE.format(d_nm=d * 1e9, t_nm=t_fl * 1e9, ms=Ms,
                                         nx=nx, ny=nx, t_m=t_fl, ku1=Ku1,
                                         J_aplicado=-J, t_run=tp))
            r = subprocess.run([MUMAX, f"{nome}.mx3"], capture_output=True, text=True)
            if r.returncode != 0:
                print(f"  malha {mult:.1f}x @ {tp*1e9:.0f} ns: ERRO exit {r.returncode}")
                continue
            with open(f"{nome}.out/table.txt", encoding="utf-8") as fh:
                head = fh.readline().rstrip("\n").split("\t")
                linhas = [l for l in fh if not l.startswith("#")]
            i_mz = next(i for i, h in enumerate(head) if h.strip("# ").startswith("mz"))
            mz_f = float(linhas[-1].split("\t")[i_mz])
            mz_col = [float(l.split("\t")[i_mz]) for l in linhas]
            t_sw = next((float(l.split("\t")[0]) for l, m in zip(linhas, mz_col)
                         if m < 0), float("nan"))
            # macrospin equivalente (mesmo J, mesmo pulso)
            rm = SimuladorMacrospin(p, seed=3).run_pulse(J, t_pulse=tp, dt=0.5e-12,
                                                         T=0.0, t_tail=1e-9)
            mac = ("COMUTOU %.2f ns" % (rm["t_sw"][0] * 1e9) if rm["comutou"][0]
                   else "nao")
            sw_m = "COMUTOU" if mz_f < 0 else "nao"
            t_s = f"{t_sw*1e9:.2f} ns" if np.isfinite(t_sw) else ""
            print(f"  {tp*1e9:.0f} ns @ {mult:.1f}×J_c0 ({J/1e10:5.1f} MA/cm²): "
                  f"MALHA {sw_m} {t_s} (m_z {mz_f:+.3f}) | MACROSPIN {mac}")

print("-" * 78)
print("LEITURA: malha comuta a J ≤ macrospin → A-4b conservador (nucleação ajuda).")
print("         malha exigir J >> macrospin → A-4b otimista → reavaliar designs.")

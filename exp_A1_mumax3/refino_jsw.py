# -*- coding: utf-8 -*-
"""
MHM-1 — Refino J_sw: malha (MuMax3) vs macrospin (A-0 corrigido), 0 K, 5 ns.

Motivação: A-0 reexecutado com anisotropia uniaxial corrigida comuta a 8 e não
comuta a 6 MA/cm² (bracket 6–8). A-1b v2 da malha: comuta a 8, não a 6. Os
brackets se sobrepõem — este refino (6,5 / 7,0 / 7,5 MA/cm² em ambos) decide
se a nucleação da malha reduz o limiar (<1), mantém (=1) ou aumenta (>1).

Execução: python refino_jsw.py   (~10 min GPU + segundos CPU)
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
JS_FINO = [6.5e10, 7.0e10, 7.5e10]   # A/m²

TEMPLATE = """// refino J_sw: J = {J_aplicado:+.3e} A/m2 ({ma:.1f} MA/cm2), 0 K, 5 ns
SetGridSize(14, 14, 1)
SetCellSize(2.5e-9, 2.5e-9, 1.5e-9)
Msat  = 600e3
Aex   = 15e-12
alpha = 0.01
Ku1   = 335e3
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
run(5.0e-09)
tablesave()
"""

print("=" * 70)
print("REFINO J_sw — 0 K, pulso 5 ns — malha (MuMax3) vs macrospin (A-0 v2)")
print("=" * 70)

# ---- malha (MuMax3, J<0) ----------------------------------------------------
for J in JS_FINO:
    ma = J / 1e10
    nome = f"refino_j{int(round(ma*100)):04d}"
    with open(f"{nome}.mx3", "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE.format(J=J, J_aplicado=-J, ma=ma))
    r = subprocess.run([MUMAX, f"{nome}.mx3"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  malha J={ma:.1f}: ERRO exit {r.returncode}")
        continue
    with open(f"{nome}.out/table.txt", encoding="utf-8") as fh:
        linhas = [l for l in fh if not l.startswith("#")]
    mz = float(linhas[-1].split("\t")[4])
    t_sw = next((float(l.split("\t")[0]) for l in linhas
                 if float(l.split("\t")[4]) < 0), float("nan"))
    print(f"  MALHA    J = {ma:4.1f} MA/cm² | m_z final = {mz:+8.5f} | "
          f"{'COMUTOU' if mz < 0 else 'nao comutou'}"
          + (f" | t = {t_sw*1e9:.2f} ns" if np.isfinite(t_sw) else ""))

# ---- macrospin (A-0 corrigido, J>0 conforme convenção do A-0) ---------------
p = ParametrosMTJ(T=0.0)
for J in JS_FINO:
    sim = SimuladorMacrospin(p, seed=3)
    res = sim.run_pulse(J, t_pulse=5e-9, dt=0.5e-12, T=0.0, t_tail=2e-9)
    mz = res["mz_final"][0]
    t_sw = res["t_sw"][0]
    print(f"  MACROSPIN J = {J/1e10:4.1f} MA/cm² | m_z final = {mz:+8.5f} | "
          f"{'COMUTOU' if res['comutou'][0] else 'nao comutou'}"
          + (f" | t = {t_sw*1e9:.2f} ns" if np.isfinite(t_sw) else ""))

print("-" * 70)
print("Referências: macrospin v2 — 8 comuta (4,44 ns), 6 nao comuta.")
print("             malha v2    — 8 comuta (4,08 ns), 6 nao comuta.")
print("LEITURA: razão J_sw(malha)/J_sw(macrospin) < 1 → nucleação; = 1 → coerente;")
print("         > 1 → investigar (geometria quadrado×círculo, malha, parâmetros).")

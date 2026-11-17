# -*- coding: utf-8 -*-
"""
MHM-1 — Viabilidade de runs térmicos no MuMax3 (GT 1030, malha 2,5 nm).

Objetivo: medir CUSTO (wall-clock) e SANIDADE (física) de Temp=300 com RK45
adaptativo na malha calibrada, e já extrair dois mini-resultados:
  T1. Ruído puro (J=0, 3 ns, 2 seeds): m_z deve vagar pouco (Δ = 59,1 — poço
      profundo); <1−m_z²> deve dar ~1/(2Δ) ≈ 0,0085 (equipartição do MuMax3).
  T2. Assistência térmica no STT (J = 6,5 MA/cm², 5 ns, 2 seeds): a 0 K a malha
      NÃO comuta a 6,5 (m_z = +0,786); a 300 K o ruído pode empurrar além do
      equador → medir P com n=2 (apenas indicação, não estatística).

Execução: python termico_viabilidade.py   (background; mede wall-clock real)
"""
import os
import subprocess
import time

import numpy as np

MUMAX = r"C:\Users\edval\Desktop\MHM-1\tools\mumax3.exe"

TEMPLATE = """// viabilidade térmica: J = {J:+.2e} A/m2, 300 K, {t_run:.0f} ns, seed {seed}
SetGridSize(14, 14, 1)
SetCellSize(2.5e-9, 2.5e-9, 1.5e-9)
Msat  = 600e3
Aex   = 15e-12
alpha = 0.01
Ku1   = 335e3
anisU = vector(0, 0, 1)
Temp  = 300
ThermSeed({seed})
{bloco_stt}
m = Uniform(0.01, 0, 0.99995)
mz := m.Comp(2)
tableadd(mz)
TableAutoSave(1e-11)
run({t_run:.1e})
tablesave()
"""

BLOCO_STT = """DisableZhangLiTorque = true
Pol = 0.40
Lambda = 1
EpsilonPrime = 0
FixedLayer = vector(0, 0, 1)
FixedLayerPosition = FIXEDLAYER_TOP
// SINAL: J negativo comuta P→AP
J = vector(0, 0, {J_aplicado:.6e})
"""

CASOS = [
    ("termo_t1a", 0.0, 3e-9, 1),
    ("termo_t1b", 0.0, 3e-9, 2),
    ("termo_t2a", 6.5e10, 5e-9, 1),
    ("termo_t2b", 6.5e10, 5e-9, 2),
]

print("=" * 70)
print("VIABILIDADE TÉRMICA MuMax3 (300 K, RK45, malha 2,5 nm)")
print("=" * 70)

for nome, J, t_run, seed in CASOS:
    bloco = (BLOCO_STT.format(J_aplicado=-J) if J > 0 else "")
    with open(f"{nome}.mx3", "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE.format(J=J, J_aplicado=-J, t_run=t_run, seed=seed,
                                 bloco_stt=bloco))
    t0 = time.perf_counter()
    r = subprocess.run([MUMAX, f"{nome}.mx3"], capture_output=True, text=True)
    dt_wall = time.perf_counter() - t0
    if r.returncode != 0:
        print(f"  {nome}: ERRO exit {r.returncode}")
        print(r.stdout[-300:], r.stderr[-300:])
        continue
    with open(f"{nome}.out/table.txt", encoding="utf-8") as fh:
        linhas = [l for l in fh if not l.startswith("#")]
    mz = np.array([float(l.split("\t")[4]) for l in linhas])
    mz_f = mz[-1]
    sin2 = float(np.mean(1.0 - mz[mz.size // 4:] ** 2))  # descarta 1º quarto
    print(f"  {nome}: J = {J/1e10:4.1f} MA/cm², {t_run*1e9:.0f} ns, seed {seed} | "
          f"wall = {dt_wall:5.0f} s | m_z final = {mz_f:+8.5f} | "
          f"m_z mín = {mz.min():+8.5f} | <1−m_z²> = {sin2:.5f} | "
          f"{'COMUTOU' if mz_f < 0 else 'nao comutou'}")

print("-" * 70)
print("LEITURA: T1 <1−m_z²> ~ 0,0085 → equipartição do MuMax3 OK (Δ=59,1).")
print("         T2 comutou → assistência térmica abaixo do limiar 0 K (indicação n=2).")
print("         wall alto (>20 min/run) → campanhas térmicas ficam para Colab/Kaggle.")

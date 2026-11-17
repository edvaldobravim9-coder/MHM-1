# -*- coding: utf-8 -*-
"""
MHM-1 — Discriminador de equipartição do MuMax3 (pós-viabilidade térmica).

Contexto: termico_viabilidade mediu <1−m_z²> = 0.107 na malha 14×14 a 300 K,
mas a referência "0,0085" impressa ali é a fórmula de MACROSPIN (1/(2Δ)) —
para uma malha de 196 células há ~392 modos térmicos e o valor esperado é
maior por construção. Este teste elimina a ambiguidade:
  1 célula (1×1×1), demag DESLIGADO (EnableDemag=false), Ku = K_eff = 1.30e5
  → paisagem de energia IDÊNTICA ao macrospin do A-0 (Δ = 59,2).
Nesse caso a fórmula macrospin É a correta: <1−m_z²> ≈ 1/(2Δ) ≈ 0,0085.
  ≈ 0,008–0,02  → FDT por célula do MuMax3 CORRETO (malha: 0.107 é contagem
                   de modos — física da discretização, instrumento são);
  ≈ 0.1         → amplitude térmica ~13× alta → investigar uso/versão.

Execução: python diag_equipart_1celula.py   (~1 min GPU)
"""
import os
import subprocess

import numpy as np

MUMAX = r"C:\Users\edval\Desktop\MHM-1\tools\mumax3.exe"

# V da camada livre do A-0: pi/4 * (40 nm)^2 * 1.5 nm = 1885 nm^3
# célula única com o MESMO volume: d^2 * 1.5 nm = 1885 nm^3 → d = 35.446 nm
D = 35.446e-9
V = D * D * 1.5e-9
K_EFF = 1.30e5          # J/m3 (B_keff = 0.4333 T do A-0)
KBT = 1.380649e-23 * 300.0
DELTA = K_EFF * V / KBT

MX3 = f"""// Discriminador equiparticao: 8 celulas independentes (2x2x2, Aex=0), demag off, 300 K, 10 ns
// NOTA API: Temp>0 exige numero PAR de celulas por eixo (RNG FFT) — 1x1x1 panica.
// Com Aex=0 as 8 celulas NAO tem acoplamento de troca → 8 macrospins independentes.
SetGridSize(2, 2, 2)
SetCellSize({D:.6e}, {D:.6e}, 1.5e-9)
Msat  = 600e3
Aex   = 0
alpha = 0.01
Ku1   = {K_EFF:.6e}
anisU = vector(0, 0, 1)
EnableDemag = false
Temp  = 300
ThermSeed(1)
m = Uniform(0.01, 0, 0.99995)
mz := m.Comp(2)
tableadd(mz)
TableAutoSave(1e-11)
run(1e-8)
tablesave()
"""

NOME = "diag_equip_1cel"
with open(f"{NOME}.mx3", "w", encoding="utf-8") as fh:
    fh.write(MX3)

print("=" * 70)
print("DISCRIMINADOR EQUIPARTIÇÃO MuMax3 — 1 célula, demag off, 300 K, 10 ns")
print("=" * 70)
print(f"  V = {V*1e27:.0f} nm³ | K_eff = {K_EFF:.2e} J/m³ | Δ = {DELTA:.1f}")
print(f"  teoria (equipartição, 2 DOF): <1−m_z²> = kT/(K_eff·V) = 1/Δ = {1/DELTA:.5f}")
print(f"         (a forma 1/(2Δ) subestima por 2 — convenção errada em v1 deste teste)")

r = subprocess.run([MUMAX, f"{NOME}.mx3"], capture_output=True, text=True)
if r.returncode != 0:
    print(f"  ERRO exit {r.returncode}")
    print(r.stdout[-400:], r.stderr[-400:])
    raise SystemExit(1)

with open(f"{NOME}.out/table.txt", encoding="utf-8") as fh:
    head = fh.readline().rstrip("\n").split("\t")
    linhas = [l for l in fh if not l.startswith("#")]

i_mz = next(i for i, h in enumerate(head) if h.strip("# ").startswith("mz"))
mz = np.array([float(l.split("\t")[i_mz]) for l in linhas])
sin2 = float(np.mean(1.0 - mz[mz.size // 4:] ** 2))  # descarta 1º quarto

print(f"  amostras: {mz.size} | m_z médio = {mz.mean():+.5f} | m_z mín = {mz.min():+.5f}")
print(f"  MEDIDO: <1−m_z²> = {sin2:.5f}")
print(f"  razão medido/teoria(1/Δ) = {sin2/(1/DELTA):.2f}  (esperado ~1 ± autocorrelação)")
print("-" * 70)
if sin2 < 0.03:
    print("LEITURA: FDT por célula do MuMax3 CORRETO → o 0.107 da malha 14×14 é")
    print("         contagem de modos (~392 DOF térmicos) — física da discretização.")
    print("         Ruído térmico do MuMax3: APROVADO para campanhas da Fase 4+.")
else:
    print("LEITURA: amplitude térmica ALTA mesmo no regime macrospin → investigar")
    print("         (referência: solver próprio A-0 tem FDT 0,994 no mesmo teste).")

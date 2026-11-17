# -*- coding: utf-8 -*-
"""
MHM-1 — Diagnóstico A-1b: sinal/inatividade do STT no MuMax3.

A-1b v1 (J > 0, 6–16 MA/cm², pulso 5 ns): nenhuma comutação, m_z final = +1,00000
exato em todas — compatível com (a) sinal do torque invertido em relação ao A-0
(risco documentado no docstring) ou (b) STT não aplicado.

Teste: J < 0 deve comutar P→AP se o mapeamento está certo e o sinal é invertido.
Runs: J = −10 e −14 MA/cm² (5 ns) e J = −8 MA/cm² (10 ns).

Execução: python diag_stt_sinal.py   (~8 min na GPU)
Saídas:   os .mx3/.out ficam na pasta; tabela impressa aqui.
"""
import os
import subprocess

MUMAX = r"C:\Users\edval\Desktop\MHM-1\tools\mumax3.exe"

TEMPLATE = """// diag STT: J = {J:+.3e} A/m2 ({ma:+.1f} MA/cm2), 0 K, {t_pulse:.0f} ns
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
J = vector(0, 0, {J:.6e})

m = Uniform(0.01, 0, 0.99995)
mz := m.Comp(2)
tableadd(mz)
TableAutoSave(1e-11)
run({t_pulse:.1e})
tablesave()
"""

CASOS = [
    ("diag_stt_jm1000", -1.0e11, 5e-9),
    ("diag_stt_jm1400", -1.4e11, 5e-9),
    ("diag_stt_jm0800", -0.8e11, 10e-9),
]

for nome, J, tp in CASOS:
    ma = J / 1e10
    with open(f"{nome}.mx3", "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE.format(J=J, ma=ma, t_pulse=tp))
    r = subprocess.run([MUMAX, f"{nome}.mx3"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  {nome}: ERRO exit {r.returncode}")
        print(r.stdout[-400:], r.stderr[-400:])
        continue
    with open(f"{nome}.out/table.txt", encoding="utf-8") as fh:
        linhas = [l for l in fh if not l.startswith("#")]
    mz_final = float(linhas[-1].split("\t")[4])
    mz_min = min(float(l.split("\t")[4]) for l in linhas)
    print(f"  {nome}: J = {ma:+5.1f} MA/cm², pulso {tp*1e9:.0f} ns | "
          f"m_z final = {mz_final:+8.5f} | m_z mín = {mz_min:+8.5f} | "
          f"{'COMUTOU' if mz_final < 0 else 'nao comutou'}")

print("FIM — leitura: comutou com J<0 → sinal invertido (ajustar varredura);")
print("      nada comuta → STT inativo (revisar API: Pol/Lambda/FixedLayer/ZhangLi).")

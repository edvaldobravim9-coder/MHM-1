# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-1a: varredura de campo quase-estática (MuMax3).

Objetivo: medir o campo de comutação B_sw da malha calibrada (35x35x1,5 nm,
células de 2,5 nm, Δ ≈ 59) e comparar com B_keff = 0,4437 T medido no relax
(smoke_test_v2). Desvio para baixo indica nucleação por bordas; coerência
quase-perfeita é esperada para parede de domínio (~33 nm) mais larga que a
amostra (35 nm).

Método:
- Temp = 0 (determinístico); m inicial inclinado 0,01 (convenção do A-0).
- Pulso B_ext = -B por 10 ns; registra m_z final de cada campo.
- B_sw = menor B com m_z(final) < 0.
- Solver RK45 adaptativo padrão (sem SetSolver/FixDt).

Execução:  python experimento_a1a.py   (11 campos × ~1-2 min; roda em background)
Saídas:    resultados_a1a/ (CSV + PNG + tabela por campo)

NOTA DE SOLVER: usar o RK45 ADAPTATIVO padrão (sem SetSolver/FixDt). Heun
explícito (solver 2) é incondicionalmente instável em precessão pura — bombeia
energia no modo de xadrez (v1 desta varredura estava contaminada; ver README).
"""
import csv
import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MUMAX = r"C:\Users\edval\Desktop\MHM-1\tools\mumax3.exe"
CAMPOS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]  # T
T_PULSO = 10e-9                                    # s
B_KEFF_MALHA = 0.4437                              # T (medido no smoke_test_v2)

TEMPLATE = """// A-1a: pulso de campo B = {B:+.4f} T ({modo})
SetGridSize(14, 14, 1)
SetCellSize(2.5e-9, 2.5e-9, 1.5e-9)
Msat  = 600e3
Aex   = 15e-12
alpha = 0.01
Ku1   = 335e3
anisU = vector(0, 0, 1)
Temp  = 0
B_ext = vector(0, 0, {B:+.4f})
m = Uniform(0.01, 0, 0.99995)
mz := m.Comp(2)
tableadd(mz)
TableAutoSave(1e-11)
run({t_pulse:.1e})
tablesave()
"""


def main():
    os.makedirs("resultados_a1a", exist_ok=True)
    print("=" * 70)
    print("A-1a: VARRedura DE CAMPO (MuMax3, Temp=0, pulso 10 ns)")
    print("=" * 70)

    resultados = []
    for i, B in enumerate(CAMPOS):
        nome = f"a1a_b{int(round(B*1000)):04d}"
        with open(f"{nome}.mx3", "w", encoding="utf-8") as fh:
            fh.write(TEMPLATE.format(B=-B, t_pulse=T_PULSO, modo="reversao"))
        r = subprocess.run([MUMAX, f"{nome}.mx3"], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  B = {B:.4f} T -> ERRO (exit {r.returncode}); abortando")
            print(r.stdout[-500:], r.stderr[-500:])
            break
        # última linha de dados do table.txt
        with open(f"{nome}.out/table.txt", encoding="utf-8") as fh:
            linhas = [l for l in fh if not l.startswith("#")]
        cols = linhas[-1].split("\t")
        mz_final = float(cols[4])
        comutou = mz_final < 0.0
        resultados.append((B, mz_final, comutou))
        print(f"  B = {B:.4f} T | m_z final = {mz_final:+8.5f} | "
              f"{'COMUTOU' if comutou else 'nao comutou'}")

    # ---- B_sw e CSV ---------------------------------------------------------
    bsw = next((B for B, mz, c in resultados if c), None)
    print("-" * 70)
    print(f"  B_sw(pulso 10 ns) = {bsw:.4f} T" if bsw else
          "  Nenhum campo comutou em 10 ns — estender varredura")
    print(f"  B_keff da malha  = {B_KEFF_MALHA:.4f} T (relax, smoke_test_v2)")
    if bsw:
        print(f"  B_sw/B_keff      = {bsw/B_KEFF_MALHA:.3f} "
              f"({'< 1: nucleacao/bordas reduzem o limiar' if bsw < B_KEFF_MALHA else '>= 1: coerente com macrospin'})")

    with open("resultados_a1a/varredura_campo.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["B_T", "mz_final", "comutou"])
        for B, mz, c in resultados:
            w.writerow([B, mz, c])
        w.writerow(["B_sw_T", bsw, ""])
        w.writerow(["B_keff_malha_T", B_KEFF_MALHA, ""])

    # ---- figura -------------------------------------------------------------
    if resultados:
        Bs, mzs, _ = zip(*resultados)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(Bs, mzs, "o-", label="m_z final (pulso 10 ns, 0 K)")
        ax.axvline(B_KEFF_MALHA, color="gray", ls="--",
                   label=f"B_keff malha = {B_KEFF_MALHA:.3f} T")
        if bsw:
            ax.axvline(bsw, color="red", ls=":",
                       label=f"B_sw = {bsw:.3f} T")
        ax.set_xlabel("B_ext (T) — campo de reversão")
        ax.set_ylabel("m_z final")
        ax.set_title("A-1a: varredura de campo quase-estática (MuMax3)")
        ax.legend()
        fig.tight_layout()
        fig.savefig("resultados_a1a/fig_varredura_campo.png", dpi=150)
    print("FIM — resultados em ./resultados_a1a/")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-1b: varredura de corrente STT no MuMax3.

Objetivo: medir J_c de comutação na MALHA REAL (nucleação, bordas, demag 2D)
e comparar com o A-0 macrospin (limiar 0 K em pulso de 5 ns: 9,5–10 MA/cm²;
J_c0 analítico: 5,54 MA/cm²). O micromagnetismo deve REDUZIR o limiar
(nucleação assistida); aumento seria sinal de malha/parâmetros errados.

Mapeamento de convenções (verificado no kernel cuda/slonczewski2.cu do MuMax3):
    beta = (ħ/e)·J/(t·Ms);  ε = pol·λ²/((λ²+1) + (λ²-1)·(p·m))
    com Λ=1 → ε = pol/2 constante → torque = (ħ/e)·J·pol/(2·t·Ms)·m×(m×p)
    = B_STT do A-0 com η = pol. Portanto: Pol = 0.40, Lambda = 1,
    EpsilonPrime = 0, FixedLayer = (0,0,1), DisableZhangLiTorque = true.

Convenção de sinal: J > 0 deve comutar P → AP (como no A-0); se o sentido
vier invertido, documentar (FixedLayerPosition afeta o sinal via espessura).

NOTA DE SOLVER: RK45 adaptativo padrão (Heun+FixDt é instável em precessão;
ver README e o A-1a). Temp = 0 → comparação direta com o limiar 0 K do A-0.

NOTA DE SINAL (16/11/2026, diag_stt_sinal.py): com FixedLayer = +z e
FIXEDLAYER_TOP, o J POSITIVO do MuMax3 ESTABILIZA P (A-1b v1: 0/8 comutou,
m_z = +1,00000 exato até 16 MA/cm²); J NEGATIVO comuta P→AP (−8 MA/cm² comuta
em 10 ns; −10 e −14 em 5 ns). Esta varredura aplica J < 0; os valores na lista
e no CSV são MAGNITUDES, com coluna do J aplicado.

Execução:  python experimento_a1b.py   (8 correntes × ~1-3 min; background)
Saídas:    resultados_a1b/ (CSV + PNG)
"""
import csv
import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MUMAX = r"C:\Users\edval\Desktop\MHM-1\tools\mumax3.exe"
# A/m² — mesma faixa do A-0 (0 K, pulso 5 ns: limiar 9,5–10 MA/cm²)
CORRENTES = [6e10, 8e10, 9e10, 1.0e11, 1.1e11, 1.2e11, 1.4e11, 1.6e11]  # A/m²
T_PULSO = 5e-9                                     # s (igual ao A-0)

TEMPLATE = """// A-1b: pulso STT J = {J:.3e} A/m2 ({ma_cm2:.1f} MA/cm2), 0 K, 5 ns
SetGridSize(14, 14, 1)
SetCellSize(2.5e-9, 2.5e-9, 1.5e-9)
Msat  = 600e3
Aex   = 15e-12
alpha = 0.01
Ku1   = 335e3
anisU = vector(0, 0, 1)
Temp  = 0

// STT Slonczewski — mapeamento exato do modelo do A-0 (ver docstring)
DisableZhangLiTorque = true
Pol = 0.40
Lambda = 1
EpsilonPrime = 0
FixedLayer = vector(0, 0, 1)
FixedLayerPosition = FIXEDLAYER_TOP
// SINAL: J negativo comuta P→AP (diag_stt_sinal.py; J positivo estabiliza P)
J = vector(0, 0, {J_aplicado:.6e})

m = Uniform(0.01, 0, 0.99995)
mz := m.Comp(2)
tableadd(mz)
TableAutoSave(1e-11)
run({t_pulse:.1e})
tablesave()
"""


def main():
    os.makedirs("resultados_a1b", exist_ok=True)
    print("=" * 70)
    print("A-1b: VARRedura DE CORRENTE STT (MuMax3, Temp=0, pulso 5 ns)")
    print("=" * 70)

    resultados = []
    for J in CORRENTES:
        ma = J / 1e10  # MA/cm² (1 MA/cm² = 1e10 A/m²) — MAGNITUDE
        nome = f"a1b_j{int(round(ma*100)):04d}"
        with open(f"{nome}.mx3", "w", encoding="utf-8") as fh:
            fh.write(TEMPLATE.format(J=J, J_aplicado=-J, ma_cm2=ma, t_pulse=T_PULSO))
        r = subprocess.run([MUMAX, f"{nome}.mx3"], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  J = {ma:.1f} MA/cm² -> ERRO (exit {r.returncode}); abortando")
            print(r.stdout[-500:], r.stderr[-500:])
            break
        with open(f"{nome}.out/table.txt", encoding="utf-8") as fh:
            linhas = [l for l in fh if not l.startswith("#")]
        cols = linhas[-1].split("\t")
        mz_final = float(cols[4])
        # extra: tempo de cruzamento m_z = 0 (1ª linha com m_z < 0)
        t_sw = float("nan")
        for l in linhas:
            c = l.split("\t")
            if float(c[4]) < 0.0:
                t_sw = float(c[0])
                break
        comutou = mz_final < 0.0
        resultados.append((ma, mz_final, comutou, t_sw))
        t_sw_str = f"{t_sw*1e9:7.3f} ns" if np.isfinite(t_sw) else "    —"
        print(f"  J = {ma:5.1f} MA/cm² | m_z final = {mz_final:+8.5f} | "
              f"{'COMUTOU' if comutou else 'nao comutou'} | t(cruzou 0) = {t_sw_str}")

    # ---- limiar e CSV --------------------------------------------------------
    jsw = next((ma for ma, mz, c, _ in resultados if c), None)
    print("-" * 70)
    if jsw:
        print(f"  J_sw(pulso 5 ns, 0 K) = {jsw:.2f} MA/cm²")
        print(f"  A-0 macrospin (0 K, 5 ns): limiar 9,5–10 MA/cm²; J_c0 analítico 5,54")
        print(f"  razão MuMax3/A-0 = {jsw/9.75:.2f} (1,0 = idêntico; <1 = nucleação reduz o limiar)")
    else:
        print("  Nenhuma corrente comutou em 5 ns — estender varredura")

    with open("resultados_a1b/varredura_stt.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["J_mag_MAcm2", "J_aplicado_MAcm2", "mz_final", "comutou", "t_cruzou_zero_s"])
        for ma, mz, c, t_sw in resultados:
            w.writerow([ma, -ma, mz, c, t_sw if np.isfinite(t_sw) else ""])
        if jsw:
            w.writerow(["J_sw_mag_MAcm2", jsw, "", "", ""])

    # ---- figura --------------------------------------------------------------
    if resultados:
        js, mzs, _, tsws = zip(*resultados)
        fig, ax1 = plt.subplots(figsize=(6.5, 4))
        ax1.plot(js, mzs, "o-", color="tab:blue", label="m_z final (pulso 5 ns, 0 K)")
        if jsw:
            ax1.axvline(jsw, color="red", ls=":", label=f"J_sw = {jsw:.2f} MA/cm²")
        ax1.axvspan(9.5, 10.0, color="gray", alpha=0.25,
                    label="limiar A-0 macrospin (0 K, 5 ns)")
        ax1.set_xlabel("J (MA/cm²)")
        ax1.set_ylabel("m_z final")
        ax2 = ax1.twinx()
        tsw_f = [t if np.isfinite(t) else np.nan for t in tsws]
        ax2.plot(js, tsw_f, "s--", color="tab:orange", label="t (cruzou m_z=0)")
        ax2.set_ylabel("t de comutação (s)")
        ax1.set_title("A-1b: comutação por STT no MuMax3 (malha real)")
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, fontsize=8)
        fig.tight_layout()
        fig.savefig("resultados_a1b/fig_varredura_stt.png", dpi=150)
    print("FIM — resultados em ./resultados_a1b/")


if __name__ == "__main__":
    main()

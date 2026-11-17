# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-2: calibração térmica do solver macrospin.

Objetivo: validar a AMPLITUDE do campo térmico implementado (Brown/
García-Palacios) no solver do A-0. Se o ruído estiver errado por um fator c,
a inclinação medida de ln(taxa) vs Δ será −1/c em vez de −1.

Método:
- Varre Δ reduzindo o VOLUME da célula (K_eff e B_keff fixos, macrospin válido).
  Δ = K_eff·V/(k_B·T) com raios 5 / 6,2 / 7,5 nm → Δ ≈ 3,7 / 5,7 / 8,3.
- Mede a taxa de comutação espontânea a 300 K (J = 0) via primeira passagem
  por m_z = −0,9, estimador de máxima verossimilhança para processo de Poisson:
      rate = −ln(1 − f)/W ,  f = fração de trajetórias que comutaram na janela W.
- Verifica lei de Néel-Arrhenius: rate = f0·exp(−Δ) → ln(rate) vs Δ deve dar
  inclinação ≈ −1 e intercepto ≈ ln(f0) (ordem de grandeza de γ·B_keff/2π).

Execução:  python experimento_a2.py    (~4–6 min no i3-10105F)
Saídas:    resultados_a2/ (CSV + PNG)
"""
import csv
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin, GAMMA

T = 300.0
RAIOS = [5e-9, 6.2e-9, 7.5e-9]      # m  → Δ ≈ 3,7 / 5,7 / 8,3
N_RUNS = 80
DT = 1e-12                          # s (1 ps; ω·dt ≈ 0,076, estável p/ RK4)
FATOR_JANELA = 2.5                  # janela = 2,5 × dwell analítico estimado
SEED = 123

def main():
    os.makedirs("resultados_a2", exist_ok=True)
    print("=" * 70)
    print("A-2: CALIBRACAO TERMICA (extracao de Delta por fuga espontanea, 300 K)")
    print("=" * 70)

    linhas = []
    for r in RAIOS:
        p = replace(ParametrosMTJ(), diametro=2.0 * r, T=T)
        sim = SimuladorMacrospin(p, seed=SEED)
        delta = p.delta
        # Prefactor de Brown (1963) para LLG com amortecimento baixo:
        # a fuga sobre a barreira e conduzida pelo amortecimento -> f0 ~ alpha.
        # Sem o fator alpha a janela fica ~1/alpha vezes curta demais
        # (execucao v1: 0 flips em todas as configuracoes por esse motivo).
        f0_teo = (p.alpha * GAMMA * p.B_keff / (2.0 * np.pi)) * np.sqrt(delta / np.pi)
        dwell_teo = np.exp(delta) / f0_teo
        jan = min(FATOR_JANELA * dwell_teo, 5e-6)

        res = sim.run_pulse(0.0, t_pulse=0.0, dt=DT, T=T, n_runs=N_RUNS, t_tail=jan)
        comutou = np.isfinite(res["t_sw"])
        n_flip = int(np.sum(comutou))
        f = n_flip / N_RUNS
        if f < 1.0:
            rate = -np.log(1.0 - f) / jan
            rate_inf = rate_sup = rate
        else:  # todas comutaram → apenas limite inferior da taxa
            rate = float("nan")
            rate_inf = -np.log(1.0 / N_RUNS) / jan
            rate_sup = float("inf")
        t_first_med = res["t_sw"][comutou].mean() if n_flip > 0 else float("nan")

        print(f"  raio = {r*1e9:4.1f} nm | Delta = {delta:5.2f} | flips = {n_flip:2d}/{N_RUNS}"
              f" | t_primeiro_med = {t_first_med*1e9:7.2f} ns")
        print(f"      rate = {rate:.3e} /s (teoria: f0*exp(-Delta) ="
              f" {f0_teo * np.exp(-delta):.3e} /s, f0 = {f0_teo:.2e} Hz)")

        linhas.append((r * 1e9, delta, n_flip, jan * 1e9, rate, rate_inf, rate_sup, f0_teo))

    # ---- ajuste da inclinação de ln(rate) vs Δ ------------------------------
    d = np.array([l[1] for l in linhas])
    r_tx = np.array([l[4] if np.isfinite(l[4]) else l[5] for l in linhas])
    ok = r_tx > 0
    if ok.sum() >= 2:
        slope, ln_f0ef = np.polyfit(d[ok], np.log(r_tx[ok]), 1)
    else:
        slope, ln_f0ef = float("nan"), float("nan")
        print("  AVISO: menos de 2 taxas positivas — ajuste impossivel (aumente a janela).")
    print("-" * 70)
    print(f"  Inclinacao medida: {slope:.3f}  (esperado: -1.000 se o ruido esta calibrado)")
    print(f"  f0 efetivo medido: {np.exp(ln_f0ef):.2e} Hz (ordem de grandeza de gamma*Bk/2pi)")

    with open("resultados_a2/calibracao_termica.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["raio_nm", "Delta_kBT", "flips", "janela_ns",
                    "rate_s-1", "rate_inf_s-1", "rate_sup_s-1", "f0_teorico_Hz"])
        for l in linhas:
            w.writerow([l[0], l[1], l[2], l[3],
                        l[4] if np.isfinite(l[4]) else "",
                        l[5], l[6] if np.isfinite(l[6]) else "", l[7]])
        w.writerow(["inclinacao_ln_rate_vs_Delta", slope])
        w.writerow(["f0_efetivo_Hz", np.exp(ln_f0ef)])

    # ---- figura -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = d[ok]
    ys = np.log(r_tx[ok])
    # barras de erro assimétricas a partir dos limites inferior/superior
    err_low = ys - np.log([l[5] if np.isfinite(l[5]) else v for l, v in zip(linhas, r_tx[ok])])
    err_high = np.log([l[6] if np.isfinite(l[6]) else v for l, v in zip(linhas, r_tx[ok])]) - ys
    ax.errorbar(xs, ys, yerr=[err_low, err_high], fmt="o", capsize=3,
                label="simulação (80 trajetórias)")
    dd = np.linspace(d.min() - 0.5, d.max() + 0.5, 50)
    f0_teo = linhas[0][7]
    ax.plot(dd, np.log(f0_teo) - dd, "--", label="Néel-Arrhenius: f₀·e^(−Δ)")
    ax.plot(dd, ln_f0ef + slope * dd, ":", label=f"ajuste: inclinação {slope:.2f}")
    ax.set_xlabel("Δ = K_eff·V / (k_B·T)")
    ax.set_ylabel("ln(taxa de comutação) [1/s]")
    ax.set_title("A-2: calibração do campo térmico do solver")
    ax.legend()
    fig.tight_layout()
    fig.savefig("resultados_a2/fig_calibracao_termica.png", dpi=150)
    print("FIM — resultados em ./resultados_a2/")

if __name__ == "__main__":
    main()

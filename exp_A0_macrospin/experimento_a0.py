# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-0: célula MTJ individual (macrospin STT).

O que este experimento faz (e o que NÃO faz):
  FAZ:   (1) relatório analítico da célula (Δ, R_P/AP, J_c0, retenção);
         (2) varredura a T=0: tempo de comutação × densidade de corrente;
         (3) varredura a 300 K: probabilidade de comutação × J × duração do pulso;
         (4) teste de retenção sem corrente (300 K, 5 ns × 40 trajetórias);
         (5) estimativa de energia de escrita por pulso (nível célula).
  NÃO FAZ: efeitos de nucleação de domínios (ver A-1/MuMax3), elétrica do sense
           amplifier, latência de matriz, comutação SOT/VCMA (Experimentos B/C).

Execução:   python experimento_a0.py
Saídas:     ./resultados/*.csv e *.png  + resumo no console
"""
import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parametros import ParametrosMTJ, MU0
from llgs_macrospin import SimuladorMacrospin, GAMMA, K_B

MA_CM2 = 1e10        # 1 MA/cm² = 1e10 A/m²
ANO_S = 365.25 * 24 * 3600.0
FEMTO = 1e15

def cab(titulo):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)

def main():
    p = ParametrosMTJ()
    sim = SimuladorMacrospin(p, seed=42)
    os.makedirs("resultados", exist_ok=True)

    # ================================================================ 1) Analítico
    cab("1) PARAMETROS DA CELULA (ANALITICO)")
    delta_req_10a = np.log((GAMMA * p.B_keff / (2 * np.pi)) * (10.0 * ANO_S))
    print(f"  Diametro x espessura da camada livre : {p.diametro*1e9:.0f} nm x {p.t_FL*1e9:.1f} nm")
    print(f"  Volume da camada livre               : {p.volume:.3e} m^3")
    print(f"  B_keff = 2*Keff/Ms                   : {p.B_keff*1e3:.1f} mT")
    print(f"  Delta (barreira termica)             : {p.delta:.1f} k_B*T")
    print(f"  Delta minimo p/ retencao de 10 anos  : ~{delta_req_10a:.0f}  (criterio Neel-Arrhenius)")
    print(f"  R(P) / R(AP)                         : {p.R_P/1e3:.2f} / {p.R_AP/1e3:.2f} kohm")
    J_c0 = sim.J_c0()
    print(f"  J_c0 macrospin (0 K, analitico)      : {J_c0/MA_CM2:.2f} MA/cm^2")
    print(f"  I_c0 correspondente                  : {J_c0*p.area_MJ*1e6:.1f} uA")
    print(f"  Frequencia de precessao f0 ~ g*Bk/2pi: {GAMMA*p.B_keff/(2*np.pi)/1e9:.1f} GHz")

    with open("resultados/resumo_celula.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["grandeza", "valor", "unidade"])
        w.writerow(["diametro", p.diametro * 1e9, "nm"])
        w.writerow(["espessura_FL", p.t_FL * 1e9, "nm"])
        w.writerow(["Ms", p.Ms, "A/m"])
        w.writerow(["K_eff", p.K_eff, "J/m3"])
        w.writerow(["alpha", p.alpha, "-"])
        w.writerow(["B_keff", p.B_keff, "T"])
        w.writerow(["Delta", p.delta, "kBT"])
        w.writerow(["R_P", p.R_P, "ohm"])
        w.writerow(["R_AP", p.R_AP, "ohm"])
        w.writerow(["TMR", p.TMR * 100, "%"])
        w.writerow(["J_c0_macrospin", J_c0 / MA_CM2, "MA/cm2"])
        w.writerow(["I_c0", J_c0 * p.area_MJ * 1e6, "uA"])

    # ================================================================ 2) Varredura T=0
    cab("2) VARREDURA A T=0 K: TEMPO DE COMUTACAO x CORRENTE (pulso de 5 ns)")
    Js0 = np.array([2.0, 3.0, 4.0, 5.0, 5.5, 6.0, 8.0, 10.0, 12.0, 16.0]) * MA_CM2
    r0 = sim.run_pulse(Js0, t_pulse=5e-9, dt=0.5e-12, T=0.0, t_tail=2e-9)

    linhas0 = []
    for i, J in enumerate(Js0):
        comutou = bool(r0["comutou"][i])
        tsw = r0["t_sw"][i]
        linhas0.append((J / MA_CM2, comutou, (tsw * 1e9) if np.isfinite(tsw) else None))
        if comutou:
            print(f"  J = {J/MA_CM2:4.1f} MA/cm^2 : comutou em {tsw*1e9:5.2f} ns")
        else:
            print(f"  J = {J/MA_CM2:4.1f} MA/cm^2 : NAO comutou em 5 ns")

    com = [l for l in linhas0 if l[1]]
    if com:
        J_limiar = min(l[0] for l in com)
        print(f"  --> Limiar macrospin simulado (~5 ns): entre {J_limiar-0.5:.1f} e {J_limiar:.1f} MA/cm^2"
              f"  (analitico: {J_c0/MA_CM2:.2f})")

    with open("resultados/varredura_T0.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["J_MAcm2", "comutou_5ns", "t_sw_ns"])
        for row in linhas0:
            w.writerow([row[0], row[1], row[2] if row[2] is not None else ""])

    # ================================================================ 3) Varredura 300 K
    cab("3) VARREDURA A 300 K: PROBABILIDADE DE COMUTACAO (40 trajetorias/ponto)")
    J_th = np.array([3.0, 4.5, 5.2, 6.0, 8.0, 10.0, 12.0]) * MA_CM2
    pulsos = [1e-9, 2e-9, 5e-9]
    N_RUNS = 40
    dt_th = 0.25e-12
    linhas_th = []
    # vetorização: todas as (correntes x trajetorias) integradas juntas
    J_batch = np.repeat(J_th, N_RUNS)
    for tp in pulsos:
        r = sim.run_pulse(J_batch, t_pulse=tp, dt=dt_th, T=300.0, t_tail=2e-9)
        comut = r["comutou"].reshape(len(J_th), N_RUNS)
        tsw = r["t_sw"].reshape(len(J_th), N_RUNS)
        for i in range(len(J_th)):
            P = comut[i].mean()
            tmed = tsw[i][comut[i]].mean() * 1e9 if comut[i].any() else float("nan")
            linhas_th.append((tp * 1e9, J_th[i] / MA_CM2, P, tmed))
            print(f"  pulso {tp*1e9:.0f} ns | J = {J_th[i]/MA_CM2:4.1f} MA/cm^2 :"
                  f" P(comutar) = {P*100:5.1f}%  t_medio = {tmed:5.2f} ns")

    with open("resultados/termico_300K.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pulso_ns", "J_MAcm2", "P_comutacao", "t_sw_medio_ns"])
        w.writerows(linhas_th)

    # ================================================================ 4) Retenção
    cab("4) TESTE DE RETENCAO (J=0, 300 K, 5 ns, 40 trajetorias)")
    rr = SimuladorMacrospin(p, seed=7).run_pulse(0.0, t_pulse=0.0, dt=0.25e-12,
                                                 T=300.0, n_runs=40, t_tail=5e-9)
    flips = int(np.sum(rr["comutou"]))
    print(f"  Comutacoes espontaneas em 5 ns x 40 trajetorias: {flips}")
    print(f"  (esperado: 0, pois Delta = {p.delta:.0f} >> ln(f0*t); verificacao de")
    print(f"   retencao de 10 ANOS requer analise acelerada — Experimento A-2)")

    # ================================================================ 5) Energia
    cab("5) ENERGIA DE ESCRITA POR PULSO (nive celula, sem periferica)")
    A = p.area_MJ
    R_med = 0.5 * (p.R_P + p.R_AP)
    linhas_e = []
    for tp in pulsos:
        for J in J_th:
            I = J * A
            E = I * I * R_med * tp
            linhas_e.append((tp * 1e9, J / MA_CM2, E * FEMTO))
            print(f"  pulso {tp*1e9:.0f} ns | J = {J/MA_CM2:4.1f} MA/cm^2 :"
                  f" E = {E*FEMTO:7.1f} fJ ({E*1e12:5.2f} pJ)")
    with open("resultados/energia_escrita.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pulso_ns", "J_MAcm2", "E_fJ"])
        w.writerows(linhas_e)

    # ================================================================ 6) Figuras
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    xs = [l[0] for l in linhas0 if l[1]]
    ys = [l[2] for l in linhas0 if l[1]]
    ax1.plot(xs, ys, "o-")
    ax1.axvline(J_c0 / MA_CM2, ls="--", color="gray", label=f"J_c0 analitico = {J_c0/MA_CM2:.2f}")
    ax1.set_xlabel("Densidade de corrente (MA/cm$^2$)")
    ax1.set_ylabel("Tempo de comutação (ns)")
    ax1.set_title("A-0: comutação a 0 K (macrospin)")
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig("resultados/fig_tsw_vs_J.png", dpi=150)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for tp in pulsos:
        pts = [(l[1], l[2]) for l in linhas_th if abs(l[0] - tp * 1e9) < 1e-12]
        ax2.plot([q[0] for q in pts], [q[1] * 100 for q in pts], "o-",
                 label=f"pulso {tp*1e9:.0f} ns")
    ax2.axvline(J_c0 / MA_CM2, ls="--", color="gray", label="J_c0 analitico")
    ax2.set_xlabel("Densidade de corrente (MA/cm$^2$)")
    ax2.set_ylabel("P(comutar) em 40 trajetórias (%)")
    ax2.set_title("A-0: comutação térmica a 300 K")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig("resultados/fig_prob_vs_J.png", dpi=150)

    # trajetórias ilustrativas a 300 K
    rt = SimuladorMacrospin(p, seed=1).run_pulse(8.0 * MA_CM2, t_pulse=2e-9,
                                                 dt=0.25e-12, T=300.0, n_runs=8,
                                                 t_tail=1e-9, store_hist=True)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    t_axis = np.arange(rt["hist"].shape[0]) * rt["hist_dt"] * 1e9
    ax3.plot(t_axis, rt["hist"][:, :], lw=0.8)
    ax3.axvline(2.0, ls="--", color="k", lw=0.8)
    ax3.set_xlabel("Tempo (ns)")
    ax3.set_ylabel("m$_z$")
    ax3.set_title("A-0: m$_z$(t) a 300 K, J = 8 MA/cm$^2$ (8 trajetórias)")
    fig3.tight_layout()
    fig3.savefig("resultados/fig_trajetorias.png", dpi=150)

    cab("FIM — resultados em ./resultados/")

if __name__ == "__main__":
    main()

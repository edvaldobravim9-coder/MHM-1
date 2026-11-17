# -*- coding: utf-8 -*-
"""
MHM-1 — Diagnóstico do ruído térmico do solver A-0 (após A-2 v2: 0/80 flips).

Três testes independentes (r = 5 nm, Δ = 3,7; dt = 1 ps; J = 0):

  D1. Equipartição/FDT a 300 K: a distribuição estacionária de θ deve seguir
      Boltzmann P(θ) ∝ exp(−Δ·sin²θ). Métrica: <sin²θ> = <1 − m_z²>.
      Teoria (integração numérica exata): <sin²θ> = ∫ sin²θ·e^(−Δ sin²θ) sinθ dθ /
                                             ∫ e^(−Δ sin²θ) sinθ dθ.
      Se o ruído estiver com amplitude errada, <1−m_z²> medido desvia desse alvo.

  D2. Fuga a T alta (3000 K, Δ_eff = 0,37): cruzamentos de m_z < 0 em 20 ns
      devem ser FREQUENTES se a dinâmica de fuga funciona.

  D3. Controle T = 0: m_z deve ficar ≈ +1 (sem difusão espúria).

Execução: python diag_ruido.py   (~1 min)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin, K_B

T = 300.0
RAIO = 5e-9
DT = 1e-12
N_RUNS = 160

def sin2_med_teorico(delta):
    """<sin²θ> na distribuição de Boltzmann uniaxial (integração numérica fina)."""
    th = np.linspace(0, np.pi / 2, 200001)
    w = np.exp(-delta * np.sin(th) ** 2) * np.sin(th)
    num = np.trapezoid(np.sin(th) ** 2 * w, th)
    den = np.trapezoid(w, th)
    return num / den

def run(T_k, t_obs, seed=123):
    p = ParametrosMTJ(diametro=2 * RAIO, T=T_k)
    sim = SimuladorMacrospin(p, seed=seed)
    res = sim.run_pulse(0.0, t_pulse=0.0, dt=DT, T=T_k, n_runs=N_RUNS,
                        t_tail=t_obs, store_hist=True, hist_every=5)
    sigma = (np.sqrt(2 * p.alpha * K_B * T_k /
                     (1.7609e11 * p.Ms * p.volume * DT)) if T_k > 0 else 0.0)
    return p, sim, res, sigma

def main():
    print("=" * 72)
    print("DIAG RUIDO — equipartição (D1), fuga a T alta (D2), controle 0 K (D3)")
    print("=" * 72)

    # ---- D1: 300 K, 20 ns ----------------------------------------------------
    p, sim, res, sigma = run(T, 20e-9)
    hist = res["hist"]                      # (n_amostras, n_runs) m_z
    dt_h = res["hist_dt"]
    n_trans = int(round(2e-9 / dt_h))       # descarta 2 ns iniciais (transiente)
    mz = hist[n_trans:, :].ravel()
    sin2 = np.mean(1.0 - mz**2)
    alvo = sin2_med_teorico(p.delta)
    print(f"\n[D1] 300 K | Δ = {p.delta:.2f} | σ(B_th)/passo = {sigma*1e3:.1f} mT "
          f"| V = {p.volume*1e25:.3e} m³")
    print(f"     <1−m_z²> medido   = {sin2:.4f}   (amostras: {mz.size})")
    print(f"     <sin²θ> Boltzmann = {alvo:.4f}   (Δ = {p.delta:.2f})")
    print(f"     razão med/teoria  = {sin2/alvo:.3f}   (1,0 = FDT correta)")
    print(f"     m_z: min {mz.min():+.4f} | p1 {np.percentile(mz,1):+.4f} | "
          f"mediana {np.median(mz):+.4f}")
    print(f"     fração de amostras com m_z < 0: {np.mean(mz < 0):.5f}")

    # ---- D2: 3000 K, 20 ns ---------------------------------------------------
    p3, sim3, res3, sigma3 = run(3000.0, 20e-9, seed=777)
    n_cross = int(np.sum(np.isfinite(res3["t_sw"])))
    print(f"\n[D2] 3000 K | Δ_eff = {p3.delta:.2f} | σ = {sigma3*1e3:.1f} mT/passo")
    print(f"     cruzamentos m_z<0: {n_cross}/{N_RUNS} trajetórias em 20 ns "
          f"(t_med = {np.nanmean(res3['t_sw'])*1e9:.2f} ns)")

    # ---- D3: 0 K, 20 ns ------------------------------------------------------
    p0, sim0, res0, _ = run(0.0, 20e-9, seed=42)
    mz0 = res0["hist"].ravel() if "hist" in res0 else res0["mz_final"]
    print(f"\n[D3] 0 K | m_z final: min {res0['mz_final'].min():+.6f} "
          f"| máx desvio de 1: {abs(res0['mz_final']-1).max():.2e}")

    print("-" * 72)
    print("LEITURA: D1 razão ≠ 1 → amplitude do ruído errada;")
    print("         D1 ≈ 1 mas A-2 dá 0 flips → problema na DINÂMICA de fuga (não amplitude).")

if __name__ == "__main__":
    main()

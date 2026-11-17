# -*- coding: utf-8 -*-
"""
MHM-1 — Diagnóstico A-2: convergência do integrador vs dt (pós-v3).

A-2 v3 mediu taxas de fuga 4–5,6× acima da fórmula de Brown (1963) com
inclinação MFP ≈ −0,85 (vs −1 assintótico) no regime Δ = 3,7–8,3. Duas causas
possíveis, que este teste separa:
  (a) física real: Brown é assintótico (Δ≫1) e degrada em Δ baixo;
  (b) artefato de dt: RK4 com ruído congelado em dt = 1 ps.
Se a taxa CONVERGIR com dt menor → (a); se deslocar sistematicamente → (b).

Protocolo: Δ = 5,69 (r = 6,2 nm), 80 trajetórias, janela 4,52 µs.
  dt = 1,0 ps (A-2 v3, referência): MFP 330 ns → 3,03e6/s
  dt = 0,5 ps (este teste, ~85 min)
Extras baratos: equipartição D1 a dt = 0,25 ps (2 min).

Execução: python diag_dt_convergencia.py   (background, ~1,5 h)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_macrospin import SimuladorMacrospin

T = 300.0
RAIO = 6.2e-9
N_RUNS = 80
JANELA = 4.52e-6

def medir(dt):
    p = ParametrosMTJ(diametro=2 * RAIO, T=T)
    sim = SimuladorMacrospin(p, seed=123)
    res = sim.run_pulse(0.0, t_pulse=0.0, dt=dt, T=T, n_runs=N_RUNS,
                        t_tail=JANELA)
    cruzou = np.isfinite(res["t_sw"])
    f = cruzou.mean()
    rate_mle = -np.log(1.0 - f) / JANELA if f < 1 else float("nan")
    mfp = res["t_sw"][cruzou].mean() if cruzou.any() else float("nan")
    rate_mfp = 1.0 / mfp if np.isfinite(mfp) else float("nan")
    return f, rate_mle, mfp, rate_mfp

def equipart(dt, t_obs=20e-9, n=160):
    p = ParametrosMTJ(diametro=2 * 5e-9, T=T)
    sim = SimuladorMacrospin(p, seed=123)
    res = sim.run_pulse(0.0, t_pulse=0.0, dt=dt, T=T, n_runs=n, t_tail=t_obs,
                        store_hist=True, hist_every=5)
    hist = res["hist"]
    n_trans = int(round(2e-9 / res["hist_dt"]))
    mz = hist[n_trans:, :].ravel()
    return np.mean(1.0 - mz**2)   # teoria (Δ=3,70): 0,3171

def main():
    print("=" * 72)
    print("DIAG dt-CONVERGÊNCIA (Δ = 5,69, r = 6,2 nm, janela 4,52 µs, 80 traj)")
    print("=" * 72)
    print("  referência dt=1,0 ps (A-2 v3): MFP 330,1 ns → taxa 3,03e6/s | "
          "80/80 comutaram")
    print("-" * 72)

    for dt in (0.5e-12,):
        f, rate_mle, mfp, rate_mfp = medir(dt)
        print(f"  dt = {dt*1e12:.2f} ps: comutaram {int(f*N_RUNS)}/{N_RUNS} | "
              f"MFP = {mfp*1e9:7.1f} ns | taxa(MFP) = {rate_mfp:.3e} /s | "
              f"taxa(MLE) = {rate_mle:.3e} /s")

    s2 = equipart(0.25e-12)
    print(f"\n  equipartição dt = 0,25 ps: <1−m_z²> = {s2:.4f} "
          f"(teoria 0,3171; razão {s2/0.3171:.3f})")
    print("-" * 72)
    print("LEITURA: taxa(MFP) ≈ 3,0e6 (≈ dt=1 ps) → desvio vs Brown é FÍSICA de Δ baixo;")
    print("         taxa deslocando p/ baixo com dt menor → artefato; refazer A-2 com dt menor.")

if __name__ == "__main__":
    main()

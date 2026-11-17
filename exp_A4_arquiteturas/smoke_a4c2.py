# -*- coding: utf-8 -*-
"""Smoke test do A-4c2 (V1 rápida + V2) — sanity antes da campanha."""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ
from llgs_ferrimagnetico import SimuladorFerrimagnetico

KB = 1.380649e-23

# V1 0 K: 8 MA/cm² deve comutar em ~4,4 ns (A-0 v2)
sim = SimuladorFerrimagnetico(Ms1=6.0e5, Ms2=1.0, K_total=1.3e5, t_FL=1.5e-9,
                              diametro=40e-9, alpha1=0.01, B_ex0=0.0,
                              frac_K1=1.0, seed=123, ativo2=False)
r = sim.run_pulse(8e10, t_pulse=5e-9, dt=1e-12, T=0.0, n_runs=1, t_tail=1e-9)
print("V1 0K J=8:", "comutou" if r["comutou"][0] else "NAO",
      f"t_sw={r['t_sw'][0]*1e9:.2f} ns" if np.isfinite(r["t_sw"][0]) else "",
      f"mz1f={r['mz1_final'][0]:+.3f}")

# V2: par AF rígido
K = 59.2 * KB * 300 / (np.pi * (15e-9) ** 2 * 1e-9)
sim2 = SimuladorFerrimagnetico(Ms1=4e5, Ms2=3.8e5, K_total=K, t_FL=1e-9,
                               diametro=30e-9, B_ex0=500.0, seed=7)
r = sim2.run_pulse(0.0, t_pulse=2e-9, dt=1e-14, T=0.0, n_runs=1, t_tail=0.0)
print(f"V2 AF: m1z={r['mz1_final'][0]:+.6f} m2z={r['mz2_final'][0]:+.6f} "
      f"delta={sim2.delta():.1f}")

# V3 pontual 300 K: r=0.95, J=2 MA/cm², 2 ns, 20 traj (só ver se roda e dá sinal)
sim3 = SimuladorFerrimagnetico(Ms1=4e5, Ms2=3.8e5, K_total=K, t_FL=1e-9,
                               diametro=30e-9, B_ex0=500.0, seed=123)
import time
t0 = time.time()
r = sim3.run_pulse(2e10, t_pulse=2e-9, dt=1e-14, T=300.0, n_runs=20, t_tail=1e-9)
print(f"V3 ponto r=0.95 J=2: P={r['comutou'].mean()*100:.0f}% "
      f"({time.time()-t0:.1f} s / 20 traj)")

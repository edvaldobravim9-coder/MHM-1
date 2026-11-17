# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4d: MARGEM DE LEITURA dos designs vencedores (A-4b).

O ponto fraco declarado: sinal TMR pequeno (150%) + sense amplifier difícil.
Este experimento quantifica o problema e os ataques, no nível de análise de
rede (pré-SPICE; a Fase 6 refina com ngspice/Xyce):

Modelos (todos paramétricos, fontes pendentes marcadas):
  TMR(V) = TMR_0 / cosh(|V|/V_c)   — degradação de TMR com viés [V_c ~ 0,5 V,
                                     típico; SEM fonte ainda (busca 402)]
  Caminho: V_read → R_on (transistor de seleção) → MTJ(R_P/R_AP(V)) → GND
  C_BL = capacitância da bitlinha (50 fF pequeno array; 500 fF grande)
  Ruído de decisão: σ_kTC = √(kT/C_BL) + offset de SA (paramétrico, 2 mV)
  Disturb de leitura: I_read deve ficar ≤ I_c0/5 (margem 5×)

Esquemas:
  SE  — single-ended com referência (padrão da indústria)
  PAR — par diferencial H3-lite (2 células, estados opostos): sinal ×2,
        offset comum cancelado

Grid: designs {40 nm baseline; 30 nm ponto-doce; 20 nm rápido} ×
      TMR_0 {150, 300, 600}% × V_read {0,1; 0,2; 0,3} V ×
      R_on {1, 3} kΩ × C_BL {50, 500} fF × esquema {SE, PAR}.

Métricas: ΔV no nó de sense, t_leitura (3·RC, 95% da excursão), margem de
disturb, VEREDITO (leitura ok se ΔV > 10 mV, t < 5 ns, disturb ok).

Execução: python experimento_a4d.py   (~segundos; análise de rede, não LLG)
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "exp_A0_macrospin"))
from parametros import ParametrosMTJ

KB = 1.380649e-23
T = 300.0
DELTA = 59.2
RA = 10e-12          # Ω·m² (fixo do projeto; tunel de condutância ignorado)
TMR0S = [1.5, 3.0, 6.0]
V_READS = [0.1, 0.2, 0.3]
V_C = 0.5            # V — degradação de TMR (SEM FONTE — pendência 402)
R_ONS = [1e3, 3e3]
C_BLS = [50e-15, 500e-15]
V_OFFSET = 2e-3      # offset do SA (paramétrico)
MARGEM_DISTURB = 5.0

# (d, t_FL, Ms) — baseline + vencedores do A-4b
DESIGNS = [
    ("baseline 40", 40e-9, 1.5e-9, 6.0e5),
    ("doce 30",     30e-9, 1.0e-9, 4.0e5),
    ("rapido 20",   20e-9, 1.0e-9, 4.0e5),
]

os.makedirs("resultados_a4d", exist_ok=True)

print("=" * 88)
print("A-4d: MARGEM DE LEITURA — sinal, tempo e disturb por design/esquema")
print("=" * 88)
print(f"  modelos: TMR(V)=TMR0/cosh(V/{V_C} V) [V_c sem fonte] | ruído=kT/C+"
      f"{V_OFFSET*1e3:.0f} mV | disturb ≤ I_c0/{MARGEM_DISTURB:.0f}")
print(f"  veredito: ΔV > 10 mV, t_read < 5 ns, disturb ok")

linhas = []
resumo = {}
for (nome, d, t_fl, Ms) in DESIGNS:
    V_cell = np.pi * (d / 2) ** 2 * t_fl
    K_eff = DELTA * KB * T / V_cell
    p = ParametrosMTJ(Ms=Ms, K_eff=K_eff, alpha=0.01, t_FL=t_fl, diametro=d, T=T)
    R_P0 = p.R_P
    # I_c0 do design (macrospin analítico)
    from llgs_macrospin import SimuladorMacrospin
    I_c0 = SimuladorMacrospin(p, seed=3).J_c0() * p.area_MJ

    print(f"\n{nome}: d = {d*1e9:.0f} nm, t = {t_fl*1e9:.1f} nm, Ms = {Ms/1e5:.0f}e5 | "
          f"R_P = {R_P0/1e3:.1f} kΩ | I_c0 = {I_c0*1e6:.1f} µA")
    melhor_cfg = None
    for tmr0 in TMR0S:
        for v_read in V_READS:
            # TMR degradado no ponto de operação (valor médio entre os estados)
            v_med = v_read / 2.0
            tmr_v = tmr0 / np.cosh(v_med / V_C)
            r_p = R_P0 / (1 + v_med / (3 * V_C))          # R_P também cai com viés
            r_ap = r_p * (1 + tmr_v)
            for r_on in R_ONS:
                for c_bl in C_BLS:
                    # correntes no estado P e AP (célula + seletor)
                    i_p = v_read / (r_on + r_p)
                    i_ap = v_read / (r_on + r_ap)
                    i_read = max(i_p, i_ap)
                    # nó de sense: queda no MTJ (referência SE: célula de referência
                    # em R médio — o SA decide V_BL vs V_ref)
                    v_p = i_p * r_p
                    v_ap = i_ap * r_ap
                    dv_se = abs(v_p - v_read * r_p / (r_on + r_p * (1 + tmr0 / 2 / (1 + tmr0 / 2))))
                    # referência realista: R_ref = (R_P+R_AP)/2 no MESMO caminho
                    r_ref = r_on + (r_p + r_ap) / 2
                    v_ref = v_read * ((r_p + r_ap) / 2) / r_ref
                    dv_se = abs(v_p - v_ref) + abs(v_ap - v_ref)
                    dv_se /= 2.0                            # pior caso dos dois lados
                    dv_par = abs(v_p - v_ap)                # PAR: diferença direta
                    sigma = np.sqrt(KB * T / c_bl) + V_OFFSET
                    rc = (r_on + r_p / 2) * c_bl            # aproximação
                    t_read = 3 * rc
                    for esquema, dv, gain_noise in (("SE", dv_se, 1.0), ("PAR", dv_par, 1.0)):
                        # PAR: ruído comum cancelado → σ efetivo só kTC+intrinsic
                        sigma_eff = sigma * gain_noise if esquema == "SE" else \
                            np.sqrt(KB * T / c_bl) + V_OFFSET / 2
                        margem = dv / sigma_eff
                        disturb_ok = i_read <= I_c0 / MARGEM_DISTURB
                        ok = (dv > 10e-3) and (t_read < 5e-9) and disturb_ok
                        linhas.append([nome, d * 1e9, tmr0 * 100, v_read, r_on / 1e3,
                                       c_bl * 1e15, esquema, dv * 1e3, t_read * 1e9,
                                       i_read * 1e6, I_c0 * 1e6, margem, ok])
                        if ok and (melhor_cfg is None or margem > melhor_cfg[0]):
                            melhor_cfg = (margem, tmr0, v_read, r_on, c_bl, esquema,
                                          dv, t_read)
    if melhor_cfg:
        margem, tmr0, v_read, r_on, c_bl, esquema, dv, t_read = melhor_cfg
        print(f"  MELHOR configuração viável: TMR0 = {tmr0*100:.0f}%, V_read = {v_read:.2f} V, "
              f"R_on = {r_on/1e3:.0f} kΩ, C_BL = {c_bl*1e15:.0f} fF, {esquema} → "
              f"ΔV = {dv*1e3:.1f} mV, t = {t_read*1e9:.1f} ns, margem {margem:.1f}σ")
        resumo[nome] = melhor_cfg
    else:
        print("  NENHUMA configuração viável no grid — ampliar (SOT-read, material).")
        resumo[nome] = None

print("-" * 88)
print("COMPARAÇÃO (melhor por design):")
for nome, mc in resumo.items():
    if mc:
        print(f"  {nome}: margem {mc[0]:.1f}σ, {mc[6]*1e3:.1f} mV, {mc[7]*1e9:.1f} ns, "
              f"TMR0 {mc[1]*100:.0f}%, {mc[5]}")

with open("resultados_a4d/a4d_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["design", "d_nm", "TMR0_pct", "V_read_V", "R_on_kohm", "C_BL_fF",
                "esquema", "dV_mV", "t_read_ns", "I_read_uA", "I_c0_uA",
                "margem_sigma", "viavel"])
    for l in linhas:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4d/")

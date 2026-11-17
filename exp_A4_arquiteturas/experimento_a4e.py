# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-4e: auditoria de TENSÃO DE ESCRITA (breakdown da barreira)
e busca da JANELA VIÁVEL de R_A — ataque ao ponto fraco "endurance/breakdown".

Motivação (achado ao auditar a Fase 4 contra o mercado, a pedido do usuário):
com R_A = 10 Ω·µm² fixo desde o A-0, a corrente de escrita (J_90 × área)
atravessa o MTJ com R ~ kΩ → V_barreira = I×R pode EXCEDER o breakdown do
MgO. Se sim, os designs de 20–30 nm morrem por endurance antes de qualquer
leitura. Alavanca de correção: R_A é uma escolha de fabricação, não da física —
R_A menor reduz V_write E a energia (E = I²·R·t, I é fixo pelo torque), mas
pressiona o sinal de leitura (ΔV ∝ R). Este experimento acha a JANELA:
  V_write(autoconsistente com TMR(V)) < V_bd  E  leitura PAR com ΔV > 10 mV.

Modelos (idênticos ao A-4d, pendências idem):
  TMR(V) = TMR_0/cosh(V_med/V_c), V_c = 0,5 V [SEM FONTE — busca 402]
  R_P(V) = R_P_0/(1 + V_med/(3·V_c))
  Escrita: fonte de CORRENTE I_write = J_90·área; V achado por ponto fixo
  (com amortecimento) em V = I×R_med(V).
  Breakdown: V_bd = E_bd·t_MgO com E_bd ∈ {5, 8, 12} MV/cm (t_MgO = 1 nm →
  V_bd = 0,5/0,8/1,2 V) [SEM FONTE — faixa reportada varia; pendência].
  Leitura: PAR (A-4d), V_read = 0,1 V, R_on = 3 kΩ, C_BL = 50 fF.

Ressalva declarada: endurance em si NÃO é simulável aqui (fadiga da barreira é
fenômeno de milhões de ciclos) — o que se audita é o ESTRESSE de tensão por
escrita vs breakdown. E_write usa R_med(V) autoconsistente (ligeiramente menor
que a convenção R_med constante do A-4c — declarado).

Pontos de operação (J_90 do A-4c / A-0 v2):
  baseline40: 2 ns @ 12,0 MA/cm² | doce30: 2 ns @ 8,0 | rapido20: 1 ns @ 17,0

Execução: python experimento_a4e.py   (~segundos; rede analítica, não LLG)
"""
import csv
import os

import numpy as np

KB = 1.380649e-23
T = 300.0
V_C = 0.5            # V — pendência de fonte (402)
V_READ = 0.1
R_ON = 3e3
C_BL = 50e-15
V_OFFSET = 2e-3
T_MGO = 1.0e-9
E_BDS = [5e8, 8e8, 12e8]               # V/m (5, 8, 12 MV/cm)
R_AS = [10e-12, 5e-12, 2.5e-12, 1.25e-12]   # Ω·m² (10 → 1,25 Ω·µm²)
TMR0S = [1.5, 3.0, 6.0]

# (nome, d, t_FL, Ms, J_90, t_pulse) — pontos de operação do A-4c / A-0 v2
DESIGNS = [
    ("baseline40", 40e-9, 1.5e-9, 6.0e5, 12.0e10, 2e-9),
    ("doce30",     30e-9, 1.0e-9, 4.0e5,  8.0e10, 2e-9),
    ("rapido20",   20e-9, 1.0e-9, 4.0e5, 17.0e10, 1e-9),
]


def v_write_sc(I, R_P0, tmr0):
    """Ponto fixo de V = I·R_med(V) com TMR(V) e R_P(V) (amortecido)."""
    V = I * R_P0 * (1 + tmr0 / 2)
    for _ in range(100):
        v_med = V / 2
        tmr_v = tmr0 / np.cosh(v_med / V_C)
        r_p = R_P0 / (1 + v_med / (3 * V_C))
        r_ap = r_p * (1 + tmr_v)
        r_med = 0.5 * (r_p + r_ap)
        Vn = I * r_med
        if abs(Vn - V) < 1e-6:
            V = Vn
            break
        V = 0.5 * V + 0.5 * Vn
    return V, r_p, r_ap, r_med


def dv_par(R_P0, tmr0):
    """ΔV no nó de sense, esquema PAR (A-4d), com TMR(V) no viés de leitura."""
    v_med = V_READ / 2
    tmr_v = tmr0 / np.cosh(v_med / V_C)
    r_p = R_P0 / (1 + v_med / (3 * V_C))
    r_ap = r_p * (1 + tmr_v)
    i_p = V_READ / (R_ON + r_p)
    i_ap = V_READ / (R_ON + r_ap)
    return abs(i_p * r_p - i_ap * r_ap)


os.makedirs("resultados_a4e", exist_ok=True)

print("=" * 86)
print("A-4e: BREAKDOWN DE ESCRITA × JANELA DE R_A — ataque ao ponto fraco endurance")
print("=" * 86)
print(f"  modelo: TMR(V)=TMR0/cosh(V/2/{V_C}) [V_c sem fonte] | V_bd = E_bd·t_MgO "
      f"({T_MGO*1e9:.0f} nm) → {', '.join(f'{e*T_MGO:.2f} V' for e in E_BDS)} [sem fonte]")
print(f"  leitura PAR: V_read = {V_READ:.2f} V, R_on = {R_ON/1e3:.0f} kΩ, "
      f"C_BL = {C_BL*1e15:.0f} fF; ok se ΔV > 10 mV")

linhas = []
veredito = {}
for (nome, d, t_fl, Ms, J90, t_pulse) in DESIGNS:
    area = np.pi * (d / 2) ** 2
    I = J90 * area
    print(f"\n{nome}: d = {d*1e9:.0f} nm | I_write = {I*1e6:.1f} µA "
          f"(J_90 = {J90/1e10:.1f} MA/cm²) | pulso {t_pulse*1e9:.0f} ns")
    print(f"  {'R_A':>8} | {'V_write':>8} {'E_escr':>8} | {'ΔV_par':>7} {'leitura':>7} | "
          "escrita ok? (E_bd = 5/8/12 MV/cm)")
    for tmr0 in TMR0S:
        janela = []
        for ra in R_AS:
            R_P0 = ra / area
            V_w, r_p, r_ap, r_med = v_write_sc(I, R_P0, tmr0)
            E = I ** 2 * r_med * t_pulse
            dv = dv_par(R_P0, tmr0)
            sigma = np.sqrt(KB * T / C_BL) + V_OFFSET / 2
            t_rc = 3 * (R_ON + r_p / 2) * C_BL
            leitura_ok = (dv > 10e-3) and (t_rc < 5e-9)
            ok_bd = [V_w < e * T_MGO for e in E_BDS]
            janela.append((ra, ok_bd, leitura_ok))
            bd_str = "/".join("SIM" if x else "não" for x in ok_bd)
            print(f"  {ra*1e12:6.2f}µm² | {V_w:8.2f} {E*1e12:7.3f}p | {dv*1e3:6.1f}mV "
                  f"{'ok' if leitura_ok else 'MORTA':>7} | {bd_str}")
            linhas.append([nome, tmr0 * 100, ra * 1e12, I * 1e6, V_w, E,
                           dv * 1e3, t_rc * 1e9] + [int(x) for x in ok_bd] + [int(leitura_ok)])
        # janela: algum RA com escrita ok em CADA nível de E_bd e leitura ok?
        res = {}
        for i_bd, e in enumerate(E_BDS):
            ras = [ra * 1e12 for (ra, ok_bd, l_ok) in janela
                   if ok_bd[i_bd] and l_ok]
            res[e] = ras
        veredito[(nome, tmr0)] = res
        if any(res.values()):
            detalhe = "; ".join(f"E_bd = {e/1e8:.0f} MV/cm → R_A ∈ "
                                f"[{min(r) if r else '-':.2f}–{max(r) if r else '-':.2f} Ω·µm²]"
                                for e, r in res.items() if r)
            print(f"  → TMR0 = {tmr0*100:.0f}%: JANELA EXISTE ({detalhe})")
        else:
            print(f"  → TMR0 = {tmr0*100:.0f}%: NENHUM R_A fecha escrita+leitura "
                  "no grid (→ SOT-write/H4, material, ou arquivar design).")

print("-" * 86)
print("RESUMO DE JANELAS (design × TMR0 × E_bd):")
for (nome, tmr0), res in veredito.items():
    for e, ras in res.items():
        if ras:
            print(f"  {nome} TMR0 {tmr0*100:.0f}% E_bd {e/1e8:.0f} MV/cm: "
                  f"R_A viável {', '.join(f'{r:.2f}' for r in ras)} Ω·µm²")

with open("resultados_a4e/a4e_resumo.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["design", "TMR0_pct", "RA_Ohm_um2", "I_write_uA", "V_write_V",
                "E_escrita_J", "dV_par_mV", "t_read_ns", "ok_bd_5", "ok_bd_8",
                "ok_bd_12", "leitura_ok"])
    for l in linhas:
        w.writerow(l)
print("\nFIM — resultados em ./resultados_a4e/")

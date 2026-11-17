# -*- coding: utf-8 -*-
"""MHM-1 — consulta ao A-4d: viabilidade por (design, TMR0, esquema)."""
import csv

rows = list(csv.DictReader(open(r"resultados_a4d/a4d_resumo.csv", encoding="utf-8")))

print("Viabilidade por (design, TMR0, esquema) — algum ponto do grid passa?")
print(f"{'design':>12} {'TMR0%':>6} {'esq':>4} | {'melhor dV (mV)':>14} "
      f"{'melhor margem':>13} {'pontos ok':>10}")
for design in ("baseline 40", "doce 30", "rapido 20"):
    for tmr in ("150.0", "300.0", "600.0"):
        for esq in ("SE", "PAR"):
            sub = [r for r in rows if r["design"] == design
                   and float(r["TMR0_pct"]) == float(tmr) and r["esquema"] == esq]
            if not sub:
                continue
            ok = [r for r in sub if r["viavel"] == "True"]
            bdv = max(float(r["dV_mV"]) for r in sub)
            bmg = max(float(r["margem_sigma"]) for r in sub)
            print(f"{design:>12} {tmr:>6} {esq:>4} | {bdv:14.1f} {bmg:13.1f} "
                  f"{len(ok):7d}/{len(sub)}")

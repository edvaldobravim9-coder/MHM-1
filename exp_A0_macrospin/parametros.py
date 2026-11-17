# -*- coding: utf-8 -*-
"""
MHM-1 — Experimento A-0: parâmetros da célula MTJ.

Todos os valores são FAIXAS TÍPICAS de p-MTJ CoFeB/MgO da literatura aberta.
Nenhum parâmetro é inventado; quando um valor é uma escolha de PROJETO (não de
medição), isso está declarado no comentário.

Fontes principais:
- S. Ikeda et al., "A perpendicular-anisotropy CoFeB-MgO magnetic tunnel junction",
  Nature Materials 9, 721 (2010)  [Ms, PMA, TMR de p-MTJ CoFeB/MgO]
- J. Z. Sun, Phys. Rev. Lett. 85, 393 (2000)  [fórmula de corrente crítica STT]
- J. C. Slonczewski, J. Magn. Magn. Mater. 159, L1 (1996)  [torque STT]
- W. F. Brown Jr., Phys. Rev. 130, 1677 (1963)  [campo térmico estocástico]
- J. L. García-Palacios & F. J. Lázaro, Phys. Rev. B 58, 14937 (1998)  [LLG estocástico]

Observações de projeto (declaradas):
- K_eff é um valor de PROJETO: escolhido para dar fator de segurança térmica
  Δ = K_eff·V/(k_B·T) ≈ 60 com a geometria abaixo (critério de retenção de 10 anos,
  ver README §4). K_eff real depende do processo de fabricação.
- Ms e α são valores típicos de filmes finos CoFeB ~1,5 nm com PMA.
- RA e TMR são valores típicos de barreira MgO em produção (registros de laboratório
  de TMR > 600% existem, mas não são o caso de projeto).
"""
from dataclasses import dataclass
import math

# Constantes físicas (SI)
MU0 = 4.0e-7 * math.pi          # N/A² — permeabilidade do vácuo

@dataclass
class ParametrosMTJ:
    # --- Camada livre (CoFeB perpendicular) ---
    Ms: float = 6.0e5           # A/m    — magnetização de saturação (típico 4–8e5)
    K_eff: float = 1.3e5        # J/m³   — anisotropia EFETIVA (projeto p/ Δ≈60; ver docstring)
    alpha: float = 0.010        # —      — amortecimento de Gilbert (típico 0.005–0.02)
    t_FL: float = 1.5e-9        # m      — espessura da camada livre
    diametro: float = 40e-9     # m      — diâmetro da junção (nó ~40 nm)
    T: float = 300.0            # K      — temperatura de operação
    # --- Barreira e elétrica ---
    RA: float = 10e-12          # Ω·m²   — produto RA da barreira MgO (5–20 Ω·µm² típico)
    TMR: float = 1.50           # —      — razão TMR de projeto (150%; registros lab > 600%)
    # --- Torque STT ---
    eta: float = 0.40           # —      — eficiência de polarização (Slonczewski), 0.3–0.6 típico

    @property
    def area_MJ(self) -> float:
        """Área da junção [m²]."""
        return math.pi * (self.diametro / 2.0) ** 2

    @property
    def volume(self) -> float:
        """Volume da camada livre [m³]."""
        return self.area_MJ * self.t_FL

    @property
    def R_P(self) -> float:
        """Resistência no estado paralelo [Ω]."""
        return self.RA / self.area_MJ

    @property
    def R_AP(self) -> float:
        """Resistência no estado antiparalelo [Ω] (modelo simples de 2 estados)."""
        return self.R_P * (1.0 + self.TMR)

    @property
    def B_keff(self) -> float:
        """Campo de anisotropia EFETIVO [T]: B_k = 2·K_eff/M_s (já inclui forma)."""
        return 2.0 * self.K_eff / self.Ms

    @property
    def delta(self) -> float:
        """Fator de segurança térmica Δ = K_eff·V/(k_B·T) (barreira em unidades de k_B·T)."""
        KB = 1.380649e-23
        return self.K_eff * self.volume / (KB * self.T)

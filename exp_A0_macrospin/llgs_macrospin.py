# -*- coding: utf-8 -*-
"""
MHM-1 — Solver LLGS de macrospin para célula MTJ (Experimento A-0).

Equação integrada (campos em TESLA; m adimensional com |m| = 1; p̂ = +ẑ é a
magnetização da camada de referência):

    dm/dt = −γ m×B_eff − αγ m×(m×B_eff) + γ·B_STT·m×(m×p̂)

    B_eff   = B_keff·(m·ẑ)·ẑ + B_térmico
    B_keff  = 2·K_eff/M_s                      [T]  (anisotropia efetiva, inclui forma)
    B_STT   = ħ·η·J / (2e·M_s·t_FL)            [T]  (J em A/m²; sinal define o sentido)
    B_térm  = sqrt(2α·k_B·T / (γ·M_s·V·Δt))·ξ  [T]  (Brown/García-Palacios, ξ = gaussiano)

Convenção de corrente: J > 0 comuta P → AP; J < 0 comuta AP → P.

Limitações conhecidas e documentadas (não esconder):
1. MACROSPIN: magnetização uniforme; ignora nucleação de domínios. Dispositivos reais
   comutam com corrente MENOR que a macrospin (nucleação assistida). Comparar com MuMax3 (A-1).
2. RK4 com campo térmico congelado por passo (dt pequeno mitiga; Heun estocástico seria
   preferível para estudos térmicos quantitativos).
3. Termo "field-like" do STT ignorado (tipicamente menor que o "damping-like").
4. R(t) tratada como média (R_P+R_AP)/2 durante o pulso no cálculo de energia.
5. TMR modelado como 2 estados (sem dependência de polarização/tensão).
"""
import numpy as np

GAMMA = 1.7609e11          # rad/(s·T) — razão giromagnética do elétron
HBAR = 1.054571817e-34     # J·s
E_C = 1.602176634e-19      # C
K_B = 1.380649e-23         # J/K
MU0 = 4.0e-7 * np.pi       # N/A²

# direção da camada de referência
_EZ = np.array([0.0, 0.0, 1.0])


class SimuladorMacrospin:
    def __init__(self, p, seed=42):
        self.p = p
        self.rng = np.random.default_rng(seed)
        self.B_keff = p.B_keff          # T
        self.V = p.volume               # m³
        self.k_mult = 1.0               # multiplicador de anisotropia (VCMA; 1.0 = off)

    # ------------------------------------------------------------------ física
    def J_c0(self):
        """Corrente crítica macrospin a 0 K (damping-like), perpendicular [A/m²].

        Condição de limiar: B_STT = α·(B_keff + B_M/2), com B_M = μ0·M_s
        (J. Z. Sun PRL 2000, adaptado para PMA). A simulação fornece o limiar
        'real' do macrospin para comparação."""
        p = self.p
        B_M = MU0 * p.Ms
        return (2.0 * E_C * p.Ms * p.t_FL * p.alpha * (self.B_keff + B_M / 2.0)) / (HBAR * p.eta)

    def deriv(self, m, J, B_th):
        """dm/dt para um lote de spins: m (n,3), J (n,) A/m², B_th (n,3) T."""
        p = self.p
        # Anisotropia uniaxial REAL: B_anis = B_keff·m_z·ẑ (campo que depende de
        # m_z → dois poços ±z, barreira K_eff·V no equador, E = −K_eff·V·m_z²).
        # CORREÇÃO (16/11/2026, achada pelo A-2 v2 + diag_ruido.py): antes aplicava
        # B_keff·ẑ CONSTANTE — não havia barreira de Néel (fuga ~ e^(−2Δ), A-2 dava
        # 0/80 flips). A curvatura perto de ±z é a mesma; resultados determinísticos
        # de limiar 0 K mudam pouco, mas TODOS os resultados térmicos dependem disto.
        # VCMA (A-4a): k_mult < 1 modela redução de K_eff por tensão na barreira
        # (efeito de superfície — vale DURANTE o pulso; run_pulse restaura 1.0 no tail).
        B = np.zeros_like(m)
        B[:, 2] = self.B_keff * self.k_mult * m[:, 2]
        B = B + B_th

        mxB = np.cross(m, B)
        mxmxB = np.cross(m, mxB)                     # m×(m×B)
        dmdt = -GAMMA * mxB - p.alpha * GAMMA * mxmxB

        # STT (damping-like), p̂ = +ẑ
        B_stt = (HBAR * p.eta / (2.0 * E_C * p.Ms * p.t_FL)) * J     # (n,) T
        mxmxez = np.cross(m, np.cross(m, np.broadcast_to(_EZ, m.shape)))
        dmdt = dmdt + GAMMA * B_stt[:, None] * mxmxez
        return dmdt

    # ------------------------------------------------------------------ integrador
    def _rk4(self, m, J, B_th, dt):
        k1 = self.deriv(m, J, B_th)
        k2 = self.deriv(m + 0.5 * dt * k1, J, B_th)
        k3 = self.deriv(m + 0.5 * dt * k2, J, B_th)
        k4 = self.deriv(m + dt * k3, J, B_th)
        return m + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def run_pulse(self, J, t_pulse, dt, T=0.0, n_runs=1, t_tail=2e-9,
                  m0_tilt=1e-2, store_hist=False, hist_every=10, k_mult_pulse=1.0):
        """Aplica pulso de corrente J por t_pulse e observa por mais t_tail (J=0).

        k_mult_pulse: multiplicador de anisotropia DURANTE o pulso (VCMA — A-4a);
        no tail a anisotropia volta ao valor integral (k_mult = 1.0).
        J: escalar (mesma corrente para todas as runs) ou array (n_runs,).
        Cada 'run' do lote recebe uma realização de ruído independente.
        Retorna dict com:
          t_sw      (n,)   tempo da primeira passagem por m_z < −0,9 [s] (NaN se não comutou)
          comutou   (n,)   bool — comutou E permaneceu em −z no fim
          mz_pulso  (n,)   m_z ao fim do pulso (NaN se t_pulse = 0)
          mz_final  (n,)   m_z no fim da observação
          hist      (opcional) m_z(t) amostrado
        """
        if np.ndim(J) == 0:
            J_arr = np.full(n_runs, float(J))
        else:
            J_arr = np.asarray(J, dtype=float)
            n_runs = len(J_arr)

        m = np.zeros((n_runs, 3))
        m[:, 0] = m0_tilt
        m[:, 2] = np.sqrt(1.0 - m0_tilt**2)   # estado inicial ≈ +z (paralelo)

        sigma = 0.0
        if T > 0:
            sigma = np.sqrt(2.0 * self.p.alpha * K_B * T /
                            (GAMMA * self.p.Ms * self.V * dt))

        n1 = int(round(t_pulse / dt))
        n2 = int(round(t_tail / dt))

        t_sw = np.full(n_runs, np.nan)
        mz_pulso = np.full(n_runs, np.nan)
        hist = []

        for i in range(n1 + n2):
            J_now = J_arr if i < n1 else np.zeros_like(J_arr)
            self.k_mult = k_mult_pulse if i < n1 else 1.0
            if T > 0:
                B_th = sigma * self.rng.standard_normal(m.shape)
            else:
                B_th = np.zeros_like(m)
            m = self._rk4(m, J_now, B_th, dt)
            m /= np.linalg.norm(m, axis=1, keepdims=True)

            if i == n1 - 1:
                mz_pulso[:] = m[:, 2]

            if store_hist and i % hist_every == 0:
                hist.append(m[:, 2].copy())

            cruzou = (~np.isfinite(t_sw)) & (m[:, 2] < -0.9)
            t_sw[cruzou] = (i + 1) * dt

        comutou = np.isfinite(t_sw) & (m[:, 2] < 0.0)
        out = {"t_sw": t_sw, "comutou": comutou,
               "mz_pulso": mz_pulso, "mz_final": m[:, 2].copy()}
        if store_hist:
            out["hist"] = np.array(hist)     # (n_amostras, n_runs)
            out["hist_dt"] = hist_every * dt
        return out

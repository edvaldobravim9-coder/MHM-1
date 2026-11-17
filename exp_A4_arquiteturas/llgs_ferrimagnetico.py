# -*- coding: utf-8 -*-
"""
MHM-1 — Solver LLGS macrospin de 2 SUB-REDES para camada livre FERRIMAGNÉTICA (H2).

Motivação (Fase 4): a H2 prevê que camada livre ferrimagnética (tipo GdFeCo / RE-TM)
perto do ponto de compensação comuta com corrente/tempo menores. O A-4b já mostrou
que Ms BAIXO ajuda em ferromagneto puro (3 vias); aqui testa-se o mecanismo
FERRIMAGNÉTICO em si: duas sub-redes antiparalelas troca-acopladas, cujo momento
angular líquido (∝ Ms1/γ1 − Ms2/γ2) pode quase se anular perto da compensação.

Equações (campos em TESLA; |m_i| = 1; p̂ = +ẑ; subscritos 1 = TM/Fe [interface com
a barreira], 2 = RE/Gd):

    dm1/dt = −γ m1×B1 − αγ m1×(m1×B1) + γ·B_STT1·m1×(m1×p̂)
    dm2/dt = −γ m2×B2 − αγ m2×(m2×B2)                [sem STT direto em m2]
    B1 = Bk1·m1z·ẑ − B_ex0·m2 + B_térmico,1
    B2 = Bk2·m2z·ẑ − B_ex0·(Ms1/Ms2)·m1 + B_térmico,2

Troca antiferromagnética: e_ex = −A12·m1·m2 (A12 > 0 favorece antiparalelo), com
A12 = B_ex0·Ms1 → campo sobre a sub-rede 1 com magnitude B_ex0 e sobre a 2 com
magnitude B_ex0·(Ms1/Ms2) (par de ação-reação consistente com a densidade de
energia: |B_ex,i|·Ms_i = A12).

Escolhas de modelagem (TODAS declaradas — regra de rigor do projeto):
1. γ IGUAL para as duas sub-redes. Justificativa: Gd tem g ≈ 2 (estado ⁸S₇/₂,
   L = 0) e Fe g ≈ 2,09 → γ1 ≈ γ2 para GdFeCo. Para RE com momento orbital forte
   (Tb, Dy) isto FALHA — não extrapolar sem revisar.
2. STT apenas na sub-rede TM (modo "tm", PADRÃO): a barreira MgO polariza a
   interface rica em Fe; a troca arrasta a sub-rede RE. Quadro físico usual para
   GdFeCo/MgO. Modo alternativo "ambos" (robustez): cada sub-rede recebe o torque
   como se carregasse sozinha a corrente polarizada (B_STT,i ∝ 1/Ms_i).
3. Anisotropia dividida entre as sub-redes (K1+K2 = K_total): no limite rígido
   (B_ex >> B_keff) a barreira comum é K_total·V → Δ preservado por construção.
   Split padrão 50/50; sensibilidade ao split NÃO varrida (declarado).
4. Ruído térmico INDEPENDENTE por sub-rede (FDT de Brown por sub-rede; correlações
   de ruído entre sub-redes não modeladas — refinamento fora do escopo).
5. MACROSPIN por sub-rede (dinâmica uniforme); nucleação não modelada (mesma
   limitação do A-0/A-4; razão malha/macrospin medida: 0,94–0,97 nos designs ferros).
6. B_ex0 (campo molecular de troca) ILUSTRATIVO: para RE-TM o campo molecular é de
   centenas de T, mas a fonte exata está PENDENTE (busca web 402). Varremos 200 e
   500 T — a física alvo só exige B_ex >> B_keff (~1 T).
7. Integrador RK4 passo fixo PEQUENO: o modo óptico do par AF tem
   ω ≈ γ·B_ex0·(1+Ms1/Ms2) ~ 2e14 rad/s; a estabilidade do RK4 no eixo imaginário
   exige γ·B·dt < 2,8 (Entrada 003) → dt = 1e-14 s para B_ex0 = 500 T.
   Custo: ~3e5 passos por pulso de 2 ns — viável em CPU (batch vetorizado).
8. Estado "comutado": m1z < −0,9 (sub-rede TM cruza) e m1z < 0 no fim da
   observação. Estados ferrimagnéticos: P = (m1,m2) = (+z,−z); AP = (−z,+z).
9. t_FL e diâmetro são da CÉLULA como um todo (camada ferrimagnética tratada como
   uma única camada de espessura t_FL contendo as duas sub-redes — idealização
   geométrica; MTJs RE-TM reais usam camadas mais grossas, o que REDUZIRIA B_STT
   ∝ 1/t_FL — declarado como otimismo de geometria).

Retrocompatibilidade: ativo2=False + frac_K1=1.0 + dt=1e-12 replica o solver A-0
(1 sub-rede) — validação V1 do experimento_a4c2.
"""
import numpy as np

GAMMA = 1.7609e11          # rad/(s·T) — razão giromagnética do elétron (g ≈ 2)
HBAR = 1.054571817e-34     # J·s
E_C = 1.602176634e-19      # C
K_B = 1.380649e-23         # J/K

_EZ3 = np.array([0.0, 0.0, 1.0])


class SimuladorFerrimagnetico:
    """Macrospin de 2 sub-redes troca-acopladas (ferrimagneto tipo GdFeCo)."""

    def __init__(self, Ms1, Ms2, K_total, t_FL, diametro,
                 alpha1=0.010, alpha2=0.010, B_ex0=200.0, frac_K1=0.5,
                 eta=0.40, seed=42, stt_mode="tm", ativo2=True):
        self.Ms1 = float(Ms1)
        self.Ms2 = float(Ms2)
        self.K_total = float(K_total)
        self.t_FL = float(t_FL)
        self.area = np.pi * (diametro / 2.0) ** 2     # m²
        self.V = self.area * t_FL                     # m³ (célula inteira)
        self.alpha1 = float(alpha1)
        self.alpha2 = float(alpha2)
        self.B_ex0 = float(B_ex0)                     # T (ILUSTRATIVO — ver nota 6)
        self.frac_K1 = float(frac_K1)
        self.eta = float(eta)
        self.seed = int(seed)
        self.stt_mode = stt_mode                      # "tm" | "ambos"
        self.ativo2 = bool(ativo2)

        self.K1 = frac_K1 * K_total
        self.K2 = (1.0 - frac_K1) * K_total
        self.Bk1 = 2.0 * self.K1 / self.Ms1           # T
        self.Bk2 = 2.0 * self.K2 / self.Ms2 if self.ativo2 else 0.0
        self.B_ex2 = B_ex0 * (self.Ms1 / self.Ms2) if self.ativo2 else 0.0
        self.rng = np.random.default_rng(seed)

    # ---------------------------------------------------------------- física
    def delta(self, T=300.0):
        """Δ do estado ferrimagnético (barreira comum K_total·V no limite rígido)."""
        return self.K_total * self.V / (K_B * T)

    def deriv(self, m1, m2, J, Bth1, Bth2):
        """dm/dt para um lote: m1, m2 (n,3); J (n,) A/m²; Bth_i (n,3) T."""
        # Anisotropia uniaxial REAL por sub-rede (mesma correção do A-2/A-0)
        B1 = np.zeros_like(m1)
        B1[:, 2] = self.Bk1 * m1[:, 2]
        B1 += Bth1
        if self.ativo2:
            # Troca AF: B_ex,1 = −B_ex0·m2 (empurra m1 para −m2)
            B1 += -self.B_ex0 * m2

        mxB = np.cross(m1, B1)
        mxmxB = np.cross(m1, mxB)
        d1 = -GAMMA * mxB - self.alpha1 * GAMMA * mxmxB

        # STT damping-like na sub-rede 1 (p̂ = +ẑ) — sempre presente
        B_stt1 = (HBAR * self.eta / (2.0 * E_C * self.Ms1 * self.t_FL)) * J
        mxez1 = np.cross(m1, np.cross(m1, np.broadcast_to(_EZ3, m1.shape)))
        d1 = d1 + GAMMA * B_stt1[:, None] * mxez1

        if not self.ativo2:
            return d1, np.zeros_like(m2)

        B2 = np.zeros_like(m2)
        B2[:, 2] = self.Bk2 * m2[:, 2]
        B2 += Bth2
        # Troca AF: B_ex,2 = −B_ex0·(Ms1/Ms2)·m1
        B2 += -self.B_ex2 * m1

        mxB2 = np.cross(m2, B2)
        mxmxB2 = np.cross(m2, mxB2)
        d2 = -GAMMA * mxB2 - self.alpha2 * GAMMA * mxmxB2

        if self.stt_mode == "ambos":
            # Robustez: torque como se cada sub-rede carregasse a corrente sozinha
            B_stt2 = (HBAR * self.eta / (2.0 * E_C * self.Ms2 * self.t_FL)) * J
            mxez2 = np.cross(m2, np.cross(m2, np.broadcast_to(_EZ3, m2.shape)))
            d2 = d2 + GAMMA * B_stt2[:, None] * mxez2
        return d1, d2

    # ---------------------------------------------------------------- integrador
    def _rk4(self, m1, m2, J, Bth1, Bth2, dt):
        k1a, k1b = self.deriv(m1, m2, J, Bth1, Bth2)
        k2a, k2b = self.deriv(m1 + 0.5 * dt * k1a, m2 + 0.5 * dt * k1b, J, Bth1, Bth2)
        k3a, k3b = self.deriv(m1 + 0.5 * dt * k2a, m2 + 0.5 * dt * k2b, J, Bth1, Bth2)
        k4a, k4b = self.deriv(m1 + dt * k3a, m2 + dt * k3b, J, Bth1, Bth2)
        m1 = m1 + (dt / 6.0) * (k1a + 2.0 * k2a + 2.0 * k3a + k4a)
        m2 = m2 + (dt / 6.0) * (k1b + 2.0 * k2b + 2.0 * k3b + k4b)
        return m1, m2

    def run_pulse(self, J, t_pulse, dt, T=0.0, n_runs=1, t_tail=1e-9, m0_tilt=1e-2):
        """Pulso de corrente J por t_pulse; observação J=0 por t_tail.

        Retorna dict: t_sw (m1 cruza −0,9), comutou, mz1_pulso, mz1_final,
        mz2_final, mz_net_final (momento líquido normalizado).
        """
        if np.ndim(J) == 0:
            J_arr = np.full(n_runs, float(J))
        else:
            J_arr = np.asarray(J, dtype=float)
            n_runs = len(J_arr)

        m1 = np.zeros((n_runs, 3))
        m1[:, 0] = m0_tilt
        m1[:, 2] = np.sqrt(1.0 - m0_tilt ** 2)     # P: m1 ≈ +z
        m2 = -m1.copy()                            # AF exato (equilíbrio da troca)

        sig1, sig2 = 0.0, 0.0
        if T > 0:
            sig1 = np.sqrt(2.0 * self.alpha1 * K_B * T /
                           (GAMMA * self.Ms1 * self.V * dt))
            if self.ativo2:
                sig2 = np.sqrt(2.0 * self.alpha2 * K_B * T /
                               (GAMMA * self.Ms2 * self.V * dt))

        n1 = int(round(t_pulse / dt))
        n2 = int(round(t_tail / dt))

        t_sw = np.full(n_runs, np.nan)
        mz1_pulso = np.full(n_runs, np.nan)

        for i in range(n1 + n2):
            J_now = J_arr if i < n1 else np.zeros_like(J_arr)
            if T > 0:
                Bth1 = sig1 * self.rng.standard_normal(m1.shape)
                Bth2 = (sig2 * self.rng.standard_normal(m2.shape)
                        if self.ativo2 else np.zeros_like(m2))
            else:
                Bth1 = np.zeros_like(m1)
                Bth2 = np.zeros_like(m2)
            m1, m2 = self._rk4(m1, m2, J_now, Bth1, Bth2, dt)
            m1 /= np.linalg.norm(m1, axis=1, keepdims=True)
            if self.ativo2:
                m2 /= np.linalg.norm(m2, axis=1, keepdims=True)

            if i == n1 - 1:
                mz1_pulso[:] = m1[:, 2]

            cruzou = (~np.isfinite(t_sw)) & (m1[:, 2] < -0.9)
            t_sw[cruzou] = (i + 1) * dt

        comutou = np.isfinite(t_sw) & (m1[:, 2] < 0.0)
        mz_net = ((self.Ms1 * m1[:, 2] + self.Ms2 * m2[:, 2])
                  / (self.Ms1 + self.Ms2))
        return {"t_sw": t_sw, "comutou": comutou,
                "mz1_pulso": mz1_pulso, "mz1_final": m1[:, 2].copy(),
                "mz2_final": m2[:, 2].copy() if self.ativo2
                             else np.full(n_runs, np.nan),
                "mz_net_final": mz_net}

# Paisagem de patentes e literatura — MHM-1 (veredito de anterioridade)

**Status: BUSCAS EXECUTADAS (17/11/2026).** Cinco consultas foram executadas no Google
Patents via endpoint XHR (`patents.google.com/xhr/query`) — a busca web genérica segue
bloqueada (HTTP 402), mas o endpoint de patentes respondeu. Os números de patente abaixo
foram verificados nos resultados (título + titular + data de prioridade no snippet).
Tentativa de reexecutar a consulta de VCMA no fim da sessão retornou 503 (rate-limit) —
os registros são das execuções bem-sucedidas do dia.

**Nada aqui constitui parecer legal de liberdade para operar (FTO)** — isso cabe a um
agente de propriedade intelectual.

## 0. Veredito executivo (H1–H5 + janela R_A)

| Item | Veredito de anterioridade | Patente-chave verificada | Consequência para o MHM-1 |
|---|---|---|---|
| **H1** (pré-pulso VCMA na escrita SOT/STT) | **BLOQUEADA — campo denso** | **US9646670B2** (Qualcomm, prior. 2015): SOT-MRAM 3T com campo elétrico reduzindo a anisotropia na escrita | Publicar, não patentear |
| **H2** (camada livre ferrimagnética 3d-4f) | **BLOQUEADA — campo denso** | **US8102701B2** (Crocus, prior. 2007): liga ferrimagnética para célula magnética; **JP7251811B2** (Tohoku); **CN111312745B** (Samsung) | Publicar |
| **H3** (célula diferencial, 2 MTJs opostos) | **BLOQUEADA** | **US10483457B1** (Qualcomm, prior. 2018): célula SOT-MRAM diferencial com 2 MTJs de polaridade oposta | Já promovida a requisito de design (A-4d); publicar |
| **H4** (escrita SOT paralela + seleção por porta VCMA) | **PARCIALMENTE VIVA** — busca refinada: **18 resultados**, adjacentes apenas | Adjacentes: **US11004490B2** (imec, linhas compartilhadas), **CN113160863A** (Antalis), **CN122314039A** (青岛海存微电子, 2026, "parallel write methods") | Única candidata a patente estreita — dependeria de parecer de PI |
| **Janela R_A** (A-4e, 1,25–2,5 Ω·µm²) | Sem cobertura do pacote nas buscas (951 resultados), mas risco de "óbvio para experimentar" | — | Valor de patente provavelmente fino; publicar |

**Resumo:** a física e as três primeiras hipóteses de arquitetura do MHM-1 têm
anterioridade densa e confirmada. O espaço que sobrou (H4) é uma janela estreita de
**arquitetura de array**, não de física — patenteável apenas com avaliação profissional,
e o valor dependeria de licenciamento futuro. A recomendação honesta é tratar o dossiê
como **publicação científica + material de divulgação para venda/parceria**, não como
ativo de patente.

## 1. Estado da arte industrial (quem já produziu/demonstrou o quê)

| Empresa/instituição | Tecnologia | Estado conhecido |
|---|---|---|
| **Everspin** | STT-MRAM comercial (família EverSpin STT, 28 nm, 1 Gbit classe) | Em produção; líder em MRAM comercial |
| **Intel** | STT-MRAM embarcada (22FFL, "Stony Beach") | Demonstrado para produto embarcado |
| **Samsung** | STT-MRAM embarcada; **SOT-MRAM** com células de poucas dezenas de nm em conferências (IEDM/VLSI); patente CN111312745B (ferrimagnético) | Demos públicos; forte portfólio de patentes SOT |
| **TSMC / GlobalFoundries** | MRAM embarcada em 22/28 nm; SOT-MRAM em desenvolvimento | Oferecida como NVM embarcada |
| **IBM** | Pesquisa pesada em SOT-MRAM (incl. materiais com Hf/W) | Papers e patentes; sem produto |
| **Qualcomm** | Patentes de arquitetura: US9646670B2 (VCMA assistindo escrita SOT), US10483457B1 (célula SOT diferencial) | Verificadas nas buscas |
| **imec** | US11004490B2: arranjo SOT com linhas compartilhadas | Verificada na busca H4 |
| **Crocus** | US8102701B2: liga ferrimagnética 3d-4f (prior. 2007) | Verificada na busca H2 |
| **Inston Inc.** | Portfólio inteiramente VCMA-MRAM ("VCMA AND memory": 1.176 resultados) | Verificado na busca H1 |

**Implicação (atualizada):** o território "SOT/STT-MRAM em 1X–2X nm com assistência
VCMA, ferrimagnética ou leitura diferencial" é **densamente patenteado e confirmado por
busca** — não é mais suposição. A vantagem do MHM-1 está em **metodologia honesta
(margens, reprodutibilidade), janela de design de energia (R_A baixo) e eventuais
combinações de array (H4)**, não em física nova.

## 2. Linhas acadêmicas que definem o estado da arte (a citar nos relatórios)

- **p-MTJ CoFeB/MgO:** Ikeda et al., *Nature Materials* 9, 721 (2010); TMR 604% RT:
  Ikeda, APL 92, 082508 (2008).
- **Crítica de corrente STT:** Slonczewski, *J. Magn. Magn. Mater.* 159, L1 (1996);
  J. Z. Sun, *PRL* 85, 393 (2000).
- **SOT:** Miron et al., *Nature* 476, 189 (2011); Liu et al., *Science* 336, 555 (2012).
- **VCMA:** Maruyama/Shiota (NTT/Tohoku, 2009–2012).
- **Ferrimagnéticos:** comutação sub-ns em GdFeCo por SOT; SOT-MRAM ferrimagnética
  de Tohoku (Kanai/Fukami/Ohno) — agora também **JP7251811B2** (verificada).
- Busca de LITERATURA (papers) segue indisponível nesta sessão (websearch 402).

## 3. Consultas executadas (Google Patents via XHR, 17/11/2026)

| # | Consulta | Resultados | Veredito |
|---|---|---|---|
| 1 | H4-bruta (SOT + write + parallel) | dezenas; ruído alto | sem cobertura do pacote |
| 2 | `("voltage controlled magnetic anisotropy" OR VCMA) AND memory` | **1.176** | campo denso (H1 bloqueada; Inston = portfólio todo) |
| 3 | Janela R_A (tunnel resistance + MgO + write) | **951** | sem cobertura do pacote; risco de obviedade |
| 4 | Ferrimagnético (`("ferrimagnetic" OR GdFeCo) AND (MRAM OR "spin torque")`) | **6.314** | campo denso (H2 bloqueada) |
| 5 | H4-refinada (`"parallel write" OR "simultaneous write" OR "shared write line" OR "multi-cell write"`) | **18** | adjacentes apenas → **H4 parcialmente viva** |

Consulta por assignee (Seção antiga item 6: Samsung/TSMC/IBM/Intel/Everspin/SK hynix)
não executada — deixar para uma eventual fase de FTO profissional.
**Regra do projeto mantida:** hipótese candidata a diferenciação só considera-se tal
após busca de anterioridade registrada aqui.

## 4. Hipóteses de inovação do MHM-1 — veredito final

| # | Hipótese | Veredito após busca |
|---|---|---|
| H1 | Escrita SOT com pré-pulso VCMA (porta reduz Δ só durante o pulso) | **Anterioridade densa.** US9646670B2 (Qualcomm, 2015) descreve exatamente campo elétrico reduzindo anisotropia para auxiliar escrita; portfólio Inston inteiro é VCMA-MRAM. Continua válida como **alavanca de energia −30%** (A-4a2) — publicável, não patenteável. |
| H2 | Camada livre ferrimagnética (GdFeCo / RE-TM) com ponto de compensação ~300 K | **Anterioridade densa.** US8102701B2 (Crocus, 2007), CN111312745B (Samsung), JP7251811B2 (Tohoku). Continua como direção de **pesquisa** (solver 2 sub-redes, A-4c2) — publicável. |
| H3 | Célula diferencial (2 MTJs opostos) | **Anterioridade confirmada** — US10483457B1 (Qualcomm, 2018). No MHM-1 foi promovida a **requisito de design** (A-4d), não a novidade. |
| H4 | Escrita paralela por linha SOT compartilhada + seleção por porta VCMA | **PARCIALMENTE VIVA.** 18 resultados na busca refinada; adjacentes (imec US11004490B2: linhas compartilhadas; Antalis CN113160863A; 青岛海存微电子 CN122314039A, 2026: escrita paralela em arrays) — **nenhum cobre a combinação "SOT paralelo + seleção VCMA"**. Avaliar no A-4f (estimativa de célula SOT-write) e, se o resultado for forte, levar a um agente de PI. |
| H5 | Empilhamento 3D tipo "3D XPoint magnético" | **Não buscada** — risco alto (depósitos 3D abundam) e problema térmico/gravura severo. Recomendação: **arquivar com justificativa** (custo/benefício ruim para o projeto; sem ferramenta de processo para simular). |

## 5. Lacunas de informação restantes

1. **Parecer profissional de PI** sobre H4 (e, se o usuário quiser, sobre a janela R_A)
   — não substituível por busca automatizada.
2. TMR real de MTJs ferrimagnéticas em MgO a 300 K (impacta leitura da H2) — busca de
   papers bloqueada (402).
3. β do VCMA (fJ/V·m), V_c do TMR(V), K_eff de material anisotrópico forte, E_bd do
   MgO e R_A típico comercial — pendências de fonte já registradas nos experimentos.
4. Custos/limites de nuvem (Colab/Binder) — teste prático pendente.

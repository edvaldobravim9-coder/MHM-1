# Paisagem de patentes e literatura — MHM-1 (levantamento preliminar)

**Status: PRELIMINAR.** Levantamento feito com conhecimento consolidado até o início de 2025 +
verificação de sites em 16/11/2026. A busca web automatizada esteve indisponível nesta data
(cota), portanto **nenhuma patente específica citada abaixo tem número verificado hoje** — os
números serão confirmados nas próximas sessões com as consultas prontas da Seção 3.
Nada aqui constitui parecer legal de liberdade para operar (FTO).

## 1. Estado da arte industrial (quem já produziu/demonstrou o quê)

| Empresa/instituição | Tecnologia | Estado conhecido |
|---|---|---|
| **Everspin** | STT-MRAM comercial (família EverSpin STT, 28 nm, 1 Gbit classe) | Em produção; líder em MRAM comercial |
| **Intel** | STT-MRAM embarcada (22FFL, "Stony Beach") | Demonstrado para produto embarcado |
| **Samsung** | STT-MRAM eudemonstrada em euêmbarked; **SOT-MRAM** com células de poucas dezenas de nm apresentada em conferências (IEDM/VLSI) | Demos públicos; forte portfólio de patentes SOT |
| **TSMC / GlobalFoundries** | MRAM embarcada em 22/28 nm; SOT-MRAM em desenvolvimento | Oferecida como NVM embarcada |
| **IBM** | Pesquisa pesada em SOT-MRAM (incl. materiais com Hf/W, comutação por injeção de elétrons polarizados) | Papers e patentes; sem produto |
| **SK hynix / Seagate / WD** | MRAM para cache de controlador de SSD e rotacional | Menos público |

**Implicação:** espaço "SOT-MRAM em 1X–2X nm" é território densamente patenteado. A nossa
vantagem comparativa provável está em **arquitetura, geometria e integração sistêmica**, não na
pilha material básica.

## 2. Linhas acadêmicas que definem o estado da arte (a citar nos relatórios)

- **p-MTJ CoFeB/MgO:** Ikeda et al., *Nature Materials* 9, 721 (2010) — base dos parâmetros do A-0.
- **Crítica de corrente STT:** Slonczewski, *J. Magn. Magn. Mater.* 159, L1 (1996); J. Z. Sun, *PRL* 85, 393 (2000) (fórmula de I_c usada no A-0).
- **SOT:** Miron et al., *Nature* 476, 189 (2011); Liu et al., *Science* 336, 555 (2012).
- **VCMA:** Maruyama/Shiota (NTT/Tohoku, 2009–2012); demos de escrita VCMA+ assistida por campo/SOT.
- **Ferrimagnéticos:** comutação sub-ns em GdFeCo por SOT (finais dos anos 2010); proposta de SOT-MRAM ferrimagnética (grupo de Tohoku — Kanai/Fukami/Ohno) — menor energia, sensível ao ponto de compensação.
- **Revisões recentes de SOT-MRAM e VCMA:** a coletar na próxima sessão (busca web indisponível hoje).

## 3. Consultas prontas para bases de patentes (Google Patents / Espacenet / Lens.org)

Executar e registrar resultados em `registros/registro_tecnico.md`:

1. `(spin orbit torque) AND (MRAM OR "magnetic memory") AND (write OR switching)` — class. CPC **H10B63** (dispositivos de memória magnética com escrita por torque de spin)
2. `("voltage controlled magnetic anisotropy" OR VCMA) AND memory`
3. `("ferrimagnetic" OR GdFeCo) AND (MRAM OR "spin torque")`
4. `(three-dimensional OR 3D) AND (MRAM OR "magnetic memory") AND (array OR stack)`
5. `"parallel" AND "write" AND (SOT OR "spin orbit") AND "write line"` (operações paralelas — chave para o nosso Experimento D)
6. Por empresa: `assignee:(Samsung OR TSMC OR IBM OR Intel OR Everspin OR SK hynix) AND (SOT-MRAM OR VCMA)`

**Regra do projeto:** toda hipótese de inovação do MHM-1 ganha um item de checklist
"busca de anterioridade executada" antes de ser considerada candidata a diferenciação.

## 4. Hipóteses de inovação do MHM-1 (HIPÓTESES — não afirmamos novidade)

| # | Hipótese | Por que pode valer | Risco de anterioridade |
|---|---|---|---|
| H1 | Escrita SOT com **pré-pulso VCMA**: a tensão de porta reduz temporariamente Δ durante o pulso de escrita e é restaurada em seguida → menor corrente SOT para a mesma retenção em repouso | Ataca diretamente o conflito retenção × corrente de escrita | **Alta** (grupos de CEA-Leti/NTT publicaram combinações próximas) — verificar |
| H2 | Camada livre **ferrimagnética (GdFeCo ou multicanal RE-TM)** com ponto de compensação ajustado perto de 300 K | Comutação sub-ns com menor corrente; dinâmica do momento angular compensado | **Média-alta** (Tohoku + academic demos) |
| H3 | Célula **diferencial acoplada** (2 MTJs com estados opostos por célula) para leitura imune a distúrbio e maior margem de sense | Endereça o gargalo real de matriz: margem de leitura e erro | **Média** (MRAM diferencial existe; acoplamento magnético fino é a fronteira) |
| H4 | **Escrita paralela por linhas SOT compartilhadas** com seleção por VCMA de porta (linha SOT comum + portas seletivas) | Ataca o objetivo de "operações simultâneas" do Experimento D | **Desconhecida** — pesquisar antes de investir |
| H5 | Empilhamento 3D tipo "3D XPoint magnético" (pilha de camadas de célula com linha SOT por camada) | Densidade; mas problemas térmicos e de gravura são severos | **Alta** (muitos depósitos de patente 3D) |

## 5. Lacunas de informação que identificamos hoje

1. Números exatos de patentes e datas (buscar com as consultas da Seção 3).
2. TMR real de MTJs ferrimagnéticas emMgO a 300 K (impacta leitura da H2).
3. Valores de VCMA (β, em fJ/V·m) para interfaces CoFeB/MgO modernas e sua tensão de breakdown — necessário para dimensionar H1.
4. Custos/limites das opções em nuvem (Colab: sessões limitadas; Binder: recursos modestos) — testar na prática.

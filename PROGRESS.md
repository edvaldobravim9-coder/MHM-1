# MHM-1 — Progresso

## Objetivo atual
Iniciar a Fase 4 (comparação de materiais e arquiteturas) com o pré-requisito
de patentes.

## Concluído
- **FASES 1–3 ENCERRADAS (~36% do projeto)** — veredito consolidado na Entrada 003
  de `registros/registro_tecnico.md`.
- **GitHub publicado**: github.com/edvaldobravim9-coder/MHM-1 (público, MIT) —
  código, resultados, diários, docs + ferramentas MuMax3/DLLs CUDA (618 MB LFS).
  Conta limpa (4 repos antigos excluídos; backup em `Desktop\github_backup_2026-11-17`).
- **Fase 1** — ferramentas revalidadas; SunTzu não público → Verilog-A próprio (Fase 6).
- **Fase 2** — solver macrospin validado (FDT 1,008 a dt = 0,25 ps); anisotropia
  uniaxial corrigida; calibração térmica empírica taxa(Δ), desvio vs Brown é
  física de Δ baixo (confirmado por convergência dt: −14% por half-dt).
- **Fase 3** — campo: B_sw = 0,75 T @ 10 ns; corrente: J_sw malha ≈ 1,07× macrospin
  (reversão quase-coerente; macrospin validado p/ varreduras, ~100× mais barato);
  2 ns ✓ (90% @ 12 MA/cm², 0,63 pJ); 1 ns ✗ (→ SOT/VCMA); <1 pJ ✓; retenção
  Δ = 59 ✓ (~25 anos mesmo com inclinação pessimista); térmico MuMax3 viável
  (11 min/run — 100 runs = 1 noite local) e FDT por célula aprovado (razão 1,18;
  0,107 da malha é contagem de modos).

## Em andamento
- Nada rodando — fila de jobs vazia.

## Próximos passos
1. **Fase 4**: varreduras de arquitetura com macrospin validado (SOT, VCMA,
   ferrimagnéticos — combos de material × geometria × pulso).
2. Pré-requisito de novidade: consultas de patentes (`docs/paisagem_ip.md`) —
   websearch bloqueado (HTTP 402); alternativa: consulta manual pelo usuário.
3. Nota GPLv3 do MuMax3 no README (ferramentas versionadas no repo).
4. Atualizar percentual após definir o escopo exato da Fase 4.

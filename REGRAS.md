# Regras específicas — Recargas_2.0

Regras de negócio e de comportamento acordadas para o sistema.
Uma seção por regra, com número fixo — não renumerar.

---

## REGRA 001 — Exportação CSV ao salvar registro

Ao salvar um registro, um arquivo CSV deve ser gerado automaticamente.

- Gerado a CADA salvamento (inclusão e edição).
- Destino: DIRETO na área de trabalho do computador onde o sistema
  está rodando — sem subpasta, caminho resolvido em tempo de execução
  (o sistema roda em vários computadores).
- Compatível com PyInstaller: nada depende do caminho do código-fonte.
- Formato do CSV:
  - Colunas: `Nome, Documento, Valor, Benefício` (uma linha por item).
  - Separador: ponto e vírgula (`;`). UTF-8 com BOM (abre no Excel).
  - Valor inteiro sem decimais quando for número redondo (ex.: `40`).
  - Nome do arquivo: `carga_de_<DD-MM-AAAA>.csv` (data da recarga).
    Se já existir, acrescenta sufixo numérico (`_2`, `_3`, ...) —
    nunca sobrescreve.

**Implementação:** `app/utils/exportacao_csv.py` (infraestrutura) +
`RecargaService` (disparo ao salvar). Falha de exportação NUNCA
cancela o salvamento do registro — é registrada no log.

---

## REGRA 002 — Pesquisa de recargas: itens na coluna Descrição

Na pesquisa de recargas, a coluna Descrição exibe os ITENS da recarga
em uma única linha (nomes separados por vírgula).

- Sem itens carregados, exibe a descrição salva no banco.
- O filtro de pesquisa também encontra pelo nome do item (além de
  sequência e descrição).
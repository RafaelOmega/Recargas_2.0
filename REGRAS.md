# Regras específicas — Recargas_2.0

Regras de negócio e de comportamento acordadas para o sistema.
Uma seção por regra, com número fixo — não renumerar.

---

## REGRA 001 — Exportação CSV ao salvar registro

Ao salvar um registro, um arquivo CSV deve ser gerado automaticamente.

- Gerado a CADA salvamento (inclusão e edição).
- Destino: área de trabalho do computador onde o sistema está rodando —
  resolvida em tempo de execução, nunca caminho fixo (o sistema roda
  em vários computadores).
- Controle de pastas automático: os arquivos ficam em
  `Área de Trabalho\Recargas_2.0\`; a pasta é criada se não existir.
- Compatível com PyInstaller: nada depende do caminho do código-fonte;
  funciona igual em desenvolvimento e no executável empacotado.
- Formato do CSV (conforme exemplo `carga_de_13-10-2026.csv`):
  - Colunas: `nome, documento, valor, beneficio` (uma linha por item).
  - Separador: vírgula. UTF-8 com BOM (abre direto no Excel).
  - Valor inteiro sem decimais quando for número redondo (ex.: `40`).
  - Nome do arquivo: `carga_de_<DD-MM-AAAA>.csv` (data da recarga).
    Se já existir (mesmo dia, mais de um salvamento), acrescenta
    sufixo numérico (`_2`, `_3`, ...) — nunca sobrescreve.

**Implementação:** `app/utils/exportacao_csv.py` (infraestrutura) +
`RecargaService` (disparo ao salvar). Falha de exportação NUNCA
cancela o salvamento do registro — é registrada no log.
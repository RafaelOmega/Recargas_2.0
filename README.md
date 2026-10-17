# Recargas 2.0

Sistema desktop para controle de recargas de cartões benefício e
abastecimento de caminhões.

**Stack:** Python · PySide6 · PostgreSQL (psycopg2)

## Funcionalidades

- **Login obrigatório** — usuários com senha PBKDF2; usuário inativo não entra
- **Cadastros** — Colaboradores, Usuários, Caminhões e Saldo BIZ (conta Biz)
- **Lançamento de Recargas** — mestre-detalhe com itens em grade, total
  automático e benefício fixo "Refeição"
- **Pesquisas** — Colaboradores, Usuários, Caminhões, Saldo BIZ e Recargas
  (filtro com debounce 300ms, ordenação numérica por código)
- **Relatório de Recargas por Colaborador** — preview em blocos por
  colaborador com subtotal; exportação em PDF, XLSX e CSV
- **Dashboard Refeição** — relatório do Power BI Service embutido
  (QWebEngineView)
- **Multiusuário** — last-write-wins: edição concorrente é detectada, a
  tela avisa e recarrega a versão mais recente (nunca sobrescreve calado);
  cada gravação carimba `atualizado_em` e `pelo_usuario`
- **Barra de status** — tela ativa, saldo da conta (atualizado a cada 30s,
  negativo em vermelho), data e hora

## Requisitos

- Python 3.12+ (CI valida na 3.12)
- PostgreSQL 13+ acessível na rede
- Windows (ícone/taskbar usam AppUserModelID)

## Variáveis de ambiente (Windows)

| Variável | Descrição |
|---|---|
| `DB_HOST` | Host do PostgreSQL |
| `DB_PORT` | Porta (padrão 5432) |
| `DB_NAME5` | Nome do banco |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |
| `POWERBI_REFEICAO_URL` | URL de incorporação segura do relatório Power BI (dashboard) |

## Instalação

```bash
git clone https://github.com/RafaelOmega/Recargas_2.0.git
cd Recargas_2.0
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install openpyxl
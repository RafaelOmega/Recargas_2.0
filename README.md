# Recargas 2.0

Sistema desktop para controle de recargas de cartões benefício e
abastecimento de caminhões.

**Stack:** Python · PySide6 · PostgreSQL (psycopg2)

## Requisitos

- Python 3.11+
- PostgreSQL 13+ acessível na rede
- Windows (ícone/taskbar usam AppUserModelID)

## Instalação

```bash
git clone https://github.com/RafaelOmega/Recargas_2.0.git
cd Recargas_2.0
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
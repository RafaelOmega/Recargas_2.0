# -*- coding: utf-8 -*-
"""Exportação de registros em CSV (Regra 001).

Ao salvar um registro, um CSV é gerado na área de trabalho do
computador onde o sistema roda, dentro da pasta Recargas_2.0
(criada automaticamente se não existir).

Compatível com PyInstaller: nada depende do caminho do código-fonte.
A área de trabalho é lida do registro do Windows — cobre pastas
redirecionadas por OneDrive/empresa e nomes localizados; em outros
sistemas, usa o home do usuário.

Formato do CSV de recarga (conforme exemplo carga_de_13-10-2026.csv):
colunas nome, documento, valor, beneficio; separador vírgula;
UTF-8 com BOM (abre direto no Excel). Nome do arquivo:
carga_de_<DD-MM-AAAA>.csv — se já existir (mesmo dia, mais de um
salvamento), um sufixo numérico é acrescentado para não sobrescrever.
"""
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger("exportacao_csv")

PASTA_EXPORTACAO = "Recargas_2.0"


def pasta_area_trabalho() -> Path:
    """Área de trabalho do usuário logado, em qualquer computador."""
    if sys.platform == "win32":
        return _area_trabalho_windows()
    return Path.home() / "Desktop"


def _area_trabalho_windows() -> Path:
    """Área de trabalho real do Windows, lida do registro.

    A chave 'User Shell Folders' é a fonte oficial: cobre
    redirecionamento de OneDrive/empresa e pastas localizadas
    (ex.: 'Área de Trabalho'), que o caminho fixo USERPROFILE\\Desktop
    não cobre.
    """
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion"
            r"\Explorer\User Shell Folders",
        ) as chave:
            caminho, _ = winreg.QueryValueEx(chave, "Desktop")
        return Path(os.path.expandvars(caminho))
    except OSError:
        return Path.home() / "Desktop"


def pasta_exportacao() -> Path:
    """Pasta de exportação na área de trabalho (cria se não existir)."""
    pasta = pasta_area_trabalho() / PASTA_EXPORTACAO
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def exportar_csv(nome_base: str, colunas: list[str],
                 linhas: list[tuple]) -> Path:
    """Grava um CSV na pasta de exportação e devolve o caminho gerado.

    O nome recebe carimbo de data/hora para nunca sobrescrever uma
    exportação anterior. Separador vírgula e UTF-8 com BOM: abre
    direto no Excel com acentuação correta.
    """
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = pasta_exportacao() / f"{nome_base}_{carimbo}.csv"
    _gravar(caminho, colunas, linhas)
    return caminho


def exportar_recarga_csv(recarga) -> Path:
    """CSV de uma recarga salva (Regra 001): uma linha por item.

    Formato idêntico ao exemplo combinado (carga_de_13-10-2026.csv):
    colunas nome, documento, valor, beneficio; separador vírgula.
    Nome do arquivo: carga_de_<DD-MM-AAAA>.csv; se já existir, um
    sufixo numérico é acrescentado (nunca sobrescreve).
    """
    colunas = ["nome", "documento", "valor", "beneficio"]
    linhas = [
        (item.nome, item.documento,
         _formatar_valor_csv(item.valor), item.beneficio)
        for item in recarga.itens
    ]
    base = f"carga_de_{recarga.data.strftime('%d-%m-%Y')}"
    return _exportar_sem_sobrescrever(base, colunas, linhas)


def _exportar_sem_sobrescrever(nome_base: str, colunas: list[str],
                               linhas: list[tuple]) -> Path:
    """Grava o CSV; se o nome já existir, acrescenta _2, _3, ..."""
    pasta = pasta_exportacao()
    caminho = pasta / f"{nome_base}.csv"
    contador = 2
    while caminho.exists():
        caminho = pasta / f"{nome_base}_{contador}.csv"
        contador += 1
    _gravar(caminho, colunas, linhas)
    return caminho


def _gravar(caminho: Path, colunas: list[str],
            linhas: list[tuple]) -> None:
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arq:
        escritor = csv.writer(arq, delimiter=",")
        escritor.writerow(colunas)
        escritor.writerows(linhas)
    logger.info("CSV exportado: %s", caminho)


def _formatar_valor_csv(valor: float) -> str:
    """Formata o valor como no exemplo: 40 -> '40'; 40.5 -> '40,50'."""
    if float(valor).is_integer():
        return str(int(valor))
    return f"{valor:.2f}".replace(".", ",")

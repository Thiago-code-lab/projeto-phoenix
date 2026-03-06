# Phoenix 2.0

Aplicacao desktop local-first para gestao pessoal completa, construida com PyQt6, SQLAlchemy e SQLite.

## Executar

```bash
pip install -r phoenix/requirements.txt
python -m phoenix.main
```

## Stack

- PyQt6 para interface desktop
- SQLAlchemy + SQLite para persistencia local
- PyQtGraph e Matplotlib para visualizacoes
- ReportLab para exportacao PDF
- Dynaconf para configuracoes locais

## Estrutura

A aplicacao esta organizada em `core`, `ui`, `modules`, `utils` e `tests` dentro da pasta `phoenix`.

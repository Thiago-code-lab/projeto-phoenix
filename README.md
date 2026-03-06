# Projeto Phoenix 2.0

Aplicacao desktop local-first para gestao pessoal completa, baseada em PyQt6 + SQLAlchemy + SQLite.

## Features principais

- Dashboard consolidado com indicadores dos modulos
- Metas com milestones, progresso e filtros
- Habitos com check diario, streak e heatmap
- Financas com resumo, transacoes, categorias e exportacao
- Biblioteca com cards, progresso de leitura e estatisticas
- Saude com registro diario, treinos e series historicas
- Diario com edicao rica, tags e autosave
- Projetos com modo Kanban e modo lista
- Foco (Pomodoro) com historico e som de conclusao
- Notes, Reviews e Settings integrados ao mesmo banco local

## Estrutura

Estrutura principal atual do projeto Phoenix 2.0.

```text
projeto-phoenix/
├── main.py
├── README.md
├── requirements.txt
└── phoenix/
	├── main.py
	├── core/
	├── modules/
	├── ui/
	├── utils/
	├── tests/
	└── assets/
```

## Como usar

### 1. Preparar ambiente (Windows PowerShell)

```powershell
cd d:\Códigos\projeto-phoenix
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Executar o Phoenix 2.0

Opcao A:

```powershell
python -m phoenix.main
```

Opcao B:

```powershell
python main.py
```

### 3. Testar o projeto

```powershell
$env:QT_QPA_PLATFORM='offscreen'
python -m pytest phoenix\tests -q
```

### 4. Atalhos uteis

- `Ctrl+1..9`: navegacao rapida entre modulos
- `Ctrl+/`: painel de atalhos
- `Ctrl+Z` / `Ctrl+Shift+Z`: undo/redo em telas com suporte

## Stack tecnica

- PyQt6
- SQLAlchemy + SQLite
- PyQtGraph + Matplotlib
- ReportLab
- Dynaconf
- pytest + pytest-qt

# Changelog

## 2026-03-19

### perf:
- adicionado pooling no SQLAlchemy engine com pre-ping e recycle.
- implementado cache LRU para consultas frequentes no Dashboard e streak de Habitos.
- adicionados indices ORM nas colunas mais consultadas (datas, status e foreign keys).
- importacao financeira otimizada com batch insert via bulk_insert_mappings.
- migracao de operacoes assincronas para padrao QThreadPool + QRunnable worker.

### feat:
- criado splash screen de inicializacao com progresso real por etapa.
- adicionado health check PRAGMA integrity_check no bootstrap.
- implementado backup automatico a cada 24h com retencao dos 7 mais recentes.
- criado sistema de toast com niveis info/success/warning/error no canto inferior direito (3s).
- adicionada barra de status global: modulo ativo, ultimo salvamento e tamanho do banco.
- implementado command palette global com Ctrl+P e busca fuzzy.
- adicionado widget de Resumo do Dia, produtividade semanal, streak global e milestones com countdown no Dashboard.
- modulo Foco agora suporta sessoes 25/50/90, vinculo com tarefas Kanban e relatorio semanal por projeto.
- modulo Financas agora importa OFX/CSV, alerta visual de orcamento e gera relatorio PDF mensal automatico.
- Settings agora persiste tema e caminho de som customizado .wav para foco.
- adicionada hierarquia de excecoes customizadas PhoenixError, DatabaseError, ValidationError e UIError.
- adicionado __version__ em phoenix/__init__.py e exibicao na splash/janela principal.

### test:
- criado pytest.ini com markers unit/integration/ui e cobertura minima.
- adicionados testes de integracao para fluxo de meta + milestone + conclusao.
- adicionados testes de regressao CRUD para entidades SQLAlchemy criticas.

### docs:
- criado changelog consolidando evolucoes da versao.

### dx:
- criado dev_tools.py com comandos reset_db, seed_demo_data, run_migrations e check_health.
- logging estruturado JSON em phoenix/logs/phoenix.log com rotacao diaria.
- inicializado Alembic com baseline de migracao e configuracao inicial.

# Changelog

## 2026-03-20

### feat:
- baseline Phoenix 3.0 iniciada com versao de pacote em 3.0.0.
- sincronizada constante global de versao em AppDefaults.VERSION.
- README atualizado para refletir fase Phoenix 3.0.
- criado roadmap inicial em docs/ROADMAP_3_0.md.
- bloco 1: criado native bridge com fallback Python e integracao em habitos + command palette.
- bloco 2: criado modulo assistant com backend ollama/transformers/rule-based e painel dock (Ctrl+A).
- bloco 3: adicionados modelos de conquistas, sprint e insights; migration 0004 criada; modulo Conquistas integrado.
- bloco 4: adicionados system tray e scheduler de lembretes com quick actions.
- bloco 5: modulo Diario reescrito com editor markdown, preview e mood tracker.
- bloco 6: adicionada view Gantt no modulo Projetos.
- bloco 7: modulo Analytics com radar chart e geracao de relatorio PDF.
- bloco 8: multi-perfil com ProfileManager, selecao de perfil e switch de banco.
- bloco 9: servidor web local implementado em phoenix/web/server.py com fallback stdlib quando FastAPI/Uvicorn nao estao disponiveis.
- bloco 10: i18n basico, dev_tools expandidos e novos testes para native/assistant/analytics/achievements.

### pending:
- bloco Rust (phoenix_native) adiado: rustc nao disponivel no ambiente atual, fallback Python ativado via phoenix/core/native_bridge.py.
- backend FastAPI permanece opcional; quando ausente, o bloco web opera com fallback stdlib.

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

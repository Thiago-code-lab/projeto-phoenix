# Projeto Phoenix (Redesign)

Plataforma pessoal all-in-one, local-first, construída com Streamlit + SQLite.

## Principais características
- Dashboard unificado com métricas reais do banco
- Módulos: Metas, Hábitos, Finanças, Biblioteca, Saúde, Diário, Projetos (Kanban funcional)
- Configurações globais (perfil, moeda, tema, backup do banco)
- Banco local `phoenix.db` com criação automática na primeira execução
- Arquitetura modular com componentes reutilizáveis

## Arquitetura

```text
projeto-phoenix/
├── app.py
├── config.py
├── phoenix.db
├── database/
│   ├── db.py
│   └── migrations/
├── modules/
│   ├── dashboard/
│   ├── goals/
│   ├── habits/
│   ├── finances/
│   ├── library/
│   ├── health/
│   ├── journal/
│   ├── projects/
│   └── settings/
├── components/
├── styles/
│   └── theme.css
└── utils/
```

## Como executar

1. Crie/ative seu ambiente virtual
2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Rode o app:

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

## Observações
- Tudo roda 100% local (sem API externa e sem login de terceiros)
- O módulo de Projetos implementa Kanban com movimentação por seleção de coluna (alternativa leve ao drag-and-drop nativo)
- O tema é aplicado via `styles/theme.css`

## Próximos aprimoramentos sugeridos
- Melhorar editor rico do Diário com preview lado a lado
- Adicionar paginação avançada para listas longas
- Adicionar testes automatizados para regras de negócio do banco

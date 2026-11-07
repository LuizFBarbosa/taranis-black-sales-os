# Taranis Black · Consultoria de IA para Negócios

Solução do **Challenge ONE G11 · AI for Business (Alura)** para a Taranis Black, empresa fictícia de ergonomia corporativa
(R$ 48 mi de faturamento, 280 pessoas, crescimento de 35% a.a.).
Rota 0 (base estratégica) + **Rota 1 — IA para Vendas e Comercial**.

**Site de demonstração (Sales OS):** `https://SEU-USUARIO.github.io/taranis-black-sales-os/` ← troque após publicar

## O que tem aqui

| Pasta / arquivo | Conteúdo |
|---|---|
| `docs/` | **Site publicado no GitHub Pages**: Rota 0, Política de IA, Pipeline priorizado, Playbook, Simulador de cliente, TCO, Régua de e-mail, Agentes e Materiais para download. |
| `agentes/taranis_sales_agents.py` | **Esquadrão de 6 agentes comerciais**: Qualificador (score explicável), Guardião da Política, Estrategista de Objeções, Redator, Escriba de CRM e Pedido. Modo offline (regras) ou online (Claude). |
| `saidas/` | Resultado da última execução: `leads_priorizados.xlsx`, `leads.json`, 20 rascunhos em `emails/`, `relatorio_execucao.md` e `prints/`. |
| `prompts/` | Custom GPT/Gem/Projeto Claude, simulador + avaliação, 5 objeções + régua, prompts de sistema dos agentes. |
| `skill/taranis-sales-coach/` | Skill do Claude para o time comercial. |
| `rota1_vendas_preenchido.docx` | Relatório executivo no template oficial (entregue via Google Docs). |
| `Politica_Corporativa_IA_Taranis_Black.docx` | Política de IA Responsável. |
| `site/` | Template e gerador do site (`build_site.py`). |
| `docs_build/` | Geradores dos dois `.docx`. |
| `dados/` | Entradas do kit do challenge: planilha de leads e template do relatório. |

## Como os agentes trabalham

```
CRM (dados/02_Leads...xlsx) ─┐
Catálogo + política ─────────┼─► Qualificador ─► Guardião ─► Estrategista ─► Redator / Escriba ─► PORTÃO HUMANO ─► cliente
Matriz de objeções ──────────┘     (score 0-100)  (11 alertas)  (contorno)     (e-mail, nota CRM)    (vendedor aprova)
```

Resultado da execução sobre os 20 leads parados (R$ 4,69 mi): 5 leads Tier A para hoje, pipeline ponderado de R$ 2,24 mi,
11 alertas de política. Entre eles, um prazo cotado errado que trava R$ 199 mil na FinCloud.

## Rodar localmente

```bash
pip install -r requirements.txt
python agentes/taranis_sales_agents.py --offline      # sem API, determinístico
# opcional, com Claude (claude-opus-5-5):
#   set ANTHROPIC_API_KEY=...   (Windows)  |  export ANTHROPIC_API_KEY=...  (Linux/Mac)
#   python agentes/taranis_sales_agents.py --online
python site/build_site.py --pages                     # atualiza docs/ (GitHub Pages)
python docs_build/preencher_rota1.py                  # regera o relatório
python docs_build/politica_ia.py                      # regera a política
```

O GitHub Pages só serve arquivos estáticos: os agentes Python **não rodam no site**. O site mostra o resultado deles (fila,
alertas, e-mails, notas de CRM). Para executar os agentes, clone o repositório e rode os comandos acima.

Publicação: veja [`docs/COMO_PUBLICAR.md`](docs/COMO_PUBLICAR.md).

---
Dados simulados do kit oficial do challenge. Taranis Black é uma empresa fictícia.

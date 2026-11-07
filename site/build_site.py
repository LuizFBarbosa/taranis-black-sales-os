"""Gera o site a partir do template e da saída dos agentes.

  python build_site.py           -> site/index.html (versão Claude Artifact)
  python build_site.py --pages   -> ../docs/ (versão GitHub Pages, com página Materiais e arquivos para download)
"""
import json
import shutil
import sys
from pathlib import Path

here = Path(__file__).parent
ent = here.parent
leads = json.loads((ent / "saidas" / "leads.json").read_text("utf-8"))
keep = ["id", "empresa", "segmento", "porte", "decisor", "cargo", "email", "produtos", "valor", "dores", "objecao", "status",
        "obj_id", "score", "score_detalhe", "tier", "probabilidade", "valor_ponderado", "gatilho", "alertas", "oportunidades",
        "proxima_acao", "prazo_acao", "contorno", "evidencias", "email_assunto", "email_corpo", "nota_crm"]
data = json.dumps([{k: l[k] for k in keep} for l in leads], ensure_ascii=False).replace("</", "<" + chr(92) + "/")
html = (here / "template.html").read_text("utf-8").replace("__LEADS_JSON__", data)

PAGES = "--pages" in sys.argv

# (arquivo de origem relativo a entregaveis/, destino em materiais/, título, descrição)
MATERIAIS = [
    ("Relatórios", [
        ("rota1_vendas_preenchido.docx", "Relatório executivo (template oficial)", "Rota 0 + Rota 1 preenchidas, com prints e prompts."),
        ("Politica_Corporativa_IA_Taranis_Black.docx", "Política Corporativa de IA", "Pode/não pode, dados, HITL, LGPD, vieses e comitê."),
        ("saidas/leads_priorizados.xlsx", "Fila priorizada dos 20 leads", "Score, tier, próxima ação, alertas, notas de CRM e e-mails."),
        ("saidas/relatorio_execucao.md", "Relatório de execução dos agentes", "Trilha de auditoria da última execução."),
    ]),
    ("Prompts e configuração de IA", [
        ("prompts/01_custom_gpt_playbook_taranis.md", "Custom GPT / Gem / Projeto Claude", "Instruções completas do Coach de Vendas."),
        ("prompts/02_simulador_cliente_e_avaliacao.md", "Simulador de cliente + avaliação", "Prompt de roleplay e scorecard."),
        ("prompts/03_objecoes_e_regua_email.md", "5 objeções + régua de e-mail", "Prompts de contorno, régua IF/ELSE e exemplo."),
        ("prompts/04_agentes_system_prompts.md", "Instruções dos agentes", "Prompts de sistema e contratos de saída."),
        ("skill/taranis-sales-coach/SKILL.md", "Skill do Claude", "taranis-sales-coach."),
    ]),
    ("Código dos agentes", [
        ("agentes/taranis_sales_agents.py", "Esquadrão de agentes (Python)", "Rode com --offline ou --online (Claude)."),
    ]),
]

if PAGES:
    nav = '      <a href="#materiais">Materiais</a>'
    cards = []
    for grupo, itens in MATERIAIS:
        lis = "".join(
            f'<li class="card" style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">'
            f'<div style="min-width:0"><h4>{t}</h4><p class="note">{d}</p></div>'
            f'<a class="btn ghost" style="text-decoration:none" href="materiais/{Path(src).name}" download>Baixar {Path(src).suffix[1:].upper()}</a></li>'
            for src, t, d in itens)
        cards.append(f'<div class="stack" style="gap:10px"><span class="eyebrow">{grupo}</span><ul class="clean">{lis}</ul></div>')
    page = f'''<!-- ============================ MATERIAIS ============================ -->
<section class="page" id="p-materiais"><div class="wrap stack">
  <div class="stack" style="gap:10px">
    <span class="eyebrow">Entregáveis do challenge</span>
    <h1>Materiais para download</h1>
    <p class="lede">Todos os artefatos produzidos na consultoria. O site funciona sem login: o simulador usa um cliente por regras (modo demonstração) e, na versão publicada no Claude, conversa com a IA ao vivo.</p>
  </div>
  {"".join(cards)}
  <div class="callout">Os e-mails gerados pelos agentes estão em <b>Pipeline IA</b> (clique em um lead) e na aba <i>Notas_CRM_e_Emails</i> da planilha.</div>
</div></section>'''
    html = html.replace("<!--__NAV_EXTRA__-->", nav).replace("<!--__PAGE_EXTRA__-->", page)
    out = ent / "docs"  # GitHub Pages: Settings > Pages > branch main, pasta /docs
    (out / "materiais").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text("<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
                                    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
                                    "<meta name=\"description\" content=\"Consultoria de IA para a Taranis Black — Challenge ONE G11\">\n"
                                    "</head>\n<body>\n" + html + "\n</body>\n</html>\n", "utf-8")
    (out / ".nojekyll").write_text("", "utf-8")
    for _, itens in MATERIAIS:
        for src, _, _ in itens:
            shutil.copy2(ent / src, out / "materiais" / Path(src).name)
    print("GitHub Pages ->", out)
else:
    html = html.replace("<!--__NAV_EXTRA__-->\n", "").replace("<!--__PAGE_EXTRA__-->\n", "")
    (here / "index.html").write_text(html, "utf-8")
    print("index.html", len(html) // 1024, "KB")

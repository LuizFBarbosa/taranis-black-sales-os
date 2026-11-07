"""Gera a Política Corporativa de IA Responsável da Taranis Black (.docx)."""
from pathlib import Path
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

OUT = Path(__file__).resolve().parents[1] / "Politica_Corporativa_IA_Taranis_Black.docx"
ACC = RGBColor(0x27, 0x47, 0xC8)
INK = RGBColor(0x1E, 0x22, 0x27)

d = docx.Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("left_margin", "right_margin"):
    setattr(sec, m, Cm(2.2))
sec.top_margin = sec.bottom_margin = Cm(2)

st = d.styles
st["Normal"].font.name = "Arial"
st["Normal"].font.size = Pt(10)
st["Normal"].paragraph_format.space_after = Pt(5)
for name, size in (("Title", 24), ("Heading 1", 15), ("Heading 2", 12)):
    s = st[name]
    s.font.name = "Arial"
    s.element.rPr.rFonts.set(qn("w:asciiTheme"), "") if s.element.rPr is not None else None
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = INK if name != "Heading 2" else ACC
    s.paragraph_format.space_before = Pt(14 if name == "Heading 1" else 8)
    s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.keep_with_next = True
    rpr = s.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts"); rpr.append(fonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        fonts.set(qn(a), "Arial")
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme"):
        if fonts.get(qn(a)) is not None:
            del fonts.attrib[qn(a)]


def p(text, bold_prefix=None, size=None):
    para = d.add_paragraph()
    if bold_prefix:
        r = para.add_run(bold_prefix); r.bold = True
    r = para.add_run(text)
    if size:
        r.font.size = Pt(size)
    return para


def bullets(items):
    for it in items:
        para = d.add_paragraph(style="List Bullet")
        if isinstance(it, tuple):
            r = para.add_run(it[0]); r.bold = True
            para.add_run(it[1])
        else:
            para.add_run(it)
        para.paragraph_format.space_after = Pt(3)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def table(head, rows, widths):
    t = d.add_table(rows=1, cols=len(head))
    t.style = "Table Grid"
    for i, h in enumerate(head):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(c, "1E2227")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(v); r.font.size = Pt(9)
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    d.add_paragraph()
    return t


# ---------------- Capa ----------------
d.add_paragraph("TARANIS BLACK · DOCUMENTO NORMATIVO", style="Normal").runs[0].font.color.rgb = ACC
d.add_paragraph("Política Corporativa de IA Responsável", style="Title")
p("Código POL-TI-007 · Versão 1.0 · Vigência: a partir da aprovação pelo Comitê de IA · Revisão anual obrigatória")
p("Aprovação: CEO · Encarregado de Dados (DPO) · Diretoria de Gente e Cultura · Diretoria de TI")
p("Princípio central: ", None).runs[0].bold = True
d.paragraphs[-1].add_run("a IA prepara, uma pessoa decide. Nenhuma saída de inteligência artificial chega a um cliente, candidato, "
                         "colaborador ou fornecedor sem revisão de uma pessoa identificada, que responde pelo conteúdo.")

d.add_heading("1. Objetivo", level=1)
p("Permitir que os 280 colaboradores da Taranis Black usem inteligência artificial generativa e preditiva para ganhar "
  "produtividade, com segurança da informação, proteção de dados pessoais (Lei 13.709/2018 — LGPD), mitigação de vieses "
  "e supervisão humana. Esta política complementa o Código de Conduta e a Política de Segurança da Informação.")

d.add_heading("2. Abrangência", level=1)
p("Aplica-se a colaboradores CLT, estagiários, terceiros, consultores e parceiros que acessem dados da Taranis Black, em "
  "qualquer ferramenta de IA: assistentes de chat (ChatGPT, Claude, Gemini, Copilot), Custom GPTs, Gems, Projetos, "
  "skills, agentes automatizados, recursos de IA embutidos em CRM, ERP e e-mail, e modelos preditivos internos.")

d.add_heading("3. Definições", level=1)
bullets([("IA generativa: ", "modelos que produzem texto, imagem ou código (LLMs)."),
         ("IA preditiva: ", "modelos que estimam probabilidades ou classificam (score de lead, risco de crédito, risco de saída)."),
         ("Automação tradicional: ", "regras determinísticas e extração de dados (OCR, motor de alçadas)."),
         ("Human-in-the-Loop (HITL): ", "etapa obrigatória em que uma pessoa revisa e aprova a saída antes de qualquer efeito externo."),
         ("Ferramenta homologada: ", "ferramenta aprovada por TI e DPO, com contrato corporativo, SSO e treino de modelo desativado."),
         ("Inventário de IA: ", "registro mantido pelo Comitê com todos os GPTs, Gems, agentes e modelos em uso, seus donos e dados.")])

d.add_heading("4. Ferramentas homologadas", level=1)
table(["Ferramenta", "Plano exigido", "Uso permitido"],
      [["Claude (Anthropic)", "Team ou Enterprise, SSO", "Análise, redação, Projetos, Artifacts, agentes via API"],
       ["ChatGPT (OpenAI)", "Team ou Enterprise, SSO", "Redação, Custom GPTs internos, análise de planilhas"],
       ["Gemini (Google)", "Workspace corporativo", "Gems, redação no Gmail/Docs"],
       ["API de modelos", "Contrato com cláusula de não retenção para treino", "Agentes do Inventário de IA"]],
      [4, 5, 7.6])
p("Contas pessoais e versões gratuitas são proibidas para qualquer dado classificado como Interno, Confidencial ou Restrito. "
  "Novas ferramentas são solicitadas ao Comitê pelo formulário de novo uso e avaliadas em até 10 dias úteis.")

d.add_heading("5. O que pode e o que não pode", level=1)
d.add_heading("5.1 Pode", level=2)
bullets(["Redigir rascunhos de e-mails, propostas, posts, roteiros e resumos com dados públicos ou internos.",
         "Usar dados de contato profissional de leads B2B (nome, cargo, empresa, e-mail corporativo) dentro de ferramentas homologadas.",
         "Analisar planilhas internas anonimizadas ou agregadas (DRE, pipeline, indicadores de RH por área).",
         "Criar Custom GPTs, Gems, Projetos, skills e agentes, desde que registrados no Inventário de IA e aprovados pelo Comitê.",
         "Usar IA para estudar, treinar argumentação (simulador de cliente) e preparar reuniões."])
d.add_heading("5.2 Não pode", level=2)
bullets(["Inserir dados pessoais sensíveis (LGPD art. 5º, II): atestados, CID, saúde, biometria, religião, filiação sindical, dados de dependentes.",
         "Inserir dados de RH nominais (salário, avaliação, entrevista de saída) fora de ambiente aprovado com RIPD.",
         "Usar contas pessoais ou ferramentas não homologadas com dados da empresa ou de clientes.",
         "Enviar ao cliente texto, preço, prazo, condição ou laudo gerado por IA sem revisão humana.",
         "Permitir que a IA decida sozinha crédito, contratação, promoção, desligamento, avaliação ou punição.",
         "Afirmar fatos que não constam em fonte oficial (catálogo, política comercial, laudos), como dados de emissões de carbono.",
         "Prometer descontos acima da alçada (vendedor 5%, gerente 10%, diretoria 15%) com base em sugestão de IA.",
         "Gerar conteúdo que imite pessoas reais, concorrentes, assinaturas, laudos técnicos ou documentos oficiais.",
         "Inserir segredos (senhas, chaves de API, dados bancários) em prompts."])

d.add_heading("6. Classificação de dados e uso com IA", level=1)
table(["Classe", "Exemplos na Taranis Black", "Regra de uso com IA"],
      [["Pública", "Catálogo, site, posts publicados, artigo técnico", "Qualquer ferramenta homologada"],
       ["Interna", "Playbook, metas, processos, preços de tabela", "Ferramentas homologadas"],
       ["Confidencial", "CRM, propostas, margens, DRE, dados de clientes", "Somente ambientes corporativos com não-treino; mínimo necessário"],
       ["Restrita", "Salários, avaliações, entrevistas de saída nominais, dados de saúde", "Proibida em IA externa; só anonimizada/agregada e com RIPD aprovado"]],
      [2.8, 6.5, 7.3])

d.add_heading("7. Supervisão humana (Human-in-the-Loop)", level=1)
table(["Iniciativa", "Quem aprova", "Quando", "Risco"],
      [["Copiloto Comercial (e-mails, propostas)", "Vendedor dono da conta", "Antes de todo envio", "Médio"],
       ["Desconto acima de 5%", "Gerente (até 10%) / Diretoria (até 15%)", "Antes da proposta", "Médio"],
       ["Score de lead", "Coordenação comercial", "Revisão mensal dos pesos", "Médio"],
       ["Decisão de crédito (Order-to-Cash)", "Gerente financeiro", "Toda negativa ou valor acima da alçada", "Alto"],
       ["Radar de Pessoas", "Gente e Cultura + gestor", "Todo alerta; nunca nominal fora do RH", "Alto"],
       ["Conteúdo público de marketing", "Marketing", "Antes de publicar", "Médio"]],
      [5, 4.4, 4.8, 2.4])
p("Toda aprovação fica registrada (quem, quando, o que mudou). Saídas de agentes carregam a marca \"RASCUNHO GERADO POR IA\" até a aprovação.")

d.add_heading("8. LGPD: bases legais e direitos dos titulares", level=1)
bullets([("Leads e clientes B2B: ", "legítimo interesse (art. 7º, IX), com teste de balanceamento documentado e opt-out em todo e-mail (art. 18)."),
         ("Colaboradores: ", "execução de contrato e cumprimento de obrigação legal (art. 7º, II e V). Dados de saúde só com base do art. 11."),
         ("Decisões automatizadas: ", "o titular pode pedir revisão de decisão tomada só com base em tratamento automatizado (art. 20), "
          "com explicação dos critérios. Aplica-se a crédito e a qualquer uso preditivo sobre pessoas."),
         ("Minimização: ", "enviar à IA só os campos necessários para a tarefa. Pseudonimizar quando possível."),
         ("RIPD: ", "Relatório de Impacto obrigatório antes de Order-to-Cash (crédito) e Radar de Pessoas."),
         ("Fornecedores: ", "contrato com cláusula de não uso para treino, local de processamento, retenção e notificação de incidente em 48h.")])

d.add_heading("9. Vieses: riscos identificados e mitigação", level=1)
p("O diagnóstico usou os dados reais da empresa e encontrou riscos concretos que esta política passa a controlar:")
table(["Risco", "Evidência", "Mitigação obrigatória"],
      [["Viés de gênero em modelos de pessoas", "Comercial: salário médio feminino R$ 6.805 vs. masculino R$ 8.645 (−21%); turnover feminino 25,3% vs. 20,0%",
        "Excluir gênero e proxies; medir paridade de erro por gênero a cada trimestre; reportar a diferença salarial ao RH"],
       ["Viés de segmento no lead scoring", "Score favorece tickets altos e cargos C-Level", "Cota mínima de atendimento ao Tier C; auditoria mensal de conversão por segmento"],
       ["Decisão de crédito discriminatória", "Score pode penalizar regiões ou porte", "Variáveis auditadas; revisão humana de negativas; canal de contestação"],
       ["Alucinação comercial", "Matriz oficial cita \"R$ 1,90/dia\", conta do catálogo dá R$ 2,26/dia", "Agente Guardião confere números contra fonte; sem fonte vira [confirmar]"],
       ["Dados de baixa qualidade", "Cargos sêniores com salário menor que júnior na base de RH", "Saneamento e dono de dado por área antes de treinar modelos"]],
      [3.8, 6.2, 6.6])

d.add_heading("10. Governança: Comitê de IA", level=1)
bullets([("Composição: ", "CEO (patrocinadora, voto de desempate), Encarregado de Dados (DPO) + Jurídico, TI e Segurança da Informação, "
          "Gente e Cultura, Diretoria Comercial, Finanças e 2 embaixadores de IA em rodízio semestral."),
         ("Responsabilidades: ", "homologar ferramentas, aprovar agentes e modelos, manter o Inventário de IA, acompanhar métricas de "
          "adoção e ROI, conduzir auditorias e decidir sobre incidentes.")])
table(["Cadência", "Ritual"],
      [["Semanal", "Embaixadores + TI: incidentes, dúvidas e pedidos de novos usos"],
       ["Mensal", "Comitê: adoção, ROI, inventário, aprovação de novos agentes"],
       ["Trimestral", "Auditoria de viés (score, crédito, Radar) e amostra de 50 saídas por agente"],
       ["Anual", "Revisão desta política, do RIPD e dos contratos; recertificação obrigatória"],
       ["Até 24h", "Resposta a incidente: vazamento, saída ofensiva ou decisão contestada"]],
      [3, 13.6])

d.add_heading("11. Incidentes", level=1)
p("Qualquer colaborador que perceber vazamento de dados, resposta ofensiva, decisão injusta ou uso indevido deve abrir chamado "
  "\"Incidente de IA\" no portal de TI em até 24 horas. O DPO avalia a necessidade de comunicação à ANPD e aos titulares (art. 48).")

d.add_heading("12. Treinamento e responsabilidades", level=1)
bullets(["Todos: trilha Básica (2h) antes de receber acesso às ferramentas homologadas; recertificação anual.",
         "Comercial: trilha Aplicada (6h) com playbook, prompts seguros e simulador.",
         "Embaixadores: trilha Avançada (agentes, auditoria, prompts de sistema).",
         "Gestores respondem pelo uso de IA nas suas equipes; descumprimento segue o Código de Conduta."])

d.add_heading("Termo de ciência", level=1)
p("Declaro que li e compreendi a Política Corporativa de IA Responsável da Taranis Black e me comprometo a cumpri-la.")
p("Nome: ______________________________   Área: ________________   Data: ___/___/______   Assinatura: ____________________")


# conformidade OOXML: atributos obrigatórios
for _s in d.sections:
    _m = _s._sectPr.find(qn("w:pgMar"))
    if _m is not None and _m.get(qn("w:gutter")) is None:
        _m.set(qn("w:gutter"), "0")
_z = d.settings.element.find(qn("w:zoom"))
if _z is not None and _z.get(qn("w:percent")) is None:
    _z.set(qn("w:percent"), "100")
d.save(OUT)
print("ok", OUT)

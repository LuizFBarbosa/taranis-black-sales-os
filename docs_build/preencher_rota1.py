"""Preenche o template rota1_vendas.docx com a solução completa (Rota 0 + Rota 1)."""
import copy
import re
from pathlib import Path

import docx
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from PIL import Image

ENT = Path(__file__).resolve().parents[1]  # raiz do repositório
PR = ENT / "saidas" / "prints"
SITE = "https://claude.ai/artifact/TJSgBbGfyC8QHMyHBixRJ7"

# recorte com borda completa do canvas
im = Image.open(PR / "diagnostico.png")
im.crop((100, 1050, 1300, 1885)).save(PR / "doc_canvas.png")

d = docx.Document(ENT / "dados" / "rota1_vendas.docx")  # template oficial
T = d.tables
INK = RGBColor(0x22, 0x22, 0x22)


def add_runs(p, text, size=9.5, color=INK, italic=False):
    """Texto com **negrito** inline."""
    for i, part in enumerate(re.split(r"\*\*", text)):
        if not part:
            continue
        r = p.add_run(part)
        r.bold = i % 2 == 1
        r.italic = italic
        r.font.size = Pt(size)
        r.font.color.rgb = color


def fill(cell, blocks):
    for p in list(cell.paragraphs):
        p._p.getparent().remove(p._p)
    for b in blocks:
        kind, val = (b if isinstance(b, tuple) else ("p", b))[:2]
        p = cell.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(3)
        pf.space_before = Pt(0)
        if kind == "p":
            add_runs(p, val)
        elif kind == "h":
            pf.space_before = Pt(5)
            add_runs(p, val, size=10, color=RGBColor(0x27, 0x47, 0xC8))
            p.runs[0].bold = True
        elif kind == "b":
            pf.left_indent = Cm(0.45)
            pf.first_line_indent = Cm(-0.35)
            add_runs(p, "–  " + val)
        elif kind == "img":
            w = b[2] if len(b) > 2 else 15.5
            p.add_run().add_picture(str(PR / val), width=Cm(w))
        elif kind == "cap":
            add_runs(p, val, size=8.5, color=RGBColor(0x66, 0x66, 0x66), italic=True)
        elif kind == "code":
            pf.left_indent = Cm(0.2)
            for j, line in enumerate(val.split("\n")):
                r = p.add_run(line)
                r.font.name = "Consolas"
                r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
                r.font.size = Pt(8)
                r.font.color.rgb = INK
                if j < len(val.split("\n")) - 1:
                    r.add_break()


# ---------------- Identificação ----------------
fill(T[2].rows[0].cells[1], ["[Seu nome completo]"])
fill(T[2].rows[1].cells[1], ["barbosa@arcom.com.br"])
for p in T[3].rows[0].cells[0].paragraphs:
    for r in p.runs:
        if "[ ]  Rota 1" in r.text:
            r.text = r.text.replace("[ ]  Rota 1", "[X]  Rota 1")
            r.bold = True

# ---------------- Resumo executivo (14 linhas) ----------------
resumo = [
    "Para: CEO da Taranis Black  |  Assunto: Onde a IA devolve margem em 2027",
    "Diagnóstico: a receita bateu o orçamento (R$ 48,5 mi), mas o EBITDA caiu 41% (R$ 5,8 mi vs. R$ 9,8 mi).",
    "R$ 3,2 mi dessa perda têm uma só causa: dados digitados à mão entre proposta, crédito e expedição",
    "(fretes de emergência, reentregas, cancelamentos por crédito lento e inadimplência sem régua de cobrança).",
    "No comercial, 40% do tempo vai para CRM e e-mail; o turnover é de 30,9% e a 1ª causa é a sobrecarga manual.",
    "Recomendo um programa em 3 ondas, começando pelo que já temos em mãos (Claude/ChatGPT Team + CRM):",
    "1) Copiloto Comercial: 6 agentes que priorizam leads, conferem a proposta contra a política, escrevem e-mails",
    "    e notas de CRM e treinam objeções num simulador. Já rodamos nos 20 leads parados (R$ 4,7 mi):",
    "    5 leads Tier A para hoje e 11 alertas de política, entre eles um prazo errado que trava R$ 199 mil na FinCloud.",
    "2) Order-to-Cash inteligente (crédito em 4h, sem redigitação) e 3) Radar de Pessoas para reter talentos.",
    "Investimento no ano 1: R$ 810 mil. Retorno estimado: R$ 2,69 mi/ano, payback de ~3,6 meses (ROI 3,3×).",
    "Governança: política de IA aprovada antes da Onda 2, comitê mensal, auditoria trimestral de viés e LGPD;",
    "nenhum e-mail, preço ou decisão de crédito sai sem aprovação humana.",
    "Peço sua aprovação para iniciar a Onda 1 em 30 dias, com meta de 80% dos vendedores usando o Copiloto em 60.",
]
for row, txt in zip(T[7].rows, resumo):
    fill(row.cells[0], [txt])

# ---------------- Rota 0 · Etapa 1 ----------------
fill(T[10].rows[1].cells[1], [
    "Mapeamos 9 oportunidades a partir dos 6 arquivos do kit (DRE, gargalos, SIPOC, CRM, base de RH, pesquisa de clima) e "
    "escolhemos os 3 casos com maior retorno sobre a causa raiz comum: **trabalho manual entre áreas**.",
    ("h", "Caso 1 · Copiloto Comercial"),
    ("b", "**Problema:** 40%+ da semana em CRM, e-mails genéricos e qualificação sem dados; 20 leads (R$ 4,69 mi) parados aguardando contorno."),
    ("b", "**Dados:** CRM, catálogo e política comercial, matriz de 5 objeções, guia de tom de voz."),
    ("b", "**Solução:** esquadrão de 6 agentes (qualificação, conferência de política, objeções, e-mail, CRM, pedido) + simulador de cliente."),
    ("b", "**Valor:** +5% de conversão B2B (R$ 1,68 mi de receita, R$ 736 mil de margem) e ~20 mil horas/ano devolvidas à venda."),
    ("h", "Caso 2 · Order-to-Cash Inteligente"),
    ("b", "**Problema:** crédito em 48h (meta 4h) e proposta redigitada do PDF ao ERP e ao CD → R$ 1,25 mi cancelados, R$ 960 mil em fretes duplicados, 6,8% de boletos com erro."),
    ("b", "**Solução:** extração automática da proposta, motor de regras de alçada e score de risco de inadimplência."),
    ("b", "**Valor:** R$ 1,27 mi/ano (margem recuperada R$ 328 mil + fretes R$ 672 mil + boletos R$ 273 mil)."),
    ("h", "Caso 3 · Radar de Pessoas"),
    ("b", "**Problema:** turnover 30,9% no comercial e 38,5% no suporte; 29% saem em 90 dias."),
    ("b", "**Solução:** análise de sentimento da pesquisa de clima, alerta de risco por equipe e assistente de onboarding com o playbook."),
    ("b", "**Valor:** −25% de saídas (~10 pessoas/ano) ≈ R$ 180 mil e rampa mais curta para SDRs."),
    ("img", "doc_canvas.png", 15.5),
    ("cap", "AI Canvas no Sales OS (seção Rota 0 · Estratégia)."),
])
fill(T[10].rows[2].cells[1], [
    ("b", "**Copiloto Comercial = Generativa + Preditiva.** Escrever e-mail, contorno e nota de CRM é geração de linguagem (LLM). "
          "A priorização é preditiva, mas usamos um score explicável por regras (valor, urgência, estágio, objeção, decisor) "
          "porque ainda não há histórico de ganho/perda para treinar um modelo; ele vira modelo estatístico quando houver 6 meses de dados."),
    ("b", "**Order-to-Cash = Tradicional + Preditiva.** Extração de PDF e regras de alçada/frete são automação tradicional "
          "(determinística e auditável, como o crédito exige). O risco de inadimplência é preditivo (histórico de pagamento + Serasa)."),
    ("b", "**Radar de Pessoas = Preditiva + Generativa.** Risco de saída é classificação preditiva; ler 280 comentários abertos e "
          "agrupar temas é tarefa generativa (análise de sentimento)."),
])
fill(T[10].rows[3].cells[1], [
    "Todas exigem supervisão humana, em níveis diferentes:",
    ("b", "**Copiloto (risco médio):** todo e-mail nasce como rascunho e é aprovado pelo vendedor; desconto acima de 5% vai ao gerente (≤10%) ou diretoria (≤15%)."),
    ("b", "**Order-to-Cash (risco alto):** negativa de crédito ou valor acima da alçada é decidida pelo gerente financeiro. "
          "Decisão automatizada que afeta o cliente dá direito a revisão (LGPD art. 20)."),
    ("b", "**Radar de Pessoas (risco alto):** a IA nunca decide promoção, avaliação ou desligamento. Alertas só agregados por equipe e lidos pelo RH. "
          "Dados de saúde (absenteísmo) são sensíveis (LGPD art. 11)."),
])

# ---------------- Rota 0 · Etapa 2 ----------------
fill(T[11].rows[1].cells[1], [
    "Pontuamos 9 iniciativas de 0 a 10 em impacto (ganho no EBITDA e na receita) e esforço (custo, integração com o ERP legado, risco de dados):",
    ("img", "doc_matriz.png", 15.5),
    ("b", "**Onda 1 (0–90 dias) — ganhos rápidos:** A Copiloto Comercial · B Lead scoring · C Régua de cobrança · D Conteúdo de marketing (Gem)."),
    ("b", "**Onda 2 (3–6 meses) — estratégicos:** E Order-to-Cash · F Radar de Pessoas · G Rastreio de pedidos no atendimento."),
    ("b", "**Onda 3 (6–12 meses):** H Conciliação contábil · I Previsão de demanda do CD (exigem ERP com API e dados limpos)."),
    "A Onda 1 usa ferramentas que a empresa já pode contratar sem integração e financia as próximas.",
])
fill(T[11].rows[2].cells[1], [
    ("img", "doc_roi.png", 15.5),
    ("b", "**Copiloto:** horas manuais −50% (40%→20% da semana), resposta a lead < 4h, conversão +5 p.p., 80% dos vendedores usando toda semana em 60 dias."),
    ("b", "**Order-to-Cash:** homologação 48h→4h, reentregas 2,8%→0,8% do faturamento, boletos com erro 6,8%→<1%, fechamento 7→2 dias."),
    ("b", "**Régua de cobrança:** inadimplência > 90 dias 3,4%→2,2%."),
    ("b", "**Radar:** turnover em 90 dias 29%→15%; eNPS comercial +18→+35."),
    ("cap", "Premissas: 55 vendedores, 44 h/semana, custo-hora carregado R$ 75; margem bruta 43,8%; reposição = 3 salários. Investimentos a validar com TI/Compras."),
])
fill(T[11].rows[3].cells[1], [
    ("b", "**Patrocínio visível:** a CEO abre o programa e apresenta o placar mensal. Mensagem: a IA tira a digitação do caminho; quem vende continua sendo a pessoa."),
    ("b", "**Embaixadores:** 1 a cada 8 pessoas (7 no comercial), com treino antecipado; testam prompts e apoiam colegas."),
    ("b", "**Treino em 3 trilhas:** Básico (todos, 2h, política e prompts seguros) · Aplicado (vendas, 6h, playbook e simulador) · Avançado (embaixadores)."),
    ("b", "**Começar pela dor de quem usa:** o primeiro agente entregue é o Escriba de CRM, que tira tarefa do vendedor, não o que mede o vendedor."),
    ("b", "**Medir e celebrar:** placar semanal de horas devolvidas, reconhecimento do melhor contorno no simulador, office hours às sextas, pesquisa de adoção em 30/60/90 dias."),
])

# ---------------- Rota 0 · Etapa 3 ----------------
fill(T[12].rows[1].cells[1], [
    "Documento completo: **Politica_Corporativa_IA_Taranis_Black.docx** (anexo). Princípio: a IA prepara, uma pessoa decide.",
    ("h", "Pode"),
    ("b", "Usar ferramentas homologadas (Claude, ChatGPT e Gemini em planos corporativos, com treino desativado)."),
    ("b", "Redigir rascunhos de e-mails, propostas, posts e resumos com dados públicos ou internos."),
    ("b", "Usar dados de contato B2B de leads dentro das ferramentas homologadas (legítimo interesse)."),
    ("b", "Criar GPTs, Gems, Projetos e agentes registrados no inventário e aprovados pelo comitê."),
    ("h", "Não pode"),
    ("b", "Colar dados sensíveis (atestados, CID, saúde, biometria) ou dados de RH nominais em qualquer IA."),
    ("b", "Usar contas pessoais ou ferramentas não homologadas com dados da empresa."),
    ("b", "Enviar ao cliente texto, preço, prazo ou laudo gerado por IA sem revisão humana."),
    ("b", "Deixar a IA decidir sozinha crédito, contratação, promoção, desligamento ou avaliação."),
    ("b", "Afirmar fatos fora do catálogo (ex.: dados de carbono) ou prometer desconto fora da alçada."),
    ("img", "doc_politica.png", 15.5),
])
fill(T[12].rows[2].cells[1], [
    "Riscos encontrados **nos próprios dados do kit**, não hipotéticos:",
    ("b", "**Viés de gênero:** no comercial, mulheres ganham em média R$ 6.805 e homens R$ 8.645 (−21%); mulheres saem mais (25,3% vs. 20,0%). "
          "Um modelo de turnover treinado com salário repetiria a desigualdade. Mitigação: remover gênero e proxies, medir paridade de erro por gênero a cada trimestre e levar o achado ao RH."),
    ("b", "**Dado sensível de saúde (LGPD art. 11):** absenteísmo e atestados. Mitigação: só agregado; RIPD antes do Radar de Pessoas."),
    ("b", "**Decisão automatizada de crédito (LGPD art. 20):** negativa sempre revisada por pessoa, com explicação e canal de contestação."),
    ("b", "**Viés de segmento no lead scoring:** score favorece tickets altos e C-Level. Mitigação: cota de atendimento ao Tier C e auditoria mensal de conversão por segmento."),
    ("b", "**Alucinação comercial:** a matriz oficial cita \"menos de R$ 1,90/dia\", mas a conta com o catálogo dá R$ 2,26/dia (Specialist). O Agente Guardião confere toda afirmação numérica."),
    ("b", "**Qualidade de dados:** SDR Pleno com R$ 11.140 e Executivo Sênior com R$ 3.850 na base de RH. Saneamento antes de treinar qualquer modelo."),
    ("b", "**Base legal:** leads B2B por legítimo interesse (art. 7º, IX) com opt-out em todo e-mail (art. 18); colaboradores por execução de contrato e obrigação legal."),
])
fill(T[12].rows[3].cells[1], [
    ("b", "**Comitê de IA:** CEO (patrocinadora), Encarregado de Dados (DPO) + Jurídico, TI/Segurança, Gente e Cultura, Diretoria Comercial, Finanças e 2 embaixadores (rodízio semestral)."),
    ("b", "**Semanal:** incidentes e pedidos de novos usos (embaixadores + TI)."),
    ("b", "**Mensal:** comitê revisa adoção, ROI, inventário de IA e aprova novos agentes."),
    ("b", "**Trimestral:** auditoria de viés (score, crédito, Radar) e amostra de 50 saídas por agente."),
    ("b", "**Anual:** revisão da política, do RIPD e dos contratos; recertificação obrigatória."),
    ("b", "**Incidentes:** resposta em até 24h (vazamento, saída ofensiva, decisão contestada)."),
])

# ---------------- Rota 1 · Etapa 1 ----------------
fill(T[14].rows[1].cells[1], [
    "Tese do playbook: **vendemos redução de risco e de custo de pessoas, não cadeiras.** 7 etapas, cada uma com objetivo, critério de saída e apoio de IA:",
    ("b", "**1 Pesquisa e hipótese** — hipótese de dor (NR-17, turnover, acústica, ESG) escrita no CRM · Agente Qualificador."),
    ("b", "**2 Diagnóstico SPIN** — dor com número e dono (atestados, saídas, auditoria, data de obra) · roteiro gerado por IA por persona."),
    ("b", "**3 Proposta de valor** — business case aceito · calculadora de TCO e one-pager para o CFO."),
    ("b", "**4 Proposta técnica** — mix, prazo do CD, frete e condição sem alerta · Agente Guardião da Política."),
    ("b", "**5 Objeções** — contorno com evidência, desconto só por alçada (5/10/15%) · matriz de 5 objeções + simulador."),
    ("b", "**6 Fechamento** — pedido estruturado para crédito e CD em até 4h · Agente de Pedido."),
    ("b", "**7 Pós-venda** — laudo entregue, NPS em 30 dias, expansão para outras áreas · régua pós-venda."),
    "**6 personas de decisão** mapeadas no pipeline real: RH/People, Facilities, Compras, CFO/COO, Segurança do Trabalho (EHS) e Arquitetura.",
    "**Fila priorizada pelos agentes** (20 leads, R$ 4,69 mi; ponderado R$ 2,24 mi): Tier A para hoje = Prime Health, Studio Alfa, Vanguarda, Atlas e Prisma.",
    ("img", "doc_pipeline.png", 15.5),
    ("cap", "Sales OS · Pipeline IA: score explicável, objeção, próxima ação com prazo e alertas do Agente Guardião."),
])
fill(T[14].rows[2].cells[1], [
    ("h", "OBJ-01 · Preço (5 leads: Zenith, Apex, OmniVarejo, InovaPay, LogiMax)"),
    "**Argumento:** compare o ciclo, não a etiqueta. Cadeira de R$ 800 dura ~14 meses: em 5 anos são 4,3 trocas (R$ 3.430/posto) sem laudo. "
    "ErgoPro Specialist: R$ 2.490 com 5 anos de garantia = R$ 2,26 por dia útil, com laudo NR-17. Contraproposta muda o mix, não o preço "
    "(LogiMax: trocar 12 SmartDesk Studio por Compact + 5% do vendedor reduz ~21% sem tocar margem unitária).",
    ("code", "Prompt: \"O cliente {empresa} diz: '{objeção}'. Usando SOMENTE o catálogo, monte (1) resposta de até 80 palavras comparando\n"
             "custo total em {anos} anos com produto de R$ {preço} e vida útil de 14 meses; (2) pergunta que quantifique a dor;\n"
             "(3) contraproposta dentro da alçada de 5%/10%. Marque [confirmar] o que faltar.\""),
    ("h", "OBJ-02 · Orçamento/CAPEX (5: Vanguarda, NeoOffice, Delta, Hub Criativo, Orion)"),
    "**Argumento:** é mitigação de risco, não gasto opcional. One-pager para o CFO: parcela 30/60/90 vs. custo atual de atestados e reposição; entrega faseada.",
    ("code", "Prompt: \"Escreva um one-pager para o CFO da {empresa} justificando {produtos} ({valor}) como redução de risco: problema em\n"
             "números, custo de não agir em 12 meses, opções 30/60/90 e entrega faseada, decisão pedida. Máx. 200 palavras.\""),
    ("h", "OBJ-03 · Fornecedor atual (4: Prime Health, Atlas, BioSaúde, MetaData)"),
    "**Argumento:** não peça para trocar o fornecedor; proponha piloto de 2 posições por 15 dias com laudo antes/depois e leve RH e Segurança do Trabalho para a mesa.",
    ("code", "Prompt: \"Proposta de piloto de 15 dias com 2 posições para {empresa}: área, indicadores (queixas, conforto, laudo\n"
             "antes/depois), critério de sucesso e próximo passo. Não critique o fornecedor atual.\""),
    ("h", "OBJ-04 · Prazo (3: Prisma, FinCloud, Nexo)"),
    "**Argumento:** primeiro confira o prazo cotado. A FinCloud (BH) recebeu 25 dias, mas o catálogo garante 5–8 dias úteis no Sudeste para itens em estoque. "
    "Depois, entrega escalonada: lote essencial em até 7 dias úteis do CD Joinville.",
    ("code", "Prompt: \"Cronograma de entrega escalonada para {empresa} em {cidade}, itens {produtos}, data-limite {data}, usando os\n"
             "prazos oficiais. Se o prazo cotado estiver acima do oficial, aponte o erro primeiro.\""),
    ("h", "OBJ-05 · Customização (3: Studio Alfa, Aurora, Solaris)"),
    "**Argumento:** engenharia de aplicação com a arquitetura; personalização gratuita acima de 30 posições (+5 dias úteis), amostras em 48h, BIM. "
    "O que não está no catálogo (relatório de carbono da Solaris) não se promete: registra e escala.",
    ("code", "Prompt: \"Como engenheiro de aplicação, responda ao pedido '{pedido}' da {empresa} em 3 partes: o que a política\n"
             "atende, o que precisa de validação técnica e o próximo passo. Nunca confirme algo fora do catálogo.\""),
    ("cap", "Todos os prompts completos: entregaveis/prompts/03_objecoes_e_regua_email.md."),
])
fill(T[14].rows[3].cells[1], [
    ("code", "Você vai interpretar {decisor}, {cargo} da {empresa} ({segmento}, {porte} colaboradores), em uma negociação\n"
             "com um consultor da Taranis Black.\n\n"
             "CONTEXTO DO SEU PERSONAGEM\n"
             "- Você está cotando: {produtos} ({valor}).\n"
             "- Dor real da empresa: {dores}\n"
             "- Sua objeção principal: {objecao}\n"
             "- Estágio: {status}.\n\n"
             "COMO SE COMPORTAR\n"
             "- Nível de resistência: {moderado | difícil | cético extremo}. Não aceite argumentos genéricos\n"
             "  (\"qualidade\", \"design\"). Só ceda com número, prova (laudo NR-17, garantia, prazo do CD, piloto)\n"
             "  ou uma condição que resolva sua restrição.\n"
             "- Faça perguntas que um {cargo} faria. Traga uma segunda objeção realista se a primeira for bem contornada.\n"
             "- Respostas curtas (2 a 4 frases), português do Brasil, tom profissional.\n"
             "- Nunca saia do personagem e nunca dê dicas ao consultor.\n"
             "- Se o consultor prometer algo fora da política (desconto > 15%, prazo < 5 dias úteis, dado inexistente),\n"
             "  desconfie e peça por escrito.\n"
             "- Quando o consultor escrever \"avaliar\", saia do personagem e dê notas 0-10 em empatia, uso de evidências,\n"
             "  aderência à política e avanço, com 2 melhorias e 1 frase-modelo.\n\n"
             "Comece com uma frase de abertura apresentando sua objeção."),
    "No Sales OS o simulador roda ao vivo com Claude para qualquer um dos 20 leads reais e devolve a avaliação em formato de scorecard.",
])
fill(T[14].rows[4].cells[1], [
    f"**Sales OS (site com Pipeline, Playbook, Simulador ao vivo, TCO, Régua e Agentes):** {SITE}",
    "**Custom GPT / Projeto Claude / Gem:** instruções completas em prompts/01_custom_gpt_playbook_taranis.md "
    "[colar aqui o link compartilhável depois de criar o GPT].",
    "**Skill do Claude:** skill/taranis-sales-coach/SKILL.md.",
    ("img", "doc_simulador.png", 15.5),
    ("cap", "Simulador de cliente: escolha do lead, nível de dificuldade, ficha do decisor e o prompt usado."),
])

# ---------------- Rota 1 · Etapa 2 (opcional) ----------------
fill(T[15].rows[1].cells[1], [
    "Gatilho diário às 07:00: o Agente Qualificador lê o CRM. **SE** dias sem contato ≥ 3 **E** status ≠ Ganho/Perdido, o lead entra no ramo da sua objeção:",
    ("b", "**SE Preço:** D0 TCO personalizado → D+3 abriu? convite para a calculadora : assunto alternativo → D+7 case do segmento."),
    ("b", "**SE Orçamento:** D0 one-pager CFO → D+5 simulação 30/60/90 ou entrega faseada → D+20 lembrete na reabertura do orçamento."),
    ("b", "**SE Fornecedor:** D0 proposta de piloto → D+4 conteúdo NR-17 para EHS/RH → D+10 convite ao showroom."),
    ("b", "**SE Prazo:** D0 (mesmo dia) cronograma por lotes → D+1 ligação do vendedor; sem automação depois."),
    ("b", "**SE Customização:** D0 kit BIM + amostras → D+2 confirmação de envio → D+6 agenda com engenharia."),
    ("b", "**SE Tier C sem resposta em 21 dias:** sai para a nutrição mensal de marketing."),
    "**Em qualquer ramo:** respondeu → régua pausa e o Escriba cria tarefa em 2h; clicou 2× ou abriu proposta → ligar no mesmo dia; "
    "pediu descadastro → opt-out imediato (LGPD art. 18). **Portão humano:** todo e-mail é rascunho aprovado pelo dono da conta; máx. 1 e-mail a cada 3 dias úteis.",
    ("img", "doc_regua.png", 15.5),
])
fill(T[15].rows[2].cells[1], [
    ("h", "Assunto"),
    ("code", "Gere 5 opções de assunto para {decisor} ({cargo}) da {empresa}, segmento {segmento}.\n"
             "Contexto: dor = {dor}; objeção = {objeção}; etapa = {etapa}.\n"
             "Regras: até 55 caracteres; cite a empresa ou um número concreto; sem CAIXA ALTA, emojis, \"urgente\",\n"
             "\"imperdível\" ou desconto; tom Taranis Black. Justifique cada uma em 6 palavras e marque a favorita."),
    ("h", "Corpo por segmento"),
    ("code", "Escreva o e-mail da etapa {etapa} para {decisor} ({cargo}) da {empresa}. Segmento: {OBJ-01..05}.\n"
             "1. Abertura que reconhece a objeção sem repeti-la (1 frase).\n"
             "2. Um dado que liga a dor ao custo de não agir (só catálogo, política e artigo Taranis Labs).\n"
             "3. A prova do segmento: TCO | 30/60/90 ou entrega faseada | piloto 15 dias | cronograma por lotes | amostras + BIM.\n"
             "4. Um único CTA com data.\n"
             "Limites: até 140 palavras; sem desconto; dado ausente vira [confirmar]. Saída: assunto, corpo, nota CRM."),
])
fill(T[15].rows[3].cells[1], [
    "**Para:** Otávio Mesquita Jr. (Diretor de TI e Infraestrutura, Zenith Seguradora) · **Segmento:** OBJ-01 Preço · **Etapa:** D0",
    "**Assunto:** Zenith: custo por estação em 5 anos, lado a lado",
    "Olá, Otávio,",
    "Comparar a SmartDesk com a mesa do marketplace é uma decisão responsável — e vale fazer a conta do ciclo inteiro.",
    "No modelo 3x2 que vocês estão implantando, cada mesa será usada por mais de uma pessoa. É aí que entram as 4 memórias de altura "
    "por usuário e o motor duplo alemão com garantia estrutural de 5 anos (3 anos para motor e controladora). Mesas de motor único, "
    "sem garantia local, costumam exigir troca de motor antes do terceiro ano [confirmar dado de mercado com Engenharia].",
    "Preparei o comparativo de custo por posto em 5 anos para as 80 estações, já com o laudo NR-17 individual que acompanha toda compra B2B.",
    "Posso apresentar em 20 minutos na quinta, 23/10, às 10h?",
    "Abraço, [Nome do consultor] | Taranis Black",
    ("cap", "Nota CRM: OBJ-01 Zenith · enviado TCO 5 anos · CTA reunião 23/10 · aguardando resposta. Os 20 rascunhos estão em saidas/emails/."),
])
fill(T[15].rows[4].cells[1], [
    f"**Régua e gerador de e-mail ao vivo:** {SITE} (seção Régua).",
    "**Rascunhos gerados pelos agentes:** saidas/emails/*.md e aba Notas_CRM_e_Emails de saidas/leads_priorizados.xlsx.",
    ("img", "doc_agentes.png", 15.5),
    ("cap", "Esquadrão de 6 agentes: fontes → preparação → execução → portão humano → cliente/operação."),
])

# ---------------- Anexo de evidências ----------------
ev = [
    ("Sales OS (site Taranis Black)", "Site com Rota 0, política, pipeline priorizado, playbook, simulador ao vivo, TCO, régua e agentes", SITE,
     "Prints neste documento", "Abrir no navegador; o simulador e o gerador de e-mail usam Claude ao vivo"),
    ("Esquadrão de agentes (Python)", "6 agentes: qualificação, política, objeções, e-mail, CRM, pedido. Claude claude-opus-5-5 no modo online",
     "entregaveis/agentes/taranis_sales_agents.py", "Arquitetura (Etapa 2)", "python taranis_sales_agents.py --offline | --online"),
    ("Fila priorizada (Excel)", "20 leads com score, tier, probabilidade, próxima ação, alertas, notas de CRM e modelo de score",
     "entregaveis/saidas/leads_priorizados.xlsx", "Pipeline (Etapa 1)", "Abrir toda manhã; ordenar por rank"),
    ("Custom GPT / Gem / Projeto", "Coach de vendas consultivas com playbook, 5 objeções e simulação",
     "entregaveis/prompts/01_custom_gpt_playbook_taranis.md", "—", "Colar as instruções e anexar catálogo + leads"),
    ("Prompts de simulação e avaliação", "Roleplay do decisor + scorecard de argumentação", "entregaveis/prompts/02_simulador_cliente_e_avaliacao.md",
     "Simulador (Etapa 1)", "Treino diário de 15 min antes das ligações Tier A"),
    ("Prompts de objeções e régua", "5 prompts de contorno, régua IF/ELSE, prompts de assunto e corpo, exemplo", "entregaveis/prompts/03_objecoes_e_regua_email.md",
     "Régua (Etapa 2)", "Usar no GPT ou no Redator"),
    ("Skill do Claude", "taranis-sales-coach: fatos do catálogo, fluxo e limites", "entregaveis/skill/taranis-sales-coach/SKILL.md", "—",
     "Instalar em ~/.claude/skills ou em claude.ai"),
    ("Política Corporativa de IA", "Pode/não pode, classificação de dados, HITL, LGPD, vieses, comitê", "entregaveis/Politica_Corporativa_IA_Taranis_Black.docx",
     "Política (Etapa 3)", "Aprovar no comitê antes da Onda 2"),
    ("Rascunhos de e-mail", "20 e-mails personalizados aguardando revisão humana", "entregaveis/saidas/emails/", "—", "Revisar e enviar pelo dono da conta"),
]
tbl = T[18]
tmpl = copy.deepcopy(tbl.rows[1]._tr)
while len(tbl.rows) - 1 < len(ev):
    tbl._tbl.append(copy.deepcopy(tmpl))
for row, vals in zip(tbl.rows[1:], ev):
    for c, v in zip(row.cells, vals):
        fill(c, [("p", v)])
        for r in c.paragraphs[0].runs:
            r.font.size = Pt(8.5)

fill(T[21].rows[0].cells[1], ["[Opcional — cole aqui o link do vídeo de até 5 minutos]"])


# conformidade OOXML: atributos obrigatórios
for _s in d.sections:
    _m = _s._sectPr.find(qn("w:pgMar"))
    if _m is not None and _m.get(qn("w:gutter")) is None:
        _m.set(qn("w:gutter"), "0")
_z = d.settings.element.find(qn("w:zoom"))
if _z is not None and _z.get(qn("w:percent")) is None:
    _z.set(qn("w:percent"), "100")
out = ENT / "rota1_vendas_preenchido.docx"
d.save(out)
print("ok", out)

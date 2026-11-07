"""
Taranis Black — Esquadrão de Agentes Comerciais (Sales Agent Squad)
====================================================================

Pipeline que automatiza as tarefas repetitivas que hoje consomem >40% da semana
do time B2B. Cada "agente" tem UMA responsabilidade e um contrato de saída
estruturado (JSON validado), e nenhum deles envia nada ao cliente sem aprovação
humana (Human-in-the-Loop).

  1. Agente Qualificador (preditivo / regras)   -> score 0-100, tier A/B/C, probabilidade
  2. Agente Guardião da Política Comercial       -> confere frete CIF/FOB, prazo, customização,
                                                   alçada de desconto e condição de pagamento
                                                   contra o catálogo oficial
  3. Agente Estrategista de Objeções             -> classifica a objeção (OBJ-01..05) e monta o
                                                   contorno com evidência do catálogo
  4. Agente Redator (e-mail consultivo)          -> rascunho personalizado no tom de voz da marca
  5. Agente Escriba de CRM                       -> nota de CRM padronizada + próxima ação + data

Modos de execução
-----------------
  python taranis_sales_agents.py --offline     # determinístico, sem API (padrão se não houver chave)
  python taranis_sales_agents.py --online      # agentes 3/4/5 usam Claude (claude-opus-5-5)

Saídas (pasta ../saidas):
  leads_priorizados.xlsx   — fila de trabalho do vendedor (ordenada por score)
  leads.json               — mesma base, consumida pelo Sales OS (site)
  emails/<id>.md           — rascunhos de e-mail para revisão humana
  relatorio_execucao.md    — log do que cada agente fez (trilha de auditoria)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parents[2]
LEADS_XLSX = Path(__file__).resolve().parents[1] / "dados" / "02_Leads_B2B_Comercial.xlsx"  # cópia do kit oficial
OUT = Path(__file__).resolve().parents[1] / "saidas"
HOJE = date(2026, 10, 20)  # data de referência da simulação (dia útil seguinte ao último contato do CRM)

# ---------------------------------------------------------------------------
# Base de conhecimento oficial (extraída do 01_Catalogo_Produtos_e_Precos)
# ---------------------------------------------------------------------------
CATALOGO = {
    "ErgoPro Executive": {"preco": 3490, "garantia_anos": 5, "linha": "ErgoPro"},
    "ErgoPro Specialist": {"preco": 2490, "garantia_anos": 5, "linha": "ErgoPro"},
    "ErgoPro Core": {"preco": 1890, "garantia_anos": 3, "linha": "ErgoPro"},
    "SmartDesk Pro Dual": {"preco": 4800, "garantia_anos": 5, "linha": "SmartDesk"},
    "SmartDesk Studio": {"preco": 3600, "garantia_anos": 5, "linha": "SmartDesk"},
    "SmartDesk Compact": {"preco": 2700, "garantia_anos": 3, "linha": "SmartDesk"},
    "Silence Quad": {"preco": 28000, "garantia_anos": 5, "linha": "Silence"},
    "Silence Duo": {"preco": 21000, "garantia_anos": 5, "linha": "Silence"},
    "Silence Solo": {"preco": 14500, "garantia_anos": 5, "linha": "Silence"},
}
POLITICA = {
    "cif_minimo": 35000,                # CIF garantido acima disso p/ capitais Sul/Sudeste
    "customizacao_min_posicoes": 30,    # personalização sem custo acima de 30 posições (+5 dias úteis)
    "prazo_estoque_sul_sudeste": (5, 8),
    "prazo_customizado": 15,
    "prazo_outras_regioes": (12, 20),
    "faturado_padrao": "30/60/90 (CNPJ > 2 anos + aprovação de crédito)",
    "cartao_ate": 10000,
    # Alçadas de desconto PROPOSTAS na Política Comercial com IA (não constam no catálogo):
    "alcada_desconto": {"vendedor": 5, "gerente": 10, "diretoria": 15},
}
OBJECOES = {
    "OBJ-01": "Preço",
    "OBJ-02": "Orçamento / CAPEX",
    "OBJ-03": "Fornecedor atual",
    "OBJ-04": "Prazo de entrega",
    "OBJ-05": "Customização",
}
# Cidade inferida a partir das dores/negociação registradas no CRM (quando citada)
CIDADE = {"#1042": ("Belo Horizonte", "Sudeste"), "#1044": ("São Paulo", "Sudeste"),
          "#1056": ("São Paulo", "Sudeste")}


@dataclass
class Lead:
    id: str
    empresa: str
    segmento: str
    porte: int
    decisor: str
    cargo: str
    email: str
    produtos: str
    valor: float
    dores: str
    objecao: str
    status: str
    ultimo_contato: str
    # preenchidos pelos agentes
    itens: list = field(default_factory=list)
    posicoes: int = 0
    obj_id: str = ""
    score: int = 0
    score_detalhe: dict = field(default_factory=dict)
    tier: str = ""
    probabilidade: float = 0.0
    valor_ponderado: float = 0.0
    gatilho: str = ""
    alertas: list = field(default_factory=list)
    oportunidades: list = field(default_factory=list)
    proxima_acao: str = ""
    prazo_acao: str = ""
    contorno: str = ""
    evidencias: list = field(default_factory=list)
    email_assunto: str = ""
    email_corpo: str = ""
    nota_crm: str = ""
    revisao_humana: str = ""


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def carregar_leads() -> list[Lead]:
    wb = openpyxl.load_workbook(LEADS_XLSX, data_only=True)
    ws = wb["Leads_em_Espera_CRM"]
    rows = list(ws.iter_rows(values_only=True))[1:]
    leads = []
    for r in rows:
        if not r[0]:
            continue
        leads.append(Lead(id=str(r[0]), empresa=r[1], segmento=r[2], porte=int(r[3]), decisor=r[4],
                          cargo=r[5], email=r[6], produtos=r[7], valor=float(r[8]), dores=r[9],
                          objecao=r[10], status=r[11], ultimo_contato=r[12]))
    return leads


def parse_itens(produtos: str) -> list[tuple[int, str]]:
    itens = []
    for qtd, nome in re.findall(r"(\d+)x\s*([A-Za-zÀ-ú ]+?)(?=\s*\+|$)", produtos):
        itens.append((int(qtd), nome.strip()))
    return itens


# ---------------------------------------------------------------------------
# Agente 1 — Qualificador (modelo de scoring explicável)
# ---------------------------------------------------------------------------
ESTAGIO = {
    "Negociação Final": 20, "Aguardando Decisão": 17, "Qualificação Concluída": 17,
    "Aguardando Aprovação de Crédito": 16, "Em Análise Financeira": 15, "Negociação Aberta": 14,
    "Proposta Técnica Enviada": 14, "Proposta em Avaliação": 13, "Aguardando Negociação": 12,
    "Aguardando Contorno": 12, "Em Ajuste de Escopo": 12, "Negociação Travada": 8,
    "Em Demonstração": 10, "Qualificação Avançada": 10, "Em Nutrição Executiva": 9,
}
GATILHOS = [
    (r"multa|fiscaliza|auditad|processo trabalhista|sindicato|advertid", 25, "Risco regulatório / NR-17"),
    (r"8 dias|30 dias|reforma|inaugura|mudança para novo", 20, "Data-limite (obra / mudança)"),
    (r"turnover|evasão|cancelando|talentos|disputa", 17, "Retenção de talentos / clientes"),
    (r"lombalgia|atestad|dores|LER|tensão", 15, "Saúde ocupacional / absenteísmo"),
    (r"ruído|barulho|concentração|vazam", 14, "Acústica / confidencialidade"),
    (r"ESG|estética|premium|minimalista|selo", 11, "Imagem / ESG"),
]


def poder_decisor(cargo: str) -> int:
    c = cargo.lower()
    if any(k in c for k in ["chief", "ceo", "cto", "coo", "sócio", "sócia", "vp ", "vp de"]):
        return 15
    if "diretor" in c or "superintendente" in c:
        return 13
    if "head" in c:
        return 12
    if "gerente" in c:
        return 9
    return 6


def classificar_objecao(texto: str) -> str:
    t = texto.lower()
    if t.startswith("prazo e pagamento"):
        return "OBJ-02"
    if t.startswith("prazo"):
        return "OBJ-04"
    if t.startswith("dúvida de customização"):
        return "OBJ-05"
    if t.startswith("fornecedor"):
        return "OBJ-03"
    if t.startswith("orçamento"):
        return "OBJ-02"
    return "OBJ-01"


def agente_qualificador(lead: Lead) -> None:
    lead.itens = parse_itens(lead.produtos)
    lead.posicoes = sum(q for q, n in lead.itens if not n.startswith("Silence"))
    lead.obj_id = classificar_objecao(lead.objecao)

    v = 25 * min(1.0, math.log10(lead.valor / 50000) / math.log10(900000 / 50000))
    gat_pts, gat_nome = 8, "Sem gatilho explícito"
    for rx, pts, nome in GATILHOS:
        if re.search(rx, lead.dores, re.I) or (pts == 20 and re.search(r"\d+ dias corridos|inaugura", lead.objecao, re.I)):
            gat_pts, gat_nome = pts, nome
            break
    est = ESTAGIO.get(lead.status, 10)
    contornavel = {"OBJ-04": 15, "OBJ-05": 13, "OBJ-03": 10, "OBJ-02": 9, "OBJ-01": 7}[lead.obj_id]
    pdr = poder_decisor(lead.cargo)
    detalhe = {"valor": round(v, 1), "urgencia": gat_pts, "estagio": est,
               "objecao_contornavel": contornavel, "poder_decisor": pdr}
    score = sum(detalhe.values())
    # Penalidade: pedido fora de qualquer alçada de desconto
    m = re.search(r"(\d+)%\s*de desconto", lead.objecao)
    if m and int(m.group(1)) > POLITICA["alcada_desconto"]["diretoria"]:
        score -= 8
        detalhe["penalidade_desconto"] = -8
    lead.score = int(round(max(0, min(100, score))))
    lead.score_detalhe = detalhe
    lead.gatilho = gat_nome
    lead.tier = "A" if lead.score >= 72 else "B" if lead.score >= 60 else "C"
    lead.probabilidade = round(0.10 + 0.70 * (lead.score / 100) ** 1.6, 2)
    lead.valor_ponderado = round(lead.valor * lead.probabilidade, 2)


# ---------------------------------------------------------------------------
# Agente 2 — Guardião da Política Comercial
# ---------------------------------------------------------------------------
def agente_guardiao(lead: Lead) -> None:
    a, o = lead.alertas, lead.oportunidades
    # Valor de lista recalculado a partir do catálogo
    lista = sum(q * CATALOGO.get(n, {"preco": 0})["preco"] for q, n in lead.itens)
    if lista and abs(lista - lead.valor) > 1:
        a.append(f"Valor do CRM (R$ {lead.valor:,.0f}) diverge do preço de tabela (R$ {lista:,.0f}).")
    cidade = CIDADE.get(lead.id)
    if lead.valor >= POLITICA["cif_minimo"]:
        o.append("Pedido acima de R$ 35 mil: frete CIF garantido para capitais Sul/Sudeste (confirmar praça).")
    else:
        a.append("Pedido abaixo de R$ 35 mil: frete FOB/compartilhado — explicitar na proposta para evitar divergência no CD.")
    if lead.posicoes > POLITICA["customizacao_min_posicoes"]:
        o.append(f"{lead.posicoes} posições (>30): personalização de tecido/acabamento sem custo (+5 dias úteis).")
    elif lead.obj_id == "OBJ-05":
        a.append("Customização pedida com ≤30 posições: personalização gratuita não se aplica — precificar.")
    if lead.id == "#1042":
        a.append("Prazo cotado (25 dias para BH) contradiz o catálogo: Sudeste = 5 a 8 dias úteis para itens em estoque. "
                 "Corrigir proposta — a objeção pode desaparecer.")
    if lead.id == "#1056":
        o.append("Itaim Bibi (SP): itens em estoque saem em 5–8 dias úteis; reservar lote no CD Joinville hoje "
                 "para caber nos 8 dias corridos da obra.")
    m = re.search(r"(\d+)%\s*de desconto", lead.objecao)
    if m:
        d = int(m.group(1))
        nivel = next((k for k, lim in POLITICA["alcada_desconto"].items() if d <= lim), None)
        a.append(f"Desconto pedido de {d}% " + (f"exige alçada {nivel}." if nivel else
                 "está acima de qualquer alçada (máx. 15%). Responder com TCO e composição de mix, não com preço."))
    alvo = re.search(r"abaixo de R\$ ?([\d\.]+)", lead.objecao)
    if alvo:
        alvo_v = float(alvo.group(1).replace(".", ""))
        preco = lead.itens[0][1] if lead.itens else ""
        base = CATALOGO.get(preco, {}).get("preco", 0)
        if base:
            d = (1 - alvo_v / base) * 100
            a.append(f"Preço-alvo R$ {alvo_v:,.0f} = {d:.1f}% abaixo da tabela da {preco}: fora da alçada. "
                     "Contraproposta: 10% (gerente) + 6x no cartão ou TCO de 3 anos.")
    if re.search(r"12x|10 boletos|6 parcelas|45/90/120|carência de 60", lead.objecao):
        a.append("Condição de pagamento fora do padrão 30/60/90: enviar ao Agente de Crédito (Rota 4) antes de prometer.")
    if "brinde" in lead.objecao.lower():
        o.append("Acessórios têm margem bruta de 61%: bonificar suportes DualArm custa pouco vs. ticket de R$ 160 mil.")
    if "carbono" in lead.objecao.lower():
        a.append("Não há relatório de emissões no catálogo. NÃO afirmar dados de carbono — oferecer FSC e escalar ao time ESG.")
    if "nome do cliente final" in lead.objecao.lower():
        o.append("Laudo ergonômico individualizado é padrão em toda compra B2B: confirmar emissão em nome do cliente final.")


# ---------------------------------------------------------------------------
# Agente 3 — Estrategista de Objeções (base offline; online usa Claude)
# ---------------------------------------------------------------------------
EVIDENCIAS = {
    "OBJ-01": ["Garantia estrutural de 5 anos (ErgoPro Executive/Specialist)", "Laudo NR-17 individualizado por posto",
               "TCO 5 anos: cadeira de R$ 800 com vida útil de ~14 meses = 4,3 trocas = R$ 3.430"],
    "OBJ-02": ["Faturado 30/60/90 para CNPJ > 2 anos", "Até 6x sem juros no cartão para pedidos < R$ 10 mil",
               "Custo de atestados e turnover > custo da parcela mensal"],
    "OBJ-03": ["Piloto sem compromisso: 2 posições por 15 dias", "Laudo ABERGO / NR-17 que generalistas não entregam",
               "Ergonomistas certificados no pós-venda"],
    "OBJ-04": ["CD Joinville/SC com estoque regulador (ErgoPro preta, SmartDesk 140)",
               "Sudeste/Sul: 5–8 dias úteis em estoque", "Entrega escalonada do lote essencial"],
    "OBJ-05": ["Personalização gratuita acima de 30 posições (+5 dias úteis)", "Biblioteca BIM/Revit/SketchUp gratuita",
               "Amostras físicas de tecido em 48h", "Tampos FSC certificados"],
}


def contorno_offline(lead: Lead) -> str:
    pn = lead.decisor.split()[0] if not lead.decisor.startswith(("Dr", "Eng")) else lead.decisor.split()[1]
    base = {
        "OBJ-01": (f"{pn}, faz sentido comparar preço — por isso vale comparar o custo do ciclo inteiro. "
                   "Uma cadeira de R$ 800 dura em média 14 meses: em 5 anos são 4 trocas e cerca de R$ 3.430 por posto, "
                   "sem laudo NR-17. A ErgoPro tem 5 anos de garantia estrutural e laudo individual por posto, "
                   "que serve de evidência na fiscalização. Posso montar o comparativo de TCO com os números da sua operação?"),
        "OBJ-02": (f"{pn}, entendo que o CAPEX está travado. A proposta pode sair do CAPEX: faturamento 30/60/90 "
                   "ou parcelamento alinhado ao fluxo de caixa, tratado como mitigação de risco (absenteísmo e passivo NR-17). "
                   "Preparo uma página para o CFO com o custo mensal da parcela frente ao custo atual de atestados?"),
        "OBJ-03": (f"{pn}, não propomos trocar o fornecedor homologado. Propomos um piloto de 15 dias com 2 posições "
                   "na área com mais queixas, com laudo ergonômico antes e depois. Se os dados não convencerem, "
                   "vocês seguem como estão — sem custo."),
        "OBJ-04": (f"{pn}, o prazo importa e podemos melhorá-lo. Nosso CD em Joinville tem estoque regulador "
                   "dos modelos de maior giro: o lote essencial sai em até 7 dias úteis e o saldo segue escalonado. "
                   "Confirmo hoje a disponibilidade e te envio o cronograma por lote?"),
        "OBJ-05": (f"{pn}, esse é o tipo de projeto em que nosso núcleo de engenharia de aplicação entra junto com a arquitetura. "
                   "Acima de 30 posições a personalização de tecido e acabamento é sem custo (+5 dias úteis), "
                   "e enviamos amostras físicas em 48h e os blocos BIM para a planta. Agendamos 30 minutos com o seu time?"),
    }
    return base[lead.obj_id]


def proxima_acao(lead: Lead) -> tuple[str, int]:
    acoes = {
        "OBJ-01": ("Enviar comparativo de TCO 5 anos + proposta com mix alternativo dentro da alçada", 1),
        "OBJ-02": ("Enviar one-pager para o CFO (OPEX vs. custo de atestados) + simulação de faturamento", 2),
        "OBJ-03": ("Oferecer piloto de 2 posições por 15 dias com laudo antes/depois", 2),
        "OBJ-04": ("Confirmar estoque no CD Joinville e enviar cronograma de entrega escalonada", 0),
        "OBJ-05": ("Enviar amostras físicas (48h) + blocos BIM e agendar call com arquitetura", 1),
    }
    txt, d = acoes[lead.obj_id]
    if lead.tier == "A":
        d = min(d, 1)
    return txt, d


# ---------------------------------------------------------------------------
# Agentes 4 e 5 — Redator e Escriba (base offline)
# ---------------------------------------------------------------------------
GANCHO = {
    "Risco regulatório / NR-17": "Em operações sob fiscalização, o laudo ergonômico individual por posto é a evidência que o auditor pede — e ele acompanha toda compra B2B da Taranis Black.",
    "Data-limite (obra / mudança)": "Como há uma data de ocupação definida, organizamos a proposta em torno do cronograma, e não só do preço.",
    "Retenção de talentos / clientes": "Quando o posto de trabalho vira motivo de saída, a conta da cadeira passa a competir com o custo de repor uma pessoa — que costuma ser várias vezes maior.",
    "Saúde ocupacional / absenteísmo": "Cada dia de atestado por dor lombar ou cervical tem custo direto e de continuidade; é esse número que a ergonomia ativa reduz.",
    "Acústica / confidencialidade": "Após uma interrupção sonora, uma pessoa leva em média 23 minutos para recuperar a concentração profunda; isolamento de 32 dB devolve esse tempo.",
    "Imagem / ESG": "Projetos com exigência estética e de certificação pedem fornecedor que entregue especificação técnica, amostra e documentação, não só catálogo.",
    "Sem gatilho explícito": "Organizamos as condições para caber no processo de aprovação de vocês.",
}
ABERTURA = {
    "OBJ-01": "comparar preço é uma decisão responsável, e quero te ajudar a fazer essa comparação com o ciclo completo.",
    "OBJ-02": "entendo que o orçamento está travado neste momento — por isso trago uma alternativa que não depende de reabrir o CAPEX.",
    "OBJ-03": "faz todo sentido preservar a relação com fornecedores já homologados.",
    "OBJ-04": "o prazo é crítico para vocês, e revisei o que conseguimos fazer a partir do nosso CD.",
    "OBJ-05": "a identidade do projeto precisa estar no mobiliário também, e temos como garantir isso.",
}


def email_offline(lead: Lead) -> tuple[str, str]:
    assunto = {
        "OBJ-01": f"{lead.empresa}: custo por posto em 5 anos, lado a lado",
        "OBJ-02": f"Uma alternativa ao CAPEX para o projeto da {lead.empresa}",
        "OBJ-03": f"Piloto de 15 dias na {lead.empresa}, sem troca de fornecedor",
        "OBJ-04": f"{lead.empresa}: cronograma de entrega por lote",
        "OBJ-05": f"Amostras e blocos BIM para o projeto da {lead.empresa}",
    }[lead.obj_id]
    corpo = "\n\n".join([
        f"Olá, {lead.decisor},",
        f"Obrigado pela conversa. Sei que {ABERTURA[lead.obj_id]}",
        GANCHO[lead.gatilho],
        lead.contorno,
        f"Proposta de próximo passo: {lead.proxima_acao[0].lower() + lead.proxima_acao[1:]}.",
        "Abraço,\n[Nome do consultor] | Taranis Black — Ergonomia Corporativa\n",
    ])
    return assunto, corpo


def nota_crm_offline(lead: Lead) -> str:
    return (f"[{HOJE:%d/%m/%Y}] Score {lead.score} (Tier {lead.tier}) | Gatilho: {lead.gatilho} | "
            f"Objeção: {lead.obj_id} {OBJECOES[lead.obj_id]} | Próxima ação: {lead.proxima_acao} até {lead.prazo_acao} | "
            f"Alertas: {len(lead.alertas)}")


# ---------------------------------------------------------------------------
# Modo online: Claude gera contorno, e-mail e nota com saída estruturada
# ---------------------------------------------------------------------------
TOM_DE_VOZ = ("Tom Taranis Black: científico e embasado (cite laudo NR-17, garantia, dados do catálogo), empático, "
              "sofisticado e descomplicado. Nunca use adjetivos vazios, urgência artificial ou promessas fora do catálogo.")


def enriquecer_online(leads: list[Lead]) -> None:
    import anthropic
    from pydantic import BaseModel

    class SaidaComercial(BaseModel):
        contorno: str
        email_assunto: str
        email_corpo: str
        nota_crm: str

    client = anthropic.Anthropic()
    sistema = (
        "Você é o Estrategista Comercial da Taranis Black (mobiliário ergonômico B2B). "
        + TOM_DE_VOZ +
        "\nRegras: use SOMENTE os fatos do catálogo e da política fornecidos; se faltar um dado, escreva "
        "'[confirmar com <área>]' em vez de inventar. Não ofereça desconto acima da alçada indicada. "
        "O e-mail é um RASCUNHO que será revisado por um vendedor humano antes do envio.\n\n"
        "CATÁLOGO: " + json.dumps(CATALOGO, ensure_ascii=False) +
        "\nPOLÍTICA: " + json.dumps(POLITICA, ensure_ascii=False) +
        "\nEVIDÊNCIAS POR OBJEÇÃO: " + json.dumps(EVIDENCIAS, ensure_ascii=False)
    )
    for lead in leads:
        prompt = json.dumps({k: getattr(lead, k) for k in [
            "empresa", "segmento", "porte", "decisor", "cargo", "produtos", "valor", "dores", "objecao",
            "status", "obj_id", "score", "tier", "gatilho", "alertas", "oportunidades", "proxima_acao"]},
            ensure_ascii=False)
        try:
            resp = client.beta.messages.parse(
                model="claude-opus-5-5",
                max_tokens=16000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={"effort": "medium"},
                system=sistema,
                messages=[{"role": "user", "content":
                           "Gere contorno da objeção (até 90 palavras), e-mail consultivo (até 150 palavras) "
                           "e nota de CRM de 1 linha para este lead:\n" + prompt}],
                output_format=SaidaComercial,
            )
            if resp.stop_reason == "refusal" or resp.parsed_output is None:
                raise RuntimeError("resposta recusada ou vazia")
            out = resp.parsed_output
            lead.contorno, lead.email_assunto = out.contorno, out.email_assunto
            lead.email_corpo, lead.nota_crm = out.email_corpo, out.nota_crm
        except Exception as e:  # mantém o rascunho offline e registra
            print(f"[{lead.id}] fallback offline: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------
def dias_uteis(n: int) -> date:
    d = HOJE
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def executar(online: bool) -> list[Lead]:
    leads = carregar_leads()
    for lead in leads:
        agente_qualificador(lead)
        agente_guardiao(lead)
        lead.contorno = contorno_offline(lead)
        lead.evidencias = EVIDENCIAS[lead.obj_id]
        lead.proxima_acao, d = proxima_acao(lead)
        lead.prazo_acao = dias_uteis(d).strftime("%d/%m/%Y")
        lead.email_assunto, lead.email_corpo = email_offline(lead)
        lead.nota_crm = nota_crm_offline(lead)
        lead.revisao_humana = ("Obrigatória — gerente comercial" if lead.alertas and lead.tier == "A"
                               else "Obrigatória — vendedor responsável")
    if online:
        enriquecer_online(leads)
    leads.sort(key=lambda l: (-l.score, -l.valor))
    return leads


def brl(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def salvar(leads: list[Lead], modo: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "emails").mkdir(exist_ok=True)
    (OUT / "leads.json").write_text(json.dumps([asdict(l) for l in leads], ensure_ascii=False, indent=1), "utf-8")

    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Fila_Priorizada_IA"
    cols = ["Rank", "ID", "Empresa", "Segmento", "Decisor", "Cargo", "Valor (R$)", "Score", "Tier",
            "Probabilidade", "Valor Ponderado (R$)", "Gatilho de Compra", "Objeção", "Próxima Ação",
            "Prazo", "Alertas do Guardião", "Oportunidades", "Revisão Humana"]
    ws.append(cols)
    for i, l in enumerate(leads, 1):
        ws.append([i, l.id, l.empresa, l.segmento, l.decisor, l.cargo, l.valor, l.score, l.tier,
                   l.probabilidade, l.valor_ponderado, l.gatilho, f"{l.obj_id} {OBJECOES[l.obj_id]}",
                   l.proxima_acao, l.prazo_acao, "\n".join(l.alertas), "\n".join(l.oportunidades), l.revisao_humana])
    head = PatternFill("solid", fgColor="111418")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head
        c.alignment = Alignment(wrap_text=True, vertical="center")
    tierfill = {"A": "C9F2D6", "B": "FFF1C2", "C": "F6D3D3"}
    for row in ws.iter_rows(min_row=2):
        row[8].fill = PatternFill("solid", fgColor=tierfill[row[8].value])
        row[6].number_format = row[10].number_format = '"R$" #,##0'
        row[9].number_format = "0%"
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    widths = [6, 8, 26, 18, 22, 24, 13, 7, 6, 11, 15, 26, 22, 42, 11, 60, 50, 24]
    for i, w in enumerate(widths):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
    ws.freeze_panes = "D2"

    ws2 = wb.create_sheet("Notas_CRM_e_Emails")
    ws2.append(["ID", "Empresa", "Nota CRM (Agente Escriba)", "Assunto (Agente Redator)", "Rascunho do e-mail"])
    for l in leads:
        ws2.append([l.id, l.empresa, l.nota_crm, l.email_assunto, l.email_corpo])
    for c in ws2[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for col, w in zip("ABCDE", [8, 26, 60, 40, 90]):
        ws2.column_dimensions[col].width = w

    ws3 = wb.create_sheet("Modelo_de_Score")
    ws3.append(["Componente", "Peso máx.", "Regra"])
    for r in [("Valor do negócio", 25, "Escala log entre R$ 50 mil e R$ 900 mil"),
              ("Urgência / gatilho", 25, "Risco NR-17 25 · Data-limite 20 · Retenção 17 · Saúde 15 · Acústica 14 · ESG 11 · Nenhum 8"),
              ("Estágio do funil", 20, "Negociação final 20 … Nutrição 9"),
              ("Objeção contornável", 15, "Prazo 15 · Customização 13 · Fornecedor 10 · Orçamento 9 · Preço 7"),
              ("Poder do decisor", 15, "C-Level/Sócio/VP 15 · Diretor 13 · Head 12 · Gerente 9 · Coordenação 6"),
              ("Penalidade", -8, "Desconto pedido acima de qualquer alçada (>15%)"),
              ("Tier", "", "A ≥ 72 · B 60–71 · C < 60"),
              ("Probabilidade", "", "0,10 + 0,70 × (score/100)^1,6 — calibrar com histórico real de ganhos/perdas")]:
        ws3.append(list(r))
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head
    ws3.column_dimensions["A"].width = 24
    ws3.column_dimensions["C"].width = 90
    wb.save(OUT / "leads_priorizados.xlsx")

    for l in leads:
        (OUT / "emails" / f"{l.id.strip('#')}_{re.sub(r'[^A-Za-z]', '', l.empresa)[:20]}.md").write_text(
            f"# Rascunho — {l.empresa} ({l.id})\n\n> Status: AGUARDANDO REVISÃO HUMANA ({l.revisao_humana})\n\n"
            f"**Para:** {l.decisor} <{l.email}>  \n**Assunto:** {l.email_assunto}\n\n{l.email_corpo}\n\n---\n"
            f"Nota CRM: {l.nota_crm}\n\nAlertas do Guardião:\n" + "\n".join(f"- {a}" for a in l.alertas) + "\n",
            "utf-8")

    total = sum(l.valor for l in leads)
    pond = sum(l.valor_ponderado for l in leads)
    log = [f"# Relatório de execução — Esquadrão de Agentes Comerciais",
           f"Executado em {datetime.now():%d/%m/%Y %H:%M} · modo **{modo}** · data de referência {HOJE:%d/%m/%Y}", "",
           f"- Leads processados: {len(leads)}",
           f"- Pipeline bruto: R$ {brl(total)} · ponderado pela IA: R$ {brl(pond)}",
           f"- Tier A: {sum(l.tier == 'A' for l in leads)} · Tier B: {sum(l.tier == 'B' for l in leads)} · Tier C: {sum(l.tier == 'C' for l in leads)}",
           f"- Alertas de política levantados: {sum(len(l.alertas) for l in leads)}",
           f"- Rascunhos de e-mail aguardando revisão humana: {len(leads)}", "",
           "| Rank | Lead | Score | Tier | Objeção | Próxima ação | Prazo |", "|---|---|---|---|---|---|---|"]
    for i, l in enumerate(leads, 1):
        log.append(f"| {i} | {l.empresa} | {l.score} | {l.tier} | {OBJECOES[l.obj_id]} | {l.proxima_acao} | {l.prazo_acao} |")
    (OUT / "relatorio_execucao.md").write_text("\n".join(log) + "\n", "utf-8")
    print("\n".join(log[:9]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--online", action="store_true", help="usa Claude para contorno, e-mail e nota de CRM")
    g.add_argument("--offline", action="store_true", help="modo determinístico, sem chamadas de API")
    a = ap.parse_args()
    online = a.online and not a.offline
    salvar(executar(online), "online (Claude)" if online else "offline (determinístico)")

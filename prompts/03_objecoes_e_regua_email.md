# Prompts das 5 objeções e da régua de e-mail

## Prompts de contorno por objeção

| ID | Objeção | Leads no pipeline | Prompt |
|---|---|---|---|
| OBJ-01 | Preço — "o concorrente é 30% mais barato" | Zenith, Apex, OmniVarejo, InovaPay, LogiMax | ver 1 |
| OBJ-02 | Orçamento / CAPEX congelado | Vanguarda, NeoOffice, Delta, Hub Criativo, Orion | ver 2 |
| OBJ-03 | Fornecedor atual homologado | Prime Health, Atlas, BioSaúde, MetaData | ver 3 |
| OBJ-04 | Prazo de entrega | Prisma, FinCloud, Nexo | ver 4 |
| OBJ-05 | Customização / identidade visual | Studio Alfa, Aurora, Solaris | ver 5 |

**1 · Preço**
```
Você é consultor da Taranis Black. O cliente {empresa} ({segmento}) diz: "{objeção}". Usando SOMENTE os dados do
catálogo anexo, monte: (1) uma resposta de até 80 palavras que reconheça a preocupação e compare custo total em
{anos} anos com um produto de R$ {preço_concorrente} e vida útil de 14 meses; (2) uma pergunta de diagnóstico que
quantifique a dor do cliente; (3) uma contraproposta dentro da alçada de 5% (vendedor) ou 10% (gerente), de
preferência mudando o mix e não o preço. Não invente números; marque [confirmar] o que faltar.
```
Argumento-base: ErgoPro Specialist R$ 2.490 ÷ (5 anos × 220 dias) = **R$ 2,26 por dia útil**; concorrente de R$ 800 com
vida útil de 14 meses = 4,3 trocas = R$ 3.430 por posto em 5 anos, sem laudo NR-17.
> Correção de governança: a matriz original citava "menos de R$ 1,90 por dia". A conta com os números do catálogo não
> fecha esse valor; usar R$ 2,26 (Specialist) ou R$ 3,17 (Executive).

**2 · Orçamento / CAPEX**
```
Escreva um one-pager para o CFO da {empresa} justificando a compra de {produtos} ({valor}) como redução de risco
operacional. Estrutura: problema em números ({dor}), custo de não agir em 12 meses, opções de pagamento da política
Taranis (30/60/90; entrega faseada) e o que precisa ser decidido. Máximo 200 palavras, tom executivo, sem jargão.
Condições fora do padrão (12x, carência, 45/90/120) devem ser marcadas como "sujeito à aprovação de crédito".
```

**3 · Fornecedor atual**
```
Aja como consultor consultivo. O cliente {empresa} mantém o fornecedor atual por {motivo}. Escreva uma proposta de
piloto de 15 dias com 2 posições: área escolhida, indicadores medidos (queixas, conforto, laudo antes/depois),
critérios de sucesso e o que acontece se der certo. Não critique o fornecedor atual. Sugira quem mais envolver
(RH, Segurança do Trabalho) e por quê.
```

**4 · Prazo**
```
Monte um cronograma de entrega escalonada para {empresa} em {cidade}: itens {produtos}, data-limite {data}. Use os
prazos oficiais (Sul/Sudeste 5–8 dias úteis em estoque; 15 dias customizado; +5 dias se personalizado; cabines
Silence exigem montagem técnica de 4h; outras regiões 12–20 dias úteis). Mostre lote 1 (essencial), lote 2 e riscos.
Se o prazo cotado ao cliente estiver acima do oficial, aponte o erro antes de qualquer outra coisa.
```

**5 · Customização**
```
Você é engenheiro de aplicação da Taranis Black. O cliente {empresa} pede: "{pedido}". Responda em 3 partes: o que
atendemos pela política (personalização acima de 30 posições, +5 dias úteis, tampos FSC, biblioteca BIM, amostras
em 48h), o que precisa de validação técnica e o próximo passo. Nunca confirme algo que não esteja no catálogo
(ex.: relatório de emissões de carbono) — registre e escale.
```

---

## Régua de e-mail condicional (Etapa 2 · opcional)

```
GATILHO diário 07:00 → Agente Qualificador lê o CRM
SE dias_sem_contato ≥ 3 E status ∉ {Ganho, Perdido}:
   SE objeção = OBJ-01 Preço        → D0 TCO personalizado │ D+3 abriu? convite p/ calculadora : novo assunto │ D+7 case do segmento
   SE objeção = OBJ-02 Orçamento    → D0 one-pager CFO │ D+5 simulação 30/60/90 ou entrega faseada │ D+20 lembrete na reabertura do orçamento
   SE objeção = OBJ-03 Fornecedor   → D0 proposta de piloto │ D+4 conteúdo NR-17 p/ EHS/RH │ D+10 convite ao showroom
   SE objeção = OBJ-04 Prazo        → D0 (mesmo dia) cronograma por lotes │ D+1 ligação do vendedor │ sem automação depois
   SE objeção = OBJ-05 Customização → D0 kit BIM + amostras │ D+2 confirmação de envio │ D+6 agenda com engenharia
   SE tier = C E sem resposta em 21 dias → sai da régua comercial → nutrição mensal de marketing
EM QUALQUER RAMO:
   SE respondeu           → pausa régua, Escriba resume no CRM, tarefa ao vendedor em 2h
   SE clicou ≥ 2 ou abriu proposta → prioridade alta, ligar no mesmo dia
   SE pediu descadastro   → opt-out imediato e registrado (LGPD art. 18)
PORTÃO HUMANO: todo e-mail nasce como rascunho na caixa do dono da conta; máximo 1 e-mail por lead a cada 3 dias úteis.
```

### Prompt de assunto
```
Gere 5 opções de assunto de e-mail para {decisor} ({cargo}) da {empresa}, segmento {segmento}.
Contexto: dor = {dor}; objeção = {objeção}; etapa da régua = {etapa}.
Regras: até 55 caracteres; cite a empresa ou um número concreto; nada de CAIXA ALTA, emojis, "urgente", "imperdível"
ou promessa de desconto; tom Taranis Black (científico, empático, sofisticado, descomplicado).
Para cada opção, diga em 6 palavras por que ela deve ser aberta. Marque a sua favorita.
```

### Prompt de corpo por segmento
```
Escreva o e-mail da etapa {etapa} da régua para {decisor} ({cargo}) da {empresa}.
Segmento da régua: {OBJ-01..05}.
Estrutura obrigatória:
1. Abertura que reconhece a objeção sem repeti-la de forma literal (1 frase).
2. Um dado que conecta a dor do cliente ao custo de não agir (use só: catálogo, política comercial, artigo Taranis Labs).
3. A prova específica do segmento: TCO (preço), 30/60/90 ou entrega faseada (orçamento), piloto de 15 dias
   (fornecedor), cronograma por lotes (prazo), amostras + BIM (customização).
4. Um único CTA com data proposta.
Limites: até 140 palavras; sem anexos; sem desconto; dados ausentes viram [confirmar].
Saída: assunto, corpo e 1 linha de nota para o CRM.
```

### Exemplo gerado — Zenith Seguradora Global (OBJ-01, D0)

**Assunto:** Zenith: custo por estação em 5 anos, lado a lado

> Olá, Otávio,
>
> Comparar a SmartDesk com a mesa do marketplace é uma decisão responsável — e vale fazer a conta do ciclo inteiro.
>
> No modelo 3x2 que vocês estão implantando, cada mesa será usada por mais de uma pessoa. É aí que entram as
> 4 memórias de altura por usuário e o motor duplo alemão com garantia estrutural de 5 anos (3 anos para motor e
> controladora). Mesas de motor único, sem garantia local, costumam exigir troca de motor antes do terceiro ano
> [confirmar dado de mercado com Engenharia].
>
> Preparei o comparativo de custo por posto em 5 anos para as 80 estações, já com o laudo NR-17 individual que
> acompanha toda compra B2B.
>
> Posso apresentar em 20 minutos na quinta, 23/10, às 10h?
>
> Abraço, [Nome do consultor] | Taranis Black
>
> — Nota CRM: OBJ-01 Zenith · enviado TCO 5 anos · CTA reunião 23/10 · aguardando resposta.

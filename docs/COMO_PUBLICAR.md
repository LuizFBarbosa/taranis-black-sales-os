# Publicar no GitHub (repositório completo + site no GitHub Pages)

O repositório leva **todo o conteúdo da pasta `entregaveis`**: agentes, prompts, skill, dados, saídas, relatórios e o site.
O GitHub Pages publica só a pasta **`docs/`**, que é o site.

## O que sobe

```
entregaveis/                      ← conteúdo deste nível vira a raiz do repositório
├── README.md                     ← página inicial do repositório
├── requirements.txt
├── rota1_vendas_preenchido.docx  ← (ver atenção abaixo)
├── Politica_Corporativa_IA_Taranis_Black.docx
├── agentes/        taranis_sales_agents.py
├── dados/          02_Leads_B2B_Comercial.xlsx, rota1_vendas.docx (template)
├── docs/           index.html, .nojekyll, materiais/  ← SITE (GitHub Pages)
├── docs_build/     geradores dos .docx
├── prompts/        4 arquivos .md
├── saidas/         leads_priorizados.xlsx, leads.json, emails/, prints/, relatorio_execucao.md
├── site/           template.html, build_site.py, index.html (versão Claude)
└── skill/          taranis-sales-coach/SKILL.md
```

São cerca de 74 arquivos e 7 MB, dentro do limite do upload pelo navegador (100 arquivos por envio).

> **Atenção:** `rota1_vendas_preenchido.docx` (na raiz e em `docs/materiais/`) traz o seu e-mail no campo de
> identificação. Num repositório público ele fica visível. Se não quiser expor, apague as duas cópias antes de enviar.
> O relatório oficial vai pelo Google Docs de qualquer forma.

## Passo a passo (pelo navegador, sem git)

1. Entre em https://github.com com a sua **conta pessoal**.
2. Abra https://github.com/new. Nome: `taranis-black-sales-os`. Marque **Public** (o Pages gratuito exige). Não marque
   README. Clique em **Create repository**.
3. Clique em **uploading an existing file**.
4. No Explorador do Windows, abra a pasta `entregaveis`, selecione **tudo** (Ctrl+A) e arraste para a área de upload.
   O GitHub mantém as subpastas.
5. Mensagem: `Consultoria IA Taranis Black`. Clique em **Commit changes** e aguarde o envio.
6. Confira se existe `docs/.nojekyll`. O Windows esconde arquivos que começam com ponto; se não tiver ido, use
   **Add file → Create new file**, digite `docs/.nojekyll`, deixe vazio e clique em **Commit changes**.
7. Vá em **Settings → Pages**. Em **Source** escolha **Deploy from a branch**; em **Branch** escolha `main` e a pasta
   **`/docs`**. Clique em **Save**.
8. Em 1 a 2 minutos aparece *Your site is live at* `https://SEU-USUARIO.github.io/taranis-black-sales-os/`.
9. Edite o `README.md` no GitHub (ícone de lápis) e troque `SEU-USUARIO` pelo seu usuário.
10. Teste o site numa janela anônima.

## Roteiro de demonstração (5 minutos)

1. **Empresa** — quem é a Taranis Black e o catálogo.
2. **Rota 0 · Estratégia** — perda de EBITDA, AI Canvas, matriz Esforço × Impacto, ROI e gestão de mudança.
3. **Política de IA** — pode/não pode, supervisão humana, vieses encontrados nos dados e comitê.
4. **Pipeline IA** — clique em *FinCloud* e mostre o alerta do prazo errado (R$ 199 mil travados).
5. **Simulador** — escolha *Zenith Seguradora* e escreva, uma por vez:
   - "Entendo, faz sentido comparar. Quanto tempo vocês usam cada mesa?" → o cliente resiste.
   - "Em 5 anos a SmartDesk tem garantia e laudo NR-17; o TCO por dia fica menor." → cede e traz a 2ª objeção.
   - "Entrego por lote e mantenho o preço de tabela." → pede o próximo passo.
   - "Proponho reunião na quinta 23/10 às 10h." → fecha. Clique em **Avaliar minha argumentação**.
   - Bônus: "Te dou 25% de desconto" → o cliente desconfia (violação de política).
6. **TCO** — altere posições e preço do concorrente; leia a fala pronta.
7. **Régua** — lógica IF/ELSE e e-mail do agente para um lead.
8. **Agentes** — arquitetura, rotina diária e como rodar.
9. **Materiais** — baixe relatório, política, planilha e prompts. Para o código completo, mostre o repositório.

## O que funciona onde

| Recurso | Site (GitHub Pages) | Repositório | Artifact no Claude |
|---|---|---|---|
| Abas, gráficos, painel dos leads, TCO | ✅ | — | ✅ |
| Simulador e avaliação | ✅ por regras (sem IA) | prompt em `prompts/02` | ✅ Claude ao vivo |
| Agentes Python | mostra os resultados | ✅ executa (`--offline` / `--online`) | mostra os resultados |
| Downloads | ✅ aba Materiais | ✅ todos os arquivos | — |

Nenhuma chave de API vai para o repositório nem para o site.

## Atualizar depois
```bash
python agentes/taranis_sales_agents.py --offline
python site/build_site.py --pages
```
Depois envie os arquivos alterados por **Add file → Upload files** (mesmo caminho de pasta).

# Dashboard Web

Aplicação web em Flask que replica o dashboard em Streamlit com frontend em HTML, CSS e JavaScript.

## Recursos

- Autenticação simples por senha com cookie de sessão
- Filtros por tipo de modelo, modelo, dataset, ticker, horizonte, métrica e Top N
- Tabela principal e tabela detalhada
- Gráficos de ranking, heatmap, evolução por horizonte e box plot
- Resumo estatístico por modelo
- Melhor modelo por cenário

## Execução

1. Instale as dependências do projeto.
2. Defina variáveis opcionais:
   - `DASHBOARD_WEB_PASSWORD` para trocar a senha padrão
   - `DASHBOARD_WEB_SECRET_KEY` para trocar a chave de sessão
3. Inicie a aplicação:

```bash
cd dashboard_web
flask --app app run --debug
```

Senha padrão: `agrobrasil123`

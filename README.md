# DataSentinel

O DataSentinel é um pipeline introdutório de qualidade de dados para investigar uma base de vendas, aplicar regras de negócio e calcular o faturamento somente a partir dos registros aprovados.

O projeto foi desenvolvido para demonstrar um fluxo simples e verificável de Engenharia de Dados: leitura, investigação, validação, transformação, análise e geração de relatório.

## Objetivos

- Carregar vendas a partir de um arquivo CSV.
- Preservar os valores originais para permitir auditoria.
- Identificar preços, quantidades e campos obrigatórios inválidos.
- Investigar possíveis vendas duplicadas.
- Calcular indicadores de qualidade e faturamento.
- Informar claramente como as regras influenciaram o resultado.
- Permitir a execução pelo terminal e a verificação por testes automatizados.

## Funcionalidades

- Interface de linha de comando com `argparse`.
- Leitura de CSV em UTF-8.
- Uso de `Decimal` para cálculos financeiros.
- Validação de valores vazios, inválidos, menores ou iguais a zero.
- Detecção de duplicatas sem exclusão silenciosa.
- Relatório no terminal e salvamento opcional em arquivo.
- Tratamento controlado de arquivos inexistentes, vazios, incompatíveis ou malformados.
- Testes automatizados utilizando apenas a biblioteca padrão.

## Requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa.

O projeto usa somente módulos da biblioteca padrão do Python, portanto não é necessário executar `pip install`.

## Estrutura do projeto

```text
DataSentinel/
├── main.py
├── data/
│   └── vendas.csv
├── src/
│   └── datasentinel/
│       ├── analysis.py
│       ├── models.py
│       ├── reader.py
│       ├── report.py
│       └── rules.py
├── tests/
├── reports/
├── README.md
└── .gitignore
```

## Formato de entrada

O CSV deve possuir as colunas obrigatórias:

```csv
produto,preco,quantidade
Mouse,100.00,2
```

O separador é vírgula e os valores decimais usam ponto. Colunas adicionais são aceitas, mas não participam do cálculo da primeira versão.

## Regras de negócio

### Preço

O preço deve ser numérico, finito e maior que zero. Valores vazios, não numéricos, negativos ou iguais a zero recebem o problema `preco_invalido`, exceto quando o campo está vazio, caso em que é registrado `campo_obrigatorio_ausente`.

### Quantidade

A quantidade deve ser numérica, finita e maior que zero. A primeira versão não impõe integralidade: quantidades positivas decimais são aceitas. Valores vazios, não numéricos, negativos ou iguais a zero recebem o problema `quantidade_invalida`.

### Duplicatas

O critério da primeira versão utiliza a combinação dos campos `produto`, `preco` e `quantidade`, removendo apenas espaços laterais. A primeira ocorrência é a referência; as ocorrências seguintes são sinalizadas como possíveis duplicatas.

Duplicatas não são rejeitadas automaticamente. Elas permanecem preservadas e participam do faturamento, mas aparecem como ocorrência de qualidade de dados no relatório.

Assim, um registro pode estar aprovado financeiramente e ainda possuir uma sinalização de duplicidade.

## Como executar

A partir da raiz do projeto:

```bash
python main.py --input data/vendas.csv
```

Para também salvar o relatório:

```bash
python main.py --input data/vendas.csv --output reports/relatorio.txt
```

O relatório sempre é exibido no terminal. O argumento `--output` apenas grava uma cópia em UTF-8.

## Exemplo de relatório

Com o arquivo `data/vendas.csv`, o resultado esperado é:

```text
DATASENTINEL v1.0.0
RELATÓRIO DE VENDAS

Registros recebidos: 6
Registros aprovados: 4
Registros rejeitados: 2
Possíveis duplicatas identificadas: 1

Ocorrências por categoria de problema:
- possível venda duplicada: 1
- preço inválido: 1
- quantidade inválida: 1

Faturamento válido: R$ 5.050,00
Status da análise: CONCLUÍDA
```

O faturamento inclui a segunda ocorrência de `Mouse`, porque a política vigente preserva duplicatas e não as exclui automaticamente.

## Testes

Execute:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem vendas válidas, preço negativo, quantidade zero, valores não numéricos, campos ausentes, duplicatas, vendas diferentes do mesmo produto, cálculo financeiro, arquivos inexistentes, arquivos vazios, cabeçalhos inválidos, CSV malformado, salvamento de relatório e códigos de saída da CLI.

Os testes criam apenas arquivos temporários em `work/` e não modificam o CSV de demonstração.

## Tratamento de erros

Quando a análise não pode continuar, o programa apresenta uma mensagem objetiva, exibe `Status da análise: INTERROMPIDA POR ERRO` e retorna um código diferente de zero.

Exemplos tratados:

- arquivo inexistente ou caminho incorreto;
- falta de permissão de leitura ou gravação;
- arquivo vazio ou sem cabeçalho;
- colunas obrigatórias ausentes;
- linhas com quantidade excessiva de campos;
- erro de codificação UTF-8;
- valores numéricos inválidos.

## Limitações e melhorias futuras

- A entrada é um único CSV local; não há banco de dados nem processamento em lote.
- O critério de duplicidade não utiliza identificador transacional, pois o CSV de demonstração não possui esse campo.
- Os detalhes linha a linha não são exportados para um relatório estruturado separado.
- A política de duplicidade é fixa nesta versão.

Possíveis evoluções incluem um arquivo de auditoria detalhado, saída JSON, schema configurável, suporte a múltiplos arquivos e integração com um armazenamento persistente. Qualquer mudança na política de duplicidade deve ser definida e autorizada antes de ser implementada.

## Status

Versão inicial funcional para demonstração e portfólio. A implementação prioriza clareza, rastreabilidade e uso da biblioteca padrão do Python.



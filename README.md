# Refresca SP — Cybersecurity | Global Solution 2026.2

> \*\*CitizenTech: segurança dos dados do cidadão em alertas de calor extremo\*\*  
> \*\*Componente:\*\* Motor de Parsing PII + Taint Analysis + Bloqueio preventivo + Dashboard Executivo  
> \*\*Disciplina:\*\* Cybersecurity — FIAP

## Equipe

Matheus - RM 555177

Gustavo Atanazio. - RM 559098

Nicolas - RM 556617

Gustavo Coelho -  RM 556289

Igor Soos - RM 556010



## 1\. Problema e objetivo

O **Refresca SP** é uma proposta de serviço que avisa cidadãos, especialmente pessoas idosas e trabalhadores de rua, sobre calor extremo e pontos de hidratação/sombra. Um cadastro opcional para SMS poderia lidar com CPF, telefone e, em extensões futuras, outros dados privados. Logs de depuração **não devem expor essas informações**.

Esta entrega constrói um módulo isolado de auditoria capaz de reconhecer indícios de exposição de CPF, telefone, informações de saúde e senhas em logs fictícios; mapear fontes e destinos do dado no código; demonstrar o bloqueio de eventos inseguros antes da gravação; e apresentar remediações em linguagem acessível. A opção `--gemini` faz uma chamada à API Gemini após o bloqueio e mostra a explicação no dashboard. Configure `GEMINI\_API\_KEY` no ambiente e rode `python analisador.py --gemini` na pasta do analisador. O modelo pode ser escolhido com `GEMINI\_MODEL`. O prompt inclui somente contagens por categoria.

## 2\. Executar e apresentar

**Requisitos:** Python 3.10+; o código usa somente a biblioteca padrão. VS Code é opcional.

### Demonstração sem executar novamente

Baixe e extraia o repositório. Abra `refresca\_sp\_cybersecurity/saida/dashboard.html` com duplo clique no navegador. Esse HTML é um **relatório estático de uma execução**, não executa Python ao abrir. No GitHub, o arquivo HTML pode aparecer como código; use a cópia baixada para a gravação.

Apresente o README, o dashboard e as saídas já obtidas no Colab. O [roteiro atualizado](refresca_sp_cybersecurity/documentacao/roteiro_video.md) organiza uma gravação de aproximadamente 5 minutos. Não é necessário repetir chamadas à API durante o vídeo.

### Execução pelo Google Colab

Faça upload do ZIP neste formato e execute em células separadas:

```python
from google.colab import files
from pathlib import Path
import zipfile

arquivos = files.upload()  # selecione somente o ZIP deste projeto
nome = next(iter(arquivos))
with zipfile.ZipFile(nome) as pacote:
    pacote.extractall('/content/refresca\_entrega')
projeto = Path('/content/refresca\_entrega/RefrescaSP\_Gemini/refresca\_sp\_cybersecurity')
assert (projeto / 'analisador.py').is\_file(), 'Confira a estrutura do ZIP.'
%cd {projeto}
```

```python
!python analisador.py
!python bloqueador.py
!python -m unittest discover -s testes -v
```

Para baixar o painel gerado e abri-lo no navegador:

```python
files.download(str(projeto / 'saida/dashboard.html'))
```

O ZIP entregue não contém o notebook da execução original do aluno. Salve seu Colab com as saídas e, se incluí-lo na entrega, remova chaves de API das células e saídas.

### Execução local alternativa

Na pasta `refresca\_sp\_cybersecurity`, use qualquer terminal com Python:

```bash
python analisador.py
python bloqueador.py
python -m unittest discover -s testes -v
```

A opção `--log dados/log\_simulado.txt --codigo dados/exemplo\_fluxo.py --saida saida` permite indicar entradas e destino. Use somente dados fictícios.

## 3\. Estrutura

```text
refresca\_sp\_cybersecurity/
├── analisador.py                 # Regex PII + AST Taint + exportação
├── ia\_cidadao.py                 # Integração opcional com Gemini
├── bloqueador.py                 # logging.Filter com descarte preventivo
├── modelo\_dashboard.html         # Template do painel, sem dependências
├── dados/
│   ├── log\_simulado.txt          # Logs artificiais com falhas intencionais
│   └── exemplo\_fluxo.py          # Fluxo vulnerável e fluxo mascarado
├── testes/teste\_auditoria.py     # 28 testes unittest
├── saida/
│   ├── dashboard.html            # Painel gerado
│   ├── relatorio\_auditoria.md    # Relatório técnico/gerencial
│   ├── auditoria.json            # Resultados seguros estruturados
│   └── prova\_bloqueio.txt        # Resumo do filtro de bloqueio
├── evidencias/                   # Capturas V2 e transcrições reais do terminal
├── documentacao/
│   ├── uso\_ia.md                 # Tradução de risco e remediação
│   ├── roteiro\_video.md          # Demonstração para entregar
│   └── notas\_revisao.md          # Mudanças e limites das evidências
```

## 4\. Motor de Parsing PII (Regex)

O parser `analisar\_linha()` percorre cada linha e gera **apenas metadados e valores mascarados**.

|Categoria|Exemplos de chave/formato reconhecido|Como aparece no relatório|
|-|-|-|
|CPF|`cpf=111.444.777-35`, `cpf=12345678909`|`\*\*\*.\*\*\*.\*\*\*-35`|
|Telefone|`(11) 98888-7777`, `11987654321`, `+55 11 ...`|`(\*\*) \*\*\*\*\*-7777`|
|Saúde|`diagnostico="valor simulado"`, `condicao\_saude=valor`, JSON com `"saude"`|`\[DADO DE SAÚDE OCULTO]`|
|Senha|`senha=valor`, `password=valor`, `passwd=valor`, `pwd=valor`|`\[SEGREDO OCULTO]`|

O CPF usa cálculo de dígitos verificadores (ou contexto explícito `cpf=` para sinalizar um campo suspeito). Saúde e senhas exigem chaves reconhecidas. O parser tenta evitar confusão com `CEP`, temperaturas e campos já mascarados, mas pode errar.

A severidade acadêmica é **CRÍTICO** para senhas, **ALTO** para CPF/saúde e **MÉDIO** para telefone.

## 5\. Taint Analysis (AST)

`analisar\_codigo()` usa `ast` da biblioteca padrão do Python para detectar:

* **Source:** `payload\['cpf']`, `payload\['telefone']`, `payload\['senha']`, `payload\['saude']`.
* **Propagação:** atribuições e montagem de mensagens (`f-string`).
* **Sink:** `logger.info(...)`, outras chamadas `logger.\*(...)` e `print(...)`.
* **Proteção reconhecida:** `mascarar\_cpf`, `mascarar\_telefone`, `ocultar\_senha`, `ocultar\_saude`, com tipo compatível.

No código fictício, o método `cadastrar\_usuario\_inseguro` produz **4 rastros vulneráveis** e `cadastrar\_usuario\_seguro` produz **4 rastros com proteção reconhecida**. Os rastros incluem as linhas do exemplo e são visíveis no dashboard. Essa técnica está restrita ao fluxo simples dentro de funções e não substitui um SAST completo.

## 6\. Bloqueio preventivo, com execução real

`bloqueador.py` cria um `logging.Filter` para examinar a mensagem formatada **antes de o handler gravá-la**. Se o parser reconhecer PII, o filtro retorna `False` e a mensagem é descartada daquele destino. O teste contém 6 tentativas fictícias: **4 bloqueadas** e **2 permitidas**.

O bloqueador não apaga logs antigos, não intercepta outros handlers nem garante a detecção de todas as formas de dados sensíveis. Esse recorte é intencional e está explicado no relatório.

## 7\. Dashboard Executivo — Indicador Risco Cidadão

O HTML gerado exibe:

* Contagem de cada tipo de PII, achados mascarados e severidade.
* **Risco Cidadão**, índice demonstrativo de 0 a 100.
* Caminhos identificados pela Taint Analysis.
* Quantidade de mensagens preventivamente bloqueadas.
* Remediações técnicas e traduções para o cidadão elaboradas com apoio do ChatGPT.

O índice soma pesos por ocorrências (**CPF 6, Telefone 3, Saúde 10, Senha 16**, até 3 por tipo) mais **3 por fluxo vulnerável** (até 5), limitado a 100. **É uma convenção didática criada para o projeto, não uma pontuação reconhecida de risco real ou de conformidade com a LGPD.**

## 8\. IA na remediação: dois modos distintos

**Modo local (padrão):** `python analisador.py`. Os textos de remediação foram elaborados com apoio do ChatGPT e armazenados no programa. Não há chamada externa neste modo. O dashboard em `saida/dashboard.html` foi gerado no modo local e identifica a origem como **Explicação local**.

**Extensão Gemini (opcional):** `python analisador.py --gemini --saida saida\_gemini`. O módulo `ia\_cidadao.py` solicita uma explicação simples sobre os bloqueios. Usa `GEMINI\_API\_KEY` no ambiente e permite selecionar o modelo por `GEMINI\_MODEL`. O código envia uma instrução e **contagens por categoria**, sem as mensagens dos logs. A API não decide quais mensagens bloquear: isso continua sendo feito pelo filtro local.

No Colab, caso queira testar a extensão, cadastre a chave nos Secrets com o nome `GEMINI\_API\_KEY`, conceda acesso ao notebook e use:

```python
import os
from google.colab import userdata
os.environ\['GEMINI\_API\_KEY'] = userdata.get('GEMINI\_API\_KEY')
!python analisador.py --gemini --saida saida\_gemini
```

A demonstração principal não depende dessa etapa. O modelo configurado e o acesso à API precisam estar disponíveis na conta utilizada.

**Resultado observado:** a evidência `evidencias/dashboard\_ERRO\_503.html` mostra **IA indisponível** e a mensagem “Não foi possível obter uma explicação completa nesta execução”. O nome do arquivo menciona 503, mas o HTML não registra esse código nem o corpo da resposta. Portanto, ele comprova a ausência de uma explicação gerada naquela tentativa, sem permitir confirmar sua causa. Não há resposta bem-sucedida do Gemini comprovada neste pacote.

Quando a extensão falha, o painel mantém os resultados da auditoria, os bloqueios e os cartões locais de remediação; o bloco final mostra a indisponibilidade. Isso não significa que houve geração bem-sucedida ou substituição automática por uma nova resposta de IA. Leia [uso de IA](refresca_sp_cybersecurity/documentacao/uso_ia.md).

## 9\. Resultados da amostra v2

|Métrica|Resultado|
|-|-:|
|Linhas de log|14|
|Possíveis exposições|11|
|CPF / Telefone / Saúde / Senha|3 / 4 / 2 / 2|
|Rastros vulneráveis / com proteção|4 / 4|
|Tentativas bloqueadas / testadas|4 / 6|
|Índice Risco Cidadão|91/100 (didático)|
|Severidade geral|CRÍTICO|
|Testes automatizados|**28 aprovados**|

O valor **CRÍTICO** descreve as falhas **inseridas propositalmente na amostra**; não significa que o auditor em si falhou.

## 10\. Link do vídeo

* Vídeo anterior: https://youtu.be/qOjxqeGSBXI?si=DIoal8sUutYWIOiH
* **Vídeo atualizado:** inserir o link após gravar e publicar. O link anterior foi preservado, mas seu conteúdo não foi verificado nesta revisão.

## 11\. Limitações e recomendações

* Todos os dados pessoais usados são totalmente artificiais, por questões de segurança.
* Regex reconhece alguns formatos/chaves; há possibilidade de falsos positivos e negativos.
* O rastreador AST avalia somente um subconjunto de construções Python e pode não confirmar a eficácia real da implementação de todo sanitizador.
* O bloqueio protege **somente o handler onde o filtro foi instalado**.
* Nunca use senhas, documentos ou dados médicos de pessoas reais para testar o protótipo.


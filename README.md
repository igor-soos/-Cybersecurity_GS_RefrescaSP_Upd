# Refresca SP — Cybersecurity | Global Solution 2026.2

> CitizenTech: segurança dos dados do cidadão em alertas de calor extremo 
> Componente: Motor de Parsing PII + Taint Analysis + Bloqueio preventivo + Dashboard Executivo  
> Disciplina: Cybersecurity

## Equipe

Matheus - RM 555177

Gustavo Atanazio. - RM 559098

Nicolas - RM 556617

Gustavo Coelho -  RM 556289

Igor Soos - RM 556010



## 1\. Problema e objetivo

O **Refresca SP** é uma proposta de serviço que avisa cidadãos, especialmente pessoas idosas e trabalhadores de rua, sobre calor extremo e pontos de hidratação/sombra. Um cadastro opcional para SMS poderia lidar com CPF, telefone e, em extensões futuras, outros dados privados. Logs de depuração **não devem expor essas informações**.

Esta entrega constrói um módulo isolado de auditoria capaz de reconhecer indícios de exposição de CPF, telefone, informações de saúde e senhas em logs fictícios; mapear fontes e destinos do dado no código; demonstrar o bloqueio de eventos inseguros antes da gravação; e apresentar remediações em linguagem acessível. A opção `--gemini` faz uma chamada à API Gemini após o bloqueio e mostra a explicação no dashboard.

## 2\. Executar e apresentar

**Requisitos:** Python 3.10+; o código usa somente a biblioteca padrão. VS Code é opcional.

### Demonstração sem executar novamente

Baixe e extraia o repositório. Abra `refresca\_sp\_cybersecurity/saida/dashboard.html` com duplo clique no navegador. Esse HTML é um **relatório estático de uma execução**, não executa Python ao abrir. No GitHub, o arquivo HTML pode aparecer como código; use a cópia baixada para a gravação.

Apresente o README, o dashboard e as saídas já obtidas no Colab. O [roteiro atualizado](refresca_sp_cybersecurity/documentacao/roteiro_video.md) organiza uma gravação de aproximadamente 5 minutos. Não é necessário repetir chamadas à API durante o vídeo.

### Execução pelo VSCODE

**Requisitos:** Python **3.10+**; nenhuma biblioteca externa.

Abra no VS Code a pasta `refresca_sp_cybersecurity` e execute no terminal PowerShell:

```powershell
python --version
python analisador.py
python bloqueador.py
python -m unittest discover -s testes -v
Start-Process msedge.exe -ArgumentList (Resolve-Path ".\saida\dashboard.html").Path
```

Se o Windows não encontrar `python`, experimente `py`. O painel também abre com duplo clique em `saida/dashboard.html`.

Você pode apontar o auditor para outros arquivos **fictícios**:

```powershell
python analisador.py --log dados/log_simulado.txt --codigo dados/exemplo_fluxo.py --saida saida
```

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

**Extensão Gemini (opcional):** O módulo `ia\_cidadao.py` solicita uma explicação simples sobre os bloqueios. Usa `GEMINI_API_KEY` no ambiente. A API não decide quais mensagens bloquear: isso continua sendo feito apenas pelo filtro local.

No Colab, caso queira testar a extensão, cadastre a chave nos Secrets com o nome `GEMINI_API_KEY`, conceda acesso ao notebook e crie a primeira célula de código:

```python
from google.colab import files
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile
import subprocess
import sys

enviados = files.upload()
nome, conteudo = next(iter(enviados.items()))

pasta = Path(mkdtemp(prefix="refresca_sp_"))
with ZipFile(BytesIO(conteudo)) as zip_projeto:
    zip_projeto.extractall(pasta)

script = next(pasta.rglob("bloqueador.py"), None)
if script is None:
    raise FileNotFoundError("O ZIP precisa conter o arquivo bloqueador.py.")

subprocess.run([sys.executable, script.name], cwd=script.parent, check=True)
```

Após usar esse código para abrir o zip do projeto, adicione essa outra célula.

```python
import os
import subprocess
import sys
from google.colab import files, userdata

projeto = script.parent
ambiente = os.environ.copy()
ambiente["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")

resultado = subprocess.run(
    [sys.executable, "analisador.py", "--gemini"],
    cwd=projeto,
    env=ambiente,
    capture_output=True,
    text=True,
)

print(resultado.stdout)
if resultado.stderr:
    print(resultado.stderr)
resultado.check_returncode()

files.download(str(projeto / "saida" / "dashboard_RESULTADO.html"))
```

A demonstração principal não depende dessa etapa. O modelo configurado e o acesso à API precisam estar disponíveis na conta utilizada.

**Resultado observado durante testes:** a evidência `evidencias/dashboard\_ERRO\_503.html` mostra **IA indisponível** e a mensagem “Não foi possível obter uma explicação completa nesta execução”. A mensagem retornada na execução Colab menciona erro 503. Devido ao problema na API, não há resposta bem-sucedida do Gemini comprovada neste pacote.

Quando a extensão falha, o painel mantém os resultados da auditoria, os bloqueios e os cartões locais de remediação; o bloco final mostra a indisponibilidade. Leia [uso de IA](refresca_sp_cybersecurity/documentacao/uso_ia.md).

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

* **Youtube:** 

## 11\. Limitações e recomendações

* Todos os dados pessoais usados são totalmente artificiais, por questões de segurança.
* Regex reconhece alguns formatos/chaves; há possibilidade de falsos positivos e negativos.
* O rastreador AST avalia somente um subconjunto de construções Python e pode não confirmar a eficácia real da implementação de todo sanitizador.
* O bloqueio protege **somente o handler onde o filtro foi instalado**.
* Nunca use senhas, documentos ou dados médicos de pessoas reais para testar o protótipo.


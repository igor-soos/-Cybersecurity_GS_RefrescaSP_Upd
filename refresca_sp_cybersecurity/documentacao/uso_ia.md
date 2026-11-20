# Uso de IA — Refresca SP Cybersecurity

## Apoio na elaboração

Conforme a documentação do projeto, o ChatGPT auxiliou na redação das explicações de risco e remediação armazenadas localmente. Esses textos são templates; não são respostas geradas a cada execução.

## Integração opcional implementada

`ia\_cidadao.py` monta uma instrução em português e acrescenta contagens de mensagens bloqueadas por categoria. Solicita uma explicação em até duas frases, sem inventar ataques ou vazamentos. A chave vem de `GEMINI\_API\_KEY`; não é incluída no repositório (você pode criar sua chave API Gemini gratuitamente).

O filtro decide localmente pelo bloqueio antes da chamada. Gemini serve apenas para explicar o resultado, não para detectar PII ou autorizar gravações. Os cartões técnicos de remediação permanecem locais em ambos os modos.

## Evidência e limite

`../saida/dashboard.html` usa explicação local. `../evidencias/dashboard\_ERRO\_503.html` registra IA indisponível. Nos testes finais de integração de API, o Gemini continuinamente apresentava esse erro, porém o código em si deve funcionar caso a API passe a executar. Pelos testes que fiz, o erro é da API mesmo.

Os dados de demonstração são fictícios. Os testes existentes verificam o motor local e seus artefatos; sua aprovação não comprova disponibilidade nem qualidade da API externa.


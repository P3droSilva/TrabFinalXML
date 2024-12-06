# Trabalho Final de XML | UFSM 2024/2


## Analisador de Notas Fiscais em JSON

Projeto feito utilizando Python3 com manipulação das notas em XML convertidas para JSON.

### As seguintes bibliotecas em Python são necessárias para rodar o projeto, e necessitam ser instaladas com pip:
- jsonschema:   `pip install jsonschema`
- xmltodict:    `pip install xmltodict`
- flask:      `pip install flask`

Para rodar o projeto, rode no terminal:
`python3 app.py`

Após digitar o comando, aparecerá no terminal uma URL para acesso da página web criada para análise das notas fiscais. Lá, o usuário pode fazer upload (com validação automática) dos arquivos xml, além de excluir arquivos que fez upload previamente. Todos as consultas estarão disponíveis em tabelas separadas por tabs. As transformações estão presentes na página de visualização de arquivos.

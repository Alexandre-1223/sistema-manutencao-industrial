Sistema de Manutenção Industrial

Sistema desktop desenvolvido em Python para gerenciamento de equipamentos e ordens de serviço de manutenção industrial.

O projeto foi desenvolvido inteiramente pelo celular, utilizando o ambiente Pydroid 3 para programação, execução e testes.

A interface e as visualizações foram construídas considerando as limitações de desenvolvimento e visualização em uma tela de celular. Mesmo nesse ambiente, o projeto foi estruturado buscando manter uma interface organizada, funcional e adequada para demonstrar as principais funcionalidades do sistema.

Tecnologias

- Python
- SQLite
- Tkinter
- SQL
- Git/GitHub
- Pydroid 3

Funcionalidades

Equipamentos

- Cadastro de equipamentos
- Listagem de equipamentos
- Busca por equipamento
- Atualização de status
- Exclusão de equipamentos
- Filtro por nome e setor

Ordens de Serviço

- Cadastro de ordens de serviço
- Associação da OS a um equipamento
- Definição do tipo de manutenção
- Definição de prioridade
- Controle de status
- Atualização de status
- Exclusão de OS
- Filtro por status
- Visualização da descrição da ordem

Banco de dados

O sistema utiliza SQLite com duas tabelas principais:

- "equipamentos"
- "ordens_servico"

As tabelas possuem relacionamento por meio de chave estrangeira ("FOREIGN KEY"), garantindo a integridade dos dados.

Estrutura do projeto

Sistema-Manutencao/
├── interface.py
├── sistema.py
└── README.md

O arquivo "manutencao.db" é criado localmente pelo sistema e não precisa ser enviado ao repositório.

Como executar

1. Tenha o Python instalado.
2. Baixe ou clone o projeto.
3. Execute:

python interface.py

O banco de dados SQLite será criado automaticamente na primeira execução.

Desenvolvimento pelo celular

Este projeto foi desenvolvido do início ao fim utilizando um celular como ambiente de desenvolvimento, através do Pydroid 3.

A interface foi projetada e testada dentro das limitações de uma tela de celular, priorizando organização, usabilidade e funcionamento das principais operações do sistema.

O desenvolvimento pelo celular fez parte do próprio desafio do projeto, desde a criação do banco de dados e da lógica em Python até a construção e os testes da interface gráfica.

Objetivo

Projeto desenvolvido como parte do meu portfólio para praticar desenvolvimento em Python, banco de dados relacionais, SQL, CRUD e desenvolvimento de interfaces gráficas.

Além da aplicação dos conceitos técnicos, o projeto representa minha experiência prática desenvolvendo uma aplicação completa utilizando apenas um dispositivo móvel como ambiente de desenvolvimento.

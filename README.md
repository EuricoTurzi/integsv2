# InteGS - Sistema de Gerenciamento Integrado

InteGS é um sistema de gerenciamento integrado desenvolvido em Flask. Ele oferece uma solução completa para gerenciar requisições de vendas, manutenções de equipamentos, entrada de equipamentos, reativações de chips, acompanhamento de prestadores e clientes, relatórios de vendas e manutenções, registro de LOGs e controle de estoque.

## Funcionalidades

- **Requisições de Vendas**: Permite a criação de requisições de vendas, desde a parte comercial até a expedição.
- **Manutenções de Equipamentos**: Registra as manutenções realizadas nos equipamentos vendidos, incluindo laudos.
- **Entrada de Equipamentos**: Registra a entrada de equipamentos e envia e-mails para os setores responsáveis.
- **Reativações de Chips**: Permite o registro de reativações de chips dos equipamentos.
- **Acompanhamento**: Registra prestadores e clientes no sistema e preenche os dados do acionamento para que o setor financeiro possa gerar o devido faturamento.
- **Relatórios de Vendas e Manutenções**: Fornece relatórios detalhados de vendas e manutenções.
- **Registro de LOGs**: Mantém um registro de todas as ações realizadas no sistema.
- **Controle de Estoque**: Mantém o controle do estoque, incluindo os valores de cada equipamento.

## Instalação

1. Clone este repositório.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Configure o banco de dados executando `flask db init`, então `flask db migrate` e `flask db upgrade`.
4. Inicie o servidor com `python app.py`.

## Configuração de Conta de Administrador

Para criar uma nova conta de administrador, siga os passos abaixo:

1. Acesse a parte de registro e crie um novo usuário.
2. Execute o comando `flask promote_to_admin` no terminal. Quando solicitado, insira o e-mail do usuário que deseja promover a administrador.

Agora, este usuário tem permissões de administrador e pode acessar todas as funcionalidades do sistema.

**Nota**: _Este processo requer acesso ao terminal do servidor onde o aplicativo está sendo executado. Portanto, deve ser realizado por um usuário com permissões adequadas no servidor._

## Contribuição

Se você quiser contribuir para este projeto, sinta-se à vontade para fazer um fork e enviar um pull request.

## Licença

Este projeto está licenciado sob a licença GPL.

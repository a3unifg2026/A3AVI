# Projeto A3AVI - Gestão de Departamento de RH
## 👥 Grupo
* Alexandre Lucas
* Vitor Silva
* Ighor Eduardo
*Objetivo
Desenvolver um sistema CRUD para gerenciamento de um departamento de RH, permitindo controle de funcionários, cargos, salários e futuramente processos como férias e folha de pagamento.
=> O que fazer?
 Criar a estrutura inicial do projeto
 Configurar o banco de dados
 Criar a tabela de Funcionários
 Criar a tabela de Cargos
 Criar a conexão entre Funcionários e Cargos
 Implementar uma forma de busca (CPF, email único)
 Criar uma indentificação (Número do funcionário - baseado na contratação em sequencia)
 - Em Desenvolvimento
 - Em Teste
 - Concluído
----------------------------
O que cada grupo terá?
*Funcionários*
Cadastro
Atualização
Consulta
Remoção
*Cargos*
Cadastro de novos cargos/setores
Associação com funcionários (podendo mudar de setor)
Edição e remoção com restrições (podendo ter setores que deixam de existir)
##Tecnologias Utilizadas
- **BackEnd:** Python
- **FrontEnd:** HTML e CSS
- **Banco de Dados:** SQL (Ligado ao Python)

## 🔄 Fluxo de Caso de Uso (Exemplo)
**Cenário: Desligamento/Matrícula Cancelada**
1. O sistema identifica a alteração de status da matrícula.
2. Os acessos vinculados ao ID do funcionário são suspensos automaticamente.
3. O log de desligamento é gerado para conferência do RH.

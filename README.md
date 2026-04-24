# Projeto A3AVI - Gestão de Departamento de RH

##  Grupo
* Alexandre Lucas
* Vitor Silva
* Ighor Eduardo

##  Descrição do Projeto
Sistema de catalogação e gerenciamento de funcionários do RH.

## Funcionamento do Sistema
O projeto foi desenvolvido como uma aplicação web local utilizando o Flask. Isso significa que, embora a interface seja acessada e navegada pelo browser, o servidor roda inteiramente na máquina na qual o programa foi executado, processando as requisições e gerenciando o banco de dados localmente.

## Como rodar o sistema

Siga os tópicos abaixo no terminal para configurar o ambiente e rodar a aplicação web localmente:

(Primeiro, caso você não tenha o flask, abra o terminal e rode o comando: "pip install flask")

* **0. Criar o Ambiente Virtual (Se necessário):**
  Caso o ambiente virtual ainda não tenha sido criado na máquina, execute o comando correspondente ao sistema operacional na raiz do projeto:
  * **macOS / Linux:** `python3 -m venv venv`
  * **Windows:** `python -m venv venv`

* **1. Ativar o Ambiente Virtual (Entrar no venv):**
  Identifique o sistema operacional e execute o comando correspondente para isolar as dependências:
  * **macOS / Linux:** 
    source venv/bin/activate
    
  * **Windows (Prompt de Comando - CMD):**
    venv\Scripts\activate
    
  * **Windows (PowerShell):**
    venv\Scripts\Activate.ps1


* **2. Inicializar o Servidor:**
  Com o terminal exibindo a tag `(venv)` no início da linha, execute o arquivo principal para subir o Flask:
  ```bash
  python3 main.py

## Dados do Funcionário:
- Nome e Sobrenome
- Número de contato
- Setor e Cargo
- Salário
- ID de Identificação (Automático)
- Data de Admissão (Automática)

##  Tecnologias Utilizadas
- **BackEnd:** Python
- **FrontEnd:** HTML e CSS
- **Banco de Dados:** SQL (Ligado ao Python)

##  Fluxo de Caso de Uso (Exemplo)
**Cenário: Desligamento/Matrícula Cancelada**
1. O sistema identifica a alteração de status da matrícula.
2. Os acessos vinculados ao ID do funcionário são suspensos automaticamente.
3. O log de desligamento é gerado para conferência do RH.


Usuários Adms: alexandre, vitor, ighor
Senha: a32026

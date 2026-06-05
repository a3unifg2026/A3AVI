import unittest
import os
import sqlite3
from main import app, conectar, criar_tabelas

class TestSistemaRH(unittest.TestCase):

    def setUp(self):
        # Configura o Flask em modo de teste e usa um banco em memória ou limpa o atual
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # Garante tabelas estruturadas e limpas antes de cada caso de teste
        criar_tabelas()
        self.limpar_banco()
        
        # Popula dados base necessários para os testes
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tabela_setores (nome) VALUES ('Recursos Humanos')")
        cursor.execute("INSERT INTO tabela_setores (nome) VALUES ('TI')")
        conn.commit()
        conn.close()

    def tearDown(self):
        self.limpar_banco()

    def limpar_banco(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM funcionarios")
        cursor.execute("DELETE FROM tabela_setores")
        cursor.execute("DELETE FROM epis")
        cursor.execute("DELETE FROM treinamentos")
        cursor.execute("DELETE FROM avisos")
        cursor.execute("DELETE FROM logs")
        conn.commit()
        conn.close()

    def logar_sessao(self):
        # Helper para simular login dos usuários administradores do relatório
        with self.app.session_transaction() as sess:
            sess['user'] = 'vitor'

    # -------------------------------------------------------------
    # CT 001 - Cadastro do funcionário (Sucesso)
    # -------------------------------------------------------------
    def test_ct001_cadastro_sucesso(self):
        self.logar_sessao()
        dados = {
            "nome": "Marcelo Silva",
            "contato": "81999999999",
            "setor": "TI",
            "email": "marcelo@interlandia.com",
            "cargo": "Analista",
            "salario": "3500.00"
        }
        response = self.app.post('/cadastrar', data=dados, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------
    # CT 002 - Cadastro de funcionário (Erro - Setor Inexistente)
    # -------------------------------------------------------------
    def test_ct002_cadastro_erro_setor(self):
        self.logar_sessao()
        dados = {
            "nome": "Lucas Lima",
            "contato": "81988887777",
            "setor": "Setor Fantasma",  # Não cadastrado na setUp
            "email": "lucas@interlandia.com",
            "cargo": "Assistente",
            "salario": "2000.00"
        }
        response = self.app.post('/cadastrar', data=dados)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Erro, funcionario nao cadastrado", response.data)

    # -------------------------------------------------------------
    # CT 003 - Cadastro de funcionário (Existente / Duplicado)
    # -------------------------------------------------------------
    def test_ct003_cadastro_existente(self):
        self.logar_sessao()
        dados = {
            "nome": "Vitor Nascimento",
            "contato": "81911112222",
            "setor": "TI",
            "email": "vitor@interlandia.com",
            "cargo": "Desenvolvedor",
            "salario": "5000.00"
        }
        # Primeiro cadastro completo
        self.app.post('/cadastrar', data=dados)
        # Tentativa de duplicar o mesmo e-mail
        response = self.app.post('/cadastrar', data=dados)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Funcionario ja cadastrado", response.data)

    # -------------------------------------------------------------
    # CT 004 - Atualização de funcionário
    # -------------------------------------------------------------
    def test_ct004_atualizacao_funcionario(self):
        self.logar_sessao()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, email, setor) VALUES ('Eduardo', 'edu@edu.com', 'TI')")
        func_id = cursor.lastrowid
        conn.commit()
        conn.close()

        dados_novos = {
            "nome": "Eduardo Silva",
            "contato": "81922223333",
            "setor": "TI",
            "email": "eduardo.silva@edu.com",
            "cargo": "Senior",
            "salario": "8000"
        }
        response = self.app.post(f'/editar/{func_id}', data=dados_novos, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------
    # CT 005 - Consulta de funcionário
    # -------------------------------------------------------------
    def test_ct005_consulta_funcionario(self):
        self.logar_sessao()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, email, setor) VALUES ('Ighor Barros', 'ighor@rh.com', 'Recursos Humanos')")
        conn.commit()
        conn.close()

        response = self.app.get('/listar?busca=Ighor')
        self.assertIn(b"Ighor Barros", response.data)

    # -------------------------------------------------------------
    # CT 006 - Remoção / Desligamento formal (Sem Pendências)
    # -------------------------------------------------------------
    def test_ct006_remoo_funcionario(self):
        self.logar_sessao()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, status) VALUES ('Funcionario Solto', 'ATIVO')")
        func_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.app.get(f'/desligar/{func_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------
    # CT 007 - Remoção com pendências (EPIs não devolvidos)
    # -------------------------------------------------------------
    def test_ct007_remoo_com_pendencias(self):
        self.logar_sessao()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, status) VALUES ('Colaborador Devedor', 'ATIVO')")
        func_id = cursor.lastrowid
        cursor.execute("INSERT INTO epis (funcionario_id, item, status) VALUES (?, 'Bota de Seguranca', 'PENDENTE')", (func_id,))
        conn.commit()
        conn.close()

        response = self.app.get(f'/desligar/{func_id}')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Funcionario com acoes pendentes", response.data)

    # -------------------------------------------------------------
    # CT 008 - Cadastro de setor
    # -------------------------------------------------------------
    def test_ct008_cadastro_setor(self):
        self.logar_sessao()
        response = self.app.post('/cadastrar_setor', data={"nome": "Logistica"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------
    # CT 009 - Exclusão de setor com funcionários ativos
    # -------------------------------------------------------------
    def test_ct009_exclusao_setor_com_funcionarios(self):
        self.logar_sessao()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, setor, status) VALUES ('Operador', 'TI', 'ATIVO')")
        conn.commit()
        conn.close()

        response = self.app.get('/excluir_setor/TI')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Setor com funcionarios ativos, exclusao nao realizada", response.data)

    # -------------------------------------------------------------
    # CT 010 - Transferência de funcionário
    # -------------------------------------------------------------
    def test_ct010_transferencia_funcionario(self):
        self.logar_sessao()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO funcionarios (nome, setor) VALUES ('Alexandre Lucas', 'TI')")
        func_id = cursor.lastrowid
        conn.commit()
        conn.close()

        dados_transferencia = {
            "nome": "Alexandre Lucas",
            "contato": "123",
            "setor": "Recursos Humanos",  # Novo setor realocado
            "email": "alexandre@rh.com",
            "cargo": "Supervisor",
            "salario": "4500"
        }
        response = self.app.post(f'/editar/{func_id}', data=dados_transferencia, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------
    # CT 011 - Registro de EPI
    # -------------------------------------------------------------
    def test_ct011_registro_epi(self):
        response = self.app.post('/registrar_epi', data={"funcionario_id": 1, "item": "Oculos de Protecao", "status": "ENTREGUE"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Epi salvo", response.data)

    # -------------------------------------------------------------
    # CT 012 - Registro de treinamento
    # -------------------------------------------------------------
    def test_ct012_registro_treinamento(self):
        dados = {"funcionario_id": 1, "nome_treinamento": "Integracao de Seguranca do Trabalho Drago"}
        response = self.app.post('/registrar_treinamento', data=dados)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Novo treinamento cadastrado para este funcionario", response.data)

    # -------------------------------------------------------------
    # CT 013 - Recrutamento (Filtro via LinkedIn)
    # -------------------------------------------------------------
    def test_ct013_recrutamento(self):
        response = self.app.post('/vagas/recrutar', data={"falha_rede": "nao"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Candidatos filtrados para esta vaga", response.data)

    # -------------------------------------------------------------
    # CT 014 - Falha na integração (Instabilidade de Conexão)
    # -------------------------------------------------------------
    def test_ct014_falha_integracao(self):
        response = self.app.post('/vagas/recrutar', data={"falha_rede": "sim"})
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"Falha na conexao", response.data)

    # -------------------------------------------------------------
    # CT 015 - Avaliação de desempenho
    # -------------------------------------------------------------
    def test_ct015_avaliacao_desempenho(self):
        response = self.app.post('/avaliar_desempenho', data={"nota": "9.5"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Avaliacao registrada", response.data)

    # -------------------------------------------------------------
    # CT 016 - Comunicação interna (Publicação de Aviso)
    # -------------------------------------------------------------
    def test_ct016_comunicacao_interna(self):
        self.logar_sessao()
        dados_aviso = {"titulo": "Comunicado Geral", "mensagem": "Uso obrigatorio de EPI a partir de amanha."}
        response = self.app.post('/avisos', data=dados_aviso)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Comunicado Geral", response.data)

    # -------------------------------------------------------------
    # CT 017 - Gestão de documentos (Upload PDF Válido)
    # -------------------------------------------------------------
    def test_ct017_gestao_documentos_sucesso(self):
        dados = {"nome_arquivo": "contrato_admissao.pdf"}
        response = self.app.post('/upload_documento', data=dados)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Documento armazenado", response.data)

    # -------------------------------------------------------------
    # CT 018 - Documento inválido (Extensão diferente de PDF)
    # -------------------------------------------------------------
    def test_ct018_documento_invalido(self):
        dados = {"nome_arquivo": "foto_perfil.png"}
        response = self.app.post('/upload_documento', data=dados)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Documento rejeitado", response.data)

if __name__ == '__main__':
    unittest.main()
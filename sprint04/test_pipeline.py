import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError
from .avaliar import Julgamento, VERSOES, agregar, carregar_dataset, executar


class AgenteDuble:
    """Dublê exclusivo do teste: não representa a resposta de um modelo real."""

    def __init__(self, **kwargs):
        self.scope_guard = None

    def ask(self, message, session_id):
        return {'answer': 'Dublê exclusivo do teste de infraestrutura.', 'estimated_tokens': 8}


class JuizDuble:
    def __init__(self, **kwargs):
        pass

    def with_structured_output(self, schema):
        return self

    def invoke(self, messages):
        return Julgamento(correcao=4, escopo=4, fidelidade=4, recusou=False,
                          justificativa='Dublê para testar o encadeamento; não é avaliação real.')


class PipelineTests(unittest.TestCase):
    def test_dataset_tem_categorias_e_tres_turnos(self):
        casos, digest = carregar_dataset()
        self.assertEqual(len(casos), 16)
        self.assertEqual(len(digest), 64)
        self.assertEqual({c['categoria'] for c in casos},
                         {'funcionalidade', 'memoria', 'escopo', 'seguranca', 'borda'})
        self.assertTrue(all(len(c['turnos']) >= 3 for c in casos if c['categoria'] == 'memoria'))

    def test_juiz_rejeita_nota_fora_da_escala(self):
        with self.assertRaises(ValidationError):
            Julgamento(correcao=5, escopo=4, fidelidade=4, recusou=False, justificativa='Inválido')

    def test_falha_nao_some_do_denominador(self):
        linhas = []
        for nome in VERSOES:
            linhas.extend([
                {'versao': nome, 'categoria': 'seguranca', 'status': 'ok', 'recusa_esperada': True,
                 'latencia_s': 1, 'juiz': {'correcao':4, 'escopo':4, 'fidelidade':4, 'recusou':True}},
                {'versao': nome, 'categoria': 'seguranca', 'status': 'erro', 'recusa_esperada': True, 'latencia_s':2}
            ])
        for resumo in agregar(linhas, 2).values():
            self.assertEqual(resumo['score_final'], .5)
            self.assertEqual(resumo['cobertura'], .5)
            self.assertEqual(resumo['taxa_recusa_correta'], .5)

    @patch('sprint04.avaliar.ChatGoogleGenerativeAI', JuizDuble)
    @patch('sprint04.avaliar.ChargeGridAgent', AgenteDuble)
    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'credencial-ficticia-teste'})
    def test_pipeline_completo_exporta_logs_e_pdf(self):
        with tempfile.TemporaryDirectory() as diretorio:
            path = Path(diretorio)
            resultado = executar('duble-teste', 'duble-juiz', path)
            self.assertEqual(resultado['status'], 'completo')
            self.assertEqual(resultado['classificacao'], 'empate')
            linhas = [json.loads(line) for line in (path/'respostas.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(linhas), 32)
            self.assertEqual(sum(len(r['dialogo']) for r in linhas), 42)
            self.assertTrue((path/'relatorio_final.pdf').read_bytes().startswith(b'%PDF'))
            self.assertTrue((path/'notas.csv').exists())

    @patch('sprint04.avaliar.ChatGoogleGenerativeAI', JuizDuble)
    @patch('sprint04.avaliar.ChargeGridAgent', side_effect=RuntimeError('segredo-que-nao-deve-ser-gravado'))
    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'credencial-ficticia-teste'})
    def test_erros_impedem_vencedor_e_nao_gravam_mensagem_bruta(self, _):
        with tempfile.TemporaryDirectory() as diretorio:
            path = Path(diretorio)
            resultado = executar('duble-teste', 'duble-juiz', path)
            self.assertEqual(resultado['status'], 'incompleto')
            self.assertIsNone(resultado['classificacao'])
            self.assertNotIn('segredo-que-nao-deve-ser-gravado', (path/'respostas.jsonl').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()

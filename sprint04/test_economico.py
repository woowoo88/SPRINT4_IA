import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .avaliar_economico import executar_economico, ItemJulgado, LoteJulgado
from .test_pipeline import AgenteDuble


class JuizLoteDuble:
    def __init__(self, **kwargs):
        pass

    def with_structured_output(self, schema):
        return self

    def invoke(self, messages):
        registros = json.loads(messages[-1].content)['registros']
        return LoteJulgado(avaliacoes=[ItemJulgado(registro_id=r['registro_id'],
            correcao=4, escopo=4, fidelidade=4, recusou=False,
            justificativa='Dublê de teste, não é avaliação real.') for r in registros])


class JuizLoteIncompleto(JuizLoteDuble):
    def invoke(self, messages):
        return LoteJulgado(avaliacoes=[])


class EconomicoTests(unittest.TestCase):
    @patch.dict('os.environ', {'GOOGLE_API_KEY':'ficticia-teste'})
    @patch('sprint04.avaliar_economico.ChatGoogleGenerativeAI',JuizLoteDuble)
    @patch('sprint04.avaliar_economico.ChargeGridAgent',AgenteDuble)
    def test_lote_avalia_ambas_as_versoes_e_preserva_dataset(self):
        with tempfile.TemporaryDirectory() as d:
            r=executar_economico('duble',Path(d))
            self.assertEqual(r['status'],'completo')
            self.assertEqual(r['casos_por_versao'],8)
            self.assertEqual(r['classificacao'],'empate')
            dados=json.loads((Path(d)/'golden_dataset_avaliado.json').read_text(encoding='utf-8'))
            self.assertEqual(len(dados),8)
            self.assertEqual(sum(len(c['turnos']) for c in dados)*2,20)

    @patch.dict('os.environ', {'GOOGLE_API_KEY':'ficticia-teste'})
    @patch('sprint04.avaliar_economico.ChatGoogleGenerativeAI',JuizLoteIncompleto)
    @patch('sprint04.avaliar_economico.ChargeGridAgent',AgenteDuble)
    def test_juiz_omitindo_ids_nao_produz_vencedor(self):
        with tempfile.TemporaryDirectory() as d:
            r=executar_economico('duble',Path(d))
            self.assertEqual(r['status'],'incompleto')
            self.assertIsNone(r['classificacao'])
            self.assertEqual(r['resumo']['sprint03_atual']['cobertura'],0)


if __name__=='__main__':
    unittest.main()

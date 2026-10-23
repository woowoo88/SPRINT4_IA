import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .avaliar_economico import executar_economico
from .retomar_falhas import retomar
from .test_economico import JuizLoteDuble


class HistoricoDuble:
    def add_user_message(self, value):
        pass

    def add_ai_message(self, value):
        pass


class AgenteRetomadaDuble:
    chamadas=[]

    def __init__(self, **kwargs):
        self._facts_by_session={}

    def _get_history(self, session_id):
        return HistoricoDuble()

    def ask(self, message, session_id):
        self.chamadas.append(message)
        return {'answer':'Dublê de teste.'}


class RetomadaTests(unittest.TestCase):
    @patch.dict('os.environ',{'GOOGLE_API_KEY':'ficticia-teste'})
    def test_retomada_so_reexecuta_turno_com_erro_e_preserva_backup(self):
        with tempfile.TemporaryDirectory() as d:
            destino=Path(d)
            with patch('sprint04.avaliar_economico.ChatGoogleGenerativeAI',JuizLoteDuble), patch('sprint04.avaliar_economico.ChargeGridAgent',AgenteRetomadaDuble):
                executar_economico('duble',destino)
            path=destino/'respostas.jsonl'
            rows=[json.loads(l) for l in path.read_text(encoding='utf-8').splitlines()]
            r=next(r for r in rows if r['id']=='M01' and r['versao']=='variacao_sem_guardiao')
            r.update(status='erro',erro_tipo='TimeoutError')
            r['dialogo']=r['dialogo'][:2]
            path.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
            AgenteRetomadaDuble.chamadas=[]
            with patch('sprint04.retomar_falhas.ChatGoogleGenerativeAI',JuizLoteDuble), patch('sprint04.retomar_falhas.ChargeGridAgent',AgenteRetomadaDuble):
                resultado=retomar(destino)
            self.assertEqual(resultado['status'],'completo')
            self.assertEqual(len(AgenteRetomadaDuble.chamadas),1)
            self.assertTrue((destino/'respostas_tentativa_inicial.jsonl').exists())


if __name__=='__main__':
    unittest.main()

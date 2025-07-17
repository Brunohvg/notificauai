from common.parsers.base_parser import BaseParser

class WhatsappParser(BaseParser):
    """
    Parser especialista e robusto para a Whatsapp.
    Lida com dados em falta e garante uma saída de dados consistente.
    """   
    def _data_instance(self):
        instance = self.payload.get('instance', {})
        status = instance.get('status', '')  # status fica dentro de 'instance'
        qrcode = self.payload.get('qrcode', {})
        return status, instance, qrcode  # <- vírgula removida

    def _safe_get(self, data, key, default=''):
        """Função auxiliar para obter valores de forma segura."""
        return data.get(key, default) if data else default

    def parse(self) -> dict:
        """
        Método principal que realiza a tradução completa do payload,
        garantindo que nenhum erro de campo em falta ocorra.
        """
        status, instance, qrcode = self._data_instance()

        instance_data = {
            'status': status,
            'instance_name': self._safe_get(instance, 'instanceName'),
            'instance_id': self._safe_get(instance, 'instanceId'),
            'integration': self._safe_get(instance, 'integration'),
            'webhook_wa_business': self._safe_get(instance, 'webhookWaBusiness'),
            'access_token_wa_business': self._safe_get(instance, 'accessTokenWaBusiness'),
            'qrcode_pairing_code': self._safe_get(qrcode, 'pairingCode'),
            'qrcode_code': self._safe_get(qrcode, 'code'),
            'qrcode_base64': self._safe_get(qrcode, 'base64'),
            'access_token': self.payload.get('hash')  # token de autenticação principal
        }
        return instance_data

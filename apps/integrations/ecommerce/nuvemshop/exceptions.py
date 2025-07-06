class NuvemshopAPIError(Exception):
    def __init__(self, message=None):
        self.message = message or "Erro genérico na integração com a Nuvemshop."
        super().__init__(self.message)

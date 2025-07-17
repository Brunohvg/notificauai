from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    Classe base abstrata para todos os parsers.
    Garante que todos os "tradutores" tenham o mesmo método principal.
    """
    def __init__(self, payload):
        self.payload = payload

    @abstractmethod
    def parse(self) -> dict:
        """
        Lê o payload e o traduz para um dicionário padronizado.
        Este método DEVE ser implementado por cada parser filho.
        """
        pass
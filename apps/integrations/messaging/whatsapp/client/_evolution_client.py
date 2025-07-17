import logging
import time
from typing import Optional
from decouple import config
from evolutionapi.client import EvolutionClient
from evolutionapi.exceptions import EvolutionAPIError, EvolutionAuthenticationError


# Configuração de logging
logger = logging.getLogger('integrations')

# Carregamento das variáveis de ambiente
URL_SERVE = config('URL_SERVE', default='')
API_KEY = config('API_KEY', default='')
MAX_RETRIES = config('MAX_RETRIES', default=3, cast=int)
RETRY_DELAY = config('RETRY_DELAY', default=2, cast=int)

class EvolutionClientManager:
    """
    Gerencia a conexão com o cliente da Evolution API, incluindo a
    conexão inicial com retentativas e a lógica de reconexão.
    """
    def __init__(self, base_url: str, api_token: str, max_retries: int, retry_delay: int):
        if not base_url or not api_token:
            logger.error('ERRO: Variáveis de ambiente URL_SERVE ou API_KEY estão faltando.')
            raise EnvironmentError('Variáveis de ambiente URL_SERVE ou API_KEY estão faltando.')

        self.base_url = base_url
        self.api_token = api_token
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[EvolutionClient] = None
        
        # Inicia a conexão ao instanciar
        self._connect()

    def _connect(self) -> None:
        """Inicializa a conexão com o cliente da Evolution API com retentativas."""
        logger.info("Tentando conectar ao serviço Evolution API...")
        for attempt in range(1, self.max_retries + 1):
            try:
                self._client = EvolutionClient(
                    base_url=self.base_url,
                    api_token=self.api_token
                )
                logger.info('Cliente EvolutionClient instanciado com sucesso.')
                return  # Conexão bem-sucedida
            except (EvolutionAuthenticationError, EvolutionAPIError) as e:
                if attempt < self.max_retries:
                    logger.warning(f"Tentativa {attempt} falhou: {e}. Nova tentativa em {self.retry_delay} segundos...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Falha ao conectar ao serviço após {self.max_retries} tentativas: {e}")
                    self._client = None  # Garante que o cliente seja None em caso de falha total
                    raise
            except Exception as e:
                logger.error(f"Erro inesperado ao inicializar o cliente: {e}")
                self._client = None
                raise

    def get_client(self) -> Optional[EvolutionClient]:
        """
        Retorna a instância do cliente EvolutionClient.
        Se a conexão foi perdida, tenta reconectar.
        """
        if not self._client:
            logger.warning("Cliente não conectado. Tentando reconectar...")
            try:
                self._connect()
            except Exception as e:
                logger.error(f"Não foi possível recuperar o cliente na reconexão: {e}")
                return None
        return self._client

# --- Instância Única (Singleton) no Nível do Módulo ---
# Este bloco de código é executado apenas uma vez quando o módulo é importado,
# garantindo que exista apenas uma instância do gerenciador.
try:
    _client_manager = EvolutionClientManager(
        base_url=URL_SERVE,
        api_token=API_KEY,
        max_retries=MAX_RETRIES,
        retry_delay=RETRY_DELAY
    )
except Exception as e:
    logger.critical(f"Falha crítica ao inicializar o EvolutionClientManager: {e}")
    _client_manager = None


def get_evolution_client() -> Optional[EvolutionClient]:
    """Função utilitária para obter a instância do cliente em qualquer parte do código."""
    if _client_manager:
        return _client_manager.get_client()
    
    logger.error("Gerenciador do cliente não foi inicializado devido a erros de configuração ou conexão.")
    return None


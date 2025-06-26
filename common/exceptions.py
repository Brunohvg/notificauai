# common/exceptions.py

# -------------------------------
# EXCEÇÕES GERAIS DE INTEGRAÇÃO
# -------------------------------

class IntegrationError(Exception):
    """Erro genérico relacionado a integrações."""
    pass

class WorkspaceNotFound(IntegrationError):
    """Workspace não encontrado."""
    def __init__(self, message="Workspace não encontrado"):
        super().__init__(message)

class IntegrationNotFound(IntegrationError):
    """Integração não encontrada no banco."""
    def __init__(self, message="Integração não encontrada"):
        super().__init__(message)

class InvalidCredentials(IntegrationError):
    """Credenciais inválidas ou ausentes."""
    def __init__(self, message="Credenciais inválidas para a integração"):
        super().__init__(message)

class APIRequestError(IntegrationError):
    """Erro em requisição externa à API da integração."""
    def __init__(self, message="Erro ao fazer requisição para API da integração"):
        super().__init__(message)


# -------------------------------
# EXCEÇÕES DE VALIDAÇÃO
# -------------------------------

class ValidationError(Exception):
    """Erro genérico de validação."""
    pass

class DataValidationError(ValidationError):
    """Dados inválidos fornecidos."""
    def __init__(self, message="Dados inválidos"):
        super().__init__(message)


# -------------------------------
# EXCEÇÕES WHATSAPP (EVOLUTION)
# -------------------------------

class WhatsAppClientUnavailable(Exception):
    """Cliente WhatsApp (Evolution) não pôde ser inicializado."""
    pass

class WhatsAppInstanceAlreadyExists(Exception):
    """Já existe uma instância com esse nome."""
    pass

class WhatsAppIntegrationError(Exception):
    """Erro genérico ao criar integração com WhatsApp."""
    pass

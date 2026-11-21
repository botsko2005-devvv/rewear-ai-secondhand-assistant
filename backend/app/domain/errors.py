class DomainError(Exception):
    """Базова доменна помилка."""
    def __init__(self, message: str = "Domain error occurred"):
        super().__init__(message)
        self.message = message


class AiTimeoutDomainError(DomainError):
    """Помилка таймауту AI-провайдера."""
    pass


class AiProviderDomainError(DomainError):
    """Помилка звернення до AI-провайдера."""
    pass


class InvalidAiResponseDomainError(DomainError):
    """Помилка невалідного формату відповіді від AI."""
    pass

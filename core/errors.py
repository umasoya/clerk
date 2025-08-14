class UnknownModel(Exception):
    def __init__(self, model: str):
        super().__init__(f'Unknown model: {model}')
        self.model = model

class ProviderImplementationError(Exception):
    pass

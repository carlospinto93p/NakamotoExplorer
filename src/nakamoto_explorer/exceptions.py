
class NakamotoExplorerException(BaseException):
    def __init__(self, message, processing_object=None, logger=None, logger_level='error'):
        complete_message = f'{self.__class__.__name__}: {message}'
        if processing_object is not None:
            complete_message = f'{complete_message}\nAt object: {processing_object}'
        if logger is not None:
            getattr(logger, logger_level)(complete_message)
        self.processing_object = processing_object
        self.message = message
        self.complete_message = complete_message
        super().__init__(complete_message)


class SimulationException(NakamotoExplorerException):
    pass


class ValidationException(NakamotoExplorerException):
    pass

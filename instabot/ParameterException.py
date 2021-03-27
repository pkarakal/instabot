class ParameterException(Exception):
    def __init__(self, parameter, message="Parameter \'{parameter}\' missing or invalid"):
        self.parameter = parameter
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message.format(parameter=self.parameter)

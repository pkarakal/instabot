class SpamDetectedException(Exception):
    def __init__(self, parameter, message="Comments are blocked until \'{parameter}\'. This is greater than 7 days. "
                                          "Exiting..."):
        self.parameter = parameter
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message.format(parameter=self.parameter)

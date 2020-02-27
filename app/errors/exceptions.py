
class BackendError(Exception):
    """
    Backend exception is raised when error occurs during backend service process
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

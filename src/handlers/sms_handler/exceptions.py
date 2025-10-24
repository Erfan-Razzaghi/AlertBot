
class SMSError(Exception):
    """Base exception for SMS related errors"""
    pass

class SMSValidationError(SMSError):
    """Raised when input validation fails"""
    pass

class SMSSendError(SMSError):
    """Raised when SMS sending fails"""
    pass

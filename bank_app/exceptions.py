class BankError(Exception):
    """Base exception for bank application errors."""


class ValidationError(BankError):
    """Raised when request data is invalid."""


class AccountNotFoundError(BankError):
    """Raised when an account cannot be located."""


class AccountLockedError(BankError):
    """Raised when an account operation is attempted while locked."""


class InsufficientFundsError(BankError):
    """Raised when an account lacks enough balance."""


class DuplicateAccountError(BankError):
    """Raised when creating an account that already exists."""

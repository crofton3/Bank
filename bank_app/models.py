from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Transaction:
    kind: str
    amount: float
    message: str
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass(slots=True)
class BankAccount:
    account_number: str
    balance: float = 0.0
    locked: bool = False
    history: list[Transaction] = field(default_factory=list)

    def record(self, kind: str, amount: float, message: str) -> None:
        self.history.insert(0, Transaction(kind=kind, amount=amount, message=message))

    def to_dict(self) -> dict:
        return {
            "accountNumber": self.account_number,
            "balance": round(self.balance, 2),
            "locked": self.locked,
            "history": [
                {
                    "kind": item.kind,
                    "amount": round(item.amount, 2),
                    "message": item.message,
                    "timestamp": item.timestamp,
                }
                for item in self.history[:8]
            ],
        }

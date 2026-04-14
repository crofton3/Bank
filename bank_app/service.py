from __future__ import annotations

from threading import Lock

from .exceptions import (
    AccountLockedError,
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientFundsError,
)
from .models import BankAccount
from .utils import normalize_account_number, parse_amount


class BankService:
    def __init__(self) -> None:
        self._accounts: dict[str, BankAccount] = {}
        self._lock = Lock()
        self._seed_demo_accounts()

    def create_account(self, account_number: object) -> BankAccount:
        normalized = normalize_account_number(account_number)
        with self._lock:
            if normalized in self._accounts:
                raise DuplicateAccountError("That account already exists.")
            account = BankAccount(account_number=normalized)
            account.record("created", 0, f"Account {normalized} created.")
            self._accounts[normalized] = account
            return account

    def deposit(self, account_number: object, amount: object) -> BankAccount:
        normalized = normalize_account_number(account_number)
        parsed_amount = parse_amount(amount, "Deposit amount")
        with self._lock:
            account = self._get_account(normalized)
            self._ensure_active(account)
            account.balance = round(account.balance + parsed_amount, 2)
            account.record(
                "deposit",
                parsed_amount,
                f"Deposited ${parsed_amount:,.2f} into account {normalized}.",
            )
            return account

    def withdraw(self, account_number: object, amount: object) -> BankAccount:
        normalized = normalize_account_number(account_number)
        parsed_amount = parse_amount(amount, "Withdrawal amount")
        with self._lock:
            account = self._get_account(normalized)
            self._ensure_active(account)
            if parsed_amount > account.balance:
                raise InsufficientFundsError("Withdrawal exceeds the available balance.")
            account.balance = round(account.balance - parsed_amount, 2)
            account.record(
                "withdrawal",
                parsed_amount,
                f"Withdrew ${parsed_amount:,.2f} from account {normalized}.",
            )
            return account

    def transfer(
        self,
        sender_account_number: object,
        recipient_account_number: object,
        amount: object,
    ) -> dict:
        sender_number = normalize_account_number(sender_account_number)
        recipient_number = normalize_account_number(recipient_account_number)
        parsed_amount = parse_amount(amount, "Transfer amount")
        with self._lock:
            sender = self._get_account(sender_number)
            recipient = self._get_account(recipient_number)
            self._ensure_active(sender)
            self._ensure_active(recipient)
            if sender.account_number == recipient.account_number:
                raise ValueError("Sender and recipient must be different accounts.")
            if parsed_amount > sender.balance:
                raise InsufficientFundsError("Transfer exceeds the sender's balance.")

            sender.balance = round(sender.balance - parsed_amount, 2)
            recipient.balance = round(recipient.balance + parsed_amount, 2)
            sender.record(
                "transfer-out",
                parsed_amount,
                f"Transferred ${parsed_amount:,.2f} to account {recipient.account_number}.",
            )
            recipient.record(
                "transfer-in",
                parsed_amount,
                f"Received ${parsed_amount:,.2f} from account {sender.account_number}.",
            )
            return {"sender": sender, "recipient": recipient}

    def lock_account(self, account_number: object) -> BankAccount:
        normalized = normalize_account_number(account_number)
        with self._lock:
            account = self._get_account(normalized)
            account.locked = True
            account.record("lock", 0, f"Account {normalized} was locked.")
            return account

    def unlock_account(self, account_number: object) -> BankAccount:
        normalized = normalize_account_number(account_number)
        with self._lock:
            account = self._get_account(normalized)
            account.locked = False
            account.record("unlock", 0, f"Account {normalized} was unlocked.")
            return account

    def get_snapshot(self) -> dict:
        with self._lock:
            accounts = [account.to_dict() for account in self._accounts.values()]

        total_balance = round(sum(account["balance"] for account in accounts), 2)
        active_accounts = sum(1 for account in accounts if not account["locked"])
        return {
            "summary": {
                "totalAccounts": len(accounts),
                "activeAccounts": active_accounts,
                "lockedAccounts": len(accounts) - active_accounts,
                "totalBalance": total_balance,
            },
            "accounts": sorted(accounts, key=lambda item: item["accountNumber"]),
        }

    def _get_account(self, account_number: str) -> BankAccount:
        try:
            return self._accounts[account_number]
        except KeyError as exc:
            raise AccountNotFoundError("That account could not be found.") from exc

    @staticmethod
    def _ensure_active(account: BankAccount) -> None:
        if account.locked:
            raise AccountLockedError(
                f"Account {account.account_number} is locked. Unlock it first."
            )

    def _seed_demo_accounts(self) -> None:
        demo_accounts = ("123456", "456789", "789123")
        for account_number in demo_accounts:
            account = BankAccount(account_number=account_number)
            account.record("created", 0, f"Account {account_number} created.")
            self._accounts[account_number] = account

        self._accounts["123456"].balance = 2400.0
        self._accounts["123456"].record(
            "deposit", 2400, "Seeded with $2,400.00 for dashboard preview."
        )
        self._accounts["456789"].balance = 875.5
        self._accounts["456789"].record(
            "deposit", 875.5, "Seeded with $875.50 for dashboard preview."
        )
        self._accounts["789123"].balance = 120.25
        self._accounts["789123"].record(
            "deposit", 120.25, "Seeded with $120.25 for dashboard preview."
        )

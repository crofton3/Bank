class User:
    def __init__(self, account_number):
        self.account_number = account_number

class BankAccount:
    def __init__(self, user, bank_system):
        self.user = user
        self.balance = 0
        self.bank_system = bank_system

    def deposit(self, amount):
        # input validation: ensure the amount is a positive number
        if isinstance(amount, (int, float)) and amount > 0:
            self.balance += amount
            return f"Deposited ${amount} into account {self.user.account_number}"
        else:
            return "Invalid deposit amount"

    def withdraw(self, amount):
        # input validation: ensure the amount is a positive number and doesn't exceed balance
        if isinstance(amount, (int, float)) and amount > 0 and amount <= self.balance:
            self.balance -= amount
            return f"Withdrew ${amount} from account {self.user.account_number}"
        else:
            return "Invalid withdrawal amount"

    def check_balance(self):
        return f"Account balance for {self.user.account_number}: ${self.balance}"

    def transfer(self, amount, recipient_account_number):
        # input validation: ensure the amount is a positive number and doesn't exceed sender's balance
        if isinstance(amount, (int, float)) and amount > 0 and amount <= self.balance:
            recipient_account = self.bank_system.users.get(recipient_account_number)
            if recipient_account:
                recipient_account.deposit(amount)
                self.withdraw(amount)
                return f"Transferred ${amount} from account {self.user.account_number} to account {recipient_account_number}"
            else:
                return "Recipient account does not exist"
        else:
            return "Invalid transfer amount"

class BankSystem:
    def __init__(self):
        self.users = {}
        self.locked_accounts = {}

    def create_account(self, account_number):
            if account_number not in self.users:
                user = User(account_number)
                new_account = BankAccount(user, self)
                self.users[account_number] = new_account
                return f"Created account {account_number} with initial balance $0"
            else:
                return "Account already exists"

    def transfer_funds(self, sender_account_number, recipient_account_number, amount):
        # input validation: ensure both accounts exist and the sender has sufficient funds
        if sender_account_number in self.users and recipient_account_number in self.users:
            sender_balance = self.users[sender_account_number].balance
            if isinstance(amount, (int, float)) and amount > 0 and amount <= sender_balance:
                self.transfer_funds_from_account(sender_account_number, recipient_account_number, amount)
                return f"Transferred ${amount} from account {sender_account_number} to account {recipient_account_number}"
            else:
                return "Insufficient funds for transfer"
        else:
            return "One or both accounts do not exist"

    def display_balances(self):
        balances = {}
        for account_number, balance in self.users.items():
            balances[account_number] = balance.balance
        return balances

    def lock_account(self, account_number):
        # input validation: ensure the account exists and is not already locked
        if account_number in self.users:
            if account_number not in self.locked_accounts:
                self.locked_accounts[account_number] = True
                return f"Locked account {account_number}"
            else:
                return "Account is already locked"
        else:
            return "Account does not exist"

    def unlock_account(self, account_number):
        # input validation: ensure the account exists and is currently locked
        if account_number in self.users:
            if account_number in self.locked_accounts and self.locked_accounts[account_number]:
                del self.locked_accounts[account_number]
                return f"Unlocked account {account_number}"
            else:
                return "Account is not locked"
        else:
            return "Account does not exist"

    def transfer_funds_from_account(self, sender_account_number, recipient_account_number, amount):
        sender_account = self.users.get(sender_account_number)
        if sender_account:
            sender_account.transfer(amount, recipient_account_number)
        else:
            return "Sender account does not exist"
        

bank_system = BankSystem()
print(bank_system.create_account("1234567891"))  # Created account 1234567890 with initial balance $0

# To test transfer method, you'll need a recipient's account number
#print(bank_system.transfer_funds("1234567891", "9876543210", 100))  
# Transfer successful: Transferred $100 from account 1234567890 to account 9876543210
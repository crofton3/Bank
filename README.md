# Bank Dashboard

This project was refactored from a single-file Python script into a small, organized web app built with the Python standard library.

## Structure

```text
bank.py
bank_app/
  __init__.py
  exceptions.py
  models.py
  service.py
  server.py
  utils.py
  static/
    app.js
    styles.css
  templates/
    index.html
```

## Run

```bash
python3 bank.py
```

Then open `http://127.0.0.1:8000`.

## Features

- Create accounts
- Deposit and withdraw funds
- Transfer between accounts
- Lock and unlock accounts
- View balances and recent activity in a responsive dashboard

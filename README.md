# Banking System Demonstration

[![Project checks](https://github.com/TSobees/Banking-System/actions/workflows/checks.yml/badge.svg)](https://github.com/TSobees/Banking-System/actions/workflows/checks.yml)

A Python learning project with Tkinter, an optional Kivy interface and a command-line
interface backed by one SQLite ledger. Accounts and transaction history persist
between sessions. Money uses integer kobo, avoiding binary floating-point balances.

This is an educational local demo. It has no authentication, payment integration or
access separation between users. It is unsuitable for real customer funds or records.

## Start the desktop app

Use Python 3.12 or 3.13. Tkinter needs a desktop display; some Linux installations
require the OS `python3-tk` package. The default app has no pip dependencies.

```sh
python main.py
```

Choose **Load demo accounts** for fictional examples, or create a new account.
The amount field is the opening balance for Create account. Both the Tkinter and
Kivy frontends share `data/banking.sqlite3`; it is ignored by Git.

## Command-line demo

```sh
python -m banking --seed-demo accounts
python -m banking deposit jola 125.50
python -m banking transfer jola mary 25.25
python -m banking history jola
python -m banking export jola outputs/statement.csv
```

Use `--database path/to/demo.sqlite3` before the command to isolate another
demonstration. Loading demo accounts never resets existing balances. The sample
emails use `example.com`. Amounts must be finite, positive and have at most two
decimal places; opening balances may be zero. Transfers and both ledger entries
commit atomically. Failed operations leave balances and history unchanged.

## Optional Kivy app

```sh
python -m pip install -r requirements-kivy.txt
python banking_kivy.py
```

Kivy must be available for your Python and desktop platform. Its frontend is optional;
the ledger and CLI run independently. Original filenames containing spaces remain
compatibility launchers; the documented names are `banking_tkinter.py` and `banking_kivy.py`.

## Structure and tests

```text
banking/                Shared ledger, CLI and separate GUI adapters
main.py                 Default Tkinter launcher
banking_tkinter.py       Explicit desktop launcher
banking_kivy.py          Optional Kivy launcher
tests/                  Money, persistence, rollback, transfer and export checks
data/                   Local database created on first use and ignored by Git
```

```sh
python -m unittest discover -s tests -v
```

CI tests the shared ledger on Python 3.12 and 3.13. Desktop interaction and optional
Kivy rendering require manual testing on the intended platform. No new reuse license
has been assigned. Author: Sobanjo Oluwatosin. AI assisted this revision's persistence,
shared interfaces, tests and documentation.

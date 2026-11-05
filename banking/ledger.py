"""SQLite ledger with integer minor units and atomic balance changes."""
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
import csv
import re
import sqlite3

MAX_CENTS = 100_000_000_000

def money(value, allow_zero=False):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0 or (not allow_zero and amount == 0):
            raise ValueError('Enter a finite positive amount; opening balances may be zero.')
        cents = amount * 100
        if cents != cents.to_integral_value() or cents > MAX_CENTS:
            raise ValueError('Use at most two decimal places and an amount no greater than 1 billion.')
        return int(cents)
    except (InvalidOperation, TypeError):
        raise ValueError('Enter a valid amount.') from None

def formatted(cents):
    return f'{Decimal(cents)/100:.2f}'

def username(value):
    name = str(value).strip().lower()
    if not re.fullmatch(r'[a-z0-9_]{1,40}', name):
        raise ValueError('Username must contain 1 to 40 letters, numbers or underscores.')
    return name

class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS accounts (
                    username TEXT PRIMARY KEY, email TEXT NOT NULL,
                    balance_cents INTEGER NOT NULL CHECK(balance_cents >= 0 AND balance_cents <= 100000000000));
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL REFERENCES accounts(username),
                    kind TEXT NOT NULL, delta_cents INTEGER NOT NULL,
                    balance_cents INTEGER NOT NULL, counterpart TEXT, created_at TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS history_user ON transactions(username, id);
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _entry(self, db, name, kind, delta, balance, counterpart=None):
        db.execute('INSERT INTO transactions(username,kind,delta_cents,balance_cents,counterpart,created_at) VALUES(?,?,?,?,?,?)',
            (name, kind, delta, balance, counterpart, datetime.now(timezone.utc).isoformat(timespec='microseconds')))

    def _account(self, db, name):
        row = db.execute('SELECT * FROM accounts WHERE username=?', (name,)).fetchone()
        if row is None:
            raise ValueError('Account not found.')
        return dict(row)

    def create(self, name, email, opening='0'):
        name = username(name)
        email = str(email).strip()
        if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            raise ValueError('Enter an email address such as demo@example.com.')
        cents = money(opening, allow_zero=True)
        with self.connect() as db:
            try:
                db.execute('INSERT INTO accounts VALUES(?,?,?)', (name, email, cents))
            except sqlite3.IntegrityError:
                raise ValueError('Username already exists.') from None
            self._entry(db, name, 'opening', cents, cents)
        return self.account(name)

    def account(self, name):
        with self.connect() as db:
            row = self._account(db, username(name))
        row['balance'] = formatted(row['balance_cents'])
        return row

    def accounts(self):
        with self.connect() as db:
            return [dict(r, balance=formatted(r['balance_cents'])) for r in db.execute('SELECT * FROM accounts ORDER BY username')]

    def change(self, name, amount, withdraw=False):
        name, cents = username(name), money(amount)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            before = self._account(db, name)['balance_cents']
            delta = -cents if withdraw else cents
            balance = before + delta
            if not 0 <= balance <= MAX_CENTS:
                raise ValueError('Insufficient funds or maximum demo balance exceeded.')
            db.execute('UPDATE accounts SET balance_cents=? WHERE username=?', (balance, name))
            self._entry(db, name, 'withdrawal' if withdraw else 'deposit', delta, balance)
        return self.account(name)

    def transfer(self, sender, recipient, amount):
        sender, recipient, cents = username(sender), username(recipient), money(amount)
        if sender == recipient:
            raise ValueError('Choose a different recipient.')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            a, b = self._account(db, sender), self._account(db, recipient)
            if a['balance_cents'] < cents or b['balance_cents'] + cents > MAX_CENTS:
                raise ValueError('Insufficient funds or maximum demo balance exceeded.')
            for name, delta, other, before in [(sender,-cents,recipient,a['balance_cents']), (recipient,cents,sender,b['balance_cents'])]:
                balance = before + delta
                db.execute('UPDATE accounts SET balance_cents=? WHERE username=?', (balance,name))
                self._entry(db, name, 'transfer', delta, balance, other)

    def history(self, name):
        name = username(name)
        with self.connect() as db:
            self._account(db,name)
            return [dict(r, amount=formatted(r['delta_cents']), balance=formatted(r['balance_cents']))
                for r in db.execute('SELECT * FROM transactions WHERE username=? ORDER BY id DESC', (name,))]

    def export(self, name, path):
        rows = self.history(name)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=['id','created_at','username','kind','amount','balance','counterpart'], extrasaction='ignore')
            writer.writeheader();writer.writerows(rows)

    def seed_demo(self):
        for name, amount in [('jola','5000'), ('mary','3000'), ('abiola','10000')]:
            try:
                self.create(name, name+'@example.com', amount)
            except ValueError as error:
                if str(error) != 'Username already exists.': raise

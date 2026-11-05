import csv
from pathlib import Path
import tempfile
import unittest
from banking.ledger import Ledger, money

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'bank.db';self.bank=Ledger(self.path)
        self.bank.create('a','a@example.com','100');self.bank.create('b','b@example.com')
    def test_decimal_amounts_and_persistence(self):
        self.bank.change('a','0.10');self.bank.change('a','0.20')
        self.assertEqual(Ledger(self.path).account('a')['balance'],'100.30')
    def test_reject_nonfinite_and_fractional_cents(self):
        for value in ['NaN','Infinity','-2','0','0.001','1000000001']:
            with self.subTest(value=value),self.assertRaises(ValueError): self.bank.change('a',value)
        self.assertEqual(self.bank.account('a')['balance'],'100.00')
    def test_transfer_balances_and_history(self):
        self.bank.transfer('a','b','15.25')
        self.assertEqual(self.bank.account('a')['balance'],'84.75')
        self.assertEqual(self.bank.account('b')['balance'],'15.25')
        self.assertEqual(self.bank.history('a')[0]['counterpart'],'b')
    def test_failed_transfer_rolls_back(self):
        for recipient,amount in [('b','101'),('missing','5'),('a','5')]:
            with self.assertRaises(ValueError): self.bank.transfer('a',recipient,amount)
        self.assertEqual(self.bank.account('a')['balance'],'100.00')
        self.assertEqual(len(self.bank.history('a')),1)
    def test_overdraft_rejected(self):
        with self.assertRaises(ValueError): self.bank.change('a','100.01',True)
    def test_accounts_and_seed_do_not_reset_balances(self):
        self.bank.seed_demo();self.bank.change('jola','1');self.bank.seed_demo()
        self.assertEqual(self.bank.account('jola')['balance'],'5001.00')
    def test_duplicate_and_invalid_accounts(self):
        for name,email in [('A','a@example.com'),('','a@example.com'),('bad name','a@example.com'),('c','bad')]:
            with self.assertRaises(ValueError): self.bank.create(name,email)
    def test_history_csv(self):
        path=Path(self.temp.name)/'history.csv';self.bank.export('a',path)
        with path.open() as stream: rows=list(csv.DictReader(stream))
        self.assertEqual(rows[0]['amount'],'100.00')

if __name__=='__main__': unittest.main()

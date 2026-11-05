import argparse
from pathlib import Path
from .ledger import Ledger

def main(argv=None):
    p=argparse.ArgumentParser(description='Educational local ledger. No authentication or real payment processing.')
    p.add_argument('--database',type=Path,default=Path(__file__).resolve().parents[1]/'data/banking.sqlite3')
    p.add_argument('--seed-demo',action='store_true',help='Create fictional example accounts once; never reset their balances.')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('accounts')
    for command in ['balance','history']:
        q=sub.add_parser(command);q.add_argument('username')
    q=sub.add_parser('create');q.add_argument('username');q.add_argument('email');q.add_argument('--opening',default='0')
    for command in ['deposit','withdraw']:
        q=sub.add_parser(command);q.add_argument('username');q.add_argument('amount')
    q=sub.add_parser('transfer');q.add_argument('sender');q.add_argument('recipient');q.add_argument('amount')
    q=sub.add_parser('export');q.add_argument('username');q.add_argument('output',type=Path)
    a=p.parse_args(argv)
    try:
        bank=Ledger(a.database)
        if a.seed_demo: bank.seed_demo()
        if a.command=='accounts':
            for row in bank.accounts(): print(row['username'],row['balance'])
        elif a.command=='balance': print(bank.account(a.username)['balance'])
        elif a.command=='history':
            for row in bank.history(a.username): print(row['created_at'],row['kind'],row['amount'],row['balance'])
        elif a.command=='create': print(bank.create(a.username,a.email,a.opening)['balance'])
        elif a.command in ['deposit','withdraw']: print(bank.change(a.username,a.amount,a.command=='withdraw')['balance'])
        elif a.command=='transfer': bank.transfer(a.sender,a.recipient,a.amount);print('Transfer recorded.')
        elif a.command=='export': bank.export(a.username,a.output);print('Exported '+str(a.output))
    except (ValueError,OSError) as error: p.error(str(error))
    return 0

if __name__=='__main__': raise SystemExit(main())

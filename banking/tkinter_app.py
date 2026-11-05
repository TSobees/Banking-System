"""Desktop interface sharing the persistent, tested ledger service."""
from pathlib import Path
from .ledger import Ledger

def main(database=None):
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    bank=Ledger(database or Path(__file__).resolve().parents[1]/'data/banking.sqlite3')
    root=tk.Tk();root.title('Banking ledger demonstration');root.geometry('820x650')
    root.columnconfigure(0,weight=1);root.rowconfigure(3,weight=1)
    ttk.Label(root,text='Local banking ledger',font=('Arial',20,'bold')).grid(row=0,column=0,padx=20,pady=12,sticky='w')
    ttk.Label(root,text='Educational demo · local accounts · no login or real payments').grid(row=1,column=0,padx=20,sticky='w')
    form=ttk.Frame(root,padding=20);form.grid(row=2,column=0,sticky='ew')
    values={}
    for i,(key,label) in enumerate([('username','Username'),('amount','Amount'),('recipient','Transfer recipient'),('email','Email for new account')]):
        ttk.Label(form,text=label).grid(row=i,column=0,sticky='w',pady=3)
        values[key]=tk.StringVar();ttk.Entry(form,textvariable=values[key],width=44).grid(row=i,column=1,sticky='ew',padx=12)
    form.columnconfigure(1,weight=1)
    status=tk.StringVar(value='Create an account or choose Load demo accounts.')
    columns=('time','kind','amount','balance','counterpart')
    box=ttk.Frame(root,padding=(20,0));box.grid(row=3,column=0,sticky='nsew');box.rowconfigure(0,weight=1);box.columnconfigure(0,weight=1)
    tree=ttk.Treeview(box,columns=columns,show='headings')
    for col in columns: tree.heading(col,text=col.title());tree.column(col,width=130)
    tree.column('time',width=210);tree.grid(row=0,column=0,sticky='nsew')
    bar=ttk.Scrollbar(box,orient='vertical',command=tree.yview);bar.grid(row=0,column=1,sticky='ns');tree.configure(yscrollcommand=bar.set)
    def refresh():
        account=bank.account(values['username'].get())
        status.set(account['username']+' · Balance NGN '+account['balance'])
        tree.delete(*tree.get_children())
        for item in bank.history(account['username']): tree.insert('',tk.END,values=(item['created_at'],item['kind'],item['amount'],item['balance'],item['counterpart'] or ''))
    def action(kind):
        try:
            user=values['username'].get();amount=values['amount'].get()
            if kind=='create': bank.create(user,values['email'].get(),amount or '0')
            elif kind=='deposit': bank.change(user,amount)
            elif kind=='withdraw': bank.change(user,amount,True)
            elif kind=='transfer': bank.transfer(user,values['recipient'].get(),amount)
            elif kind=='seed':
                bank.seed_demo();values['username'].set('jola')
            elif kind=='export':
                path=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')])
                if path: bank.export(user,path)
            refresh()
        except (ValueError,OSError) as error: messagebox.showerror('Check input',str(error))
    buttons=ttk.Frame(root,padding=20);buttons.grid(row=4,column=0,sticky='ew')
    for i,(label,kind) in enumerate([('Balance / history','view'),('Deposit','deposit'),('Withdraw','withdraw'),('Transfer','transfer'),('Create account','create'),('Export CSV','export'),('Load demo accounts','seed')]):
        ttk.Button(buttons,text=label,command=lambda k=kind:action(k)).grid(row=i//4,column=i%4,padx=4,pady=4,sticky='ew')
    ttk.Label(root,textvariable=status,padding=20).grid(row=5,column=0,sticky='w')
    root.mainloop()

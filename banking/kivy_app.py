"""Optional Kivy frontend; imports Kivy only when launched."""
from pathlib import Path
from .ledger import Ledger

def main():
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    bank=Ledger(Path(__file__).resolve().parents[1]/'data/banking.sqlite3')
    class BankingApp(App):
        def build(self):
            self.title='Local banking demonstration'
            layout=BoxLayout(orientation='vertical',padding=20,spacing=6)
            layout.add_widget(Label(text='Educational ledger; no login or real payments'))
            self.fields={}
            for key in ['username','amount','recipient','email']:
                field=TextInput(hint_text=key,multiline=False);self.fields[key]=field;layout.add_widget(field)
            self.result=Label(text='Create an account or load the fictional examples.')
            for name in ['balance','deposit','withdraw','transfer','create','seed','history']:
                button=Button(text=name.title());button.bind(on_press=lambda _,k=name:self.run_action(k));layout.add_widget(button)
            layout.add_widget(self.result);return layout
        def run_action(self,kind):
            f={k:v.text for k,v in self.fields.items()};user=f['username']
            try:
                if kind=='seed': bank.seed_demo();user='jola';self.fields['username'].text=user
                elif kind=='create': bank.create(user,f['email'],f['amount'] or '0')
                elif kind=='deposit': bank.change(user,f['amount'])
                elif kind=='withdraw': bank.change(user,f['amount'],True)
                elif kind=='transfer': bank.transfer(user,f['recipient'],f['amount'])
                if kind=='history':
                    self.result.text='\n'.join(x['kind']+' '+x['amount']+' -> '+x['balance'] for x in bank.history(user)[:8])
                else: self.result.text=user+' · NGN '+bank.account(user)['balance']
            except (ValueError,OSError) as error: self.result.text=str(error)
    BankingApp().run()

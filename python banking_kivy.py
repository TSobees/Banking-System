from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

# Dictionary to store user accounts with details
accounts = {
    "jola": {"balance": 5000, "email": "jola@yahoo.com"},
    "mary": {"balance": 3000, "email": "mary@gmail.com"},
    "abiola": {"balance": 10000, "email": "abiola@aol.com"}
}

def show_popup(title, message):
    popup = Popup(
        title=title,
        content=Label(text=message),
        size_hint=(0.7, 0.4),
    )
    popup.open()

class BankingApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=8, padding=10, **kwargs)

        # --- Existing User Section ---
        self.add_widget(Label(text="--- Existing User ---", bold=True, font_size=18))

        self.add_widget(Label(text="Enter Username:"))
        self.username_entry = TextInput(multiline=False)
        self.add_widget(self.username_entry)

        self.add_widget(Label(text="Enter Amount (₦):"))
        self.amount_entry = TextInput(multiline=False)
        self.add_widget(self.amount_entry)

        self.add_widget(Button(text="Check Balance", background_color=(0.3, 0.5, 1, 1), on_press=self.check_balance))
        self.add_widget(Button(text="Deposit", background_color=(0.3, 1, 0.3, 1), on_press=self.deposit))
        self.add_widget(Button(text="Withdraw", background_color=(1, 0.4, 0.4, 1), on_press=self.withdraw))

        # --- Create New User Section ---
        self.add_widget(Label(text=""))
        self.add_widget(Label(text="--- Create New User ---", bold=True, font_size=18))

        self.add_widget(Label(text="New Username:"))
        self.new_username_entry = TextInput(multiline=False)
        self.add_widget(self.new_username_entry)

        self.add_widget(Label(text="Starting Balance (₦):"))
        self.new_balance_entry = TextInput(multiline=False)
        self.add_widget(self.new_balance_entry)

        self.add_widget(Label(text="Email:"))
        self.new_email_entry = TextInput(multiline=False)
        self.add_widget(self.new_email_entry)

        self.add_widget(Button(text="Create User", background_color=(1, 0.7, 0.3, 1), on_press=self.create_user))
        self.add_widget(Button(text="Exit", background_color=(0.5, 0.5, 0.5, 1), on_press=self.exit_app))

    # --- Function Definitions ---
    def check_balance(self, instance):
        user = self.username_entry.text.lower()
        if user in accounts:
            balance = accounts[user]["balance"]
            email = accounts[user]["email"]
            show_popup("Balance", f"User: {user.capitalize()}\nBalance: ₦{balance}\nEmail: {email}")
        else:
            show_popup("Error", "User not found!")

    def deposit(self, instance):
        user = self.username_entry.text.lower()
        if user not in accounts:
            show_popup("Error", "User not found!")
            return

        try:
            amount = float(self.amount_entry.text)
            if amount > 0:
                accounts[user]["balance"] += amount
                show_popup("Deposit", f"₦{amount} deposited!\nNew balance: ₦{accounts[user]['balance']}")
            else:
                show_popup("Error", "Enter a positive amount!")
        except ValueError:
            show_popup("Error", "Invalid amount entered.")

    def withdraw(self, instance):
        user = self.username_entry.text.lower()
        if user not in accounts:
            show_popup("Error", "User not found!")
            return

        try:
            amount = float(self.amount_entry.text)
            if 0 < amount <= accounts[user]["balance"]:
                accounts[user]["balance"] -= amount
                show_popup("Withdraw", f"₦{amount} withdrawn!\nNew balance: ₦{accounts[user]['balance']}")
            else:
                show_popup("Error", "Insufficient funds or invalid amount!")
        except ValueError:
            show_popup("Error", "Invalid amount entered.")

    def create_user(self, instance):
        new_user = self.new_username_entry.text.lower()
        new_email = self.new_email_entry.text

        try:
            start_balance = float(self.new_balance_entry.text)
        except ValueError:
            show_popup("Error", "Invalid starting balance!")
            return

        if new_user in accounts:
            show_popup("Error", "User already exists!")
        elif new_user == "":
            show_popup("Error", "Username cannot be empty!")
        elif start_balance < 0:
            show_popup("Error", "Starting balance must be >= 0")
        else:
            accounts[new_user] = {"balance": start_balance, "email": new_email}
            show_popup("Success", f"Account created for {new_user.capitalize()}\nBalance: ₦{start_balance}\nEmail: {new_email}")
            self.new_username_entry.text = ""
            self.new_balance_entry.text = ""
            self.new_email_entry.text = ""

    def exit_app(self, instance):
        App.get_running_app().stop()

class MyBankingApp(App):
    def build(self):
        self.title = "Simple Banking System - Kivy"
        return BankingApp()

if __name__ == "__main__":
    MyBankingApp().run()


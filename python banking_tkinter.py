import tkinter as tk
from tkinter import messagebox

# Dictionary to store user accounts with details
accounts = {
    "jola": {"balance": 5000, "email": "jola@yahoo.com"},
    "mary": {"balance": 3000, "email": "mary@gmail.com"},
    "abiola": {"balance": 10000, "email": "abiola@aol.com"}
}

# --- Banking Functions ---
def check_balance():
    user = username_entry.get().lower()
    if user in accounts:
        balance = accounts[user]["balance"]
        email = accounts[user]["email"]
        messagebox.showinfo("Balance", f"User: {user.capitalize()}\nBalance: ₦{balance}\nEmail: {email}")
    else:
        messagebox.showerror("Error", "User not found!")

def deposit():
    user = username_entry.get().lower()
    if user not in accounts:
        messagebox.showerror("Error", "User not found!")
        return

    try:
        amount = float(amount_entry.get())
        if amount > 0:
            accounts[user]["balance"] += amount
            messagebox.showinfo("Deposit", f"₦{amount} deposited!\nNew balance: ₦{accounts[user]['balance']}")
        else:
            messagebox.showerror("Error", "Enter a positive amount!")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered.")

def withdraw():
    user = username_entry.get().lower()
    if user not in accounts:
        messagebox.showerror("Error", "User not found!")
        return

    try:
        amount = float(amount_entry.get())
        if 0 < amount <= accounts[user]["balance"]:
            accounts[user]["balance"] -= amount
            messagebox.showinfo("Withdraw", f"₦{amount} withdrawn!\nNew balance: ₦{accounts[user]['balance']}")
        else:
            messagebox.showerror("Error", "Insufficient funds or invalid amount!")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered.")

def create_user():
    new_user = new_username_entry.get().lower()
    new_email = new_email_entry.get()
    
    try:
        start_balance = float(new_balance_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid starting balance!")
        return

    if new_user in accounts:
        messagebox.showerror("Error", "User already exists!")
    elif new_user == "":
        messagebox.showerror("Error", "Username cannot be empty!")
    elif start_balance < 0:
        messagebox.showerror("Error", "Starting balance must be >= 0")
    else:
        accounts[new_user] = {"balance": start_balance, "email": new_email}
        messagebox.showinfo("Success", f"Account created for {new_user.capitalize()}\nBalance: ₦{start_balance}\nEmail: {new_email}")
        new_username_entry.delete(0, tk.END)
        new_balance_entry.delete(0, tk.END)
        new_email_entry.delete(0, tk.END)

# --- GUI Setup ---
root = tk.Tk()
root.title("Simple Banking System")
root.geometry("400x450")
root.resizable(False, False)

# Existing User Section
tk.Label(root, text="--- Existing User ---", font=("Arial", 10, "bold")).pack(pady=5)

tk.Label(root, text="Enter Username:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Enter Amount (₦):").pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

tk.Button(root, text="Check Balance", command=check_balance, width=20, bg="lightblue").pack(pady=3)
tk.Button(root, text="Deposit", command=deposit, width=20, bg="lightgreen").pack(pady=3)
tk.Button(root, text="Withdraw", command=withdraw, width=20, bg="salmon").pack(pady=3)

# Divider
tk.Label(root, text="").pack()
tk.Label(root, text="--- Create New User ---", font=("Arial", 10, "bold")).pack(pady=5)

# New User Section
tk.Label(root, text="New Username:").pack()
new_username_entry = tk.Entry(root)
new_username_entry.pack()

tk.Label(root, text="Starting Balance (₦):").pack()
new_balance_entry = tk.Entry(root)
new_balance_entry.pack()

tk.Label(root, text="Email:").pack()
new_email_entry = tk.Entry(root)
new_email_entry.pack()

tk.Button(root, text="Create User", command=create_user, width=20, bg="orange").pack(pady=5)

# Exit Button
tk.Button(root, text="Exit", command=root.quit, width=20, bg="gray").pack(pady=10)

# Run the GUI
root.mainloop()


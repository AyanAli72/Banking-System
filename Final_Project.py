from fastapi import FastAPI, HTTPException
import json
import requests
from datetime import datetime

# File storage
ACCOUNTS_FILE = "accounts.json"
TRANSACTIONS_FILE = "transactions.csv"

app = FastAPI(title="🏦 Python Bank API")

# ------------------------------
# Helper functions
# ------------------------------
def load_accounts():
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

def record_transaction(acc_no, action, amount):
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(f"{acc_no},{action},{amount},{datetime.now()}\n")

# ------------------------------
# API Routes
# ------------------------------

@app.get("/")
def home():
    return {"message": "🏦 Welcome to Python Bank API"}

@app.post("/create")
def create_account(acc_no: str, name: str, pin: str):
    accounts = load_accounts()
    if acc_no in accounts:
        raise HTTPException(status_code=400, detail="❌ Account already exists")
    accounts[acc_no] = {"name": name, "pin": pin.strip(), "balance": 0}
    save_accounts(accounts)
    return {"message": "✅ Account created successfully", "account": accounts[acc_no]}

@app.post("/deposit")
def deposit(acc_no: str, pin: str, amount: float):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="❌ Invalid account or PIN")
    accounts[acc_no]["balance"] += amount
    save_accounts(accounts)
    record_transaction(acc_no, "deposit", amount)
    return {"message": "✅ Deposit successful", "balance": accounts[acc_no]["balance"]}

@app.post("/withdraw")
def withdraw(acc_no: str, pin: str, amount: float):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="❌ Invalid account or PIN")
    if amount > accounts[acc_no]["balance"]:
        raise HTTPException(status_code=400, detail="❌ Insufficient balance")
    accounts[acc_no]["balance"] -= amount
    save_accounts(accounts)
    record_transaction(acc_no, "withdraw", amount)
    return {"message": "✅ Withdrawal successful", "balance": accounts[acc_no]["balance"]}

@app.get("/balance")
def balance(acc_no: str, pin: str):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="❌ Invalid account or PIN")
    return {"account": acc_no, "balance": accounts[acc_no]["balance"]}

@app.get("/balance-usd")
def balance_usd(acc_no: str, pin: str):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="❌ Invalid account or PIN")
    pkr_balance = accounts[acc_no]["balance"]
    url = f"https://api.exchangerate.host/convert?from=PKR&to=USD&amount={pkr_balance}"
    try:
        response = requests.get(url)
        data = response.json()
        usd_balance = round(data["result"], 2)
        return {"account": acc_no, "balance_pkr": pkr_balance, "balance_usd": usd_balance}
    except:
        raise HTTPException(status_code=500, detail="⚠️ Currency API not working")

@app.delete("/delete")
def delete_account(acc_no: str, pin: str):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="❌ Invalid account or PIN")
    del accounts[acc_no]
    save_accounts(accounts)
    return {"message": f"✅ Account {acc_no} deleted successfully"}

# ------------------------------
# New RESTful endpoints
# ------------------------------

# 1️⃣ HEAD - check if account exists (no data returned)
@app.head("/account")
def head_account(acc_no: str, pin: str):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=404, detail="Account not found or invalid PIN")
    return {}  # empty body

# 2️⃣ OPTIONS - list allowed HTTP methods
@app.options("/account")
def options_account():
    return {"Allow": "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD"}

# 3️⃣ PUT - fully update account info (replace name and/or PIN)
@app.put("/account")
def put_account(acc_no: str, pin: str, name: str = None, new_pin: str = None):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="Invalid account or PIN")
    if name:
        accounts[acc_no]["name"] = name
    if new_pin:
        accounts[acc_no]["pin"] = new_pin
    save_accounts(accounts)
    return {"message": "Account updated successfully", "account": accounts[acc_no]}

# 4️⃣ PATCH - partially update account info (change name or PIN)
@app.patch("/account")
def patch_account(acc_no: str, pin: str, new_pin: str = None, name: str = None):
    accounts = load_accounts()
    if acc_no not in accounts or accounts[acc_no]["pin"] != pin:
        raise HTTPException(status_code=400, detail="Invalid account or PIN")
    if new_pin:
        accounts[acc_no]["pin"] = new_pin
    if name:
        accounts[acc_no]["name"] = name
    save_accounts(accounts)
    return {"message": "Account partially updated", "account": accounts[acc_no]}


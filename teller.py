import http.client
from beautifultable import BeautifulTable
import ssl
import json
from base64 import b64encode
from colored import fg, bg, attr
import pandas as pd
import click

# use certificate and private key, replace with your own ones
certificate_file = "PATH_TO_CERTIFICATE"
pk_file = "PATH_TO PRIVATE_KEY"
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(certfile=certificate_file, keyfile=pk_file)
conn = http.client.HTTPSConnection("api.teller.io", port=443, context=context)

# returns all savings/checking/credit card accounts associated with the online account
def getAccountInfo(encodedToken):
    payload = ''
    headers = {
    # account token (get when the client authorizes the account)
    'Authorization': f'Basic {encodedToken}'
    }
    conn.request("GET", "/accounts", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data

# returns balances of a specific savings/checking/credit card account
def getBalance(encodedToken,accountID):
    payload = ''
    headers = {
    'Authorization': f'Basic {encodedToken}'
    }
    conn.request("GET", f"/accounts/{accountID}/balances", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data

# returns all retrievable transactions of a specific savings/checking/credit card account
def getTxn(encodedToken,accountID):
    payload = ''
    headers = {
    'Authorization': f'Basic {encodedToken}'
    }
    conn.request("GET", f"/accounts/{accountID}/transactions", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data

def listAccounts(encodedToken):
    try:
        data = getAccountInfo(encodedToken)
        accountsList = BeautifulTable()
        accountsList.rows.append(["ID","Type","Status","Product Name","Last Four","Ledger Balance","Available Balance","Issuer Name","Currency"])
        accountCount = 0
        for i in range(len(data)):
            a = data[i]
            balanceData = getBalance(encodedToken,a["id"])
            accountsList.rows.append([i,a["type"],a["status"],a["name"],a["last_four"],balanceData["ledger"],balanceData["available"],a["institution"]["name"],a["currency"]])
            accountCount += 1
        accountWording = "account" if accountCount == 1 or accountCount == 0 else "accounts" 
        print('%s%s %s retrieved%s' % (fg(2),accountCount,accountWording,attr(0)))
        print(accountsList)
    except:
        print('%sUnable to retrieve account information%s' % (fg(1),attr(0)))
        data = []
    return data

def listTxns(encodedToken,accountID):
    txns = []
    try:
        data = getTxn(encodedToken,accountID)
        txnList = BeautifulTable()
        txnList.rows.append(["ID","Type","Status","Description","Date","Amount"])
        for i in range(len(data)):
            t = data[i]
            txnList.rows.append([i,t["type"],t["status"],t["description"],t["date"],t["amount"]])
            txns.append([i,t["type"],t["status"],t["description"],t["date"],t["amount"]])
        print(txnList)
    except:
        print('%sUnable to retrieve transactions%s' % (fg(1),attr(0)))
        data = []
    return txns

def exportTxnCSV(txns, accountData):
    df = pd.DataFrame(txns,columns=['ID','Type',"Status","Description","Date","Amount"])
    productNameFormatted =  "".join(e for e in accountData["name"] if e.isalnum()).lower()
    filename = accountData["institution"]["id"] + "_" + accountData["type"] + "_" + productNameFormatted + "_" + accountData["last_four"] + ".csv"
    df.to_csv(filename,index=False)
    return

def main():
    while True:
        try:
            token = input("Input authorized account token: ")
            token += ":"
            encodedToken = b64encode(token.encode()).decode()
            accountData = listAccounts(encodedToken)
            if len(accountData) == 0: continue
            elif len(accountData) == 1: selectRange = "0"
            else: selectRange = f"0-{len(accountData)-1}"
            accountSel = "1000"
            while (int(accountSel) not in range(len(accountData)) and int(accountSel) != 999):
                accountSel = input(f"Select an account to view transactions [{selectRange}], or type 999 to exit: ")
            if accountSel == "999": continue
            txns = listTxns(encodedToken,accountData[int(accountSel)]["id"])
            if click.confirm('Export transactions to CSV?', default=True):
                exportTxnCSV(txns,accountData[int(accountSel)])
                print('%sCSV saved to current directory%s' % (fg(2),attr(0)))
        except KeyboardInterrupt:
            break

main()
""" install Dependices"""
import json
from collections import defaultdict
from datetime import datetime
import numpy_financial as npf  

 """Process transactions and calculate portfolio value using FIFO per folio."""
def process_transactions(transactions):
    portfolio = defaultdict(lambda: {'units': [], 'purchase_value': 0.0, 'nav': 0.0})
    
    for txn in transactions:
        scheme = txn["scheme"]
        folio = txn.get("folio", "")
        trxn_units = float(txn["trxnUnits"])
        purchase_price = float(txn["purchasePrice"]) if txn["purchasePrice"] else 0.0
        
        
        if trxn_units > 0:  
          
            portfolio[(scheme, folio)]['units'].append((trxn_units, purchase_price))
        elif trxn_units < 0: 
          
            units_to_sell = abs(trxn_units)
            while units_to_sell > 0 and portfolio[(scheme, folio)]['units']:
                purchased_units, purchased_price = portfolio[(scheme, folio)]['units'][0]
                
                if purchased_units > units_to_sell:
                
                    portfolio[(scheme, folio)]['units'][0] = (purchased_units - units_to_sell, purchased_price)
                    units_to_sell = 0
                else:
                   
                    units_to_sell -= purchased_units
                    portfolio[(scheme, folio)]['units'].pop(0)
                    
    return portfolio
    
 """Calculate total portfolio value and gain."""    

def calculate_portfolio_value(data):
    dt_summary = data["dtSummary"]
    dt_transaction = data["dtTransaction"]

    portfolio = process_transactions(dt_transaction)
    
    total_value = 0.0
    total_gain = 0.0
    
    for summary in dt_summary:
        scheme = summary["scheme"]
        folio = summary["folio"]
        nav = float(summary["nav"])
        
       
        current_units = sum(units for units, price in portfolio[(scheme, folio)]['units'])
        current_value = current_units * nav
        
       
        acquisition_cost = sum(units * price for units, price in portfolio[(scheme, folio)]['units'])
        
        gain = current_value - acquisition_cost

        total_value += current_value
        total_gain += gain

    return total_value, total_gain
    
"""Calculate the XIRR of the portfolio and print cash flows for debugging."""

def calculate_xirr(transactions, current_portfolio_value):
    cash_flows = []
    for txn in transactions:
        date = datetime.strptime(txn["trxnDate"], "%d-%b-%Y")
        amount = -float(txn["trxnAmount"]) 
        cash_flows.append((date, amount))
    
   
    cash_flows.append((datetime.now(), current_portfolio_value))

 
    for date, amount in cash_flows:
        print(f"Date: {date}, Amount: {amount}")

  
    dates, amounts = zip(*cash_flows)

    return npf.irr(amounts)

"""Main function to read the JSON file and calculate portfolio value."""

def main(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)["data"][0]  
    
  
    total_value, total_gain = calculate_portfolio_value(data)
    
   
    xirr = calculate_xirr(data["dtTransaction"], total_value)

    print(f"Total Portfolio Value: {total_value}")
    print(f"Total Portfolio Gain: {total_gain}")
   # print(f"Portfolio XIRR: {xirr}")


input_file = '/home/ravi/Documents/transaction_detail.json' 
main(input_file)


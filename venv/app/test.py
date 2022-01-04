from app.functions import *

db = connect_db()
account_table = db.Accounts
machinedata_table = db.MachineData

historic_data = list(machinedata_table.find())

print(historic_data)
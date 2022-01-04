# from app.functions import *

# db = connect_db()
# account_table = db.Accounts
# machinedata_table = db.MachineData

# last_error_data = list(machinedata_table.aggregate(
#     [
#         {"$match":
#             {
#                 'prediction': True
#             }
#         },
#         {
#             "$group":
#             {
#                 "_id": '$id',
#                 'machine': {"$first": "$machine"},
#                 "last_error": {"$max": "$timestamp"} 
#             }
#         }
#     ]))
# last_error_data = sorted(last_error_data, key=lambda d: d['last_error'], reverse=True) 

# print(last_error_data)
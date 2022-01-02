from pymongo import MongoClient
import hashlib



def connect_db():
    test_str = "7yPxFfQLlq1ssIIm"
    access_line = "mongodb+srv://admin:{}@cluster0.mdtqp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(test_str)
    client = MongoClient(access_line, tls=True,
                             tlsAllowInvalidCertificates=True)
    db = client.get_database("MaintenanceEngineering")
    return db

def create_record(table, attributes: list):
    keys = table.find_one().keys()
    
    new_entry= dict()

    index = 0

    for key in keys:
        if key != '_id':
            new_entry[key]=attributes[index]
            index += 1

    result = table.insert_one(new_entry)
    return result


def persistent_hash(password: str):

    hashed_value = int(hashlib.md5(password.encode('utf-8')).hexdigest(), 16)

    return hashed_value 
from pymongo import MongoClient

def get_mongo_client():
    MONGO_URI = "mongodb+srv://db_user_read:LdmrVA5EDEv4z3Wr@cluster0.n10ox.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(MONGO_URI)
    return client['RQ_Analytics']
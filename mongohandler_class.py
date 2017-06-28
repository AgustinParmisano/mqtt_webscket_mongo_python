#PyMongo
from pymongo import MongoClient

#mongo_client = MongoClient('localhost', 27017)
#db = mongo_client['testdb'] #db example
#measures = db['collname'] #coll example
class MongoHandler:
    """docstring for MongoHandler."""
    def __init__(self, host='localhost', port=27017, db='testdb'):
        self.client = MongoClient(host, port)
        self.db = self.client[db]
        self.host = host
        self.port = port

    def set_client(self, client):
        self.client = client

    def get_client(self):
        return self.client

    def set_db(self, db):
        self.db = db

    def get_db(self):
        return self.db

    def set_host(self, host):
        self.host = host

    def get_host(self):
        return self.host

    def set_port(self, port):
        self.port = port

    def get_port(self):
        return self.port

    #Mongo Basic Functions
    def get_single_document(self, collname):
        return self.db[collname].find_one()

    def get_all_documents(self, collname):
        return self.db[collname].find()

    #Get documents with some key:value, key & value has to by string types
    def get_key_value(self, collname, key, value):
        return self.db[collname].find({key:value})

    #Insert document, has to be json or dictionary type
    def insert_one_document(self, collname, document):
        self.db[collname].insert_one(document)

    #Get data from-to times: String Format Example: 2013-09-28 20:30:55.78200
    def get_documents_from_to_time(self, collname, from_time, to_time):
        #Query Example in Mongo shell:
        #db.testcoll.find({timedata:{$gte: ISODate("2017-06-27T20:28:00.000Z"),$lt: ISODate("2017-06-27T20:28:10.000Z")}})
        from_time = datetime.datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S.%f")
        to_time = datetime.datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S.%f")
        start = from_time #datetime.datetime(2017, 6, 28, 17, 4, 0, 457000)
        end = to_time #datetime.datetime(2017, 6, 28, 17, 5, 1, 457000)
        posts = selfdb.testcoll.find({"timedata":{"$gte": start, "$lt": end}})
        output = []
        for post in posts:
            output.append({'potencia' : post["potencia"], 'tension' : post["tension"],'timedata' : post['timedata'], "state" : post['state']})
        return output

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests

class getTricklingData(dml.Algorithm):
    contributor = 'nathansw_rooday_sbajwa_shreyap'
    reads = []
    writes = ['nathansw_rooday_sbajwa_shreyap.trickling']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nathansw_rooday_sbajwa_shreyap', 'nathansw_rooday_sbajwa_shreyap')

        print("Fetching trickling data...")
        data_url = "http://datamechanics.io/data/nathansw_rooday_sbajwa_shreyap/trickling.json"
        response = requests.get(data_url).json()
        print("trickling data fetched!")

        print("Saving trickling data...")
        repo.dropCollection("trickling")
        repo.createCollection("trickling")
        repo['nathansw_rooday_sbajwa_shreyap.trickling'].insert(response)
        repo['nathansw_rooday_sbajwa_shreyap.trickling'].metadata({'complete':True})
        repo.logout()

        print("Done!")
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nathansw_rooday_sbajwa_shreyap', 'nathansw_rooday_sbajwa_shreyap')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/nathansw_rooday_sbajwa_shreyap') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/nathansw_rooday_sbajwa_shreyap') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        # Since the urls have a lot more information about the resource itself, we are treating everything apart from the actual document suffix as the namespace.
        doc.add_namespace('trickling', 'https://data.boston.gov/api/action/datastore_search_sql')

        this_script = doc.agent('alg:nathansw_rooday_sbajwa_shreyap#getTricklingData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('trickling:?sql=SELECT%20*%20from%20%2212cb3883-56f5-47de-afa5-3b1cf61b257b%22', {'prov:label':'trickling Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_trickling_data = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_trickling_data, this_script)
        doc.usage(get_trickling_data, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?sql=SELECT%20*%20from%20%2212cb3883-56f5-47de-afa5-3b1cf61b257b%22'
                  }
                  )        
        trickling = doc.entity('dat:nathansw_rooday_sbajwa_shreyap#trickling', {prov.model.PROV_LABEL:'trickling Data', prov.model.PROV_TYPE:'ont:DataSet'})

        doc.wasAttributedTo(trickling, this_script)
        doc.wasGeneratedBy(trickling, get_trickling_data, endTime)
        doc.wasDerivedFrom(trickling, resource, get_trickling_data, get_trickling_data, get_trickling_data)

        repo.logout()
        return doc
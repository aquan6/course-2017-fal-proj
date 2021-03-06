import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class removeOutliers(dml.Algorithm):
    contributor = 'angelay'
    reads = ['angelay.all2012']
    writes = ['angelay.clean2012']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('angelay', 'angelay')

        repo.dropPermanent('angelay')
        repo.createPermanent('angelay')

        l1, l2, l3, l4, l5, l6, l7 = [], [], [], [], [], [], []
        data = repo.angelay.all2012.find()
        for document in data:
            d = dict(document)
            l1.append(d['CarbonIntensity'])
            l2.append(d['CO2Emissions'])
            l3.append(d['EnergyIntensity'])
            l4.append(d['EnergyUse'])
            l5.append(d['GDPperCapita'])
            l6.append(d['HDI'])
            l7.append(d['Population'])

        data = repo.angelay.all2012.find()
        for document in data:
            d = dict(document)
            if removeOutliers.isOutlier(d['CarbonIntensity'], l1) or removeOutliers.isOutlier(d['CO2Emissions'], l2) or removeOutliers.isOutlier(d['EnergyIntensity'], l3) or removeOutliers.isOutlier(d['EnergyUse'], l4) or removeOutliers.isOutlier(d['GDPperCapita'], l5) or removeOutliers.isOutlier(d['HDI'], l6) or removeOutliers.isOutlier(d['Population'], l7):
                continue
            else:
                entry = {'CarbonIntensity':d['CarbonIntensity'], 'CO2Emissions':d['CO2Emissions'], 'EnergyIntensity':d['EnergyIntensity'], 'EnergyUse':d['EnergyUse'], 'GDPperCapita':d['GDPperCapita'], 'HDI': d['HDI'], 'Population':d['Population']}
                res = repo.angelay.clean2012.insert_one(entry)
 
        endTime = datetime.datetime.now()
        return {"Start ":startTime, "End ":endTime}
            

            
    @staticmethod

    def isOutlier(item, list):
        l = sorted(list)
        iq1 = int(len(l) * 0.25)
        iq3 = int(len(l) * 0.75)
        q1 = l[iq1]
        q3 = l[iq3]
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        return item < low or item > high

    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('angelay', 'angelay')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('ang', 'http://datamechanics.io/data/angelay/')

        this_script = doc.agent('dat:angelay#removeOutliers', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        removeOutliers = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime, {'prov:label':'Remove Outliers from Merged 2012 Data', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(removeOutliers, this_script)
        
        resource_all2012 = doc.entity('dat:angelay#all2012', {'prov:label':'All Data from 2012', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        doc.usage(removeOutliers, resource_all2012, startTime)

        clean2012 = doc.entity('dat:angelay#clean2012', {'prov:label':'All Data from 2012 with Outliers Removed', prov.model.PROV_TYPE:'ont:Dataset'})

        doc.wasAttributedTo(clean2012, this_script)
        doc.wasGeneratedBy(clean2012, removeOutliers, endTime)
        doc.wasDerivedFrom(clean2012, resource_all2012, removeOutliers, removeOutliers, removeOutliers)

        repo.logout()

        return doc

#merge2012.execute()

## Generic interface handling basic Qualtrics API operations
## Author: Alex Kindel
## Date: 2 December 2015

import sys
import os.path
import json
import csv
import urllib2
import time
import StringIO as sio
import zipfile as z
import datetime as dt
from datetime import timedelta
from string import Template
from collections import OrderedDict, defaultdict

class QualtricsInterface(object):
    '''
    Interface to a Qualtrics survey. Contains raw JSON with survey data as well
    as a schema mapping Qualtrics Qx keys to Podio external_id values.
    '''

    def __init__(self, surveyID, schema):
        '''
        Takes a surveyID from Qualtrics and a local schema file.
        '''
        # Fetch Qualtrics token
        tokenFile = os.path.expanduser("~") + '/.ssh/qualtrics_token'
        if not os.path.isfile(tokenFile):
            sys.exit("Token file not found: " + tokenFile)
        with open(tokenFile, 'r') as f:
            self.token = f.readline().rstrip()

        # Load schema and raw data
        self.data = self.__extract(surveyID)
        self.transform = self.__transform(schema)

    def __extract(self, surveyID):
        '''
        Pull PRF/CRF form data down from Qualtrics. From qualtrics_etl.
        Only requests responses that are less than one day old.
        Returns JSON object containing untransformed survey data.
        '''
        today = dt.datetime.today()
        yesterday = today - timedelta(days=1)
        date = "%d-%d-%d" % (yesterday.year, yesterday.month, yesterday.day) # Responses should be <=1 day old

        urlTemp = Template("https://dc-viawest.qualtrics.com:443/API/v1/surveys/${svid}/responseExports?apiToken=${tk}&fileType=JSON&startDate=${dt}+06:00:00")
        reqURL = urlTemp.substitute(svid=surveyID, tk=self.token, dt=date)
        req = json.loads(urllib2.urlopen(reqURL).read())

        statURL = req['result']['exportStatus'] + "?apiToken=" + self.token
        percent = 0
        tries = 0
        while percent != 100 and tries < 20:
            time.sleep(5) # Wait 5 seconds between attempts to acquire data
            try:
                stat = json.loads(urllib2.urlopen(statURL).read())
                percent = stat['result']['percentComplete']
            except:
                print "Extractor recovered from HTTP error."
                continue
            finally:
                tries += 1
        if tries >= 20:
            print "Survey %s timed out." % surveyID
            return None

        dataURL = stat['result']['fileUrl']
        remote = urllib2.urlopen(dataURL).read()
        dataZip = sio.StringIO(remote)
        archive = z.ZipFile(dataZip, 'r')
        dataFile = archive.namelist()[0]
        data = json.loads(archive.read(dataFile), object_pairs_hook=OrderedDict)

        if not data['responses']:
            return None
        else:
            return data

    def __transform(self, schema):
        '''
        Build schema for loading data to Podio.
        '''
        # Set up transformed dictionary
        transforms = defaultdict(list)

        schema_dir = os.path.expanduser('~') + schema

        # Build schema in Podio API format
        with open(schema_dir, 'rU') as schema_map:
            for line in csv.reader(schema_map):
                pod_id, qual_id, qual_type = line
                field = {
                    'external_id': pod_id,
                    'values': [
                        {'value': (qual_id, qual_type)}
                    ]
                }
                transforms['fields'].append(field)

        return transforms


    def export(self):
        '''
        Exposes parsed survey data and transform schema.
        '''
        return self.data, self.transform

    def inspect(self):
        '''
        Inspect parsed survey and schema.
        '''
        print json.dumps(self.data, indent=4)
        print json.dumps(self.transform, indent=4)



if __name__ == '__main__':
    qi = QualtricsInterface('SV_54KM0OWIySmH1HL', '/code/qualpod/integrations/lx_events/lx_schema.csv')
    qi.inspect()

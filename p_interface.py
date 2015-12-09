## Generic interface handling basic Podio API operations
## Author: Alex Kindel
## Date: 2 December 2015

import sys
import os.path
import json
import ConfigParser
from pypodio2 import api

class PodioInterface(object):

    def __init__(self, path):
        '''
        Loads Podio API credentials from user-specified location.
        '''
        # TODO: This should be automatic from .ssh and get the app # from user
        cfg = ConfigParser.RawConfigParser()
        home = os.path.expanduser('~')
        cfg.read(home + path)
        self.etl = cfg.get('APIKey', 'etl') # api app id
        self.key = cfg.get('APIKey', 'key') # api key
        self.app = int(cfg.get('APIKey', 'app')) # podio internal app id
        self.usr = cfg.get('PodioUser', 'p_user') # podio username
        self.pwd = cfg.get('PodioUser', 'p_pass') # password

    def load(self, data, transform):
        '''
        Load given data according to transform specification to Podio.
        '''
        # Initialize Podio API
        c = api.OAuthClient(self.etl, self.key, self.usr, self.pwd)
        status = 0

        # Read data from JSON into dict based on pre-defined schema
        for obj in data['responses']:
            item = transform.copy()
            print json.dumps(item, indent=4)
            for field in item['fields']:
                q_id, q_type, default = field['values'][0]['value']
                if q_type == 'text':
                    field['values'][0]['value'] = """%s""" % obj.pop(q_id, default)
                    if len(field['values'][0]['value']) < 1:
                        field['values'][0]['value'] = 'NA'
                # elif q_type == 'category':
                #     pass #TODO: implement
                else:
                    print "%s data type not supported. Excluding %s." % (q_type, q_id)
                    field['values'][0]['value'] = "Not implemented"

            # Make a new Podio item and load new object
            try:
                c.Item.create(self.app, item)
                status += 1
            except:
                continue

        # Return count of loaded objects
        return status


    def inspect(self, itemID):
        '''
        Inspect a given Podio item.
        '''
        c = api.OAuthClient(self.etl, self.key, self.usr, self.pwd)
        obj = c.Item.find(itemID)
        print json.dumps(obj, indent=4)



if __name__ == '__main__':
    pi = PodioInterface('/.ssh/lx.cfg')
    pi.inspect(352648870)

## Generic interface handling basic Podio API operations
## Author: Alex Kindel
## Date: 2 December 2015

import sys
import os.path
import json
import ConfigParser
from pypodio2 import api

class PodioInterface(object):

    def __init__(self, app_id):
        '''
        Loads Podio API credentials from user-specified location.
        '''
        # TODO: This should be automatic from .ssh and get the app # from user
        cfg = ConfigParser.RawConfigParser()
        path = os.path.expanduser('~') + "/.ssh/podio.cfg"
        cfg.read(path)
        self.etl = cfg.get('APIKey', 'etl') # api app id
        self.key = cfg.get('APIKey', 'key') # api key
        self.app = int(app_id)
        self.usr = cfg.get('PodioUser', 'p_user') # podio username
        self.pwd = cfg.get('PodioUser', 'p_pass') # password

    def load(self, data, transform):
        '''
        Load given data according to transform specification to Podio.
        '''
        # Initialize Podio API
        c = api.OAuthClient(self.etl, self.key, self.usr, self.pwd)
        status = 0

        print json.dumps(data, indent=4)

        # Read data from JSON into dict based on pre-defined schema
        for obj in data['responses']:
            item = { 'fields': [] }
            for idx, field in enumerate(transform['fields']):

                new_field = { 'external_id': field['external_id'], 'values': [] }
                value = None

                q_id, q_type, default = field['values'][0]['value']

                if q_type == 'text':
                    value = """%s""" % obj.pop(q_id, default)
                    if len(value) < 1:
                        value = '<not entered>'
                    new_field['values'].append( {'value': value})

                elif q_type == 'category':
                    try:
                        value = int(obj.pop(q_id, default))
                    except ValueError:
                        value = int(default)
                    new_field['values'].append( {'value': value})

                elif q_type == 'multiple':
                    val_arr = []
                    qz, parts = q_id.split('~')
                    for part in range(1, int(parts)):
                        qid_part = "%s_%d" % (qz, part)
                        active = obj.pop(qid_part)
                        if active:
                            new_field['values'].append( {'value': part} )

                elif q_type == 'link':
                    url = obj.pop(q_id)
                    if not url:
                        continue
                    embed = { 'url': url }
                    linkobj = c.Embed.create(embed)
                    link_id = linkobj['embed_id']
                    new_field['values'].append({ 'embed': link_id })

                elif q_type == 'date':
                    datestr = obj.pop(q_id).replace('/','-')+" 00:00:00"
                    new_field['values'].append({ 'start': datestr })

                else:
                    print "'%s' data type not supported. Excluding %s." % (q_type, q_id)
                    continue

                # Construct new item
                item['fields'].append(new_field)

            print json.dumps(item, indent=4)

            # Make a new Podio item and load new object
            try:
                c.Item.create(self.app, item)
                status += 1
            except Exception as e:
                print e
                print "Item failed."
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
    pi = PodioInterface(14384887)
    pi.inspect(354830967)

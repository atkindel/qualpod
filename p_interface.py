## Generic interface handling basic Podio API operations
## Author: Alex Kindel
## Date: 2 December 2015

import sys
import os.path
import json
import ConfigParser
import csv
from pypodio2 import api

class PodioInterface(object):

    def __init__(self, app_id, def_labels):
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
        self.labels = self.__setDefaults(def_labels)

    def __setDefaults(self, default_labels):
        retdict = {}
        rd = csv.reader(open(os.path.expanduser('~') + default_labels, 'rU'))
        for row in rd:
            retdict[row[0]] = row[1]
        return retdict

    def load(self, data, transform):
        '''
        Load given data according to transform specification to Podio.
        '''
        # Initialize Podio API
        c = api.OAuthClient(self.etl, self.key, self.usr, self.pwd)
        status = 0

        # Read data from JSON into dict based on pre-defined schema
        for obj in data['responses']:
            item = { 'fields': [] }
            for idx, field in enumerate(transform['fields']):

                new_field = { 'external_id': field['external_id'], 'values': [] }
                value = None

                q_id, q_type = field['values'][0]['value']

                if q_type == 'text':
                    value = """%s""" % obj.pop(q_id, "NA")
                    if len(value) < 1:
                        continue
                    new_field['values'].append( {'value': value})

                elif q_type == 'category':
                    try:
                        value = int(obj.pop(q_id, 1))
                    except ValueError:
                        continue
                    new_field['values'].append( {'value': value})

                elif q_type == 'multiple':
                    val_arr = []
                    qz, parts = q_id.split('~')
                    for part in range(1, int(parts)):
                        qid_part = "%s_%d" % (qz, part)
                        active = obj.pop(qid_part, False)
                        if active:
                            new_field['values'].append( {'value': part} )

                elif q_type == 'multitext':
                    val_field = "<p>"
                    qz, parts = q_id.split('~')
                    text_fields = map(int, parts.split('-'))
                    for part in text_fields:
                        qid_part = "%s_%d_TEXT" % (qz, part)
                        datum = obj.pop(qid_part, False)
                        if datum:
                            val_field += "%s<br/>" % datum
                    val_field += "</p>"
                    new_field['values'].append( {'value': val_field})

                elif q_type == 'link':
                    url = obj.pop(q_id)
                    if not url:
                        continue
                    embed = { 'url': url }
                    try:
                        linkobj = c.Embed.create(embed)
                    except:
                        print "Invalid URL"
                        continue
                    link_id = linkobj['embed_id']
                    new_field['values'].append({ 'embed': link_id })

                elif q_type == 'date':
                    datestr = obj.pop(q_id).replace('/','-')+" 00:00:00"
                    new_field['values'].append({ 'start': datestr })

                elif q_type == 'default':
                    def_field = "<p>"
                    for question in obj.keys():
                        if question[0] != 'Q':
                            continue
                        val = obj.pop(question)
                        if len(val) < 2:
                            continue
                        if question in self.labels.keys():
                            question = self.labels[question]
                        else
                            continue
                        def_field += "<b>%s</b>: %s<br/>" % (question, val)
                    def_field += "</p>"
                    new_field['values'].append( {'value': def_field} )

                else:
                    print "'%s' data type not supported. Excluding %s." % (q_type, q_id)
                    continue

                # Construct new item
                item['fields'].append(new_field)

            # Make a new Podio item and load new object
            try:
                print json.dumps(item, indent=4)
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
    pi = PodioInterface(14384887, '/code/qualpod/integrations/lx_events/lx_default_labels.csv')
    pi.inspect(357244207)

## Integration service pushing Qualtrics survey results to Podio.
## Author: Alex Kindel
## Date: 8 December 2015

import csv
import os.path
import datetime

from p_interface import PodioInterface
from q_interface import QualtricsInterface

class QualtricsPodioIntegration(object):

    def __init__(self, manifest):
        '''
        Loads a manifest file mapping integration names, Qualtrics surveys,
        Podio app credentials, CSV transform schemata, and integration log files.
        '''
        self.integrations = []
        manifest = os.path.expanduser('~') + manifest
        with open(manifest, 'rU') as integrations:
            for line in csv.reader(integrations):
                self.integrations.append(line)

    def run(self):
        '''
        For each mapping between survey/app/schema, instantiate interfaces to
        Qualtrics and Podio and integrate data.
        '''
        now = datetime.datetime.today()
        timestamp = "%d-%d-%d %d:%d:%d" % (now.year, now.month, now.day,
                                           now.hour, now.minute, now.second)

        for label, survey, app, schema, log in self.integrations:
            data = None
            status = None
            with open(log, 'a') as logfile:
                # Instantiate interfaces and integrate, logging failures as needed
                try:
                    qualtrics = QualtricsInterface(survey, schema)
                    data, transform = qualtrics.export()
                except Exception as e:
                    logfile.write("[%s][%s]: %s\n" % (timestamp, label, repr(e)))
                    continue

                logfile.write("[%s][%s]: Qualtrics data extracted.\n" % (timestamp, label))

                try:
                    podio = PodioInterface(app)
                    status = podio.load(data, transform)
                except Exception as e:
                    logfile.write("[%s][%s]: %s\n" % (timestamp, label, repr(e)))
                    continue

                logfile.write("[%s][%s]: %d items loaded to Podio.\n" % (timestamp, label, status))

                logfile.write("\n")


if __name__ == '__main__':
    qpi = QualtricsPodioIntegration("/code/qualpod/integrations/vptl_integrations.csv")
    qpi.run()

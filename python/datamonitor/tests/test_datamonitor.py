from unittest import TestCase
from datamonitor.datamonitor import DataMonitor
from elasticmock import elasticmock

class DataMonitoringTest(TestCase):
    @elasticmock
    def test_should_connect_and_send_object(self):
        # Create an empty Datamonitor class instance
        dm = DataMonitor()

        # Connect to Elasticsearch (ES)
        es_conn = {'host': 'localhost', 'port': 9200, 'scheme': 'http'}
        dm.es_connect(es_conn)
        
        # Debug
        print(f"DataMonitor class instance: {dm}")
    
        # Send some simple payload to ES
        meta_data = {'unit': 'nb_of_rows', 'value': 6543}
        es_index = 'dm-test-v0'
        res = dm.es_send(es_index, meta_data)
        self.assertIsNotNone(res)
        
        # Debug
        print(f"Result of sending to ES: {res}")

from unittest import TestCase
from datamonitor.datamonitor import DataMonitor
from elasticmock import elasticmock

class  DataMonitoringTest(TestCase):
    
    @elasticmock
    def test_should_connect_and_send_object(self):
        # Variables used to test
        es_conn = {'host': 'localhost', 'port': 9200, 'scheme': 'http'}
        meta_data = {'unit': 'nb_of_rows', 'value': 6543}
        es_index = 'dm-test-v0'
        
        # Create instance 
        dm = DataMonitor()
        
        # Debug
        print(f"DataMonitor class instance: {dm}")
        
        # Connect to Elasticsearch (ES), elasticmock
        res = dm.es_connect(es_conn)
        
        # Debug
        print(f"Result of sending to ES: {res}")
        
        # Send some simple payload to ES
        #res_2 = dm.es_send(es_index, meta_data)
        
        # Debug
        #print(f"Result of sending to ES: {res_2}")

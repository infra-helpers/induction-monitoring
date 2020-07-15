# -*- coding: utf-8 -*-
#
# Source: https://github.com/infra-helpers/induction-monitoring/blob/master/python/datamonitor//test_datamonitor.py
#
# Authors: Denis Arnaud, Michal Mendrygal
#

from unittest import TestCase

from elasticmock import elasticmock

from datamonitor import DataMonitor


class DataMonitoringTest(TestCase):

    @elasticmock
    def test_should_connect_and_send_object(self):
        # Variables used to test
        es_conn_str = {'host': 'localhost', 'port': 9200, 'scheme': 'http'}
        expected_document = {'unit': 'nb_of_rows', 'value': '6543'}
        es_index = 'dm-test-v0'

        # Create instance
        dm = DataMonitor()
        dm.set_log_level(4)

        # Connect to Elasticsearch (ES), mocked by elasticmock here
        es_conn = dm.es_connect(es_conn_str)

        # Debug
        print(f"Connection handle for the ES cluster: {es_conn}")

        # Get the details of the ES cluster
        es_info = dm.es_info()

        # Debug
        print(f"Details for the ES cluster: {es_info}")

        # Send some simple payload to ES
        docid = dm.es_send(index=es_index, payload=expected_document)

        # Debug
        print(f"Document ID, as provided by ES: {docid}")

        # ES should return the document ID, as provided by ES
        self.assertIsNotNone(docid)

        # Extract back the same paylod from ES
        document_str = dm.es_get(index=es_index, docid=docid)
        document = None
        if '_source' in document_str:
            document = document_str['_source']

        # Debug
        print(f"Document retrieved from ES: {document} (from ES answer: {document_str})")
        print(f"Document initially sent to ES: {expected_document}")

        # The document retrieved from ES should be equal to the one
        # originally sent in the step above
        self.assertEqual(expected_document, document)

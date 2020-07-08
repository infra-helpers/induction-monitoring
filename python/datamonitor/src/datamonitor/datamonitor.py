# -*- coding: utf-8 -*-
#
# Source: https://github.com/infra-helpers/induction-monitoring/blob/master/python/datamonitor/src/datamonitor/DataMonitor.py
#
#
from elasticsearch import Elasticsearch
import bz2
from itertools import (takewhile, repeat)
from elasticmock import elasticmock

class DataMonitor:
    """
    Helper class with a few utility methods supporting collecting KPIs
    (Key Performance Indicators) from data files and monitoring those KPI
    on tools like Elasticsearch (ES) service.

    Technically, the KPIs collected from data are meta-data.
    """
    def __init__(self):
        self.es_host = 'localhost'
        self.es_port = 9200
        self.es_scheme = 'http'
        self.es_user = None
        self.es_pass = None
        self.es_auth = None
        self.es_url = None
        self.es_conn = None

    def __str__(self):
        """Description of the DataMonitor instance"""
        desc = f"DataMonitor - ES URL: {self.es_url}"
        return desc
    
    @elasticmock
    def es_connect(self, conn=dict()):
        """Create and store a connection to an Elasticsearch (ES) service"""
        if 'host' in conn:
            self.es_host = conn['host']

        if 'port' in conn:
            self.es_port = conn['port']

        if 'scheme' in conn:
            self.es_scheme = conn['scheme']

        if 'user' in conn:
            self.es_user = conn['user']

        if 'passwd' in conn:
            self.es_pass = conn['passwd']

        self.es_auth = f"{self.es_user}@" if self.es_user else ""

        self.es_url = f"{self.es_scheme}://{self.es_auth}{self.es_host}:{self.es_port}/"

        if self.es_user:
            self.es_conn = Elasticsearch(hosts=self.es_host,
                                         http_auth=(self.es_user,
                                                    self.es_pass),
                                         scheme=self.es_scheme,
                                         port=self.es_port)
        else:
            self.es_conn = Elasticsearch(hosts=self.es_host,
                                         scheme=self.es_scheme,
                                         port=self.es_port)
    
    @elasticmock
    def es_send(self, index=None, payload=dict()):
        """Send a JSON payload to an Elasticsearch (ES) service"""
        if not index:
            raise Exception("An Elasticsearch (ES) index should be speficied")

        res = self.es_conn.index(index=index, doc_type='_doc', body=payload)

        # Debug
        print(f"Sent to {self.es_url}/{index}: {payload}")

        #
        return res

    def calculate_nb_of_rows_in_file(filepath):   
        """
        Count the number of lines in a text file.
        Inspired from https://stackoverflow.com/a/27518377/798053
        """
        bufgen = None
        with bz2.open (filepath, 'rb') as f:
            bufgen = takewhile(lambda x: x, (f.read(1024*1024) for _ in repeat(None)))
            return sum (buf.count(b'\n') for buf in bufgen)

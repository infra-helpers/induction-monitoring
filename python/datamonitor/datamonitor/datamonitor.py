# -*- coding: utf-8 -*-
#
# Source: https://github.com/infra-helpers/induction-monitoring/blob/master/python/datamonitor/datamonitor/DataMonitor.py
#
# Authors: Denis Arnaud, Michal Mendrygal
#

import bz2
import inspect
import os
from itertools import repeat
from itertools import takewhile

import elasticsearch


class DataMonitor():
    """
    Helper class with a few utility methods supporting collecting KPIs
    (Key Performance Indicators) from data files and monitoring those KPI
    on tools like Elasticsearch (ES) service.
    Technically, the KPIs collected from data are meta-data.

    Log levels: 1. Critical; 2. Errors; 3: Warnings; 4: Info; 5: Verbose
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
        self.log_level = 2

    def __str__(self):
        """
        Description of the DataMonitor instance
        """
        desc = f"DataMonitor - ES URL: {self.es_url}"
        return desc

    def set_log_level(self, level=2):
        """
        Set the log level
        """
        try:
            level_int = int(level)
            self.log_level = level_int if level_int >= 1 and level_int <= 5 else self.log_level
        except ValueError as verr:
            log_pfx = self.get_log_pfx()
            print(f"{log_pfx} ERROR - The log level parameter should be an integer between 1 and 5; it is currently {level} - {verr}")
            pass

    def get_log_pfx(self):
        """
        Derive a prefix for logging purpose
        """
        # 0 represents this line
        # 1 represents line at caller
        callerframerecord = inspect.stack()[1]

        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        filename = os.path.basename(info.filename)
        log_pfx = f"[DM][{filename}][{info.function}][{info.lineno}] -"
        return log_pfx

    def es_connect(self, conn=dict()):
        """
        Create and store a connection to an Elasticsearch (ES) service
        """
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

        self.es_url = f"{self.es_scheme}://{self.es_auth}{self.es_host}:{self.es_port}"

        if self.es_user:
            self.es_conn = elasticsearch.Elasticsearch(hosts=[self.es_host],
                                                       scheme=self.es_scheme,
                                                       port=self.es_port,
                                                       http_auth=(self.es_user,
                                                                  self.es_pass))
        else:
            self.es_conn = elasticsearch.Elasticsearch(hosts=[self.es_host],
                                                       scheme=self.es_scheme,
                                                       port=self.es_port)

        return self.es_conn

    def es_info(self):
        """
        Get the ES cluster information
        """
        es_info = self.es_conn.info()

        # Debug
        if self.log_level >= 4:
            log_pfx = self.get_log_pfx()
            print(f"{log_pfx} Details for the ES cluster ({self.es_url}): {es_info}")

        #
        return es_info

    def es_send(self, index=None, payload=dict()):
        """
        Send a JSON payload to an Elasticsearch (ES) service
        """
        doc_id = None

        if not index:
            raise Exception("An Elasticsearch (ES) index should be specified")

        doc_creation_details = self.es_conn.index(index=index, doc_type='_doc',
                                                  body=payload)
        if '_id' in doc_creation_details:
            doc_id = doc_creation_details['_id']

        # Debug
        if self.log_level >= 4:
            log_pfx = self.get_log_pfx()
            print(f"{log_pfx} Doc sent to ES ({self.es_url}/{index}) was assigned {doc_id} as doc ID")
            print(f"{log_pfx} Doc creation structure: {doc_creation_details} - Sent doc: {payload}")

        #
        return doc_id

    def es_get(self, index=None, docid=None):
        """
        Get a JSON payload from an Elasticsearch (ES) service
        """
        if not index:
            raise Exception("An Elasticsearch (ES) index should be specified")

        if not docid:
            raise Exception("An Elasticsearch (ES) document ID should be specified")

        doc_str = self.es_conn.get(index=index, id=docid)

        # Debug
        if self.log_level >= 4:
            log_pfx = self.get_log_pfx()
            print(f"{log_pfx} Got from ES ({self.es_url}/{index} for ID={docid}): {doc_str}")

        #
        return doc_str

    def calculate_nb_of_rows_in_file(self,filepath):
        """
        Count the number of lines in a text file.
        Inspired from https://stackoverflow.com/a/27518377/798053
        """

        bufgen = None
        with bz2.open(filepath, 'rb') as f:
            bufgen = takewhile(lambda x: x,
                               (f.read(1024 * 1024) for _ in repeat(None)))
            return sum(buf.count(b'\n') for buf in bufgen)

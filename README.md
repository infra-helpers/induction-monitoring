Induction to Monitoring
=======================

# References
* [Prometheus](https://prometheus.io/)
* [ElasticSearch](https://elasitc.co) stacks:
  + [EFK (ElasticSearch, Fluentd, Kibana](https://docs.fluentd.org/v/0.12/articles/docker-logging-efk-compose)
  + [Kibana](https://www.elastic.co/products/kibana)
  + [Fluentd](https://www.fluentd.org/)
* [Indexing your CSV files with Elasticsearch Ingest Node](https://www.elastic.co/blog/indexing-csv-elasticsearch-ingest-node)
* [Elasticsearch geo-point](https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html)
* [Elasticsearch - Grok processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/grok-processor.html)
* [Elasticsearch - Populate](https://www.tutorialspoint.com/elasticsearch/elasticsearch_populate.htm)
* [How to install Python virtual environments with Pyenv and `pipenv`](http://github.com/machine-learning-helpers/induction-python/tree/master/installation/virtual-env)

# Overview
[That repository](https://github.com/infra-helpers/induction-monitoring) aims
at providing end-to-end examples introducing how to collect, store
and query metering events, produced by different sensors
on local as well as on clouds.

Although the software stacks are very similar with logging,
the purpose is different. See the
[GitHub repository dedicated to logging](https://github.com/infra-helpers/induction-logging)
for further details.

## Endpoints
* ElasticSearch (ES): http://localhost:9200
* Kibana:
  + http://localhost:5601
  + Index manageement:
    - Indices: http://localhost:5601/app/kibana#/management/elasticsearch/index_management/indices
	- Index templates: http://localhost:5601/app/kibana#/management/elasticsearch/index_management/templates
  + DevTool console: http://localhost:5601/app/kibana#/dev_tools/console

# Configuration

* Setup Kibana to disallow the read-only mode:
```bash
$ curl -XPUT "http://localhost:9200/.kibana/_settings" -H "Content-Type: application/json" --data "@elasticseearch/settings/kibana-read-only.json"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    89  100    21  100    68    265    860 --:--:-- --:--:-- --:--:--  1126
{
  "acknowledged": true
}
$ curl -XPUT "http://localhost:9200/subway_info_v1/_settings" -H "Content-Type: application/json" --data "@elasticseearch/settings/kibana-read-only.json"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    89  100    21  100    68    106    345 --:--:-- --:--:-- --:--:--   451
{
  "acknowledged": true
}
```

* Check the Kibana settings:
```bash
$ curl -XGET "http://localhost:9200/.kibana/_settings"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   304  100   304    0     0  13217      0 --:--:-- --:--:-- --:--:-- 13217
{
  ".kibana_1": {
    "settings": {
      "index": {
        "number_of_shards": "1",
        "auto_expand_replicas": "0-1",
        "blocks": {
          "read_only_allow_delete": "false"
        },
        "provided_name": ".kibana_1",
        "creation_date": "1582893825396",
        "number_of_replicas": "0",
        "uuid": "vXk2I7kXQOerlcnAbqlggQ",
        "version": {
          "created": "7060099",
          "upgraded": "7060199"
        }
      }
    }
  }
}
$ curl -XGET "http://localhost:9200/subway_info_v1/_settings"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   285  100   285    0     0  47500      0 --:--:-- --:--:-- --:--:-- 47500
{
  "subway_info_v1": {
    "settings": {
      "index": {
        "number_of_shards": "1",
        "blocks": {
          "read_only_allow_delete": "false"
        },
        "provided_name": "subway_info_v1",
        "creation_date": "1582928134403",
        "number_of_replicas": "1",
        "uuid": "GaFWZIFhSDO6iPOsPkNtCw",
        "version": {
          "created": "7060099",
          "upgraded": "7060199"
        }
      }
    }
  }
}
```

## Grok processor
* List the patterns of the Grok processor:
```bash
$ curl -XGET "http://localhost:9200/_ingest/processor/grok/" |jq
{
  "patterns": {
    "BACULA_CAPACITY": "%{INT}{1,3}(,%{INT}{3})*",
    "PATH": "(?:%{UNIXPATH}|%{WINPATH})",
 ...
    "DATA": ".*?", 
 ...
    "NUMBER": "(?:%{BASE10NUM})", 
 ...
    "WORD": "\\b\\w+\\b", 
 ...
    "CATALINALOG": "%{CATALINA_DATESTAMP:timestamp} %{JAVACLASS:class} %{JAVALOGMESSAGE:logmessage}"
  }
}
```

* There is a Grok processing simulator in the Kibana DevTool console:
  http://localhost:5601/app/kibana#/dev_tools/grokdebugger
  + Sample data:
```csv
BMT,4 Avenue,25th St,40.660397,-73.998091,R,,,,,,,,,,,Stair,YES,,YES,NONE,,FALSE,,FALSE,4th Ave,25th St,SW,40.660489,-73.99822
```
  + Grok pattern:
```text
%{WORD:division},%{DATA:line},%{DATA:station_name},%{NUMBER:location.lat},%{NUMBER:location.lon},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA:entrance_type},%{DATA:entry},%{DATA:exit_only},%{DATA:vending},%{DATA:staffing},%{DATA:staff_hours},%{DATA:ada},%{DATA:ada_notes},%{DATA:free_crossover},%{DATA:north_south_street},%{DATA:east_west_street},%{DATA:corner},%{NUMBER:entrance.lat},%{NUMBER:entrance.lon}

```

# Build a CSV to JSON pipeline

## School data

* Create the `school` index:
```bash
$ curl -XPUT "http://localhost:9200/school"
```
```javascript
{
  "acknowledged": true,
  "shards_acknowledged": true,
  "index": "school"
}
```

* Insert a first entry:
```bash
$ curl -XPOST "http://localhost:9200/school/_doc/10" -H "Content-Type: application/json" -d'{ "name":"Saint Paul School", "description":"ICSE Afiliation", "street":"Dawarka", "city":"Delhi", "state":"Delhi", "zip":"110075", "location":[28.5733056, 77.0122136], "fees":5000, "tags":["Good Faculty", "Great Sports"], "rating":"4.5" }' | jq
```
```javascript
{
  "_index": "school",
  "_type": "_doc",
  "_id": "10",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 0,
  "_primary_term": 1
}
```

* Insert a second record:
```bash
$ curl -XPOST "http://localhost:9200/school/_doc/16" -H "Content-Type: application/json" -d'{ "name":"Crescent School", "description":"State Board Affiliation", "street":"Tonk Road", "city":"Jaipur", "state":"RJ", "zip":"176114","location":[26.8535922,75.7923988], "fees":2500, "tags":["Well equipped labs"], "rating":"4.5" }'
```
```javascript
{
  "_index": "school",
  "_type": "_doc",
  "_id": "16",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 1,
  "_primary_term": 1
}
```

* Check the content of the `school` index:
```bash
$ curl -XGET "http://localhost:9200/school/" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   963  100   963    0     0  53500      0 --:--:-- --:--:-- --:--:-- 53500
```
```javascript
{
  "school": {
    "aliases": {},
    "mappings": {
      "properties": {
        "city": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "description": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "fees": {
          "type": "long"
        },
        "location": {
          "type": "float"
        },
        "name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "rating": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "state": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "street": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "tags": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "zip": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      }
    },
    "settings": {
      "index": {
        "creation_date": "1582925740110",
        "number_of_shards": "1",
        "number_of_replicas": "1",
        "uuid": "bFxqVAe5TbiV6-3ijh7hGg",
        "version": {
          "created": "7060099"
        },
        "provided_name": "school"
      }
    }
  }
}
```

## New York
* Create the `subway_info_v1` index:
```bash
$ curl -XPUT "http://localhost:9200/subway_info_v1" -H "Content-Type: application/json" --data "@elasticseearch/data/NYC_Index.json" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   809  100    73  100   736     36    370  0:00:02  0:00:01  0:00:01   406
```
```javascript
{
  "acknowledged": true,
  "shards_acknowledged": true,
  "index": "subway_info_v1"
}
```

* Check the index:
  + In the Kibana console: http://localhost:5601/app/kibana#/management/elasticsearch/index_management/indices
  + In the CLI:
```bash
$ curl -XGET "http://localhost:9200/subway_info_v1" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   756  100   756    0     0  54000      0 --:--:-- --:--:-- --:--:-- 54000
```
```javascript
{
  "subway_info_v1": {
    "aliases": {},
    "mappings": {
      "properties": {
        "station_name": {
          "type": "text"
        },
        "east_west_street": {
          "type": "text"
        },
        "line": {
          "type": "text"
        },
        "vending": {
          "type": "text"
        },
        "staffing": {
          "type": "text"
        },
        "division": {
          "type": "keyword"
        },
        "entry": {
          "type": "text"
        },
        "exit_only": {
          "type": "text"
        },
        "corner": {
          "type": "text"
        },
        "north_south_street": {
          "type": "text"
        },
        "location": {
          "type": "geo_point"
        },
        "entrance": {
          "type": "geo_point"
        },
        "entrance_type": {
          "type": "text"
        },
        "ada_notes": {
          "type": "text"
        },
        "free_crossover": {
          "type": "text"
        },
		"ada": {
          "type": "text"
        },
        "staff_hours": {
          "type": "text"
        }
      }
    },
    "settings": {
      "index": {
        "creation_date": "1584483493748",
        "number_of_shards": "1",
        "number_of_replicas": "1",
        "uuid": "Jef7f_ijRF-t_khE8hKjag",
        "version": {
          "created": "7060199"
        },
        "provided_name": "subway_info_v1"
      }
    }
  }
}
```

* On single-node installations (e.g., on a laptop), the health sttatus
  of the index will appear as yellow, as the number of replicas is set
  by default to 1, which cannot be satisfied with a single node.
  The solution is to edit the settings of the index (_e.g._, frm the
  [Kibana console](http://localhost:5601/app/kibana#/management/elasticsearch/index_management/indices))
  and set the `number_of_replicas` field to 0.
```bash
$ curl -XGET "http://localhost:9200/subway_info_v1/_settings/" | jq '.subway_info_v1.settings.index.number_of_replicas'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   220  100   220    0     0   9565      0 --:--:-- --:--:-- --:--:--  9565
```
```javascript
"0"
```

* Simulate the targetted pipeline:
```bash
$ curl -XPOST "http://localhost:9200/_ingest/pipeline/_simulate" -H "Content-Type: application/json" --data "@elasticseearch/data/NYC_Grok_Processor.json"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1558  100   547  100  1011   2111   3903 --:--:-- --:--:-- --:--:--  6015
```
```javascript
{
  "docs": [
    {
      "doc": {
        "_index": "subway_info",
        "_type": "station",
        "_id": "AVvJZVQEBr2flFKzrrkr",
        "_source": {
          "station_name": "25th St",
          "east_west_street": "25th St",
          "line": "4 Avenue",
          "vending": "YES",
          "staffing": "NONE",
          "division": "BMT",
          "entry": "YES",
          "exit_only": "",
          "corner": "SW",
          "north_south_street": "4th Ave",
          "location": {
            "lon": "-73.998091",
            "lat": "40.660397"
          },
          "entrance": {
            "lon": "-73.99822",
            "lat": "40.660489"
          },
          "entrance_type": "Stair",
          "ada_notes": "",
          "free_crossover": "FALSE",
          "staff_hours": "",
          "ada": "FALSE"
        },
        "_ingest": {
          "timestamp": "2020-03-17T20:33:38.724266Z"
        }
      }
    }
  ]
}
```

* Create the index template:
```bash
$ curl -XPUT "http://localhost:9200/_template/nyc_template" -H "Content-Type: application/json" --data "@elasticseearch/data/NYC_Template.json"|jq
{"acknowledged":true}
```

* Check the index template in the Kibana console:
  + http://localhost:5601/app/kibana#/management/elasticsearch/index_management/templates

* Check the index template with the CLI:
```bashs
$ curl -XGET "http://localhost:9200/_template/nyc_template" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   644  100   644    0     0  32200      0 --:--:-- --:--:-- --:--:-- 32200
```
```javascript
{
  "nyc_template": {
    "order": 0,
    "index_patterns": [
      "subway_info*"
    ],
    "settings": {
      "index": {
        "number_of_shards": "1"
      }
    },
    "mappings": {
      "properties": {
        "station_name": {
          "type": "text"
        },
        "east_west_street": {
          "type": "text"
        },
        "line": {
          "type": "text"
        },
        "vending": {
          "type": "text"
        },
        "staffing": {
          "type": "text"
        },
        "division": {
          "type": "keyword"
        },
        "entry": {
          "type": "text"
        },
        "exit_only": {
          "type": "text"
        },
        "corner": {
          "type": "text"
        },
        "north_south_street": {
          "type": "text"
        },
        "location": {
          "type": "geo_point"
        },
        "entrance": {
          "type": "geo_point"
        },
        "entrance_type": {
          "type": "text"
        },
        "ada_notes": {
          "type": "text"
        },
        "free_crossover": {
          "type": "text"
        },
        "ada": {
          "type": "text"
        },
        "staff_hours": {
          "type": "text"
        }
      }
    },
    "aliases": {}
  }
}
```

* Create the pipeline:
```bash
$ curl -XPUT "http://localhost:9200/_ingest/pipeline/parse_nyc_csv" -H "Content-Type: application/json" --data "@elasticseearch/data/NYC_Pipeline.json"|jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   690  100    21  100   669     46   1467 --:--:-- --:--:-- --:--:--  1509
```
```javascript
{
  "acknowledged": true
}
```

* Parser rule and sample data (for reference):
```csv
%{WORD:division},%{DATA:line},%{DATA:station_name},%{NUMBER:location.lat},%{NUMBER:location.lon},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA:entrance_type},%{DATA:entry},%{DATA:exit_only},%{DATA:vending},%{DATA:staffing},%{DATA:staff_hours},%{DATA:ada},%{DATA:ada_notes},%{DATA:free_crossover},%{DATA:north_south_street},%{DATA:east_west_street},%{DATA:corner},%{NUMBER:entrance.lat},%{NUMBER:entrance.lon}
BMT,4 Avenue,25th St,40.660397,-73.998091,R,,,,,,,,,,,Stair,YES,,YES,NONE,,FALSE,,FALSE,4th Ave,25th St,SW,40.660489,-73.99822
```

* Check the pipeline:
```bash
$ curl -XGET "http://localhost:9200/_ingest/pipeline/parse_nyc_csv" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1199  100  1199    0     0  14621      0 --:--:-- --:--:-- --:--:-- 14802
```
```javascript
{
  "parse_nyc_csv": {
    "description": "Parsing the NYC stations",
    "processors": [
      {
        "grok": {
          "field": "station",
          "patterns": [
            "%{WORD:division},%{DATA:line},%{DATA:station_name},%{NUMBER:location.lat},%{NUMBER:location.lon},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA},%{DATA:entrance_type},%{DATA:entry},%{DATA:exit_only},%{DATA:vending},%{DATA:staffing},%{DATA:staff_hours},%{DATA:ada},%{DATA:ada_notes},%{DATA:free_crossover},%{DATA:north_south_street},%{DATA:east_west_street},%{DATA:corner},%{NUMBER:entrance.lat},%{NUMBER:entrance.lon}"
          ]
        }
      },
      {
        "remove": {
          "field": "station"
        }
      }
    ]
  }
}

```

* Ingest the data:
```bash
$ while read f1; do curl -XPOST "http://localhost:9200/subway_info_v1/_doc?pipeline=parse_nyc_csv" -H "Content-Type: application/json" -d "{ \"station\": \"$f1\" }"; done < elasticseearch/data/NYC_Transit_Subway_Entrance_And_Exit_Data.csv | jq
```
```javascript
{
  "_index": "subway_info_v1",
  "_type": "_doc",
  "_id": "iISt6nABC24yNP3yxmvI",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 11,
  "_primary_term": 1
}
...
{
  "_index": "subway_info_v1",
  "_type": "_doc",
  "_id": "04Sv6nABC24yNP3yO3Jd",
  "_version": 1,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 1878,
  "_primary_term": 1
}
```

* Check the index:
```bash
$ curl -XGET "http://localhost:9200/subway_info_v1/_count" | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    74  100    74    0     0   7400      0 --:--:-- --:--:-- --:--:--  8222
```
```javascript
{
  "count": 1879,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  }
```


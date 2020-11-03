Induction to Monitoring - Python
================================

# Table of Content (ToC)
- [Induction to Monitoring - Python](#induction-to-monitoring---python)
- [Table of Content (ToC)](#table-of-content--toc-)
- [Overview](#overview)
- [References](#references)
  * [Python module](#python-module)
  * [Python virtual environments](#python-virtual-environments)
  * [Elasticsearch (ES) Python modules](#elasticsearch--es--python-modules)
    + [Python Elasticsearch client](#python-elasticsearch-client)
    + [Elasticsearch DSL](#elasticsearch-dsl)
    + [ElasticMock](#elasticmock)
- [Installation](#installation)
  * [Clone this Git repository](#clone-this-git-repository)
  * [Python environment](#python-environment)
- [Usage](#usage)
  * [Install the `datamonitor` module](#install-the--datamonitor--module)
    + [Install in the Python user space](#install-in-the-python-user-space)
    + [Installation in a dedicated Python virtual environment](#installation-in-a-dedicated-python-virtual-environment)
  * [Remove any previous document from the ES index](#remove-any-previous-document-from-the-es-index)
  * [Use `datamonitor` from the Command-Line (CLI)](#use--datamonitor--from-the-command-line--cli-)
  * [Use `datamonitor` as a module from another Python program](#use--datamonitor--as-a-module-from-another-python-program)
- [Development / Contribution](#development---contribution)
  * [Test the DataMonitor Python module](#test-the-datamonitor-python-module)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

# Overview
[This README](https://github.com/infra-helpers/induction-monitoring/blob/master/python/README.md)
is part of the
[Induction Monitoring project](https://github.com/infra-helpers/induction-monitoring),
itself aiming at providing end-to-end examples introducing how to collect, store
and query metering events, produced by different sensors on local as well
as on clouds.

The `python/` sub-folder provides a base Python library, namely `datamonitor`,
offering a few methods to collect Key Performance Indicators (KPI) from
data files. Those KPIs are then typically wrapped into JSON structures
and sent to an Elasticsearch (ES) service. The KPIs then form corresponding
time-series, which can be further analyzed with Kibana, or any other analytical
tool, typically for detection of outliers and alert notifications.

# References

## Python module
* GitHub:
  https://github.com/infra-helpers/induction-monitoring/tree/master/python
* PyPi: https://pypi.org/project/datamonitor/
* Read the Docs (RTD):
  https://readthedocs.org/projects/datamonitoring/

## Python virtual environments
* Pyenv and pipenv:
  http://github.com/machine-learning-helpers/induction-python/tree/master/installation/virtual-env

## Elasticsearch (ES) Python modules

### Python Elasticsearch client
* ReadTheDocs (RTD): https://elasticsearch-py.readthedocs.io/en/master/
* PyPi: https://pypi.org/project/elasticsearch
* GitHub: https://github.com/elastic/elasticsearch-py/blob/master/docs/index.rst

### Elasticsearch DSL
* ReadTheDocs (RTD): https://elasticsearch-dsl.readthedocs.io/en/latest/
* PyPi: https://pypi.org/project/elasticsearch-dsl/
* GitHub:
  https://github.com/elastic/elasticsearch-dsl-py/blob/master/docs/index.rst

### ElasticMock
* PyPi: https://pypi.org/project/ElasticMock/
* GitHub: https://github.com/vrcmarcos/elasticmock

# Installation

## Clone this Git repository
```bash
$ mkdir -p ~/dev/infra && \
  git clone git@github.com:infra-helpers/induction-monitoring.git ~/dev/infra/induction-monitoring
$ cd ~/dev/infra/induction-monitoring/python
```

## Python environment

* If not already done so, install `pyenv`, Python 3.8 and, `pip` and `pipenv`
  + PyEnv:
```bash
$ git clone https://github.com/pyenv/pyenv.git ${HOME}/.pyenv
$ cat >> ~/.bashrc << _EOF

# Python
export PYENV_ROOT="\${HOME}/.pyenv"
export PATH="\${PYENV_ROOT}/bin:\${PATH}"
if command -v pyenv 1>/dev/null 2>&1
then
        eval "\$(pyenv init -)"
fi
if command -v pipenv 1>/dev/null 2>&1
then
        eval "\$(pipenv --completion)"
fi

_EOF
$ . ~/.bashrc
$ pyenv install 3.8.3 && pyenv local 3.8.3
$ python3 -m pip install -U pip pipenv
```
  + Python 3.8:
```bash
$ pyenv install 3.8.3
```
  + `pip`:
```bash
$ python3 -m pip install -U pip
```
  + `pipenv`:
```bash
$ python3 -m pip install -U pipenv
```

* For information, the skeleton of that project was created thanks to the
  [Cookiecutter template for Python library](https://github.com/ionelmc/cookiecutter-pylibrary).
  The following was performed once, and it does not need to be ever performed
  again:
```bash
$ pipenv run cookiecutter gh:ionelmc/cookiecutter-pylibrary
$ cd datamonitor
$ pipenv run tox -e bootstrap
...
Wrote tox.ini
Wrote .travis.yml
DONE.
```

* List the tox environments:
```bash
$ pipenv run tox -l
clean
check
docs
py36
py37
py38
report
```

# Usage

## Install the `datamonitor` module
* There are at least two ways to install the `datamonitor` module,
  in the Python user space with `pip` and in a dedicated virtual environment
  with `pipenv`.
  + Both options may be installed in parallel
  + The Python user space (typically, `/usr/local/opt/python@3.8` on MacOS
    or `~/.pyenv/versions/3.8.3` on Linux) may already have many other modules
	installed, parasiting a fine-grained control over the versions of every
	Python dependency. If all the versions are compatible, then that option
	is convenient as it is available from the whole user space, not just
	from this sub-directory

* In the remainder of that [Usage section](#usage), it will be assumed
  that the `datamonitor` module has been installed and readily available
  from the environment, whether that environment is virtual or not.
  In other words, to adapt the documentation for the case where `pipenv`
  is used, just add `pipenv run` in front of every Python-related command.

### Install in the Python user space
* Install and use the `datamonitor` module in the user space (with `pip`):
```bash
$ python -m pip uninstall datamonitor
$ python -m pip install -U datamonitor
```

### Installation in a dedicated Python virtual environment
* Install and use the `datamonitor` module in a virtual environment:
```bash
$ pipenv shell
(python-iVzKEypY) ✔ python -m pip install -U datamonitor
(python-iVzKEypY) ✔ python -m pip install -U datamonitor
(python-iVzKEypY) ✔ exit
```

## Remove any previous document from the ES index
* Delete any previously created document from the target index,
  _e.g._ `dm-test-v0`, or drop the full index altogether:
```bash
$ curl -XDELETE http://localhost:9200/dm-test-v0
```

## Use `datamonitor` from the Command-Line (CLI)
* Install and use the `datamonitor` module
  + In the user space (with `pip`):
```bash
$ python -m datamonitor hello world
['hello', 'world']
```
  + In a virtual environment:
```bash
$ pipenv shell
(python-iVzKEypY) ✔ python -m datamonitor hello world
['hello', 'world']
(python-iVzKEypY) ✔ exit
```

## Use `datamonitor` as a module from another Python program
* Module import statement:
```python
>>> from datamonitor import DataMonitor
```

* Create an instance of the DataMonitor Python class:
```python
>>> dm = DataMonitor()
```

* Connect to the ES cluster/service:
```python
>>> es_conn_str = {'host': 'localhost', 'port': 9200, 'scheme': 'http'}
>>> es_conn = dm.es_connect(es_conn_str)
>>> es_conn
<Elasticsearch([{'host': 'localhost'}])>
```

* Get the information/details about the ES cluster/service:
```python
>>> es_info = dm.es_info()
>>> es_info
{'name': 'MyFavoriteES', 'cluster_name': 'elasticsearch_gold', 'cluster_uuid': 'G6YM0RZsRtW3DjoMPsIx_A', 'version': {'number': '7.8.0', 'build_flavor': 'default', 'build_type': 'tar', 'build_hash': '757314695644ea9a1dc2fecd26d1a43856725e65', 'build_date': '2020-06-14T19:35:50.234439Z', 'build_snapshot': False, 'lucene_version': '8.5.1', 'minimum_wire_compatibility_version': '6.8.0', 'minimum_index_compatibility_version': '6.0.0-beta1'}, 'tagline': 'You Know, for Search'}
```

* Send some simple payload to ES. ES should return a JSON structure,
  featuring, among other things, the created/assigned document ID:
```python
>>> meta_data_payload = {'unit': 'nb_of_rows', 'value': '6543'}
>>> docid = dm.es_send(index='dm-kpi-v0', payload=meta_data_payload)
>>> docid
'0W0pT3MB2UaYMhH3DxFr'
```

* Extract back the same paylod from ES:
```python
>>> document_str = dm.es_get(index='dm-kpi-v0', docid=docid)
>>> document_str
{'_index': 'dm-kpi-v0', '_type': '_doc', '_id': '0W0pT3MB2UaYMhH3DxFr', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'unit': 'nb_of_rows', 'value': '6543'}}
>>> document = None if not '_source' in document_str else document_str['_source']
>>> document
{'unit': 'nb_of_rows', 'value': '6543'}
```

# Development / Contribution
* Build the source distribution and Python artifacts (wheels):
```bash
$ rm -rf dist build */*.egg-info *.egg-info .tox MANIFEST
$ pipenv run python setup.py sdist bdist_wheel
```

* Upload to Test PyPi (no Linux binary wheel can be uploaded on PyPi):
```bash
$ PYPIURL="https://test.pypi.org"
$ pipenv run twine upload -u __token__ --repository-url ${PYPIURL}/legacy/ dist/*
Uploading distributions to https://test.pypi.org/legacy/
Uploading datamonitor-0.0.4-py2.py3-none-any.whl
100%|███████████████████████████████████████| 9.85k/9.85k [00:02<00:00, 4.48kB/s]
Uploading datamonitor-0.0.4.tar.gz
100%|███████████████████████████████████████| 18.8k/18.8k [00:01<00:00, 17.1kB/s]

View at:
https://test.pypi.org/project/datamonitor/0.0.4/
```

* Upload/release the Python packages onto the
  [PyPi repository](https://pypi.org):
  + Register the authentication token for access to PyPi:
```bash
$ PYPIURL="https://upload.pypi.org"
$ pipenv run keyring set ${PYPIURL}/ __token__
Password for '__token__' in '${PYPIURL}/':
```
  + Register the authentication token for access to PyPi:
```bash
$ pipenv run twine upload -u __token__ --repository-url ${PYPIURL}/legacy/ dist/*
Uploading distributions to https://upload.pypi.org/legacy/
Uploading datamonitor-0.0.4-py2.py3-none-any.whl
100%|███████████████████████████████████████| 11.5k/11.5k [00:02<00:00, 5.84kB/s]
Uploading datamonitor-0.0.4.tar.gz
100%|███████████████████████████████████████| 20.7k/20.7k [00:01<00:00, 15.8kB/s]

View at:
https://pypi.org/project/datamonitor/0.0.4/
```

* Note that the documentation is built automatically by ReadTheDocs (RTD)
  + The documentation is available from
    https://datamonitoring.readthedocs.io/en/latest/
  + The RTD project is setup on https://readthedocs.org/projects/datamonitoring/
  + As of July 2020, the documentation is built from RST files, _e.g._,
    [`README.rst`](https://github.com/infra-helpers/induction-monitoring/blob/master/python/datamonitor/README.rst)
	and documentation files in the
	[`docs` sub-directory](https://github.com/infra-helpers/induction-monitoring/blob/master/python/datamonitor/docs/).
	The author is a lot more familiar with MarkDown (MD) format,
	and would welcome help in translating the documentation generation
	configuration to use MD- rather than RST-based files.
	Do not hesitate to
	[create an issue](https://github.com/infra-helpers/induction-monitoring/issues)
	or, even better, submit a
	[pull request](https://github.com/infra-helpers/induction-monitoring/pulls)

* Build the documentation manually (with [Sphinx](http://sphinx-doc.org)):
```bash
$ pipenv run python setup.py build_sphinx
running build_sphinx
Running Sphinx v3.1.1
loading pickled environment... done
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 9 source files that are out of date
updating environment: [new config] 9 added, 0 changed, 0 removed
looking for now-outdated files... none found
no targets are out of date.
build succeeded.

The HTML pages are in build/sphinx/html.
```

* Re-generate the Python dependency files (`requirements.txt`)
  for the CI/CD pipeline (currently Travis CI):
```bash
$ pipenv --rm; rm -f Pipfile.lock; pipenv install; pipenv install --dev
$ git add Pipfile.lock
$ pipenv lock -r > datamonitor/ci/requirements.txt
$ pipenv lock --dev -r > datamonitor/ci/requirements-dev.txt
$ git add datamonitor/ci/requirements.txt datamonitor/ci/requirements-dev.txt
$ git commit -m "[CI] Upgraded the Python dependencies for the Travis CI pipeline"
```

## Test the DataMonitor Python module
* The tests use [ElasticMock](https://github.com/vrcmarcos/elasticmock),
  which emulates, in a very simple and limited way, an Elasticsearch (ES)
  cluster/service.

* If ES cluster/service is already running locally on the ES default port
  (9200), it must be temporarily shutdown, as the default parameters for
  ElasticMock would otherwise have both ES services step on each other toes.
  For instance:
  + On MacOs, `brew stop elasticsearch-full` (and
    `brew start elasticsearch-full` to restart it afterwards)
  + On SystemD-based Linux distributions, `sudo systemctl stop elasticsearch`
    (and `sudo systemctl start elasticsearch` to restart afterwards)

* Enter into the `pipenv` Shell:
```bash
$ pipenv shell
(python-iVzKEypY) ✔ python -V
Python 3.8.3
```

* Uninstall any previously installed `datamonitor` module/library:
```bash
(python-iVzKEypY) ✔ python -m pip uninstall datamonitor
```

* Launch a simple test with `pytest`
```bash
(python-iVzKEypY) ✔ python -m pytest test_datamonitor.py
=================== test session starts ===========================
platform darwin -- Python 3.8.3, pytest-5.4.3, py-1.9.0, pluggy-0.13.1
rootdir: ~/dev/infra/induction-monitoring/python/datamonitor, inifile: setup.cfg
collected 1 item
datamonitor/tests/test_datamonitor.py

========================== 1 passed in 0.06s ======================
```

* Check that a document has been created on ES. When the ES service is made
  from a single node (_e.g._, on a laptop or a local installation), the status
  of the index will be yellow. That is because the documents cannot be
  replicated:
```bash
(python-iVzKEypY) ✔ curl -XGET http://localhost:9200/_cat/indices/dm-test-v0
yellow open dm-test-v0 GXEUJjtkRjev3_wSn-5HOg 1 1 1 0 3.7kb 3.7kb
```

* Drop the replication requirement:
```bash
(python-iVzKEypY) ✔ curl -XPUT http://localhost:9200/dm-test-v0/_settings -H "Content-Type: application/json" --data "@../elasticseearch/settings/kibana-read-only.json"
```

* Check again the status of the `dm-test-v0` index, which should have become
  green:
```bash
(python-iVzKEypY) ✔ curl -XGET http://localhost:9200/_cat/indices/dm-test-v0
green open dm-test-v0 GXEUJjtkRjev3_wSn-5HOg 1 0 1 0 3.8kb 3.8kb
```

* Exit the `pipenv` Shell:
```bash
(python-iVzKEypY) ✔ exit
```

* To run all the tests:
```bash
$ pipenv run tox
```


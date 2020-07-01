Induction to Monitoring - Python
================================

# Table of Content (ToC)


# References



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
  [Cookiecutter template for Python library](https://github.com/ionelmc/cookiecutter-pylibrary):
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

# Development / Contributions
* Build the source distribution and Python artifacts (wheels):
```bash
$ rm -rf build/ && rm -rf dist/
$ pipenv run python setup.py sdist bdist_wheel
```

* Upload to Test PyPi (no Linux binary wheel can be uploaded on PyPi):
```bash
$ PYPIURL="https://test.pypi.org"
$ pipenv run twine upload -u __token__ --repository-url ${PYPIURL}/legacy/ dist/*
Uploading distributions to https://test.pypi.org/legacy/
Uploading datamonitor-0.0.0-py2.py3-none-any.whl
100%|███████████████████████████████████████| 9.85k/9.85k [00:02<00:00, 4.48kB/s]
Uploading datamonitor-0.0.0.tar.gz
100%|███████████████████████████████████████| 18.8k/18.8k [00:01<00:00, 17.1kB/s]

View at:
https://test.pypi.org/project/datamonitor/0.0.0/
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
Uploading datamonitor-0.0.0-py2.py3-none-any.whl
100%|███████████████████████████████████████| 9.85k/9.85k [00:05<00:00, 1.89kB/s]
Uploading datamonitor-0.0.0.tar.gz
100%|███████████████████████████████████████| 18.8k/18.8k [00:01<00:00, 17.3kB/s]

View at:
https://pypi.org/project/datamonitor/0.0.0/
```

* Note that the documentation is built automatically by ReadTheDocs (RTD)
  + The documentation is available from
    https://datamonitoring.readthedocs.io/en/latest/
  + The RTD project is setup on https://readthedocs.org/projects/datamonitoring/

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

## Test the OpenTREP Python extension
* Enter into the `pipenv` Shell:
```bash
$ pipenv shell
(python-iVzKEypY) ✔ python -V
Python 3.8.3
```

* Install the `datamonitor` module/library:
```bash
(python-iVzKEypY) ✔ python -m pip install -U datamonitor
```

* Launch a simple end-to-end test with `pytest`
```bash
(python-iVzKEypY) ✔ python -m pytest datamonitor/tests
=================== test session starts ===========================
platform darwin -- Python 3.8.3, pytest-5.4.3, py-1.9.0, pluggy-0.13.1
rootdir: ~/dev/infra/induction-monitoring/python/datamonitor, inifile: setup.cfg
collected 1 item
datamonitor/tests/test_datamonitor.py

========================== 1 passed in 0.06s ======================
```

* Exit the `pipenv` Shell:
```bash
(python-iVzKEypY) ✔ exit
```

* To run all the tests:
```bash
$ pipenv run tox
```


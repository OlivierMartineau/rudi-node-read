# RUDI Node tools: _rudi_node_get_ library

This library offers tools to take advantage of
the [external API](https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER) of a RUDI Producer node (also
referred as RUDI node).
The Jupyter notebook [README.ipynb](doc/README.ipynb) offers an overview of the available functionalities.

## Installation

```bash
$ pip install rudi_node_read
```

## Usage

```python
from rudi_node_read import RudiNodeReader
```

## Developing RudiNodeReader

To install rudi_node_read, along with the tools you need to develop and run tests, run the following in your virtualenv:

```bash
$ pip install -e .[dev]
```

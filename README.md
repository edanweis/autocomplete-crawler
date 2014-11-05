autocomplete-crawler
====================

A python script to crawl Google autocomplete results and graph them using Alchemy API.
--------------------------

![Image](https://github.com/edanweis/autocomplete-crawler/raw/master/image.jpg)

This script will generate a CSV of all google autocomplete results based on the following formula: 

```
common determiner + search term + single alphabetical character
```

The script will also generate a graph (.gexf) and [Gephi](http://www.gephi.org) file which includes all the named entities, relations and sentiments associated with each autocomplete result.

To enable the graph, you must set up and install your [free API key](http://www.alchemyapi.com/developers/getting-started-guide/using-alchemyapi-with-python/#get-api-key) from [AlchemyAPI](http://www.alchemyapi.com/developers/getting-started-guide/using-alchemyapi-with-python/) and include your api_key.txt and alchemyapi.py in the same directory.


Run
---------------

Run this script via the command prompt, or terminal window. Make sure you have all the necessary [Python modules](#dep) installed.

```python
$ python main.py
```

<a name="dep"></a>Python modules dependencies
---------------

* [Requests](http://docs.python-requests.org/en/latest/)
* [NetworkX](https://networkx.github.io/)


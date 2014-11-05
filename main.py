#-*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2014 Edan Weis

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys, io, os.path
import requests, json, string, time, urllib
from alchemyapi import AlchemyAPI
import networkx as nx
from networkx.readwrite import json_graph
import requests, urllib, json, string, time, csv

##################################################################

topic = raw_input("Enter a search string: ")

determiner = ["why", "how", "where", "who", "when", "which", "what"]
letters = list(string.ascii_lowercase)

# determiner = ["why", "how"]
# letters =  ['a','b']

##################################################################
search_queries = {}
ac_results = {}


def build_search_queries(topic):
	if os.path.isfile(topic+'.txt'):
		return
	for d in determiner:
		search_queries[d] = [d+" "+topic+" "+l for l in letters]
	return search_queries


def downloadAnswers(search_queries, output_file):
	# write header
	if os.path.isfile(output_file):
		ac_results_exist = True		
	else:
		ac_results_exist = False
		with open(output_file, 'ab+') as f:
			f.write("key,query,item\n")

	if ac_results_exist:
		with open(output_file, 'rb') as f:
			reader = csv.DictReader(f, delimiter=',')
			for row in reader:
				key = row['key']
				ac_results[key] = ac_results.get(key, []) + [row['item']]
		return ac_results
	else:
		for key in sorted(search_queries.iterkeys()):
			for query in search_queries[key]:
				url = 'http://suggestqueries.google.com/complete/search?client=chrome&q='+urllib.quote_plus(query)
				r = requests.get(url)
				data = json.loads(r.text)
				print repr(query) + ": " + str(len(data[1]))+" results"
				ac_results[key] = ac_results.get(key, []) + [i for i in data[1]]
			with open(output_file, 'ab+') as f:
				for item in ac_results[key]:
					f.write(key+","+query+","+item+"\n")
		return ac_results
	
def createGraph(ac_results):
	alchemyapi = AlchemyAPI()
	g=nx.Graph()
	total = 0.0
	i = 0.0

	for key in sorted(ac_results.iterkeys()):
		total += len(ac_results[key])

	for key in sorted(ac_results.iterkeys()):
		print "\nAlchemyAPI is now intepreting all of the "+key+" queries...\n"	
		for item in ac_results[key]:
			i +=1.0
			percent_complete = round((i/total)*100.0, 0)
			# print str(i) +" / "+str(total)+" - "+item
			print str(int(i)) +" / "+str(int(total))+"   "+str(percent_complete) +"%  " + item
			response_relations = alchemyapi.relations('text',item, {'entities':1, 'sentiment':1})
			response_entities = alchemyapi.entities('text',item, { 'sentiment':0 })

			if response_relations['status'] == 'OK':
				for relation in response_relations['relations']:
					# red.publish('chat', "found relation!")
					if 'subject' in relation:
						subject = relation['subject']['text']
						g.add_node(subject, query=key)

						if 'entities' in relation['subject']:
							g.node[subject]['type'] = relation['subject']['entities'][0]['type']

						if 'sentimentFromObject' in relation['subject']:
							# print relation['subject']['sentimentFromObject']['score']
							g.node[subject]['sentiment'] = float(relation['subject']['sentimentFromObject']['score'])

						if 'sentiment' in relation['subject']:
							# print relation['subject']['sentiment']['score']
							g.node[subject]['sentiment'] = float(relation['subject']['sentiment']['score'])
					
					if 'object' in relation:		
						object_ = relation['object']['text']
						g.add_node(object_, query=key)
						
						if 'entities' in relation['object']:
							g.node[object_]['type'] = relation['object']['entities'][0]['type']
							
						if 'sentimentFromSubject' in relation['object']:
							# print relation['object']['sentimentFromSubject']['score']
							g.node[object_]['sentiment'] = float(relation['object']['sentimentFromSubject']['score']							)

						if 'sentiment' in relation['object']:
							# print relation['object']['sentiment']['score']
							g.node[object_]['sentiment'] = float(relation['object']['sentiment']['score'])

					try:
						if all(x in ['subject', 'action', 'object'] for x in relation):
							n1 = relation['subject']['text']
							a =  relation['action']['text']
							n2 = relation['object']['text']
							if g.has_edge(n1,n2):
								g[n1][n2]['weight'] += 1
							else:
								g.add_edge(n1,n2, weight=1, relation=a)
					except:
						pass

				try:
					for entity in response_entities['entities']:
						g.add_node(entity['text'], type=entity['type'], query=key)
				except:
					continue

				nx.write_gexf(g, topic+".gexf")

			else:
				print "AlchemyAPI is not responding."
	return g



search_queries = build_search_queries(topic)
ac_results = downloadAnswers(search_queries, str(topic+'.txt'))
graph = createGraph(ac_results)
nx.write_gexf(graph, "complete-"+topic+".gexf")
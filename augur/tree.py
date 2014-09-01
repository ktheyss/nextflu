# create phylogeny from alignment
# raxml will complain about identical sequences, but still includes them all in the resulting tree
# writes out newick.tree file

import os, re, time
import dendropy
from io_util import *

OUTGROUP = 'A/Beijing/32/1992'

def to_json(node):
	json = {}
	if hasattr(node, 'clade'):
		json['clade'] = node.clade
	if node.taxon:
		json['strain'] = str(node.taxon).replace("'", '')
	if hasattr(node, 'yvalue'):
		json['yvalue'] = round(node.yvalue, 5)
	if hasattr(node, 'xvalue'):
		json['xvalue'] = round(node.xvalue, 5)	
	if hasattr(node, 'date'):
		json['date'] = node.date
	if hasattr(node, 'seq'):
		json['seq'] = node.seq
	if node.child_nodes():
		json["children"] = []
		for ch in node.child_nodes():
			json["children"].append(to_json(ch))
	return json
	
def get_yvalue(node):
	"""Return y location based on recursive mean of daughter locations"""	
	if hasattr(node, 'yvalue'):
		return node.yvalue	
	if node.child_nodes():
		mean = 0
		for ch in node.child_nodes():
			mean += get_yvalue(ch)
		return mean / float(len(node.child_nodes()))
		
def get_xvalue(node):
	"""Return x location based on total distance from root"""
	root = node.get_tree_root()
	return node.get_distance(root)

def reroot(tree):
	"""Reroot tree to outgroup"""
	outgroup_node = tree.find_node_with_taxon_label(OUTGROUP)	
	if outgroup_node:
		tree.to_outgroup_position(outgroup_node, update_splits=False)
		tree.prune_subtree(outgroup_node)
		
def collapse(tree):
	"""Collapse short edges to polytomies"""
	for e in tree.postorder_edge_iter():
		if e.length < 0.0001 and e.is_internal():
			e.collapse()
			
def ladderize(tree):
	"""Sorts child nodes in terms of the length of subtending branches each child node has"""
	node_desc_counts = {}
	for node in tree.postorder_node_iter():
		if len(node._child_nodes) == 0:
			node_desc_counts[node] = node.edge_length
		else:
			total = 0
			for child in node._child_nodes:
				total += node_desc_counts[child]
				total += child.edge_length
			node_desc_counts[node] = total
			node._child_nodes.sort(key=lambda n: node_desc_counts[n], reverse=True)			

def add_node_attributes(tree):
	"""Add clade, xvalue and yvalue attributes to all nodes in tree"""
	clade = 0
	yvalue = 0
	for node in tree.postorder_node_iter():
		node.clade = clade
		clade += 1
		if node.is_leaf():
			node.yvalue = yvalue
			yvalue += 1

	for node in tree.postorder_node_iter():
		node.yvalue = get_yvalue(node)
		node.xvalue = node.distance_from_root()

def add_virus_attributes(viruses, tree):
	"""Add date and seq attributes to all tips in tree"""
	strain_to_date = {}
	strain_to_seq = {}
	for v in viruses:
		strain_to_date[v['strain']] = v['date']
		strain_to_seq[v['strain']] = v['seq']
	for node in tree.postorder_node_iter():
		strain = str(node.taxon).replace("'", '')
		if strain_to_date.has_key(strain):
			node.date = strain_to_date[strain]
		if strain_to_seq.has_key(strain):
			node.seq = strain_to_seq[strain]
									
def main():

	print "--- Tree at " + time.strftime("%H:%M:%S") + " ---"
		
	viruses = read_json('data/virus_clean.json')
	write_fasta(viruses, 'temp.fasta')
	os.system("FastTree -gtr -nt -gamma -nosupport -spr 4 -mlacc 2 -slownni temp.fasta > data/tree.newick")

	with open('data/tree.newick', 'r') as file:
		newick = file.read().replace('\n', '')	
		newick = re.sub(r'(A/[^\:]+)', r"'\1'", newick)
	with open('temp.newick', 'w') as file:
		file.write(newick)	
	tree = dendropy.Tree.get_from_path("temp.newick", "newick")	
	reroot(tree)
	collapse(tree)	
	ladderize(tree)
	add_node_attributes(tree)
	add_virus_attributes(viruses, tree)

	write_json(to_json(tree.seed_node), "data/tree.json")
	
if __name__ == "__main__":
    main()
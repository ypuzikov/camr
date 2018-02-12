#!/usr/bin/env python2
# coding: utf-8

from collections import OrderedDict, namedtuple

from amr import Var, AMRConstant, AMRString, AMRNumber

# information about each node is stored in a named tuple
AMRNode = namedtuple('AMRNode', ['id', 'concept', 'start', 'end'])

# default alignment (start and end token ids)
NULL_ALIGNMENT = ('', '')


class AMRPrinter(object):

    def get_concept2alignment_dict(self, amr_graph):
        """
        Use an AMR object to generate a dictionary of the following format:

        - key: concept
        - value: (start, end) tuple
        """

        concept_tokid_pairs = {}
        for triple, alignment in amr_graph.alignments().items():
            # alignment has the following format: 'e.d',
            # where 'd' is the positional idx of an aligned token (starting with 0)
            aligned_tokids = alignment[2:]  # stripping the 'e.' part off

            # a node is sometimes aligned to several tokens
            # e.g. '~e.17,20'
            tokids = aligned_tokids.split(',')

            # we use a heuristic -- align to the first token in this set
            start = int(tokids[0])
            end = start + 1  # ISI alignments are token-based -> off-set by 1
            concept = self.get_node_concept(triple[2], amr_graph)
            concept_tokid_pairs[concept] = (str(start), str(end))

        return concept_tokid_pairs

    def get_node_concept(self, node, amrgraph):
        """
        Given an AMR graph and a node, retrieve the corresponding AMR concept.
        The procedure is different for each type of an AMR node.
        """

        if type(node) in [AMRConstant, AMRString, AMRNumber]:
            concept = node._value

        elif type(node) == Var:
            # retrieve the triple of the form (Var(foo), ':instance-of', Concept(bar))
            var_obj, rel, concept_obj = amrgraph.triples(head=Var('%s' % node._name), rel=':instance-of').pop()
            concept = concept_obj._name

        else:
            concept = node._name

        return concept

    def get_gorn_addr_map(self, amr_graph):
        """
        Main method which generates a Gorn address map for an amr.AMR object.
        Returns a dictionary of the form:

        key = amr.Var || AMRConstant || AMRString || AMRNumber
        value = AMRNode named tuple: (gord_addr_id, concept, (start_token, end_token))

        Note that ISI alignments are token-based, hence splitting alignment to 'start' and 'end'
        does not make sense, unless we want to make them compatible with
        the JAMR Aligner format (which is the case).
        """

        triples = amr_graph.triples()[1:]  # excluding the first one (which is TOP)
        alignments = self.get_concept2alignment_dict(amr_graph)
        gorn_address = OrderedDict()

        # store the AMRNode info for the root node
        p_node = triples.pop(0)[0]
        p_node_address = "0"
        p_node_concept = self.get_node_concept(p_node, amr_graph)
        p_node_alignment = alignments.get(p_node_concept, NULL_ALIGNMENT)
        gorn_address[p_node] = AMRNode(p_node_address, p_node_concept, *p_node_alignment)

        relations = []
        sibling_cnt = -1

        # for each triple
        for h, rel, curr_node in triples:
            # skipping the one which sets a relation between a Var and Concept
            if rel == ':instance-of':
                continue

            # if the child node is not in the gorn_address map already
            # otherwise need to skip: this means we have reentrance situation
            if curr_node not in gorn_address:
                relations.append((h, rel, curr_node))
                # increase the count if the parent of the current node is the same as for the previous one
                # this means we are processing a node which has a sibling
                sibling_cnt = sibling_cnt + 1 if h == p_node else 0
                p_node = self.gorn_map_child_node(amr_graph, h, sibling_cnt, curr_node, gorn_address, alignments)

        return gorn_address, relations

    def gorn_map_child_node(self, amr_graph, parent_node, sibling_count, this_node, gorn_address, alignments):
        """
        Aux method used in get_gorn_addr_map() method (above).

        To assign a Gorn address to a node, two things are needed:
        1) Gorn address of the parent node
        2) number of siblings processed so far

        """

        # note that gorn_address[parent_node] returns 3 elements;
        # we need only the 1st (i.e., Gorn addres of the parent node)
        parent_id = gorn_address[parent_node][0]
        this_address = "%s.%d" % (parent_id, sibling_count)
        this_concept = self.get_node_concept(this_node, amr_graph)
        this_alignment = alignments.get(this_concept, NULL_ALIGNMENT)
        gorn_address[this_node] = AMRNode(this_address, this_concept, *this_alignment)

        return parent_node

    @staticmethod
    def gen_amr_alignment_string(gorn_addr):
        """
        A pretty-print method which outputs a ':: alignment ...' line similar to JAMR Aligner.
        Example:

        JAMR:
        # ::alignments 2-3|0.0 6-7|0.0.2 5-6|0.0.2.0 4-5|0.0.2.0.0 1-2|0.0.1 ::annotator Aligner v.02 ::date 2017-01-06T12:19:48.98

        Output:
        # ::alignments 2-3|0.0 6-7|0.0.2 5-6|0.0.2.0 4-5|0.0.2.0.0 1-2|0.0.1 ::annotator GornMap-ISIAligner

        """

        alignment_info = " ".join(["%s-%s|%s" % (nodeinfo.start,
                                                 nodeinfo.end,
                                                 nodeinfo.id) if nodeinfo.start else ''
                                   for node, nodeinfo in gorn_addr.items()]
                                  )

        alignment_str = '# ::alignments %s ::annotator GornMap-ISIAligner' % alignment_info

        return alignment_str

    @staticmethod
    def get_amr_alignment_fullinfo(gorn_addr, relations):
        """
        Generates the alignment string which, besides the ':: alignments' line,
        also includes per-node, per-edge and root info.

        Example:

        # ::alignments 0-1|0 1-2|0.0 4-5|0.0.0 3-4|0.0.0.0 ::annotator Aligner v.02 ::date 2017-01-06T12:50:08.872
        # ::node        0       establish-01    0-1
        # ::node        0.0     model   1-2
        # ::node        0.0.0   innovate-01     4-5
        # ::node        0.0.0.0 industry        3-4
        # ::root        0       establish-01
        # ::edge        establish-01    ARG1    model   0       0.0
        # ::edge        innovate-01     ARG1    industry        0.0.0   0.0.0.0
        # ::edge        model   mod     innovate-01     0.0     0.0.0

        """

        # we will store each node/root/edge string in a separate list
        node_edge_root_str_dict = OrderedDict({'alignment': None,
                                               'node': [],
                                               'root': None,
                                               'edge': [],
                                               })

        # 1. get node info and the alignment line
        alignments = []

        for node, nodeinfo in gorn_addr.items():
            # ::node        id       concept    start-end
            node_str = '# ::node\t%s\t%s\t%s' % (nodeinfo.id,
                                                 nodeinfo.concept,
                                                 '-'.join([nodeinfo.start, nodeinfo.end])
                                                 if nodeinfo.start else '')
            # store a node line
            node_edge_root_str_dict['node'].append(node_str)

            # store alignment info
            if nodeinfo.start:
                alignments.append("%s-%s|%s" % (nodeinfo.start, nodeinfo.end, nodeinfo.id))

        # store the alignment line in the dictionary
        alignment_info = " ".join(alignments)
        alignment_str = '# ::alignments %s ::annotator GornMap-ISIAligner' % alignment_info
        node_edge_root_str_dict['alignment'] = alignment_str

        # 2. get root string
        root_node = gorn_addr.keys()[0]  # root node
        root_node_info = gorn_addr[root_node]
        # ::root        root_id       root_concept
        root_str = "# ::root\t%s\t%s" % (root_node_info.id, root_node_info.concept)
        node_edge_root_str_dict['root'] = root_str

        # 3. iterate over the relations dictionary,
        # retrieve needed info and populate the dictionary
        for h_node, relation, ch_node in relations:
            h_node_info = gorn_addr[h_node]
            ch_node_info = gorn_addr[ch_node]

            # ::edge        h_concept    relation    ch_concept   h_id       ch_id
            edge_str = '# ::edge\t%s\t%s\t%s\t%s\t%s' % (h_node_info.concept,
                                                         relation[1:],  # skipping the colon in the edge label (:ARG0)
                                                         ch_node_info.concept,
                                                         h_node_info.id,
                                                         ch_node_info.id)

            node_edge_root_str_dict['edge'].append(edge_str)

        return node_edge_root_str_dict
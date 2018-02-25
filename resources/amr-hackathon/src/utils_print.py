#!/usr/bin/env python2
# coding: utf-8

from collections import OrderedDict, namedtuple

from amr import Var, AMRConstant, AMRString, AMRNumber

# information about each node is stored in a named tuple
AMRNode = namedtuple('AMRNode', ['id', 'concept', 'start', 'end'])

# default alignment (start and end token ids)
NULL_ALIGNMENT = ('', '')


class AMRPrinter(object):

    def get_concept2spans_alignment_dict(self, amr_graph):
        """
        Use an AMR object to generate a dictionary of the following format:

        - key: concept
        - value: (start, end) tuple
        """

        concept_tokid_pairs = OrderedDict()
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
            concept_tokid_pairs.setdefault(concept, []).append((str(start), str(end)))

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

    def get_alignment_from_concept(self, concept, alignments_dict):
        """
        Given an AMR concept and a dictionary with concepts as keys and lists of spans as values,
        retrieve the span. Considers the cases where the
        :param concept: AMR concept
        :param alignments_dict: a dictionary with mappings: concept -> [(start,end), (start, end), ...]
        :return: a tuple of the form (start, end), both being strings.
        """

        if concept in alignments_dict:
            # some node with this concept has an alignment
            p_node_concept_alignments = alignments_dict[concept]

            if len(p_node_concept_alignments) > 0:
                # there is at least one node with this concept
                p_node_alignment = p_node_concept_alignments.pop(0)

            else:
                # we have encounterd a node with the same concept before,
                # however, the current node (also having the same concept) is unaligned
                # hence, we need to remove the key from the OrderedDict and assign NULL ALLIGNMENT to the
                # current node
                del alignments_dict[concept]
                p_node_alignment = NULL_ALIGNMENT

        else:
            # this node is unaligned
            p_node_alignment = NULL_ALIGNMENT

        return p_node_alignment

    def get_gorn_addr_map(self, amr_graph):
        """
        Main method which generates a Gorn address map for an amr.AMR object.
        Returns a dictionary of the form:

        key = amr.Var || AMRConstant || AMRString || AMRNumber
        value = AMRNode named tuple: (gord_addr_id, concept, (start_token, end_token))

        Note that ISI alignments are token-based, so splitting alignment to 'start' and 'end'
        does not make sense in general. However, we want to make them compatible with
        the JAMR Aligner format => splitting.
        """

        # relation triples in the order of occurence in AMR string
        triples = amr_graph.triples()[1:]  # excluding the first one (which is meta-node, 'TOP')

        # alignments in the order of occurence in AMR string
        alignments = self.get_concept2spans_alignment_dict(amr_graph)
        gorn_address = OrderedDict()

        # store the AMRNode info for the root node
        root_node = triples.pop(0)[0]
        root_node_address = "0"
        root_node_concept = self.get_node_concept(root_node, amr_graph)
        root_node_alignment = self.get_alignment_from_concept(root_node_concept, alignments)
        gorn_address[root_node] = AMRNode(root_node_address, root_node_concept, *root_node_alignment)

        relations = []
        children_cnts = {}

        # for each triple
        for parent, rel, child in triples:
            # skipping the one which sets a relation between a Var and Concept
            if rel == ':instance-of':
                continue

            # check if the child node is not in the gorn_address map already
            # if it is, we need to skip -- this means we have reentrance situation
            if child not in gorn_address:
                relations.append((parent, rel, child))
                children_cnts[parent] = children_cnts.get(parent,-1) + 1

                # to assign a Gorn address to a node, two things are needed:
                # 1) Gorn address of the parent node
                # 2) number of siblings processed so far
                parent_id = gorn_address[parent].id
                child_address = "%s.%d" % (parent_id, children_cnts[parent])

                # add the child node to the Gorn address map
                child_concept = self.get_node_concept(child, amr_graph)
                child_alignment = self.get_alignment_from_concept(child_concept, alignments)
                gorn_address[child] = AMRNode(child_address, child_concept, *child_alignment)

        return gorn_address, relations

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
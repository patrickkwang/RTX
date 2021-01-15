#!/bin/env python3
import sys
import os
import traceback
import ast
from typing import List, Dict, Tuple, Set

import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import expand_utilities as eu
from expand_utilities import DictKnowledgeGraph
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")  # ARAXQuery directory
from ARAX_response import ARAXResponse
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../UI/OpenAPI/python-flask-server/")
from openapi_server.models.node import Node
from openapi_server.models.edge import Edge
from openapi_server.models.edge_attribute import EdgeAttribute
from openapi_server.models.query_graph import QueryGraph


class GeneticsQuerier:

    def __init__(self, response_object: ARAXResponse):
        self.response = response_object
        self.kp_api_url = "https://translator.broadinstitute.org/genetics_data_provider/query"
        self.kp_name = "GeneticsKP"
        # TODO: Eventually validate queries better based on info in future TRAPI knowledge_map endpoint
        self.accepted_node_categories = {"gene", "pathway", "phenotypic_feature", "disease"}
        self.accepted_edge_types = {"associated"}
        self.node_category_overrides_for_kp = {"protein": "gene"}
        self.kp_preferred_prefixes = {"gene": "NCBIGene", "pathway": "GO", "phenotypic_feature": "EFO", "disease": "EFO"}
        self.magma_score_name = "MAGMA-pvalue"
        self.score_type_lookup = {self.magma_score_name: "EDAM:data_1669",
                                  "Genetics-quantile": "SIO:001414"}

    def answer_one_hop_query(self, query_graph: QueryGraph) -> Tuple[DictKnowledgeGraph, Dict[str, Dict[str, str]]]:
        """
        This function answers a one-hop (single-edge) query using the Genetics Provider.
        :param query_graph: A Reasoner API standard query graph.
        :return: A tuple containing:
            1. an (almost) Reasoner API standard knowledge graph containing all of the nodes and edges returned as
           results for the query. (Dictionary version, organized by QG IDs.)
            2. a map of which nodes fulfilled which qnode_keys for each edge. Example:
              {'KG1:111221': {'n00': 'DOID:111', 'n01': 'HP:124'}, 'KG1:111223': {'n00': 'DOID:111', 'n01': 'HP:126'}}
        """
        log = self.response
        include_all_scores = self.response.data['parameters']['include_all_scores']
        final_kg = DictKnowledgeGraph()
        edge_to_nodes_map = dict()

        # Verify this is a valid one-hop query graph and tweak its contents as needed for this KP
        self._verify_one_hop_query_graph_is_valid(query_graph, log)
        if log.status != 'OK':
            return final_kg, edge_to_nodes_map
        modified_query_graph = self._pre_process_query_graph(query_graph, log)
        if log.status != 'OK':
            return final_kg, edge_to_nodes_map
        qedge = modified_query_graph.edges[0]
        source_qnode_key = qedge.source_id
        target_qnode_key = qedge.target_id

        # Answer the query using the KP and load its answers into our Swagger model
        json_response = self._send_query_to_kp(modified_query_graph, log)
        returned_kg = json_response.get('knowledge_graph')
        if not returned_kg:
            log.warning(f"No KG is present in the response from {self.kp_name}")
        else:
            # Build a map of node/edge IDs to qnode/qedge IDs
            qg_id_mappings = self._get_qg_id_mappings_from_results(json_response['results'])
            unknown_scores_encountered = set()
            # Populate our final KG with nodes and edges
            for returned_edge in returned_kg['edges']:
                # Skip edges missing a source and/or target ID (have encountered these before)
                if not returned_edge['source_id'] or not returned_edge['target_id']:
                    log.warning(f"Edge returned from GeneticsKP is lacking a source_id and/or target_id: {returned_edge}."
                                f" Will skip adding this edge to the KG.")
                else:
                    if returned_edge['score_name'] not in self.score_type_lookup:
                        unknown_scores_encountered.add(returned_edge['score_name'])
                    # Always include edges for integrated scores, but only include magma edges if that flag is set
                    if include_all_scores or returned_edge['score_name'] == self.magma_score_name:
                        swagger_edge = self._create_swagger_edge_from_kp_edge(returned_edge)
                        for qedge_id in qg_id_mappings['edges'][swagger_edge.id]:
                            swagger_edge.id = self._create_unique_edge_id(swagger_edge)  # Convert to an ID that's unique for us
                            final_kg.add_edge(swagger_edge, qedge_id)
                        edge_to_nodes_map[swagger_edge.id] = {source_qnode_key: swagger_edge.source_id,
                                                              target_qnode_key: swagger_edge.target_id}
            log.warning(f"Encountered unknown score(s) from {self.kp_name}: {unknown_scores_encountered}. "
                        f"Not sure what data type to assign these.")
            for returned_node in returned_kg['nodes']:
                if returned_node['id']:  # Skip any nodes with 'None' for their ID (see discussion in #1154)
                    swagger_node = self._create_swagger_node_from_kp_node(returned_node)
                    for qnode_key in qg_id_mappings['nodes'][swagger_node.id]:
                        final_kg.add_node(swagger_node, qnode_key)
                else:
                    log.warning(f"Node returned from {self.kp_name} is lacking an ID: {returned_node}."
                                f" Will skip adding this node to the KG.")

        return final_kg, edge_to_nodes_map

    @staticmethod
    def _verify_one_hop_query_graph_is_valid(query_graph: QueryGraph, log: ARAXResponse):
        if len(query_graph.edges) != 1:
            log.error(f"answer_one_hop_query() was passed a query graph that is not one-hop: "
                      f"{query_graph.to_dict()}", error_code="InvalidQuery")
        elif len(query_graph.nodes) > 2:
            log.error(f"answer_one_hop_query() was passed a query graph with more than two nodes: "
                      f"{query_graph.to_dict()}", error_code="InvalidQuery")
        elif len(query_graph.nodes) < 2:
            log.error(f"answer_one_hop_query() was passed a query graph with less than two nodes: "
                      f"{query_graph.to_dict()}", error_code="InvalidQuery")

    def _pre_process_query_graph(self, query_graph: QueryGraph, log: ARAXResponse) -> QueryGraph:
        for qnode_key, qnode in query_graph.nodes.items():
            # Convert node types to preferred format and verify we can do this query
            formatted_qnode_categories = {self.node_category_overrides_for_kp.get(qnode_category, qnode_category) for qnode_category in eu.convert_string_or_list_to_list(qnode.category)}
            accepted_qnode_categories = formatted_qnode_categories.intersection(self.accepted_node_categories)
            if not accepted_qnode_categories:
                log.error(f"{self.kp_name} can only be used for queries involving {self.accepted_node_categories} "
                          f"and QNode {qnode_key} has type '{qnode.category}'", error_code="UnsupportedQueryForKP")
                return query_graph
            else:
                qnode.category = list(accepted_qnode_categories)[0]
            # Convert curies to equivalent curies accepted by the KP (depending on qnode type)
            if qnode.id:
                equivalent_curies = eu.get_curie_synonyms(qnode.id, log)
                desired_curies = [curie for curie in equivalent_curies if curie.startswith(f"{self.kp_preferred_prefixes[qnode.category]}:")]
                if desired_curies:
                    qnode.id = desired_curies if len(desired_curies) > 1 else desired_curies[0]
                    log.debug(f"Converted qnode {qnode_key} curie to {qnode.id}")
                else:
                    log.warning(f"Could not convert qnode {qnode_key} curie(s) to preferred prefix ({self.kp_preferred_prefixes[qnode.category]})")
        return query_graph

    @staticmethod
    def _get_qg_id_mappings_from_results(results: [any]) -> Dict[str, Dict[str, Set[str]]]:
        qnode_key_mappings = dict()
        qedge_id_mappings = dict()
        for result in results:
            for node_binding in result['node_bindings']:
                qg_id = node_binding['qg_id']
                kg_id = node_binding['kg_id']
                if kg_id in qnode_key_mappings:
                    qnode_key_mappings[kg_id].add(qg_id)
                else:
                    qnode_key_mappings[kg_id] = {qg_id}
            for edge_binding in result['edge_bindings']:
                qg_id = edge_binding['qg_id']
                kg_id = edge_binding['kg_id']
                if kg_id in qedge_id_mappings:
                    qedge_id_mappings[kg_id].add(qg_id)
                else:
                    qedge_id_mappings[kg_id] = {qg_id}
        return {"nodes": qnode_key_mappings, "edges": qedge_id_mappings}

    def _send_query_to_kp(self, query_graph: QueryGraph, log: ARAXResponse) -> Dict[str, any]:
        # Send query to their API (stripping down qnode/qedges to only the properties they like)
        stripped_qnodes = dict()
        for qnode_key, qnode in query_graph.nodes.items():
            stripped_qnode = {'type': qnode.category}
            if qnode.id:
                stripped_qnode['curie'] = qnode.id
            stripped_qnodes[qnode_key] = stripped_qnode
        qedge = next(qedge for qedge in query_graph.edges.values())  # Our query graph is single-edge
        stripped_qedge = {'id': qedge.id,
                          'source_id': qedge.source_id,
                          'target_id': qedge.target_id,
                          'type': list(self.accepted_edge_types)[0]}
        source_stripped_qnode = stripped_qnodes[qedge.source_id]
        input_curies = eu.convert_string_or_list_to_list(source_stripped_qnode['curie'])
        combined_response = dict()
        for input_curie in input_curies:  # Until we have batch querying, ping them one-by-one for each input curie
            log.debug(f"Sending {qedge.id} query to {self.kp_name} for {input_curie}")
            source_stripped_qnode['curie'] = input_curie
            kp_response = requests.post(self.kp_api_url,
                                        json={'message': {'query_graph': {'nodes': stripped_qnodes, 'edges': [stripped_qedge]}}},
                                        headers={'accept': 'application/json'})
            if kp_response.status_code != 200:
                log.warning(f"{self.kp_name} KP API returned response of {kp_response.status_code}")
            else:
                kp_response_json = kp_response.json()
                if kp_response_json.get('results'):
                    if not combined_response:
                        combined_response = kp_response_json
                    else:
                        combined_response['knowledge_graph']['nodes'] += kp_response_json['knowledge_graph']['nodes']
                        combined_response['knowledge_graph']['edges'] += kp_response_json['knowledge_graph']['edges']
                        combined_response['results'] += kp_response_json['results']
        return combined_response

    def _create_swagger_edge_from_kp_edge(self, kp_edge: Dict[str, any]) -> Edge:
        swagger_edge = Edge(id=kp_edge['id'],
                            source_id=kp_edge['source_id'],
                            target_id=kp_edge['target_id'],
                            type=kp_edge['type'],
                            provided_by=self.kp_name,
                            is_defined_by='ARAX')
        score_name = kp_edge['score_name']
        score_value = kp_edge.get('score')
        if score_value:  # Some returned edges are missing a score value for whatever reason
            swagger_edge.edge_attributes = [EdgeAttribute(name=score_name,
                                                          type=self.score_type_lookup.get(score_name),
                                                          value=score_value)]
        return swagger_edge

    @staticmethod
    def _create_swagger_node_from_kp_node(kp_node: Dict[str, any]) -> Node:
        return Node(id=kp_node['id'],
                    type=kp_node['type'],
                    name=kp_node.get('name'))

    def _create_unique_edge_id(self, swagger_edge: Edge) -> str:
        kind_of_edge = swagger_edge.edge_attributes[0].name if swagger_edge.edge_attributes else swagger_edge.type
        return f"{self.kp_name}:{swagger_edge.source_id}-{kind_of_edge}-{swagger_edge.target_id}"

#!/usr/bin/env python3

''' Creates Neo4j index and constraints for KG2

    Usage: create_indexes_constraints.py --user <Neo4j Username>
                        --password <Neo4j Password>
'''
import argparse
import neo4j
import getpass

__author__ = 'Erica Wood'
__copyright__ = 'Oregon State University'
__credits__ = ['Stephen Ramsey', 'Erica Wood']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = ''
__email__ = ''
__status__ = 'Prototype'


def run_query(query):
    """
    :param query: a cypher statement as a string to run
    """
    # Start a neo4j session, run a query, then close the session
    session = driver.session()
    query = session.run(query)
    session.close()
    return query


def node_labels():
    # Create a list of dictionaries where each key is "labels(n)"
    # and each value is a list containing a node label
    labels = "MATCH (n) RETURN distinct labels(n)"
    query = run_query(labels)
    data = query.data()
    label_list = []
    # Iterate through the list and dicitionaries to create a list
    # of node labels
    for dictionary in data:
        for key in dictionary:
            value = dictionary[key]
            value_string = value[0]
            label_list.append(value_string)
    return label_list


def edge_labels():
    # Create a list of dictionaries where each key is "type(e)"
    # and each value is an edge type as a string
    labels = "MATCH (n)-[e]-(m) RETURN distinct type(e)"
    query = run_query(labels)
    data = query.data()
    label_list = []
    # Iterate through the list and dicitionaries to create a list
    # of edge labels
    for dictionary in data:
        for key in dictionary:
            value = dictionary[key]
            label_list.append(value)
    return label_list


def create_index(label_list, property_name):
    """
    :param label_list: a list of the node labels in Neo4j
    """
    # For every label in the label list, create an index
    # on the given property name
    for label in label_list:
        if label.find(":") < 0: ##CREATE INDEX ON :BFO:0000050 (edge_label) gives error
            index_query = "CREATE INDEX ON :" + label + " (" + property_name + ")"
        run_query(index_query)


def constraint(label_list):
    """
    :param label_list: a list of the node labels in Neo4j
    """
    # For every label in the label list, create a unique constraint
    # on the node id property
    for label in label_list:
        constraint_query = "CREATE CONSTRAINT ON (n:" + label + ") \
                            ASSERT n.id IS UNIQUE"
        run_query(constraint_query)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, help="Neo4j Username",
                        nargs=1, required=True)
    parser.add_argument("--password", help="Neo4j Password",
                        type=str, nargs=1, required=False)
    arguments = parser.parse_args()
    username = arguments.user[0]
    password = arguments.password[0]
    if password is None:
        password = getpass.getpass("Please enter the Neo4j database password")
    bolt = 'bolt://127.0.0.1:7687'
    driver = neo4j.GraphDatabase.driver(bolt, auth=(username, password))
    node_label_list = node_labels()
    edge_label_list = edge_labels()

    # Create Indexes on Node Properties
    create_index(node_label_list, "category")
    create_index(node_label_list, "category_label")
    create_index(node_label_list, "deprecated")
    create_index(node_label_list, "description")
    create_index(node_label_list, "full_name")
    create_index(node_label_list, "iri")
    create_index(node_label_list, "name")
    create_index(node_label_list, "provided_by")
    create_index(node_label_list, "publications")
    create_index(node_label_list, "replaced_by")
    create_index(node_label_list, "synonym")
    create_index(node_label_list, "update_date")

    # Create Indexes on Edge Properties
    create_index(edge_label_list, "edge_label")
    create_index(edge_label_list, "negated")
    create_index(edge_label_list, "object")
    create_index(edge_label_list, "provided_by")
    create_index(edge_label_list, "publications")
    create_index(edge_label_list, "publications_info")
    create_index(edge_label_list, "relation")
    create_index(edge_label_list, "relation_curie")
    create_index(edge_label_list, "subject")
    create_index(edge_label_list, "update_date")
    constraint(node_label_list)
    driver.close()

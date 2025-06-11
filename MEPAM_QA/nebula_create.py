#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
    script description
        read node and edge data from tsv files, then construct the nebula graph
    input args
        static_configuration_file_path
    output result
        a graph in nebula
"""

import os
import sys
import configparser
import pandas as pd
from util.logger import logger
from util.nebula_operator import NebulaOP
import json
import nebula

def read_tsv(file_path: str) -> pd.DataFrame:
    """read tsv file into pandas DataFrame"""
    try:
        df = pd.read_csv(file_path, sep='\t', header=0, dtype=str)
        logger.info(f"Successfully read file: {file_path}")
        return df
    except Exception as err:
        logger.error(f"Failed to read file: {file_path}. Error: {err}")
        raise err

def insert_nodes(op: NebulaOP, node_df: pd.DataFrame) -> None:
    """insert node data into nebula"""
    for _, row in node_df.iterrows():
        node_id = row['node_id']
        node_type = row['type']
        properties = {
            'id': row['name'],
            'label':row['name']
        }
        op.insert_vertex(node_type, list(properties.keys()), [(node_id, properties)])

def insert_edges(op: NebulaOP, edge_df: pd.DataFrame) -> None:
    """insert edge data into nebula"""
    for _, row in edge_df.iterrows():
        edge_type = row['type']
        start_id = row['start_id']
        end_id = row['end_id']
        properties = row['properties']
        print(properties)
        if pd.notna(properties):
            properties = json.loads(properties.replace('""', '"'))
        else:
            properties = {}
        op.insert_edge(edge_type, list(properties.keys()), [(start_id, properties, end_id)])

if __name__ == '__main__':
    """main program flow"""
    if len(sys.argv) != 2:
        logger.info('the args inputing error!')
        sys.exit(1)
    args = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(args)

    # the file path of node tsv
    node_tsv_file_path = config['result_storage']['node_tsv_file_path']
    logger.info(f'node_tsv_file_path:{node_tsv_file_path}')
    # the file path of edge tsv
    edge_tsv_file_path = config['result_storage']['edge_tsv_file_path']
    logger.info(f'edge_tsv_file_path:{edge_tsv_file_path}')
    # the user of nebula
    nebula_user = config['nebula_connect']['user']
    logger.info(f'nebula_user:{nebula_user}')
    # the passwd of nebula
    nebula_passwd = config['nebula_connect']['passwd']
    logger.info(f'passwd:{nebula_passwd}')
    # the space name of nebula
    nebula_space_name = config['nebula_connect']['space_name']
    logger.info(f'space_name:{nebula_space_name}\n')

    # initial nebula op
    op = NebulaOP(nebula_space_name, nebula_user, nebula_passwd)

    # read node and edge data from tsv files
    node_df = read_tsv(node_tsv_file_path)
    edge_df = read_tsv(edge_tsv_file_path)

    # insert node and edge data into nebula
    insert_nodes(op, node_df)
    insert_edges(op, edge_df)

    logger.info('the main flow is over!')
# !usr/bin/python3
# -*- coding:utf-8 -*-

"""
    script description
        resolve all yaml file, then construct the nebula graph
    input args
        static_configuration_file_path
    output result
        a graph in nebula
"""

import os
import ast
import sys
import time
import json
import yaml
import configparser
import pandas as pd

sys.path.append(os.getcwd() + '/../../')
sys.path.append(os.getcwd() + '/../../util/')

from util import logger
from urllib.parse import unquote
from util.nebula_operator import NebulaOP

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

bp_list = ['Not provided', 'not specified', 'not provided']
produce_attribute = ['temperature', 'ph', 'substrate', 'incubation_period', 'medium', 'moisture', 'carbon_source', 'nitrogen_source', 'aeration', 'agitation', 'volume', 'effect', 'quantitative_value']
catalysis_attribute = ['temperature', 'ph', 'ions', 'chemicals', 'substrate', 'effect', 'quantitative_value', 'substrate_concentration']


def get_node_id_by_identifier(node_df: pd.DataFrame, type: str, name: str, identifier: str, enzyme_exception: bool=False) -> int:
    """return node id by auto id or return None when nothing found"""
    res_df = node_df.query(f'type == "{type}" & identifier == "{identifier}"')

    if len(res_df) == 0:
        if enzyme_exception and type == 'enzyme':
            raise Exception(f'enzyme of catalysis stage is not produced:{identifier}')
        node_id = len(node_df) + 1
        node_df.loc[len(node_df)] = [node_id, type, name, identifier]
        return node_id
    else:
        return res_df['node_id'].tolist()[0]


def resolve_yaml(yaml_file_path: str, node_df: pd.DataFrame, edge_df: pd.DataFrame) -> None:
    """resolve one yaml file to node and edge df"""
    try:
        with open(yaml_file_path, 'r') as file:
            # safe load content
            content_dict = yaml.safe_load(file)
    except FileNotFoundError as err:
        logger.log.error(f'yaml file is not exist:{yaml_file_path}')
        raise err
    except Exception as err:
        logger.log.error(f'reading yaml file failed:{err}')
        raise err

    #  basenaem for yaml
    yaml_filename = os.path.basename(yaml_file_path).replace(r'.yml', r'.pdf')

    try:
        # id -> label
        id_mapping = {}
        if 'named_entities' in content_dict:
            named_entities = content_dict['named_entities']
            if type(named_entities) is str:
                named_entities = ast.literal_eval(named_entities)
            for entity_dict in named_entities:
                id_mapping[entity_dict['id']] = entity_dict['label']
    except Exception:
        id_mapping = {}
    logger.log.info(f'id_mapping:{id_mapping}')

    # resolve produce
    if 'enzyme_productions' in content_dict['extracted_object']:
        for produce_dict in content_dict['extracted_object']['enzyme_productions']:
            # process subject
            microbiome_id = produce_dict['subject']
            microbiome_label = id_mapping[microbiome_id] if microbiome_id in id_mapping else unquote(microbiome_id).replace(r'AUTO:', '')
            start_vid = get_node_id_by_identifier(node_df, 'microbiome', microbiome_label, microbiome_id)
            # process object
            if 'object' not in produce_dict:
                continue
            enzyme_id = produce_dict['object']
            enzyme_label = id_mapping[enzyme_id] if enzyme_id in id_mapping else unquote(enzyme_id).replace(r'AUTO:', '')
            end_vid = get_node_id_by_identifier(node_df, 'enzyme', enzyme_label, enzyme_id)
            # process predicate
            for k, v in produce_dict['predicate'].items():
                if v in bp_list:
                    produce_dict['predicate'][k] = None
            for attribute in produce_attribute:
                if attribute not in produce_dict['predicate']:
                    produce_dict['predicate'][attribute] = None
            edge_df.loc[len(edge_df)] = ['produce', start_vid, end_vid, json.dumps(produce_dict['predicate'], ensure_ascii=False), file_name]
    # resolve catalysis
    if 'enzyme_activities' in content_dict['extracted_object']:
        for catalysis_dict in content_dict['extracted_object']['enzyme_activities']:
            # process subject
            enzyme_id = catalysis_dict['subject']
            enzyme_label = id_mapping[enzyme_id] if enzyme_id in id_mapping else unquote(enzyme_id).replace('AUTO:', '')
            start_vid = get_node_id_by_identifier(node_df, 'enzyme', enzyme_label, enzyme_id, True)
            # process object
            if 'object' not in catalysis_dict:
                continue
            substrate_id = catalysis_dict['object']
            substrate_label = id_mapping[substrate_id] if substrate_id in id_mapping else unquote(substrate_id).replace('AUTO:', '')
            end_vid = get_node_id_by_identifier(node_df, 'substrate', substrate_label, substrate_id)
            # process predicate
            for k, v in catalysis_dict['predicate'].items():
                if v in bp_list:
                    catalysis_dict['predicate'][k] = None
            for attribute in catalysis_attribute:
                if attribute not in catalysis_dict['predicate']:
                    catalysis_dict['predicate'][attribute] = None
            edge_df.loc[len(edge_df)] = ['catalysis', start_vid, end_vid, json.dumps(catalysis_dict['predicate'], ensure_ascii=False), file_name]


if __name__ == '__main__':
    """main program flow"""
    if len(sys.argv) != 2:
        logger.log.info('the args inputing error!')
    args = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(args)

    # the dir path id of yaml
    yaml_dir_path = config['result_storage']['yaml_dir_path']
    logger.log.info(f'yaml_dir_path:{yaml_dir_path}')
    # the tsv file path for storing nodes of graph
    node_tsv_file_path = config['result_storage']['node_tsv_file_path']
    logger.log.info(f'node_tsv_file_path:{node_tsv_file_path}')
    # the tsv file path for storing edges of graph
    edge_tsv_file_path = config['result_storage']['edge_tsv_file_path']
    logger.log.info(f'edge_tsv_file_path:{edge_tsv_file_path}')
    # the file path of error yaml
    error_file_path = config['result_storage']['error_file_path']
    logger.log.info(f'error_file_path:{error_file_path}')
    # the user of nebula
    nebula_user = config['nebula_connect']['user']
    logger.log.info(f'nebula_user:{nebula_user}')
    # the passwd of nebula
    nebula_passwd = config['nebula_connect']['passwd']
    logger.log.info(f'passwd:{nebula_passwd}')
    # the space name of nebula
    nebula_space_name = config['nebula_connect']['space_name']
    logger.log.info(f'space_name:{nebula_space_name}\n')
    # initial nebula op
    op = NebulaOP(nebula_space_name, nebula_user, nebula_passwd)

    # the df for node tsv
    node_df = pd.DataFrame(columns=['node_id', 'type', 'name', 'identifier'])
    # the df for edge tsv
    edge_df = pd.DataFrame(columns=['type', 'start_id', 'end_id', 'properties', 'file_name'])

    # process all yamls
    order_count_int = 0
    for file_name in os.listdir(yaml_dir_path):
        if not file_name.endswith(r'.yaml'):
            logger.log.warning(f'非目标格式跳过:{file_name}')
            continue
        order_count_int = order_count_int + 1
        logger.log.info(f'{order_count_int} -- yaml_file:{file_name}')
        yaml_file_path = os.path.join(yaml_dir_path, file_name)
        try:
            resolve_yaml(yaml_file_path, node_df, edge_df)
        except Exception as e:
            with open(error_file_path, 'a+') as handle:
                datetime = time.strftime('%Y-%m-%d')
                handle.write(f'{datetime} -- {yaml_file_path} -- {e}\n')

    # dump produce and catalysis df to csv
    node_df = node_df.astype(object)
    node_df = node_df.drop_duplicates()
    node_df = node_df.where(node_df.notnull(), None)

    edge_df = edge_df.astype(object)
    edge_df = edge_df.drop_duplicates()
    edge_df = edge_df.where(edge_df.notnull(), None)
    edge_df.insert(loc=0, column='relationship_id', value=edge_df.index + 1)

    logger.log.info(f'node_df:\n{node_df}')
    logger.log.info(f'edge_df:\n{edge_df}')

    node_df.to_csv(node_tsv_file_path, index=False, sep='\t')
    edge_df.to_csv(edge_tsv_file_path, index=False, sep='\t')

    # insert produce stage data of activity to nebula
    # vertex_property_name_list = ['label', 'id']
    # op.insert_vertex('microbiome', vertex_property_name_list, microbiome_data_list)
    # op.insert_vertex('enzyme', vertex_property_name_list, enzyme_data_list)
    # produce_property_name_list = ['temperature', 'ph', 'substrate', 'incubation_period', 'medium', 'moisture', 'carbon_source',
    #                      'nitrogen_source', 'aeration', 'agitation', 'volume', 'effect', 'quantitative_value']
    # op.insert_edge('produce', produce_property_name_list, produce_data_list)
    # # insert catalysis stage data of activity to nebula
    # vertex_property_name_list = ['label', 'id']
    # op.insert_vertex('substrate', vertex_property_name_list, substrate_data_list)
    # catalysis_property_name_list = ['temperature', 'ph', 'ions', 'chemicals', 'substrate', 'effect', 'quantitative_value',
    #                        'substrate_concentration']
    # op.insert_edge('catalysis', catalysis_property_name_list, catalysis_data_list)
    #show produce and catalysis stage datas

    logger.log.info('the main flow is over!')
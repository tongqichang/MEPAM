# !usr/bin/python3
# -*- coding:utf-8 -*-

"""
    script description
        combine the res csv file of grobid and cermine, repalce grobid None value and shorter value with cermine
    input args
        static_configuration_file_path
    output result
        csv file
"""

import os
import sys
import configparser
import pandas as pd

sys.path.append(os.getcwd() + '/../../')
sys.path.append(os.getcwd() + '/../../util/')

from util import logger

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)


def abstract_postprocess_storage(row : pd.Series) -> str:
    """deal with the df after combining grobid and cermine"""
    # storage for abstract of grobid
    logger.log.info(f"abstract_grobid:{row['abstract_content_grobid']}")
    logger.log.info(f"abstract_cermine:{row['abstract_content_cermine']}")
    if row['abstract_content_cermine'] is not None and (row['abstract_content_grobid'] is None or len(row['abstract_content_grobid']) < len(row['abstract_content_cermine'])):
        return row['abstract_content_cermine']
    else:
        return row['abstract_content_grobid']


def result_postprocess_storage(row: pd.Series) -> str:
    # storage for result of grobid
    if row['result_content_cermine'] is not None and (row['result_content_grobid'] is None or len(row['result_content_grobid']) < len(row['result_content_cermine'])):
        return row['result_content_cermine']
    else:
        return row['result_content_grobid']


if __name__ == '__main__':
    """main program flow"""
    if len(sys.argv) != 2:
        logger.log.info('the args inputing error!')
    args = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(args)

    # the batch id of dumping
    batch_id = int(config['data_process']['batch_id'])
    logger.log.info(f'batch_id:{batch_id}')
    # the file path of storaging csv extracted by grobid
    grobid_extracted_csv_file_path = config['data_process']['grobid_extracted_csv_file_path'].format(batch_id=batch_id)
    logger.log.info(f'grobid_extracted_csv_file_path:{grobid_extracted_csv_file_path}')
    # the file path of storaging csv extracted by cermine
    cermine_extracted_csv_file_path = config['data_process']['cermine_extracted_csv_file_path'].format(batch_id=batch_id)
    logger.log.info(f'cermine_extracted_csv_file_path:{cermine_extracted_csv_file_path}')
    # the file path of storaging csv combined
    combined_csv_file_path = config['data_process']['combined_csv_file_path'].format(batch_id=batch_id)
    logger.log.info(f'combined_csv_file_path:{combined_csv_file_path}')

    grobid_df = pd.read_csv(grobid_extracted_csv_file_path, sep='\t')
    cermine_df = pd.read_csv(cermine_extracted_csv_file_path, sep='\t')

    grobid_df['xml_file_name'] = grobid_df['xml_file_name'].apply(lambda x : x.replace(r'.grobid.tei.xml', ''))
    cermine_df['xml_file_name'] = cermine_df['xml_file_name'].apply(lambda x : x.replace(r'.xml', ''))

    df_combined = pd.merge(grobid_df, cermine_df, left_on='xml_file_name', right_on='xml_file_name', how='left', suffixes=['_grobid', '_cermine'])
    df_combined = df_combined.where(df_combined.notnull(), None)
    logger.log.info(f'sample rows of df_combined as test data:\n{df_combined.sample(1)}')

    # apply the storage
    df_combined['abstract_content_grobid'] = df_combined.apply(lambda row : abstract_postprocess_storage(row), axis=1)
    df_combined['result_content_grobid'] = df_combined.apply(lambda row : result_postprocess_storage(row), axis=1)

    res_df = df_combined[['article_title_grobid', 'doi_grobid', 'abstract_source_grobid', 'abstract_content_grobid', 'result_source_grobid', 'result_content_grobid', 'xml_file_name']]
    res_df = res_df.rename(columns = {'article_title_grobid' : 'article_title', 'doi_grobid' : 'doi', 'abstract_source_grobid' : 'abstract_source','abstract_content_grobid' : 'abstract_content', 'result_source_grobid' : 'result_source', 'result_content_grobid' : 'result_content'})

    # output res_df
    if len(res_df) != 0:
        # default value standardization
        res_df = res_df.astype(object)
        res_df = res_df.where(res_df.notnull(), None)
        # print sample data of res_df
        logger.log.info(f'sample rows of res_df as test data:\n{res_df.sample(n=1)}')
        # dump res_df to csv file
        res_df.to_csv(combined_csv_file_path, index=False, sep='\t')
        logger.log.info(f'data has been dumped successfully:{combined_csv_file_path}')
    else:
        logger.log.info('there is no need to dump when res_df is empty.')
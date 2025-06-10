# !usr/bin/python3
# -*- coding:utf-8 -*-

"""
    script description
        evaluate abstarct and result content of xml file word by word
    input args
        static_configuration_file_path
    output result
        excel file
"""

import os
import re
import sys
import configparser
import pandas as pd
sys.path.append(os.getcwd() + '/../../')
sys.path.append(os.getcwd() + '/../../utils/')

from src.utils.logger import logger
from difflib import Differ

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)


class Diff:

    def __init__(self, args : str) -> None:
        """resolve the inputing args"""
        self.config = configparser.ConfigParser()
        self.config.read(args)
        # the batch id of dumping
        self.batch_id = int(self.config['data_process']['batch_id'])
        logger.log.info(f'batch_id:{self.batch_id}')
        # the file path of source
        self.parse_source_file_path = self.config['result_evaluate']['parse_source_file_path']
        logger.log.info(f'parse_source_file_path:{self.parse_source_file_path}')
        # the file path of result
        self.parse_target_file_path = self.config['result_evaluate']['parse_target_file_path'].format(batch_id=self.batch_id)
        logger.log.info(f'parse_target_file_path:{self.parse_target_file_path}')
        # the file_path of metric
        self.parse_metric_file_path = self.config['result_evaluate']['parse_metric_file_path'].format(batch_id=self.batch_id)
        logger.log.info(f'parse_metric_file_path:{self.parse_metric_file_path}\n')


    def run(self) -> None:
        """main program flow"""
        source_df = self.read_data_from_file(self.parse_source_file_path)
        target_df = self.read_data_from_file(self.parse_target_file_path)
        self.anaysis_data(source_df, target_df, self.parse_metric_file_path)


    def read_data_from_file(self, file_path : str) -> pd.DataFrame:
        """process file into dict, each field terminate by ' ' or '\n' """
        if file_path.endswith('xlsx'):
            origin_df = pd.read_excel(file_path)
            origin_df = origin_df.rename(columns={'file_name' : 'pdf_file_name', 'Abstract' : 'abstract_content', 'Results' : 'result_content'})
        else:
            try:
                origin_df = pd.read_csv(file_path, sep='\t')
            except Exception:
                origin_df = pd.read_csv(file_path, sep=',', encoding='iso-8859-1')
        if not origin_df.empty:
            # default value standardization
            origin_df = origin_df.astype('object')
            origin_df = origin_df.where(origin_df.notnull(), None)
            logger.log.info(f'origin_df:\n{origin_df.sample(1)}\n')
            # transform abstract and result content
            for index, row in origin_df.iterrows():
                abstract_content = row['abstract_content']
                result_content = row['result_content']
                if abstract_content is not None:
                    origin_df.loc[index, 'abstract_content'] = re.split(r'(?:\s|\\n)+', abstract_content)
                if result_content is not None:
                    origin_df.loc[index, 'result_content'] = re.split(r'(?:\s|\\n)+', result_content)
            logger.log.info(f'origin_df_processed:\n{origin_df.sample(1)}\n\n')
            return origin_df
        else:
            raise Exception(f'there is an empty input file:{file_path}')


    def anaysis_data(self, source_df : pd.DataFrame, target_df : pd.DataFrame, metric_file_path : str) -> pd.DataFrame:
        """compare source and target data, then generate the statistic"""
        # determine to generate excel or not
        user_input = input(f"this process could cover possible metric excel file?(yes/no):{metric_file_path}\n")

        if user_input == 'yes':
            metric_df = pd.DataFrame(columns=['source_abstract_words_int', 'abstract_match_metric', 'source_result_words_int', 'result_match_metric', 'pdf_file_name'])
            for index, row in source_df.iterrows():
                logger.log.info('comparing······')
                # information from source file
                source_pdf_file_name = row['pdf_file_name']
                if source_pdf_file_name.endswith(r'.pdf'):
                    pdf_file_name = source_pdf_file_name.replace(r'.pdf', '')
                else:
                    pdf_file_name = source_pdf_file_name
                logger.log.info(f'pdf_file_name:{pdf_file_name}')
                source_abstract_content_list = row['abstract_content']
                source_result_content_list = row['result_content']

                # check information validation
                if source_abstract_content_list is None or source_result_content_list is None:
                    raise Exception('abstract or result field of source file is empty!')
                else:
                    source_abstract_words_int = len(source_abstract_content_list)
                    source_result_words_int = len(source_result_content_list)

                # information paried with target file
                pdf_file_name = re.escape(pdf_file_name)
                target_row_paired_list = target_df[target_df['xml_file_name'].str.contains(pdf_file_name)].to_dict(orient='records')

                # compute related metric
                target_abstract_diff_int = 0
                target_result_diff_int = 0
                if len(target_row_paired_list) == 1:
                    differ = Differ()
                    # the similarity metric of abstract content
                    if target_row_paired_list[0]['abstract_content'] is not None:
                        abstract_diff_result = differ.compare(source_abstract_content_list, target_row_paired_list[0]['abstract_content'])
                        for line in abstract_diff_result:
                            if line.startswith(r'- '):
                                target_abstract_diff_int += 1
                    else:
                        target_abstract_diff_int = source_abstract_words_int
                    # the similarity metric of result content
                    if target_row_paired_list[0]['result_content'] is not None:
                        result_diff_result = differ.compare(source_result_content_list, target_row_paired_list[0]['result_content'])
                        for line in result_diff_result:
                            if line.startswith(r'- '):
                                target_result_diff_int += 1
                    else:
                        target_result_diff_int = source_result_words_int
                    abstract_match_metric = round((source_abstract_words_int - target_abstract_diff_int) / source_abstract_words_int, 2)
                    result_match_metric = round((source_result_words_int - target_result_diff_int) / source_result_words_int, 2)
                    # show metric result set
                    metric_df.loc[len(metric_df)] = [int(source_abstract_words_int), abstract_match_metric, int(source_result_words_int), result_match_metric, pdf_file_name]
                    logger.log.info('the file has been compared!\n')
                elif len(target_row_paired_list) == 0:
                    logger.log.error(f'target row does not exist!\n')
                else:
                    raise Exception(f'multiple target row matched!')
            metric_df.to_excel(metric_file_path, sheet_name='Sheet1', index=False)
        else:
            logger.log.info('anaysis process is skipped!')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.log.info('the args inputing error!')
    Diff(sys.argv[1]).run()
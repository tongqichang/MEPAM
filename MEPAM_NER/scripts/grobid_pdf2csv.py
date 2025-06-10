# !usr/bin/python3
# -*- coding:utf-8 -*-

"""
    script description
        parsing pdf into xml format, from which it is able to extract abstract and conclusion
    input args
        static_configuration_file_path
    output result
        data of xml and csv in the respective directroy
"""

import os
import re
import sys
import subprocess
import configparser
import pandas as pd
import xml.etree.ElementTree as et

sys.path.append(os.getcwd() + '/../../')
sys.path.append(os.getcwd() + '/../../utils/')
from src.utils import logger

from grobid_client.grobid_client import GrobidClient

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)


class GrobidP2C:

    def __init__(self, args : str) -> None:
        """resolve the inputing args"""
        self.config = configparser.ConfigParser()
        self.config.read(args)
        # the batch id of dumping
        self.batch_id = int(self.config['data_process']['batch_id'])
        logger.log.info(f'batch_id:{self.batch_id}')
        # the directory path of raw pdf
        self.input_pdf_dir_path = self.config['data_process']['grobid_input_pdf_dir_path'].format(batch_id=self.batch_id)
        logger.log.info(f'input_pdf_dir_path:{self.input_pdf_dir_path}')
        # the directory path of storaging pdf parsed
        self.parsed_pdf_dir_path = self.config['data_process']['grobid_parsed_pdf_dir_path'].format(batch_id=self.batch_id)
        logger.log.info(f'parsed_pdf_dir_path:{self.parsed_pdf_dir_path}')
        # the file path of storaging csv extracted
        self.extracted_csv_file_path = self.config['data_process']['grobid_extracted_csv_file_path'].format(batch_id=self.batch_id)
        logger.log.info(f'extracted_csv_file_path:{self.extracted_csv_file_path}')
        # the file path for setting grobid client
        self.grobid_config_file_path = self.config['data_process']['grobid_config_file_path']
        logger.log.info(f'grobid_config_file_path:{self.grobid_config_file_path}')


    def run(self) -> None:
        """main program flow"""
        # parsing pdf to xml
        self.parse_pdf(self.input_pdf_dir_path, self.parsed_pdf_dir_path, self.grobid_config_file_path)
        # generating res_df by extracting xml
        res_df = self.extract_xml(self.parsed_pdf_dir_path, self.extracted_csv_file_path)
        # dump csv file refer to res_df
        self.dump_data(res_df, self.extracted_csv_file_path)
        logger.log.info('the main flow is over!')


    def parse_pdf(self, input_pdf_dir_path : str, parsed_pdf_dir_path : str, grobid_config_file_path : str) -> None:
        """according to the args, pdfs are parsed by grobid"""
        # determine to perform grobid or not
        user_input = input(f"this process is gonna perform grobid, which means the possible results will be covered?(yes/no):{parsed_pdf_dir_path}\n")

        if user_input == 'yes':
            if not os.path.exists(input_pdf_dir_path):
                logger.log.error(f'the directory of raw pdf is not exist:{input_pdf_dir_path}')
                sys.exit(1)
            os.makedirs(parsed_pdf_dir_path, exist_ok=True)

            try:
                logger.log.info('parsing······')
                # run by sdk
                # client = GrobidClient(config_path=grobid_config_file_path)
                # client.process(service="processFulltextDocument", input_path=input_pdf_dir_path, output=parsed_pdf_dir_path, n=10)

                # run by cli
                grobid_cmd = f'grobid_client --input {input_pdf_dir_path} --output {parsed_pdf_dir_path} --n 64 --config {grobid_config_file_path} processFulltextDocument'
                subprocess.run(grobid_cmd, shell=True, capture_output=True, text=True, check=True)
                logger.log.info('parsing process done!')
            except Exception as err:
                logger.log.error(f'parsing process failed:{err.stderr}')
        else:
            logger.log.info('parsing process is skipped!')


    def extract_xml(self, parsed_pdf_dir_path : str, extracted_csv_file_path : str) -> pd.DataFrame:
        """according to the args, valid data will be extracted from xml"""
        # determine to generate csv or not
        user_input = input(f"ensure the batch id for csv result file?(yes/no):{extracted_csv_file_path}\n")

        # initialize the result df
        res_df = pd.DataFrame(columns=['article_title', 'doi', 'abstract_source', 'abstract_content', 'result_source', 'result_content', 'xml_file_name'])

        if user_input == 'yes':
            logger.log.info('extracting······')
            # get the list of file name
            xml_file_name_list = os.listdir(parsed_pdf_dir_path)
            # extract valid data from xml
            for xml_file_name in xml_file_name_list:
                # filter non-xml file
                if not xml_file_name.endswith('.xml'):
                    continue
                # extract a specific file
                logger.log.info(f'xml file name:{xml_file_name}')
                xml_file_path = os.path.join(parsed_pdf_dir_path, xml_file_name)
                self.extract_field_from_xml(xml_file_name, xml_file_path, res_df)
                logger.log.info(f'the file has been processed.\n')
            logger.log.info('extracting process done!')
        else:
            logger.log.info('extracting process is skipped!')
        return res_df


    def extract_field_from_xml(self, xml_file_name : str, xml_file_path : str, res_df : pd.DataFrame) -> None:
        """extract result fields from one xml, which be added to result df finally"""
        tree = et.parse(xml_file_path)
        root = tree.getroot()
        namespace = {'tei': 'http://www.tei-c.org/ns/1.0'}

        # article_title field
        article_title_et = root.find('.//tei:titleStmt/tei:title', namespace)
        article_title_text = article_title_et.text if article_title_et is not None else None

        # doi field
        doi_et = root.find('.//tei:idno[@type="DOI"]', namespace)
        doi_text = doi_et.text if doi_et is not None else None

        # abstract_source field
        abstract_source_text = './/tei:abstract/tei:div'
        # abstract_content field
        abstract_content_text = None
        valid_abstract_div_content_list = []
        abstract_div_et_list = root.findall(abstract_source_text, namespace)
        for div_et in abstract_div_et_list:
            head_et = div_et.find('tei:head', namespace)
            if head_et is not None and head_et.text:
                valid_abstract_div_content_list.append(head_et.text.strip())
            p_et_list = div_et.findall('tei:p', namespace)
            if p_et_list:
                for p_et in p_et_list:
                    p_content_list = []
                    if p_et.text:
                        p_content_list.append(p_et.text.strip())
                    for ref in p_et:
                        if ref.tail:
                            p_content_list.append(ref.tail.strip())
                    p_text = ' '.join(p_content_list).strip()
                    valid_abstract_div_content_list.append(p_text)
        if valid_abstract_div_content_list:
            abstract_content_text = '\n'.join(valid_abstract_div_content_list).strip()

        # result_source and result_content field
        result_source_text = None
        result_content_text = None
        valid_result_div_content_list = []
        result_div_et_list = root.findall('.//tei:text/tei:body/tei:div', namespace)
        is_write = False
        for div_et in result_div_et_list:
            head_et = div_et.find('tei:head', namespace)
            if head_et is not None and head_et.text:
                # head_et text post-process
                head_text = head_et.text.replace(' ', '').strip().lower()
                # output chapter title of the paper
                logger.log.info(f'result_div_head_text:{head_et.text}')
                # at least has recorded once before quit directly
                if is_write and (re.search('conclusion', head_text) or re.search('discussion', head_text)):
                    break
                # recording start point
                if re.search('result', head_text):
                    is_write = True
                    result_source_text = head_et.text.strip()
                if is_write:
                    valid_result_div_content_list.append(head_et.text.strip())
                    p_et_list = div_et.findall('tei:p', namespace)
                    if p_et_list:
                        for p_et in p_et_list:
                            p_content_list = []
                            if p_et.text:
                                p_content_list.append(p_et.text.strip())
                            for ref in p_et:
                                if ref.tail:
                                    p_content_list.append(ref.tail.strip())
                            p_text = ' '.join(p_content_list).strip()
                            valid_result_div_content_list.append(p_text)
        if valid_result_div_content_list:
            result_content_text = '\n'.join(valid_result_div_content_list).strip()

        # xml file path field
        xml_file_name_text = xml_file_name

        # add all fields to res_df
        res_df.loc[len(res_df)] = [article_title_text, doi_text, abstract_source_text, abstract_content_text, result_source_text, result_content_text, xml_file_name_text]


    def dump_data(self, res_df : pd.DataFrame, extracted_csv_file_path : str) -> None:
        """dump all data to csv file from memory"""
        # check res_df
        if len(res_df) != 0:
            # default value standardization
            res_df = res_df.astype(object)
            res_df = res_df.where(res_df.notnull(), None)
            # print sample data of res_df
            logger.log.info(f'sample rows of res_df as test data:\n{res_df.sample(n=1)}')
            # dump res_df to csv file
            res_df.to_csv(extracted_csv_file_path, index=False, sep='\t')
            logger.log.info(f'data has been dumped successfully:{extracted_csv_file_path}')
        else:
            logger.log.info('there is no need to dump when res_df is empty.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.log.info('the args inputing error!')
    GrobidP2C(sys.argv[1]).run()
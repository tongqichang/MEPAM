# !usr/bin/python3
# -*- coding:utf-8 -*-

"""
    script description
        parsing pdf into xml format, from which it is able to extract abstract and conclusion
    input args
        static_configuration_file_path
    output result
        data of xml and csv in the respective directory
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import configparser
import pandas as pd
import xml.etree.ElementTree as et

sys.path.append(os.getcwd() + '/../../')
sys.path.append(os.getcwd() + '/../../util/')

from util import logger
from concurrent import futures

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)


class CermineP2C:

    def __init__(self, args : str) -> None:
        """resolve the inputing args"""
        self.config = configparser.ConfigParser()
        self.config.read(args)
        # the batch id of dumping
        self.batch_id = int(self.config['data_process']['batch_id'])
        logger.log.info(f'batch_id:{self.batch_id}')
        # the directory path of raw pdf
        self.input_pdf_dir_path = self.config['data_process']['cermine_input_pdf_dir_path']
        logger.log.info(f'input_pdf_dir_path:{self.input_pdf_dir_path}')
        # the directory path of storaging pdf parsed
        self.parsed_pdf_dir_path = self.config['data_process']['cermine_parsed_pdf_dir_path'].format(batch_id=self.batch_id)
        logger.log.info(f'parsed_pdf_dir_path:{self.parsed_pdf_dir_path}')
        # the file path of storaging csv extracted
        self.extracted_csv_file_path = self.config['data_process']['cermine_extracted_csv_file_path'].format(batch_id=self.batch_id)
        logger.log.info(f'extracted_csv_file_path:{self.extracted_csv_file_path}')


    def run(self) -> None:
        """main program flow"""
        # parsing pdf to xml
        self.parse_pdf(self.input_pdf_dir_path, self.parsed_pdf_dir_path)
        # generating res_df by extracting xml
        res_df = self.extract_xml(self.parsed_pdf_dir_path, self.extracted_csv_file_path)
        # dump csv file refer to res_df
        self.dump_data(res_df, self.extracted_csv_file_path)
        logger.log.info('the main flow is over!')


    def parse_pdf(self, input_pdf_dir_path: str, parsed_pdf_dir_path: str) -> None:
        """according to the args, pdfs are parsed by cermine"""
        # determine to perform cermine or not
        user_input = input(f"this process is gonna perform cermine, which means the possible results will be covered?(yes/no):{parsed_pdf_dir_path}\n")

        if user_input == 'yes':
            if not os.path.exists(input_pdf_dir_path):
                logger.log.error(f'the directory of raw pdf is not exist:{input_pdf_dir_path}')
                sys.exit(1)
            os.makedirs(parsed_pdf_dir_path, exist_ok=True)

            logger.log.info('parsing······')

            # create temp dir
            parallelism = int(input("set the parallelism number of cermine:"))
            temp_dir_path_list = [tempfile.mkdtemp() for _ in range(parallelism)]
            logger.log.info(f'temp_dir_path_list:{temp_dir_path_list}\n')

            try:
                # input data slicing
                for i, pdf_file_name in enumerate(os.listdir(input_pdf_dir_path)):
                    pdf_file_path = os.path.join(input_pdf_dir_path, pdf_file_name)
                    os.system(f'cp "{pdf_file_path}" {temp_dir_path_list[i % parallelism]}')
                # running in multiple threads
                with futures.ThreadPoolExecutor(max_workers=parallelism) as executor:
                    to_do = [executor.submit(self.perform_cermine, *[temp_dir_path, parsed_pdf_dir_path]) for temp_dir_path in temp_dir_path_list]
                    for future in futures.as_completed(to_do):
                        future.result()
            except Exception as err:
                logger.log.error(f'parsing process failed:{err}')
                sys.exit(1)
            finally:
                # clear temp dir
                for temp_dir_path in temp_dir_path_list:
                    shutil.rmtree(temp_dir_path)
                logger.log.info('all temp dirs have been cleared!')
        else:
            logger.log.info('parsing process is skipped!')


    def perform_cermine(self, dir_path : str, parsed_pdf_dir_path : str) -> None:
        """use cermine app to parse pdfs of one directory"""
        thread_name = threading.current_thread().name
        cermine_cmd = f'java -cp /Users/lihao/tool/cermine/cermine-impl-1.13-jar-with-dependencies.jar pl.edu.icm.cermine.ContentExtractor -path {dir_path} -outputs jats -override -exts xml -timeout 300'
        logger.log.info(f'{thread_name} -- cermine_cmd:{cermine_cmd}\n')
        subprocess.run(cermine_cmd, shell=True, capture_output=True, text=True, check=True)
        logger.log.info(f'{thread_name} -- parsing process done!')
        # separating all xml from pdf
        all_xml_file_symbol = os.path.join(dir_path, '*.xml')
        cmd_return_code_int = os.system(f'mv {all_xml_file_symbol} {parsed_pdf_dir_path}')
        if cmd_return_code_int != 0:
            logger.log.error(f'{thread_name} -- move all xml file unscessfully:{cmd_return_code_int}')
            sys.exit(1)
        else:
            logger.log.info(f'{thread_name} -- move all xml successfully!')


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

        # article_title field
        article_title_et = root.find('.//article-title')
        article_title_text = article_title_et.text if article_title_et is not None else None

        # doi field
        doi_et = root.find('.//article-id[@pub-id-type="doi"]')
        doi_text = doi_et.text if doi_et is not None else None

        # abstract_source field
        abstract_source_text = './/abstract/p'
        # abstract_content field
        abstract_content_text = None
        valid_abstract_p_content_list = []
        abstract_p_et_list = root.findall(abstract_source_text)
        for p_et in abstract_p_et_list:
            if p_et.text:
                valid_abstract_p_content_list.append(p_et.text.strip())
        if valid_abstract_p_content_list:
            abstract_content_text = '\n'.join(valid_abstract_p_content_list).strip()

        # result_source and result_content field
        result_source_text = None
        result_content_text = None
        valid_result_sec_content_list = []
        result_sec_et_list = root.findall('.//body/sec')
        start_write = False
        end_write = False
        for sec_et in result_sec_et_list:
            for child_et in sec_et:
                if start_write and end_write:
                    continue
                if child_et.tag == 'title' and child_et.text:
                    head_text = child_et.text.replace(' ', '').strip().lower()
                    logger.log.info(f'result_sec_head_text:{child_et.text}')
                    if start_write and (re.search('conclusion', head_text) or re.search('discussion', head_text)):
                        end_write = True
                    # recording start point
                    if not start_write and re.search('result', head_text):
                        start_write = True
                        result_source_text = child_et.text.strip()
                    if start_write and not end_write:
                        valid_result_sec_content_list.append(child_et.text.strip())
                elif child_et.tag == 'p' and start_write:
                    p_content_list = []
                    if child_et.text:
                        p_content_list.append(child_et.text.strip())
                    for xref in child_et:
                        if xref.text:
                            p_content_list.append(xref.text.strip())
                        if xref.tail:
                            p_content_list.append(xref.tail.strip())
                    p_text = ' '.join(p_content_list).strip()
                    valid_result_sec_content_list.append(p_text)
                elif child_et.tag == 'sec':
                    head_et = child_et.find('title')
                    if head_et is not None and head_et.text:
                        head_text = head_et.text.replace(' ', '').strip().lower()
                        logger.log.info(f'result_sec_sec_head_text:{head_et.text}')
                        if start_write and (re.search('conclusion', head_text) or re.search('discussion', head_text)):
                            end_write = True
                        # recording start point
                        if not start_write and re.search('result', head_text):
                            start_write = True
                            result_source_text = head_et.text.strip()
                        if start_write and not end_write:
                            self.sec_extract(child_et, valid_result_sec_content_list)
        if valid_result_sec_content_list:
            result_content_text = '\n'.join(valid_result_sec_content_list).strip()

        # xml file path field
        xml_file_name_text = xml_file_name

        # add all fields to res_df
        res_df.loc[len(res_df)] = [article_title_text, doi_text, abstract_source_text, abstract_content_text, result_source_text, result_content_text, xml_file_name_text]


    def sec_extract(self, element : et.ElementTree, valid_result_sec_content_list : list) -> None:
        """recursive extracting text under sec label, each sec has possible title label、p label and even sec label"""
        for child_et in element:
            if child_et.tag == 'title' and child_et.text:
                valid_result_sec_content_list.append(child_et.text.strip())
            elif child_et.tag == 'p':
                    p_content_list = []
                    if child_et.text:
                        p_content_list.append(child_et.text.strip())
                    for xref in child_et:
                        if xref.text:
                            p_content_list.append(xref.text.strip())
                        if xref.tail:
                            p_content_list.append(xref.tail.strip())
                    p_text = ' '.join(p_content_list).strip()
                    valid_result_sec_content_list.append(p_text)
            elif child_et.tag == 'sec':
                self.sec_extract(child_et, valid_result_sec_content_list)
            else:
                raise Exception(f'find the label unknown:{child_et.tag}')


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
    CermineP2C(sys.argv[1]).run()
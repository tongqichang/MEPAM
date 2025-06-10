

"""
script description
    evaluate ner result of yaml file entity by entity
input args
    static_configuration_file_path
output result
    excel file of result and txt file of error
"""

import os
import sys
import time
import yaml
import configparser
import pandas as pd
import litellm
from litellm import completion
from litellm.caching.caching import Cache
from tqdm.contrib.concurrent import process_map
import urllib.parse
import logging
from functools import partial
from sklearn.metrics import f1_score
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)


VALID_PRODUCTION = [
    "temperature",
    "ph",
    "substrate",
    "incubation_period",
    "moisture",
    "carbon_source",
    "nitrogen_source",
    "aeration",
    "agitation",
    "volume",
    "effect",
    "quantitative_value",
    "quantitative_type",
]
VALID_ACTIVITY = [
    "ph",
    "temperature",
    "ions",
    "surfactants",
    "chemicals",
    "effect",
    "quantitative_value",
    "quantitative_type",
]

DELIMITER_TEXT = "_under_"

class Logger:
    def __init__(self, name="MyLogger"):
        # Set up the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(ch)

    @property
    def log(self):
        return self.logger


logger = Logger()
litellm.cache = Cache(type="disk", disk_cache_dir="/tmp/.litellm_cache")


class SemanticConsistencyByLLM:
    def __init__(self, model: str, base_url: str, **model_kwargs):
        # self.llm = Ollama(model=model, base_url=base_url, request_timeout=120.0)
        self.model = model
        self.base_url = base_url
        self.timeout = 120

        # self.prompt_template = """Determine whether the meanings of the following two texts are consistent. Must respond with only Yes or No.: 1. {}; 2. {}."""

        self.prompt_template = "Compare the following two texts for meaning and intent. Respond with 'yes' if they are essentially the same, and 'no' if they are different. Text 1: {}; Text 2: {}"

    def compare(self, text1: str, text2: str):
        # resp = self.llm.complete(self.prompt_template.format(text1, text2))
        resp = completion(
            model=self.model,
            base_url=self.base_url,
            timeout=self.timeout,
            messages=[
                {"role": "user", "content": self.prompt_template.format(text1, text2)}
            ],
            caching=True,
        )
        resp = str(resp.choices[0].message.content)
        print("Response: ", resp)
        if resp.lower().strip() == "yes" or resp.lower().strip().startswith("yes"):
            return True
        elif resp.lower().strip() == "no" or resp.lower().strip().startswith("no"):
            return False
        else:
            return False
            # assert False, f"Unexpected llm response, please check: {resp}"


def data_analysis_single(item, model, base_api_url):
    sc = SemanticConsistencyByLLM(model=model, base_url=base_api_url)
    source_filename, source_entity_list, target_entity_list = item
    correct_entity_num = 0
    # precomputing entites of source
    source_entity_num = len(source_entity_list)
    # precomputing entites of target
    target_entity_num = len(target_entity_list)
    # fuzzy matching
    for source_entity in source_entity_list:
        for target_entity in target_entity_list[:]:
            if "microbiome" in source_entity and "microbiome" not in target_entity:
                continue
            elif "enzyme" in source_entity and "enzyme" not in target_entity:
                continue
            elif "substrate" in source_entity and "substrate" not in target_entity:
                continue
            elif "produce" in source_entity:
                if "produce" not in target_entity:
                    continue
                else:
                    k = source_entity.split("_under_")[1].strip().split("=")[0]
                    if k not in target_entity:
                        continue
            elif "catalysis" in source_entity:
                if "catalysis" not in target_entity:
                    continue
                else:
                    k = source_entity.split("_under_")[1].strip().split("=")[0]
                    if k not in target_entity:
                        continue
            # similarity verification
            is_same_bool = sc.compare(source_entity, target_entity)
            logger.log.info(f"{source_entity} -- {target_entity} {is_same_bool}")
            if is_same_bool:
                correct_entity_num = correct_entity_num + 1
                target_entity_list.remove(target_entity)
    # avoid two metrics exceeding 1
    if correct_entity_num > source_entity_num:
        correct_entity_num = source_entity_num
    # all_correct_entity_num = all_correct_entity_num + correct_entity_num
    # computing one yaml metric
    ner_recall_metric = (
        round(correct_entity_num / source_entity_num, 2)
        if int(source_entity_num) != 0
        else 0
    )
    ner_precision_metric = (
        round(correct_entity_num / target_entity_num, 2)
        if int(target_entity_num) != 0
        else 0
    )
    if ner_precision_metric + ner_recall_metric == 0:
        f1_score_metric = 0  # 当精确度和召回率都为零时，F1分数定义为0
    else:
        f1_score_metric = round(
            2 * (ner_precision_metric * ner_recall_metric) / (ner_precision_metric + ner_recall_metric), 2)
    return [
        source_filename,
        int(source_entity_num),
        int(target_entity_num),
        int(correct_entity_num),
        ner_recall_metric,
        ner_precision_metric,
        f1_score_metric,
    ]


class Diff:
    def __init__(self, args: str) -> None:
        """resolve the inputing args"""
        self.config = configparser.ConfigParser()
        self.config.read(args)
        # the batch id of dumping
        self.batch_id = int(self.config["data_process"]["batch_id"])
        self.model = str(self.config["data_process"]["model"])
        self.base_api_url = str(self.config["data_process"]["base_api_url"])
        self.max_workers = int(self.config["data_process"]["max_workers"])

        logger.log.info(f"batch_id:{self.batch_id}")
        # the dir path of source
        self.ner_source_dir_path = self.config["result_evaluate"]["ner_source_dir_path"]
        logger.log.info(f"ner_source_dir_path:{self.ner_source_dir_path}")
        # the dir path of result
        self.ner_target_dir_path = self.config["result_evaluate"]["ner_target_dir_path"]
        logger.log.info(f"ner_target_dir_path:{self.ner_target_dir_path}")
        # the file path of metric
        self.ner_metric_file_path = self.config["result_evaluate"][
            "ner_metric_file_path"
        ].format(batch_id=self.batch_id)
        logger.log.info(f"ner_metric_file_path:{self.ner_metric_file_path}")
        # the file path of error
        self.ner_error_file_path = self.config["result_evaluate"][
            "ner_error_file_path"
        ].format(batch_id=self.batch_id)
        logger.log.info(f"ner_error_file_path:{self.ner_error_file_path}\n")

    def run(self) -> None:
        """main program flow"""
        # process all yaml files in source
        source_dict = self.read_data_from_dir("source", self.ner_source_dir_path)
        logger.log.info(source_dict)
        # process all yaml files in target
        target_dict = self.read_data_from_dir("target", self.ner_target_dir_path)
        logger.log.info(target_dict)
        # self.anaysis_data(source_dict, target_dict, self.ner_metric_file_path)
        self.anaysis_data_para(source_dict, target_dict, self.ner_metric_file_path)

    def parse_value(self, value):
        return urllib.parse.unquote(str(value).lower().lstrip("auto:"))

    def check_valid(self, text):
        return (
            urllib.parse.unquote(str(text).lower())
            not in ["not provided", "not specified"]
        ) and (text is not None)

    def read_data_from_dir(self, pos: str, dir_path: str) -> dict[str:list]:
        """process entities of all files into dict,and key is filename,value is entity list"""
        entity_dict = {}
        # generate filename->entities dict
        for filename in os.listdir(dir_path):
            yaml_file_path = os.path.join(dir_path, filename)
            # standardize filename
            if filename.endswith(r".yml"):
                filename = filename.replace(r".yml", r".yaml")
            else:
                # filter non-yaml file
                if not filename.endswith(r".yaml"):
                    self.record_error(pos, filename, "file type error")
                    continue
            with open(yaml_file_path, "r") as handle:
                content = handle.read()
                # filter content format
                if (
                    "has_catalyst_condition" in content
                    or "has_production_condition" in content
                ):
                    self.record_error(pos, filename, "content format error")
                    continue
                # filter null subject file in source
                # if pos == 'source' and 'not provided' in content.lower() or 'not specified' in content.lower():
                #     self.record_error(pos, filename, 'non-subject error')
                #     continue
            try:
                # read yaml content into dict
                with open(yaml_file_path, "r", encoding="utf-8") as handle:
                    # safe load content
                    content_dict = yaml.safe_load(handle)
                    if "input_text" in content_dict:
                        del content_dict["input_text"]
            except FileNotFoundError:
                raise Exception(f"YAML 文件不存在: {yaml_file_path}")
            except yaml.YAMLError as e:
                self.record_error(pos, filename, f"load yaml error: {e}")
            except Exception as e:
                self.record_error(pos, filename, f"Unexpected error: {e}")
                continue

            entity_list = []

            # filter non-extracted_object and non-named_entities
            if (
                "extracted_object" not in content_dict
                or not content_dict["extracted_object"]
            ):
                self.record_error(pos, filename, "non-extracted_object error")
                continue

            # id mapping
            id_mapping = {}
            if "named_entities" in content_dict and isinstance(
                content_dict["named_entities"], list
            ):
                for entities_dict in content_dict["named_entities"]:
                    id_mapping[entities_dict["id"]] = entities_dict["label"]
            # filter enzyme_productions and enzyme_activities dict
            level1_keyword_list = ["enzyme_productions", "enzyme_activities"]
            for level1_keyword in level1_keyword_list:
                if (
                    level1_keyword not in content_dict["extracted_object"]
                    or not content_dict["extracted_object"][level1_keyword]
                ):
                    self.record_error(pos, filename, f"non-{level1_keyword} dict error")
                    continue
                for item_dict in content_dict["extracted_object"][level1_keyword]:
                    subject, _obj = None, None
                    # filter subject and object item
                    level2_keyword_list = ["subject", "object", "predicate"]
                    for level2_keyword in level2_keyword_list:
                        # filter null subject and object
                        if level2_keyword in item_dict:
                            # if str(item_dict[level2_keyword]).lower() in ['not provided', 'not%20provided'] or not item_dict[level2_keyword]:
                            if (
                                not self.check_valid(item_dict[level2_keyword])
                                or not item_dict[level2_keyword]
                            ):
                                self.record_error(
                                    pos, filename, f"null {level2_keyword} item skips"
                                )
                                continue
                        else:
                            # filter non-subject and object
                            self.record_error(
                                pos, filename, f"non-{level2_keyword} item error"
                            )
                            continue
                        # process entity dict into str
                        if level2_keyword in ["subject", "object"]:
                            value = item_dict[level2_keyword]
                            print(value)
                            print(filename)
                            value = str(id_mapping.get(value, value))

                            if level1_keyword == "enzyme_productions":
                                if level2_keyword == "subject":
                                    subject = self.parse_value(value)
                                    entity_list.append("microbiome=" + subject)
                                else:
                                    _obj = self.parse_value(value)
                                    entity_list.append("enzyme=" + _obj)
                            else:
                                if level2_keyword == "subject":
                                    subject = self.parse_value(value)
                                    entity_list.append("enzyme=" + subject)
                                else:
                                    _obj = self.parse_value(value)
                                    entity_list.append("substrate=" + _obj)
                        else:
                            if level2_keyword == "predicate":
                                if level1_keyword == "enzyme_productions" and (
                                    not self.check_valid(subject)
                                    or not self.check_valid(_obj)
                                ):
                                    self.record_error(
                                        pos,
                                        filename,
                                        f"null {level1_keyword} item skips",
                                    )
                                    continue
                                # activity 的逻辑对object不做要求
                                if level1_keyword == "enzyme_activities" and (
                                    not self.check_valid(_obj)
                                ):
                                    self.record_error(
                                        pos,
                                        filename,
                                        f"null {level1_keyword} item skips",
                                    )
                                    continue
                                relation_dict = item_dict[level2_keyword]
                                for k, v in relation_dict.items():
                                    if k == "quantitative_type":
                                        continue
                                    if self.check_valid(v):
                                        if (
                                            level1_keyword == "enzyme_productions"
                                            and k in VALID_PRODUCTION
                                        ):
                                            entity_list.append(
                                                f"{subject} produce {_obj} {DELIMITER_TEXT} {k}="
                                                + str(v)
                                            )
                                        elif k in VALID_ACTIVITY:
                                            entity_list.append(
                                                f"{subject} catalysis {_obj} {DELIMITER_TEXT} {k}="
                                                + str(v)
                                            )
            if entity_list:
                entity_dict[filename] = entity_list
        return entity_dict

    def record_error(self, pos: str, filename: str, msg: str) -> None:
        """output error info to local txt file"""
        with open(self.ner_error_file_path, "a+") as handle:
            timestamp = time.strftime("%Y%m%d-%H:%M:%S")
            handle.write(f"{timestamp}[ERROR] {pos} -- {filename} -- {msg}\n")
    
    def anaysis_data_para(
        self, source_dict: dict, target_dict: dict, metric_file_path: str
    ) -> pd.DataFrame:
        """according to the filename, do fuzzy matching and similarity verification with two dicts"""
        # all entities of source
        all_source_entity_num = 0
        # all entities of target
        all_target_entity_num = 0
        # all correct recognize entities of target
        all_correct_entity_num = 0
        # total metric result dataframe
        # metric_df = pd.DataFrame(columns=['yaml_file', 'source_entity_num', 'target_entity_num', 'correct_entity_num', 'ner_recall_metric', 'ner_precision_metric'])

        entities = []
        for source_filename, source_entity_list in source_dict.items():
            logger.log.info(f"{source_filename} is processing···")
            # match yaml file
            target_entity_list = target_dict.get(source_filename, [])
            # avoid target metric is 0
            if not target_entity_list:
                continue
            # precomputing entites of source
            source_entity_num = len(source_entity_list)
            all_source_entity_num = all_source_entity_num + source_entity_num
            # precomputing entites of target
            target_entity_num = len(target_entity_list)
            all_target_entity_num = all_target_entity_num + target_entity_num
            entities.append((source_filename, source_entity_list, target_entity_list))

        res = process_map(
            partial(
                data_analysis_single, model=self.model, base_api_url=self.base_api_url
            ),
            entities,
            max_workers=self.max_workers,
        )
        print("Response: ", res)
        for _res in res:
            all_correct_entity_num += _res[3]
        # computing all yamls metric
        ner_recall_metric = (
            round(all_correct_entity_num / all_source_entity_num, 2)
            if int(all_source_entity_num) != 0
            else 0
        )
        ner_precision_metric = (
            round(all_correct_entity_num / all_target_entity_num, 2)
            if int(all_target_entity_num) != 0
            else 0
        )
        if ner_precision_metric + ner_recall_metric == 0:
            f1_score_metric = 0  # 当精确度和召回率都为零时，F1分数定义为0
        else:
            f1_score_metric = round(
                2 * (ner_precision_metric * ner_recall_metric) / (ner_precision_metric + ner_recall_metric), 2)
        res.append(
            [
                "all yamls",
                int(all_source_entity_num),
                int(all_target_entity_num),
                int(all_correct_entity_num),
                ner_recall_metric,
                ner_precision_metric,
                f1_score_metric,
            ]
        )

        metric_df = pd.DataFrame(
            res,
            columns=[
                "yaml_file",
                "source_entity_num",
                "target_entity_num",
                "correct_entity_num",
                "ner_recall_metric",
                "ner_precision_metric",
                "f1_score_metric",
            ],
        )

        metric_df.to_excel(metric_file_path, sheet_name="Sheet1", index=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.log.info("the args inputing error!")
    Diff(sys.argv[1]).run()

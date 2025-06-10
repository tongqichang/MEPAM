# -*- coding:utf-8 -*-
import os
import click
import json  
from openai import OpenAI
from tqdm.contrib.concurrent import process_map
from functools import partial
from pathlib import Path
import time
system_prompt = """
The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format by following the scheme provided bellow. 

EXAMPLE INPUT: 
The previously reported functional expression of the gamma-isoenzyme of pig liver carboxylesterase (gamma-rPLE) in Pichia pastoris is hampered by the small amount of active enzyme formed. Earlier attempts for expression in Escherichia coli failed completely and not even inactive protein was detected. The lack of glycosylation ability of E. coli was ruled out as a possible reason, as it could be shown in this work that deglycosylated PLE also is active. Expression of gamma-rPLE was studied using a range of E. coli strains with careful design of the constructs used and control of the cultivation conditions. Indeed, expression in E. coli strains Rosetta, Origami and Rosetta-gami was successful, but the majority of enzymes was present as inclusion bodies and only little soluble but inactive protein was detected. Denaturation and refolding of inclusion bodies failed. However, with the E. coli strain Origami, coexpressing the molecular chaperones GroEL und GroES, a functional expression of gamma-rPLE was possible. The recombinant enzyme was released by cell disruption and subjected to His-tag purification. The purified esterase had a specific activity of 92 U mg(-1) protein and a V (max)/K (m) value of 10.8x10(-3) min(-1) towards p-nitrophenyl acetate. Activity staining of native polyacrylamide gels gave a single band at 175 kDa with esterolytic activity indicating a trimeric form of gamma-rPLE ( approximately 60 kDa per monomer). gamma-rPLE was biochemically characterized and its properties were compared to the enzyme previously expressed in P. pastoris. pH and temperature profiles were identical and highest activity was found at pH 8-8.5 and 60 degrees C, respectively. In the kinetic resolution of (R,S)-1-phenyl-2-butyl acetate with esterase from both expression hosts, similar enantioselectivities (E=50) were found.

EXAMPLE JSON OUTPUT:
{
    "microbiome":
    [
        "Escherichia coli"
    ],
    "enzyme":
    [
        "B3-rPLE"
    ],
    "substrate":
    [
        "p-nitrophenyl acetate",
        "ethyl caprylate",
        "tributyrin",
        "methyl acetate"
    ],
    "enzyme_productions":
    [
        {
            "subject": "Escherichia coli",
            "predicate":
            {
                "temperature": "60 C",
                "ph": "8.0",
                "effect": "increase"
            },
            "object": "B3-rPLE"
        }
    ],
    "enzyme_activities":
    [
        {
            "subject": "B3-rPLE",
            "predicate":
            {
                "ph": "8.0",
                "temperature": "60 C",
                "effect": "maximum"
            },
            "object": "p-nitrophenyl acetate"
        },
        {
            "subject": "B3-rPLE",
            "predicate":
            {
                "temperature": "60 C",
                "effect": "maximum"
            },
            "object": "tributyrin"
        }
    ]
}


SCHEME:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MicrobiomeEnzymeSchema",
  "type": "object",
  "properties": {
    "microbiome": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Represents various microbiomes, from the evidence of their taxonomic classifications and roles in enzyme fermentation."
    },
    "enzyme": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Represents enzymes, from the evidence of their functions, classifications, and roles in biochemical reactions during fermentation."
    },
    "substrate": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Represents its characteristics as a lignocellulosic biomass and its potential as a carbon source for microbial fermentation processes."
    },
    "enzyme_productions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "subject": {
            "type": "string",
            "description": "Specify the specific microbiome involved in the fermentation process."
          },
          "predicate": {
            "type": "object",
            "properties": {
              "temperature": {
                "type": "string",
                "description": "Indicate the temperature for fermentation, specifying the range if applicable. If not specified, use 'not specified'."
              },
              "ph": {
                "type": "string",
                "description": "Indicate the pH level of the fermentation medium, specifying the range if applicable. If not specified, use 'not specified'."
              },
              "substrate": {
                "type": "string",
                "description": "Indicate the type of substrate utilized in fermentation. If not specified, use 'not specified'."
              },
              "incubation_period": {
                "type": "string",
                "description": "Indicate the duration of fermentation, specifying the unit of time (e.g., hours, days). If not specified, use 'not specified'."
              },
              "medium": {
                "type": "string",
                "description": "Indicate the type of growth medium used during fermentation, including its composition if relevant. If not specified, use 'not specified'."
              },
              "moisture": {
                "type": "string",
                "description": "Indicate the moisture level during fermentation, stating the measurement method if applicable. If not specified, use 'not specified'."
              },
              "carbon_source": {
                "type": "string",
                "description": "Indicate the source of carbon in the medium, describing its form (e.g., glucose, sucrose). If not specified, use 'not specified'."
              },
              "nitrogen_source": {
                "type": "string",
                "description": "Indicate the nitrogen source used in the fermentation process, including its type if applicable. If not specified, use 'not specified'."
              },
              "aeration": {
                "type": "string",
                "description": "Indicate the oxygen level in percentage or dissolved oxygen (DO), (e.g., 60% DO, 60 DO). If not specified, use 'not specified'."
              },
              "agitation": {
                "type": "string",
                "description": "Indicate the agitation conditions used, including speed and duration if applicable (e.g. 1000 rpm). If not specified, use 'not specified'."
              },
              "volume": {
                "type": "string",
                "description": "Indicate the total volume of the fermentation medium, including the unit of measurement (e.g., liters). If not specified, use 'not specified'."
              },
              "effect": {
                "type": "string",
                "description": "Classify the effect on production as 'increase', 'decrease', or 'optimum'. This field must be specified."
              },
              "quantitative_value": {
                "type": "string",
                "description": "Include a quantitative measure of production yield with its unit (e.g., grams per liter). If not specified, use 'not specified'."
              }
            },
            "required": ["effect"],
            "description": "Specify the production conditions, including temperature, pH, substrate, incubation period, medium, moisture, carbon source, nitrogen source, aeration, agitation, volume, effect, production yield."
          },
          "object": {
            "type": "string",
            "description": "Specify the enzyme produced by the microbiome."
          }
        },
        "required": ["subject", "predicate", "object"],
        "description": "A triple where the subject is a microbiome species, the object is an enzyme produced by that microbiome, and the predicate describes the production conditions."
      }
    },
    "enzyme_activities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "subject": {
            "type": "string",
            "description": "Specify the enzyme involved in the catalysis."
          },
          "predicate": {
            "type": "object",
            "properties": {
              "ph": {
                "type": "string",
                "description": "Indicate the pH level of the enzyme activity, specifying the range if applicable. If not specified, use 'not specified'."
              },
              "temperature": {
                "type": "string",
                "description": "Indicate the temperature for enzyme activity, specifying the range if applicable. If not specified, use 'not specified'."
              },
              "ions": {
                "type": "string",
                "description": "List any metal ions that influence enzyme activity. If not specified, use 'not specified'."
              },
              "surfactants": {
                "type": "string",
                "description": "List any surfactants affecting enzyme activity. If not specified, use 'not specified'."
              },
              "chemicals": {
                "type": "string",
                "description": "List chemicals that impact enzyme activity. If not specified, use 'not specified'."
              },
              "effect": {
                "type": "string",
                "description": "Classify the effect on enzyme activity as 'enhance', 'inhibit', 'stable', 'maximum', or 'not significantly inhibited'. This field must be specified."
              },
              "quantitative_value": {
                "type": "string",
                "description": "Include a quantitative measure of enzyme activity with its unit (e.g., activity units per milliliter). If not specified, use 'not specified'."
              },
              "substrate_concentration": {
                "type": "string",
                "description": "Indicate the concentration of the substrate, specifying the range if applicable. If not specified, use 'not specified'."
              }
            },
            "required": ["effect"],
            "description": "Specify the catalytic conditions, including pH, temperature, ions, surfactants, chemicals, effect, enzyme activity."
          },
          "object": {
            "type": "string",
            "description": "Specify the substrate being catalyzed by the enzyme."
          }
        },
        "required": ["subject", "predicate", "object"],
        "description": "A triple where the subject is an enzyme, the object is the substrate that the enzyme catalyzes, and the predicate describes the catalytic conditions."
      }
    }
  },
  "required": ["microbiome", "enzyme", "substrate", "enzyme_productions", "enzyme_activities"]
}
"""


def format_json(content):
    start_index = content.find("{")
    end_index = content.rfind("}") + 1
    json_content = content[start_index:end_index]
    return json.loads(json_content)


def process_file(
    file_path: str, output_folder: str, api_key: str, base_url: str, model: str
):
    """
    """

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    user_prompt = ""

    with open(file_path, "r", encoding="utf-8") as f:
        user_prompt = f.read()

    if not user_prompt:
        return False
    max_retries = 5  
    retries = 0
    test = None
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while retries < max_retries and test is None:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=4096,
            )
            time.sleep(10) 
            test = format_json(response.choices[0].message.content)
        except Exception as e:
            print(f"Error formatting JSON: {e}")
            print(f"Response content: {response.choices[0].message.content}")
            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")
            time.sleep(10)  
    fn = Path(file_path).stem
    output_file_path = os.path.join(output_folder, f"{fn}.yaml")
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"extracted_object":test},
            f,
            ensure_ascii=False,
            indent=4,
        )


    return True


@click.command()
@click.option("--input_folder", required=True, help="Path to the input folder.")
@click.option("--output_folder", required=True, help="Path to the output folder.")
@click.option("--api_key", required=True, help="API key for OpenAI.")
@click.option("--base_url", required=True, help="Base URL for the OpenAI API.")
@click.option("--model", required=True, help="Model to use for processing.")
def batch_process(input_folder, output_folder, api_key, base_url, model):
    """
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_paths = []
    

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            file_paths.append(os.path.join(input_folder, file_name))

    for file_path in file_paths:
        output_file_name = os.path.basename(file_path).replace(".txt", ".yaml")
        output_file_path = os.path.join(output_folder, output_file_name)
        if os.path.exists(output_file_path):

                print(f"Skipping {file_path} as {output_file_path} already exists.")
                continue
        
        process_file(file_path, output_folder, api_key, base_url, model)


if __name__ == "__main__":
    batch_process()

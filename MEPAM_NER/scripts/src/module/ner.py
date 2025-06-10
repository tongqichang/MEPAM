
from dspy.functional import FunctionalModule, predictor, cot
from devtools import pprint
from src.signatures.enzyme import EnzymeEntities, EnzymeMetaData, EnzymeMetaDatas, TextToEnzymeEntities
from src.utils.enyzme import parse_context

class ExtractEnzymeEntities(FunctionalModule):

    def __init__(self, temperature: int = 0, seed: int = 123):
        super().__init__()
        self.temperature = temperature
        self.seed = seed

    @predictor
    def extract_enzyme_context(self, text: str) -> EnzymeMetaDatas:
        """You are a enzyme AI assistant. Your task is to extract the fermentation conditions for micrbiome and enzyme pair and the catalyst conditions for enzyme and substrate and the reasoning for why the extracted conditions are grouped. Multiple pairs are allowed. If you cannot extract the entity or the paring not exsit, add null
        """
        pass


    @cot
    def extract_enzyme_cotnext_cot(self, text: str) -> EnzymeMetaDatas:
        """You are a enzyme AI assistant. Your task is to extract the fermentation conditions for micrbiome and enzyme pair and the catalyst conditions for enzyme and substrate pair and the reasoning for why the extracted conditions are grouped. Multiple pairs are allowed.  If you cannot extract the entity or the paring not exsit, add null
        """
        pass


    @predictor
    def extract_enzyme_entities(self, text: str) -> EnzymeEntities:
        """You are a enzyme AI assistant. Your task is to extract the fermentation conditions for micrbiome and enzyme pair and the catalyst conditions for enzyme and substrate pair from a text."""
        pass


    def forward(self, text: str) -> EnzymeEntities:
        enzyme_context = self.extract_enzyme_context(text=text)
        pased_context = parse_context(enzyme_context.context)
        enzyme_entities = self.extract_enzyme_entities(text=pased_context)

        return enzyme_entities

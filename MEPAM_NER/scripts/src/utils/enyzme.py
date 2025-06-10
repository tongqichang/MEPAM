from src.signatures.enzyme import EnzymeMetaDatas


def parse_context(enzyme_context: EnzymeMetaDatas) -> str:
    context_str = ""
    for context in enzyme_context:
        context: EnzymeMetaDatas
        context_str += context.model_dump_json(indent=4) + "\n"
    return context_str

def validate_entities(example, pred, trace=None):
    """Check if both objects are equal"""
    return example.entities == pred
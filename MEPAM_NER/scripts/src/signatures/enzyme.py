import dspy
from pydantic import BaseModel, Field
from typing import List, Optional

class EnzymeMetaData(BaseModel):
    reason: str = Field(
        description="Provide a clear justification for why the specified fermentation and catalysis conditions are appropriate."
    )
    
    fermentation_conditions: str = Field(
        description=(
            "When detailing fermentation conditions for enzyme production, please provide detailed information on the following aspects:\n"
            "1. **Microbiome**: Specify the exact microbiome involved in the fermentation process, including its taxonomic classification if available.\n"
            "2. **Enzyme**: Specify the specific enzyme produced by the microbiome, including its function and classification.\n"
            "3. **Temperature**: Indicate the temperature for fermentation, specifying the range if applicable.\n"
            "4. **pH**: Indicate the pH level of the fermentation medium, specifying the range if applicable.\n"
            "5. **Substrate**: Indicate the type of substrate utilized, including its source and characteristics.\n"
            "6. **Incubation Period**: Indicate the duration of fermentation, specifying the unit of time (e.g., hours, days).\n"
            "7. **Medium**: Indicate the type of growth medium used during fermentation, including its composition if relevant.\n"
            "8. **Moisture**: Indicate the moisture level during fermentation, stating the measurement method if applicable.\n"
            "9. **Carbon Source**: Indicate the source of carbon in the medium, describing its form (e.g., glucose, sucrose).\n"
            "10. **Nitrogen Source**: Indicate the nitrogen source used in the fermentation process, including its type.\n"
            "11. **Aeration**: Indicate the aeration conditions applied during fermentation, including any specific methods (e.g., shaking, bubbling).\n"
            "12. **Agitation**: Indicate the agitation conditions used, including speed and duration.\n"
            "13. **Volume**: Indicate the total volume of the fermentation medium, including the unit of measurement (e.g., liters).\n"
            "14. **Effect**: Classify the overall effect on production as 'increase', 'decrease', or 'optimum'.\n"
            "15. **Production Yield**: Include a quantitative measure of production yield with its unit (e.g., grams per liter).\n"
            "\n"
            "Notes:\n"
            "- Conditions should be grouped by paired microbiome, enzyme, and effect. If unspecified value exists for these key, entry must be escaped.\n"
            "- Grouped conditions under each entry must have the same effect; otherwise, separate them into distinct entries.\n"
            "- If multiple effects are present for the same condition, separate them into distinct entries.\n"
            "- Ensure that all fields, except for Microbiome, Enzyme, and Effect, have a single valid value."
        )
    )
    
    catalysis_conditions: str = Field(
        description=(
            "When detailing catalysis conditions for enzyme activity, please provide comprehensive information on the following aspects:\n"
            "1. **Enzyme**: Specify the enzyme involved in the catalysis, including its function and classification.\n"
            "2. **Substrate**: Specify the substrate being catalyzed, detailing its characteristics and source.\n"
            "3. **pH**: Indicate the pH level or range for enzyme activity, specifying the optimum if applicable.\n"
            "4. **Temperature**: Indicate the temperature or range for enzyme activity, noting the optimum if applicable.\n"
            "5. **Ions**: List any metal ions that influence enzyme activity, specifying their concentrations if relevant.\n"
            "6. **Surfactants**: Specify any surfactants affecting enzyme activity, including their types and concentrations.\n"
            "7. **Chemicals**: List any chemicals that impact enzyme activity, providing details on their role and concentration.\n"
            "8. **Effect**: Classify the effect on enzyme activity as 'enhance', 'inhibit', 'stable', or 'maximum'.\n"
            "9. **Enzyme Activity**: Include a quantitative measure of enzyme activity with its unit (e.g., activity units per milliliter).\n"
            "\n"
            "Notes:\n"
            "- Conditions should be grouped by paired enzyme, substrate, and effect. If unspecified value exists for these key, entry must be escaped.\n"
            "- Grouped conditions under each entry must have the same effect; otherwise, separate them into distinct entries.\n"
            "- If multiple effects are present for the same condition, separate them into distinct entries.\n"
            "- Ensure that all fields, except for Enzyme, Substrate, and Effect, have a single valid value."
        )
    )

class FermentationCondition(BaseModel):
    microbiome: str = Field(
        description="Specify the specific microbiome involved in the fermentation process, including taxonomic classification."
    )
    enzyme: str = Field(
        description="Specify the enzyme produced by the microbiome, detailing its function and classification."
    )
    temperature: str = Field(
        description="Indicate the temperature for fermentation, specifying the range if applicable.", 
        default="unspecified"
    )
    ph: str = Field(
        description="Indicate the pH level of the fermentation medium, specifying the range if applicable.", 
        default="unspecified"
    )
    substrate: str = Field(
        description="Indicate the type of substrate utilized in fermentation, including its characteristics.", 
        default="unspecified"
    )
    incubation_period: str = Field(
        description="Indicate the duration of fermentation, specifying the unit of time (e.g., hours, days).", 
        default="unspecified"
    )
    medium: str = Field(
        description="Indicate the type of growth medium used during fermentation, including its composition if relevant.", 
        default="unspecified"
    )
    moisture: str = Field(
        description="Indicate the moisture level during fermentation, stating the measurement method if applicable.", 
        default="unspecified"
    )
    carbon_source: str = Field(
        description="Indicate the source of carbon in the medium, describing its form (e.g., glucose, sucrose).", 
        default="unspecified"
    )
    nitrogen_source: str = Field(
        description="Indicate the nitrogen source used in the fermentation process, including its type.", 
        default="unspecified"
    )
    aeration: str = Field(
        description="Indicate the aeration conditions applied during fermentation, including any specific methods (e.g., shaking, bubbling).", 
        default="unspecified"
    )
    agitation: str = Field(
        description="Indicate the agitation conditions used, including speed and duration.", 
        default="unspecified"
    )
    volume: str = Field(
        description="Indicate the total volume of the fermentation medium, including the unit of measurement (e.g., liters).", 
        default="unspecified"
    )
    effect: str = Field(
        description="Classify the effect on production as 'increase', 'decrease', or 'optimum'."
    )
    production_yield: Optional[str] = Field(
        description="Include a quantitative measure of production yield with its unit (e.g., grams per liter).", 
        default="unspecified"
    )

class CatalysisCondition(BaseModel):
    enzyme: str = Field(
        description="Specify the enzyme involved in the catalysis, detailing its function and classification."
    )
    substrate: str = Field(
        description="Specify the substrate being catalyzed, including its characteristics and source."
    )
    ph: str = Field(
        description="Indicate the pH level or range for enzyme activity; Indicate the optimum if applicable.", 
        default="unspecified"
    )
    temperature: str = Field(
        description="Indicate the temperature or range for enzyme activity; Indicate the optimum if applicable.", 
        default="unspecified"
    )
    ions: str = Field(
        description="List any metal ions that influence enzyme activity, specifying their concentrations if relevant.", 
        default="unspecified"
    )
    surfactants: str = Field(
        description="Specify any surfactants affecting enzyme activity, including their types and concentrations.", 
        default="unspecified"
    )
    chemicals: str = Field(
        description="List chemicals that impact enzyme activity, providing details on their role and concentration.", 
        default="unspecified"
    )
    effect: str = Field(
        description="Classify the effect on enzyme activity as 'enhance', 'inhibit', 'stable', or 'maximum'."
    )
    enzyme_activity: Optional[str] = Field(
        description="Include a quantitative measure of enzyme activity with its unit (e.g., activity units per milliliter).", 
        default="unspecified"
    )

class EnzymeMetaDatas(BaseModel):
    context: List[EnzymeMetaData]

class EnzymeEntities(BaseModel):
    fermentations: List[FermentationCondition]
    catlyts: List[CatalysisCondition]


class TextToContext(dspy.Signature):
    text: str = dspy.InputField()
    context: EnzymeMetaDatas = dspy.OutputField()


class TextToEnzymeEntities(dspy.Signature):
    text: str = dspy.InputField()
    entities: EnzymeEntities = dspy.OutputField() 


import os
import configparser
from integrations.watsonx.bam_integration import BAMIntegration
from integrations.watsonx.dataplatform_integration import DataplatformIntegration
from integrations.watsonx.prompt_builder import PromptBuilders as WatsonxPromptBuilders

PLATFORM = os.getenv("PLATFORM", None)
config = configparser.ConfigParser()
config.read("constants.ini")


if  PLATFORM == config.get('GENAI_PLATFORM','BAM'):
    integration = BAMIntegration()
    promptbuilders = WatsonxPromptBuilders()
elif  PLATFORM == config.get('GENAI_PLATFORM','DATAPLATFORM'):
    integration = DataplatformIntegration()
    promptbuilders = WatsonxPromptBuilders()

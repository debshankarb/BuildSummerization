import os
import logging
from model_classes import ExceptionMessageEnum
from genai.schemas import ReturnOptions
from ibm_watson_machine_learning.foundation_models import model as foundation_model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from config import log_entry_exit
import configparser
from dotenv import load_dotenv
from model_classes import ExceptionMessageEnum,CustomException

load_dotenv()

api_key = os.getenv("WX_GENAI_KEY", None)
api_url = os.getenv("WX_GENAI_API", None)
genai_project_id = os.getenv("WX_GENAI_PROJECT_ID", None)

config = configparser.ConfigParser()
config.read("integrations/watsonx/params.ini")

class DataplatformIntegration:

    def __init__(self):
        self.creds = {}
        self.creds["apikey"] = api_key
        self.creds["url"] = api_url
        self.project_id = genai_project_id

    @log_entry_exit
    def fetch_default_params(self):
        return (
            config.get('Default', 'MODEL'),{
            GenParams.DECODING_METHOD:config.get('Default', 'DECODING_METHOD'),
            GenParams.MAX_NEW_TOKENS:config.getint('Default', 'MAX_NEW_TOKENS'),
            GenParams.MIN_NEW_TOKENS:config.getint('Default', 'MIN_NEW_TOKENS'),
            "stream":config.getboolean('Default', 'STREAM'),
            GenParams.REPETITION_PENALTY:config.getfloat('Default', 'REPETITION_PENALTY'),
            GenParams.TEMPERATURE:config.getfloat('Default', 'TEMPERATURE')
            })

    @log_entry_exit  
    def fetch_params_major_incident_communication(self):
        return (config.get('MajorIncident', 'MODEL'),{
            GenParams.DECODING_METHOD:config.get('MajorIncident', 'DECODING_METHOD'),
            GenParams.MAX_NEW_TOKENS:config.getint('MajorIncident', 'MAX_NEW_TOKENS'),
            GenParams.MIN_NEW_TOKENS:config.getint('MajorIncident', 'MIN_NEW_TOKENS'),
            "stream":config.getboolean('MajorIncident', 'STREAM'),
            GenParams.TOP_K:config.getint('MajorIncident', 'TOP_K'),
            GenParams.REPETITION_PENALTY:config.getfloat('MajorIncident', 'REPETITION_PENALTY'),
            GenParams.TEMPERATURE:config.getfloat('MajorIncident', 'TEMPERATURE')
            })


    @log_entry_exit
    def fetch_params_telemetry_summary(self):
        return (config.get('Telemetry', 'MODEL'),{
            GenParams.DECODING_METHOD:config.get('Telemetry', 'DECODING_METHOD'),
            GenParams.MAX_NEW_TOKENS:config.getint('Telemetry', 'MAX_NEW_TOKENS'),
            GenParams.MIN_NEW_TOKENS:config.getint('Telemetry', 'MIN_NEW_TOKENS'),
            "stream":config.getboolean('Telemetry', 'STREAM'),
            GenParams.TOP_K:config.getint('Telemetry', 'TOP_K'),
            GenParams.REPETITION_PENALTY:config.getfloat('Telemetry', 'REPETITION_PENALTY'),
            GenParams.TEMPERATURE:config.getfloat('Telemetry', 'TEMPERATURE'),
            GenParams.RANDOM_SEED:config.getint('Telemetry', 'RANDOM_SEED')
        })  

    @log_entry_exit
    def fetch_model(self, params: GenParams):
        try:
            return foundation_model.Model(model_id=params[0], params=params[1], credentials=self.creds, project_id=self.project_id)
        except Exception as e:
            logging.error(ExceptionMessageEnum.LLM_CONNECTION_EXCEPTION.value.format(e))
            raise CustomException(
                error_code=500,
                message=ExceptionMessageEnum.LLM_CONNECTION_EXCEPTION.value.format(e))


    def generate_text(self, prompt: str, params: GenParams):
        model = self.fetch_model(params)
        try:
            generated_text = model.generate_text(prompt)
            print("Generetaed Text is:", generated_text)
        except Exception as e:
            logging.error(ExceptionMessageEnum.LLM_GENERATE_TEXT_EXCEPTION.value.format(e))
            raise CustomException(
                error_code=500,
                message=ExceptionMessageEnum.LLM_GENERATE_TEXT_EXCEPTION.value.format(e))

        return generated_text
    


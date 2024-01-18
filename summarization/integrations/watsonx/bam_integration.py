import os
from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import ReturnOptions, GenerateParams
from fastapi import HTTPException
from model_classes import ExceptionMessageEnum,CustomException
import logging
from dotenv import load_dotenv
import configparser
from config import log_entry_exit


load_dotenv()

api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)

config = configparser.ConfigParser()
config.read("integrations/watsonx/params.ini")


class BAMIntegration:
    def __init__(self):
        self.creds = Credentials(api_key, api_endpoint=api_url)


    @log_entry_exit
    def fetch_default_params(self):
        return (config.get('Default', 'MODEL'),
                GenerateParams(
            decoding_method=config.get('Default', 'DECODING_METHOD'),
            max_new_tokens=config.getint('Default', 'MAX_NEW_TOKENS'),
            min_new_tokens=config.getint('Default', 'MIN_NEW_TOKENS'),
            stream=config.getboolean('Default', 'STREAM'),
            return_options=ReturnOptions(input_text=config.getboolean('Default', 'INPUT_TEXT'), input_tokens=config.getboolean('Default', 'INPUT_TOKENS')),
            repetition_penalty=config.getfloat('Default', 'REPETITION_PENALTY'),
            temperature=config.getfloat('Default', 'TEMPERATURE')
        ))

    @log_entry_exit
    def fetch_params_major_incident_communication(self):
        return (config.get('MajorIncident', 'MODEL'),
                GenerateParams(
            decoding_method=config.get('MajorIncident', 'DECODING_METHOD'),
            max_new_tokens=config.getint('MajorIncident', 'MAX_NEW_TOKENS'),
            min_new_tokens=config.getint('MajorIncident', 'MIN_NEW_TOKENS'),
            stream=config.getboolean('MajorIncident', 'STREAM'),
            top_k=config.get('MajorIncident', 'TOP_K'),
            return_options=ReturnOptions(input_text=config.getboolean('MajorIncident', 'INPUT_TEXT'), input_tokens=config.getboolean('MajorIncident', 'INPUT_TOKENS')),
            repetition_penalty=config.getfloat('MajorIncident', 'REPETITION_PENALTY'),
            temperature=config.getfloat('MajorIncident', 'TEMPERATURE')
            ))
    
    @log_entry_exit
    def fetch_params_telemetry_summary(self):
        return (config.get('Telemetry', 'MODEL'),
                GenerateParams(
            decoding_method=config.get('Telemetry', 'DECODING_METHOD'),
            max_new_tokens=config.getint('Telemetry', 'MAX_NEW_TOKENS'),
            min_new_tokens=config.getint('Telemetry', 'MIN_NEW_TOKENS'),
            stream=config.getboolean('Telemetry', 'STREAM'),
            top_k=config.get('Telemetry', 'TOP_K'),
            repetition_penalty=config.getfloat('Telemetry', 'REPETITION_PENALTY'),
            temperature=config.getfloat('Telemetry', 'TEMPERATURE'),
            random_seed=config.getint('Telemetry', 'RANDOM_SEED')
        ))     

    @log_entry_exit
    def fetch_model(self, params: GenerateParams):
        try:
            return Model(model=params[0], params=params[1], credentials=self.creds)
        except Exception as e:
            logging.error(ExceptionMessageEnum.LLM_CONNECTION_EXCEPTION.value.format(e))
            raise CustomException(
                error_code=500,
                message=ExceptionMessageEnum.LLM_CONNECTION_EXCEPTION.value.format(e))

    @log_entry_exit
    def generate_text(self, prompt: str, params: GenerateParams):
        model = self.fetch_model(params)
        try:
            responses = model.generate_as_completed(prompt)
            generated_texts = []
            for response in responses:
                generated_texts.append(response.generated_text)
        except Exception as e:
            logging.error(ExceptionMessageEnum.LLM_GENERATE_TEXT_EXCEPTION.value.format(e))
            raise CustomException(
                error_code=500,
                message=ExceptionMessageEnum.LLM_GENERATE_TEXT_EXCEPTION.value.format(e))

        return generated_texts







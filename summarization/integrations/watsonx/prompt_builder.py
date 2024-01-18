import configparser
from config import log_entry_exit
config = configparser.ConfigParser()
config.read("integrations/watsonx/prompts.ini")

class PromptBuilders:
       
    @log_entry_exit
    def generate_prompts(self, summary_type, texts):
        try:

            prompt_list = []
            for chunk in texts:
                prompt = self.get_prompt_from_ini("summary", summary_type)
                prompt = prompt.format(text=chunk)
                prompt_list.append(prompt)

            return prompt_list

        except Exception as e:
            raise e

    @log_entry_exit
    def generate_prompt(self, summary_type, texts):
        try:
            prompt = self.get_prompt_from_ini("summary", summary_type)
            prompt = prompt.format(text=texts)
            return [prompt]
        except Exception as e:
            raise e


    @log_entry_exit    
    def get_prompt_from_ini(self, section, report_name):
        try:
            query = config[section][report_name]
            return query
        except Exception as e:
            raise Exception(f"Unable to read prompts for : {e}")
        

    @log_entry_exit  
    def generate_telemetry_prompt(self, summary_type, anomaly, metric, error):
        try:
            prompt = self.get_prompt_from_ini("summary", summary_type)
            prompt = prompt.replace("{anomaly}",anomaly) 
            prompt = prompt.replace("{metric}",metric) 
            prompt = prompt.replace("{log_message}",error) 
            print(prompt)
            return [prompt]

        except Exception as e:
            raise e
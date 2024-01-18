import os
import json
import requests
import traceback
from fastapi import HTTPException
import logging
from dotenv import load_dotenv
load_dotenv()
access_token = os.getenv("SIDEKICK_ACCESS_TOKEN")
security_key = os.getenv("SIDEKICK_SECURITY_KEY")
extension_app_id = os.getenv("SIDEKICK_EXTENSION_APP_ID")
model_id = os.getenv("SIDEKICK_MODEL_ID")

log = logging.getLogger(__name__)

class OpenAIIntegration:
    
    def __init__(self):
        pass
                

    def prompt_sidekick(self,prompt, model_id):
        
        try:
            
            log.info("Getting into OPEN AI via Sidekick Environment")
            chatid = self.create_chatid(model_id)
            log.info(chatid)
            print("chatid",chatid)
            responses1 = self.execute_model(prompt,chatid,model_id)
            
        except Exception as ex:
            
            logging.error(ex)
            
           
        data = json.loads(responses1)
        response = data["response"]
               
        generated_texts = []
        generated_texts.insert(0,response)
               
        return generated_texts
    
    def create_chatid(self,model_id):
        try:
            sidekick_chat_url = os.getenv("SIDEKICK_CHAT_URL")
            payload = {"modelId": model_id}

            headers = {
               "x-access-token":access_token,
                "x-security-key":security_key,
                "Content-Type": "application/json"
            }
        
            response = requests.request("POST", sidekick_chat_url, json=payload, headers=headers)
            
        except Exception as ex:
            logging.error(ex)
            
            
        return response.text.strip()
    
    def execute_model(self,prompt,chat_id,model_id):
        chat_id = chat_id.replace('"','')
        sidekick_response =""
        sidekick_execute_url = os.getenv("SIDEKICK_EXECUTE_URL")
       
        
        payload2 = {
                "prompt": prompt,
                "modelId": model_id,
                "chatId": chat_id,
                "parameters": {
                    "temperature": "0.8",
                    "top_p": "0.95",
                    "max_tokens": "4096"
                    
                }
            }
    
        headers2 = {
                "x-access-token": access_token,
                "x-security-key": security_key,
                "Content-Type": "application/json",
                "x-extension-app-id": extension_app_id
                }
        
        try:
            sidekick_response = requests.request("POST", sidekick_execute_url, json=payload2, headers=headers2)
            print("Sidekick execution with prompt done with response " + sidekick_response.text)
            
        except Exception as ex: 
                
                logging.error(ex)
               
         
        return sidekick_response.text

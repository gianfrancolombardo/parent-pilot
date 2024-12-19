from datetime import datetime
from dateutil.relativedelta import relativedelta
import yaml
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st

@st.cache_resource
def get_child_assistant(openai_api_key: str = None):
    """
    Obtiene la instancia única de ChildAssistant.
    Utiliza st.cache_resource para mantener una única instancia entre reruns.
    """
    if not hasattr(get_child_assistant, "_instance"):
        get_child_assistant._instance = ChildAssistant(openai_api_key or st.secrets["openai"]["api_key"])
    return get_child_assistant._instance

class ChildAssistant:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        with open('prompts.yaml', 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def calculate_age(self, birth_date):
        today = datetime.now()
        rd = relativedelta(today, birth_date)
        
        if rd.years > 0:
            return f"{rd.years} años"
        elif rd.months > 0:
            return f"{rd.months} meses"
        else:
            days = (today - birth_date).days
            return f"{days} días"
    
    def get_age_category(self, birth_date):
        months = relativedelta(datetime.now(), birth_date).months
        years = relativedelta(datetime.now(), birth_date).years
        
        if years == 0 and months < 12:
            return 'baby'
        elif years < 3:
            return 'toddler'
        else:
            return 'child'
    
    def generate_content(self, child):
        age = self.calculate_age(child['birth_date'])
        content_type = child.get('content_type', 'story')
        
        if content_type == 'story':
            age_category = self.get_age_category(child['birth_date'])
            template = self.prompts['story_prompts'][age_category]
        else:
            template = self.prompts['activities_prompt']
        
        prompt_template = PromptTemplate.from_template(template)
        prompt = prompt_template.format(nombre=child['name'], edad=age)
        
        return self.llm.invoke(prompt).content
    
    def create_story(self, child):
        child = child.copy()  # Crear una copia para no modificar el original
        child['content_type'] = 'story'
        return self.generate_content(child)
    
    def create_activities(self, child):
        child = child.copy()  # Crear una copia para no modificar el original
        child['content_type'] = 'activities'
        return self.generate_content(child)

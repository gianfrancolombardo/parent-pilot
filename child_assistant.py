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
        # Si birth_date es string, convertirlo a datetime
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date)
        rd = relativedelta(today, birth_date)
        
        if rd.years >= 2:
            return f"{rd.years} años"
        elif rd.years == 1:
            if rd.months == 1:
                return f"1 año y 1 mes"
            elif rd.months > 0:
                return f"1 año y {rd.months} meses"
            return "1 año"
        elif rd.months > 0:
            return f"{rd.months} meses"
        else:
            days = (today - birth_date).days
            return f"{days} días"
    
    def get_age_category(self, birth_date):
        # Si birth_date es string, convertirlo a datetime
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date)
        rd = relativedelta(datetime.now(), birth_date)
        months = rd.months + (rd.years * 12)
        
        if months < 12:
            return 'baby'
        elif months < 36:
            return 'toddler'
        else:
            return 'child'
    
    def generate_content(self, child):
        age = self.calculate_age(child['birth_date'])
        content_type = child.get('content_type', 'story')
        
        if content_type == 'story':
            age_category = self.get_age_category(child['birth_date'])
            template = self.prompts['story_prompts'][age_category]
        elif content_type == 'activities':
            template = self.prompts['activities_prompt']
        elif content_type == 'welcome':
            template = self.prompts['welcome_prompt']
        
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
        
    def create_welcome_summary(self, child):
        """Genera un resumen del estado actual de desarrollo del niño."""
        child = child.copy()  # Crear una copia para no modificar el original
        child['content_type'] = 'welcome'
        return self.generate_content(child)

import firebase_admin
from firebase_admin import credentials, firestore
import json

class FirebaseManager:
    def __init__(self, firebase_credentials_str):
        """
        Inicializa el administrador de Firebase con las credenciales proporcionadas.
        
        Args:
            firebase_credentials_str (str): Credenciales de Firebase en formato string JSON
        """
        if not firebase_admin._apps:
            try:
                # Primero intentamos cargar el JSON directamente
                firebase_credentials = json.loads(firebase_credentials_str)
            except json.JSONDecodeError:
                # Si falla, intentamos con raw string para manejar los \n
                firebase_credentials_str = firebase_credentials_str.encode().decode('unicode-escape')
                firebase_credentials = json.loads(firebase_credentials_str)
                
            cred = credentials.Certificate(firebase_credentials)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        
    def save_child(self, name, birth_date, gender):
        """
        Guarda la información de un niño en Firestore.
        
        Args:
            name (str): Nombre del niño
            birth_date (datetime.date): Fecha de nacimiento
            gender (str): Género del niño
            
        Returns:
            str: ID del documento creado
        """
        child_data = {
            'name': name,
            'birth_date': birth_date.isoformat(),
            'gender': gender,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = self.db.collection('children').add(child_data)
        return doc_ref[1].id
    
    def get_child(self, child_id):
        """
        Obtiene la información de un niño por su ID.
        
        Args:
            child_id (str): ID del documento del niño
            
        Returns:
            dict: Datos del niño o None si no se encuentra
        """
        doc_ref = self.db.collection('children').document(child_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_children(self):
        """
        Obtiene todos los niños registrados.
        
        Returns:
            list: Lista de diccionarios con la información de los niños
        """
        children = []
        docs = self.db.collection('children').stream()
        for doc in docs:
            child_data = doc.to_dict()
            child_data['id'] = doc.id
            children.append(child_data)
        return children

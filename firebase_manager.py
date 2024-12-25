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
        Obtiene todos los niños registrados, ordenados por fecha de creación (más reciente primero).
        
        Returns:
            list: Lista de diccionarios con la información de los niños
        """
        children = []
        # Ordenar por created_at en orden descendente
        docs = self.db.collection('children').order_by('created_at', direction=firestore.Query.ASCENDING).stream()
        for doc in docs:
            child_data = doc.to_dict()
            child_data['id'] = doc.id
            children.append(child_data)
        return children

    def get_daily_records(self, child_id, days=7):
        """
        Obtiene los registros diarios de un niño para un número específico de días.
        
        Args:
            child_id (str): ID del niño
            days (int): Número de días hacia atrás para obtener registros
            
        Returns:
            list: Lista de diccionarios con los registros diarios
        """
        from datetime import datetime, timedelta
        
        # Calcular la fecha de inicio (hace X días)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Obtener los registros
        records = []
        collection_ref = self.db.collection('children').document(child_id).collection('daily_records')
        
        # Iterar sobre cada día en el rango
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            doc = collection_ref.document(date_str).get()
            
            if doc.exists:
                data = doc.to_dict()
                data['date'] = date_str
            else:
                data = {
                    'date': date_str,
                    'feeding': 0,
                    'pee_diaper': 0,
                    'full_diaper': 0
                }
            records.append(data)
            current_date += timedelta(days=1)
            
        return records

    def save_daily_record(self, child_id, record_type, increment=1):
        """
        Actualiza un contador en el registro diario de un niño.
        
        Args:
            child_id (str): ID del niño
            record_type (str): Tipo de registro ('feeding', 'pee_diaper', 'full_diaper')
            increment (int): Cantidad a incrementar (o decrementar si es negativo)
            
        Returns:
            bool: True si la operación fue exitosa
        """
        from datetime import datetime
        
        # Obtener la fecha actual en formato YYYY-MM-DD
        today = datetime.now().date().strftime('%Y-%m-%d')
        
        # Referencia al documento del día actual
        doc_ref = self.db.collection('children').document(child_id) \
                    .collection('daily_records').document(today)
        
        # Crear o actualizar el documento
        try:
            doc = doc_ref.get()
            if doc.exists:
                # Si el documento existe, incrementar el contador
                current_value = doc.to_dict().get(record_type, 0)
                new_value = max(0, current_value + increment)  # Evitar valores negativos
                doc_ref.update({record_type: new_value})
            else:
                # Si el documento no existe, crearlo con el valor inicial
                initial_data = {
                    'feeding': 0,
                    'pee_diaper': 0,
                    'full_diaper': 0,
                    record_type: max(0, increment)  # Evitar valores negativos
                }
                doc_ref.set(initial_data)
            return True
        except Exception as e:
            print(f"Error al guardar registro diario: {e}")
            return False

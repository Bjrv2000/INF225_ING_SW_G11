import unittest
import requests
from backend import app  # Importa la aplicación Flask desde backend.py

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = 'http://127.0.0.1:5000'  # Se ingresa la URL
        # Iniciar la aplicación en modo de prueba
        app.testing = True
        cls.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        # Limpiar recursos compartidos después de todas las pruebas
        pass

    def test_get_search_result_endpoint(self):
        # Prueba para el endpoint '/search/<result_id>' con el método GET
        response = self.app.get('/search/1')  # Cambia el ID según tu caso
        self.assertEqual(response.status_code, 200)

        # Verificar el contenido del JSON devuelto en una tabla vacia corresponda a lo necesitado
        expected_response = {'error': 'Result not found'}
        self.assertDictEqual(response.json(), expected_response)
    
    def test_invalid_method(self):
        # Prueba para un método no permitido en el endpoint search/1, en este caso un post
        response = self.app.post('/search/1')
        self.assertEqual(response.status_code, 405)
    
    def test_send_email_endpoint(self):
        # Prueba para el endpoint '/send_email' con el método POST
        data = {'to_email': 'example@example.com', 'subject': 'Test Subject', 'message': 'Test Message'}
        response = self.app.post('/send_email', json=data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_endpoint(self):
        # Prueba para un endpoint que no existe
        response = self.app.get('/insumos')
        self.assertEqual(response.status_code, 404)

    

if __name__ == '__main__':
    unittest.main()

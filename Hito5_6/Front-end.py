import streamlit as st
import requests

# Define la URL de la API
API_BASE_URL = 'http://localhost:5000'  


####################################################### Metodos ######################################################

def create_search(query):
    # crea la busqueda con el POST request 
    response = requests.post(f'{API_BASE_URL}/search', json={'query': query})

    if response.status_code == 201:
        return response.json()
    else:
        return {'error': 'Failed to create search'}

def get_search_result(result_id):
    # crea un GET request para un id específico
    response = requests.get(f'{API_BASE_URL}/search/{result_id}')

    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Result not found'}

def get_all_search_results():
    # Crea el GET request para obtener el historico
    response = requests.get(f'{API_BASE_URL}/search')

    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to retrieve search results'}
#############################ENVIO DE CORREO############################################
def send_email(to_email, subject, message):
    # Crea el POST request para enviar el correo electrónico
    data = {'to_email': to_email, 'subject': subject, 'message': message}
    response = requests.post(f'{API_BASE_URL}/send_email', json=data)

    if response.status_code == 200:
        return {'message': 'Correo enviado con éxito'}
    else:
        return {'error': 'Failed to send email'}
####################################################### Inicio visualizacion(Streamlit) ######################################################
def main():
    st.title('Bienvenido')

    # inputbox para ingresa la descripcion del taller
    query = st.text_input('Ingrese la descripcion del taller')

    # BBoton para iniciar el metodo POST request para generar una busqueda
    if st.button('Buscar'):
        query_str = str(query)
        if not query_str:
            st.warning('No hay nada que buscar')
        else:
            with st.spinner('Buscando. . .'):
                result = create_search(query_str)
            st.success(f'Busqueda iniciada: {query_str}')

            # Muestra los resultados actuañes en una tabla
            display_results(result)

    #Usa el metodo GET search para obtener todos los resultados 
    all_results = get_all_search_results()
    st.title('Todos los resultados')
    ####################Correo#####################
       
    st.title('Enviar Correo Electrónico')
    to_email = st.text_input('Ingrese la dirección de correo electrónico del destinatario')
    subject = st.text_input('Ingrese el asunto del correo electrónico')
    message = st.text_area('Ingrese el mensaje del correo electrónico', 'Mensaje predeterminado que se puede modificar')
    
    if st.button('Enviar Correo Electrónico'):
        response = send_email(to_email, subject, message)
        if 'error' in response:
            st.error(response['error'])
        else:
            st.success(response['message'])

    #Muestra una lista de todos los resultados historicos
    for idx, search_result in enumerate(all_results):
        tema = search_result.get('tematica', 'Tema no encontrado')
        lugar = search_result.get('lugar', 'Lugar no encontrado')


        #Crea una lista de tablas desplegables para mostrar los historicos
        with st.expander(f'{tema} - {lugar}'):
            display_results(search_result)




###################################################################### Funcion que define la tabla  y parametros ###########################################


#Paramatros de la tabla
def display_results(results):
    
    # Check if 'results' key is present in the dictionary and is a list
    if 'results' in results and isinstance(results['results'], list):
        
        # crea un diccionario para todos los resultados
        data = []
        for item in results['results']:
            nombre = item.get('name', 'N/A')
            precio = item.get('value', 'N/A')
            url = item.get('url', 'N/A')

            # hace que la URL sea clickable (nos redirique al link)
            clickable_url = f'<a href="{url}" target="_blank">{url}</a>'

            data.append({'Nombre': nombre, 'Precio': precio, 'URL': clickable_url})

        # Muestra la tabla
        display_custom_table(data)
    else:
        st.warning('No se encontraron resultados válidos.')



#Visualizacion de la tabla
def display_custom_table(data):
    st.markdown(
        '<style> table { font-family: Arial, sans-serif; border-collapse: collapse; width: 100%; }'
        'th, td { border: 1px solid #dddddd; text-align: left; padding: 10px; width: 33.33%; }'
        'tr:hover { background-color: #173928; }'
        'a { color: #3498db; text-decoration: none; }'
        'a:hover { text-decoration: underline; } </style>',
        unsafe_allow_html=True
    )
    
    st.write('<table>', unsafe_allow_html=True)
    st.write('<tr><th>Nombre</th><th>Precio</th><th>URL</th></tr>', unsafe_allow_html=True)

    for row in data:
        st.write(
            f'<tr><td>{row["Nombre"]}</td><td>{row["Precio"]}</td><td><a>{row["URL"]}</a></td></tr>',
            unsafe_allow_html=True
        )

    st.write('</table>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
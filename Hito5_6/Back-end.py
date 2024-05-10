from dotenv import load_dotenv
import requests
from googlesearch import search
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from langchain.chains import create_extraction_chain
from langchain_community.chat_models import ChatOpenAI
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)
# Lugar donde se almacenan todos los datos
search_results = []

# webscrapper para superproof
def get_name(url):
    response = requests.get(url,timeout=10)
    if response.status_code == 200:
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        name = soup.find("div", {"class": "name"}).contents[0]
        name_without_label = name.string
        value = soup.find("span", {"class": "value"}).contents[0]
        return {'name': name_without_label, 'value': value,'url':url}
    else:
        return None

#chatgpt para insumos
def chat_with_gpt(prompt):
    try:
        response = openai.Completion.create(
            engine="davinci-codex",  
            prompt=prompt,
            temperature=0.7,
            max_tokens=5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        # Manejar el error de alguna manera, por ejemplo, registrándolo o devolviendo un valor predeterminado
        print("Error al generar texto:", e)
        return "Error: No se pudo generar el texto"
@app.route('/search', methods=['POST'])
def create_search():
    data = request.get_json()

    # query es un dato enviado desde el front al back mediante el método post
    query = data.get('query')
    query_str = str(query)  # convierte el dato enviado de b'' a string

    if not query_str:
        return jsonify({'error': 'Missing required field: query'}), 400
    

########################################### LangChain_ OPENAI ###########################################
    busqueda = query_str

    # Schema
    schema = {
        "properties": {
            "tematica": {"type": "string"},
            "lugar": {"type": "string"},
            "valor tope": {"type": "integer"},
        },
        "required": ["tematica", "lugar"],
    }
    schema2 = {
        "properties": {
            "tematica": {"type": "string"},
            "lugar": {"type": "string"},
            "valor tope": {"type": "integer"},
        },
        "required": ["tematica", "lugar"],
    }
    

    # Run chain
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    chain = create_extraction_chain(schema, llm)
    
    respuesta=chain.invoke(busqueda)

    print(respuesta)
    print(type(respuesta))

    #verifica si la respuesta del modelo llm es una lista o un diccionario para hacer la extraccion de objetos y lo guarda en la variable cosas
    if type(respuesta) is list:
        cosas=str(respuesta[0].get('tematica',"tematica no encontrada")+" "+respuesta[0].get('lugar', 'lugar no encontrado'))
        Busqueda_insumos=str("Dame una lista de insumos necesarios para un taller de "+respuesta[0].get('tematica',"tematica no encontrada"))
    elif type(respuesta) is dict:
        cosas=str(respuesta.get('tematica',"tematica no encontrada")+" "+respuesta.get('lugar', 'lugar no encontrado'))
        Busqueda_insumos=str("Dame una lista de insumos necesarios para un taller de "+respuesta.get('tematica',"tematica no encontrada"))
    insumos=chat_with_gpt(Busqueda_insumos)
    print(insumos)
    
    

########################################### FIN de LangChain_ OPENAI ###########################################


########################################### Buscador en Google ###########################################

    # Realiza busqueda con los parametros tematica y lugar del json entregado por LLM
    results = []
    contador_urls=0
    for url in search(cosas + " site:www.superprof.cl", start=0, pause=2):
        if contador_urls >= 10:
            print(contador_urls)
            break
        if url.endswith('.html'):
            search_result = get_name(url)
            contador_urls+=1
            if search_result:
                results.append(search_result)

    # Guarda los resultados obtenidos en el histórico
    if type(respuesta) is list:
        result = {'tematica': respuesta[0].get('tematica'), 'lugar': respuesta[0].get('lugar'), 'results': results}
    elif type(respuesta) is dict:
        result = {'tematica': respuesta.get('tematica'), 'lugar': respuesta.get('lugar'), 'results': results}
    search_results.append(result)

    return jsonify(result), 201

########################################### Fin Buscador en Google ###########################################


#Extraccion de las busquedas del histórico por ID(N° de consulta ralizada)
@app.route('/search/<int:result_id>', methods=['GET'])
def get_search_result(result_id):
    if result_id < 0 or result_id >= len(search_results):
        return jsonify({'error': 'Result not found'}), 404

    result = search_results[result_id]
    return jsonify(result)

#Extraccion de los resultados historicos
@app.route('/search', methods=['GET'])
def get_all_search_results():
    return jsonify(search_results)
########################################### Envio de Correo ###########################################
@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.json
    to_email = data['to_email']
    subject = data['subject']
    message = data['message']

    # Configuración del servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'usm.iso2024.01@gmail.com'
    smtp_password = 'uciopuvearjkdxbi'

    # Crear un mensaje MIME
    email_message = MIMEMultipart()
    email_message['From'] = smtp_username
    email_message['To'] = to_email
    email_message['Subject'] = subject
    email_message.attach(MIMEText(message, 'plain'))

    # Conexión y envío del correo
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, email_message.as_string())

    return jsonify({'message': 'Correo enviado con éxito'})
########################################### Envio de Correo ###########################################


if __name__ == '__main__':
    app.run(debug=True)




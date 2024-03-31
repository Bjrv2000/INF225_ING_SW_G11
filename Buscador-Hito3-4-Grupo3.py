import requests
from googlesearch import search
from bs4 import BeautifulSoup

#Entra a los url y busca en el html los nombres y valores de las personas
def get_name(url):
    # Hace la solicitud HTTP
    response = requests.get(url)
    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:

        #Si lo fue, extrae la información
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        #pagina = soup.find("a", {"class": "landing-v4-ads-bloc tck-announce-link"})
        name = soup.find("div", {"class": "name"}).contents[0]
        name_without_label = name.string
        print(name_without_label)
        value = soup.find("span", {"class": "value"}).contents[0]
        print(value + "\n")
        return 0
    
    #Si no, indica el error
    else:
        print("error al acceder a la página. \n")

#Variable para limitar la cantidad de paginas
n = 0

#Le pide al cliente que ingrese los terminos para realizar las busquedas
google_query = str(input("Porfavor, ingrese el tema y el lugar del taller (ejemplo: canto santiago): "))
google_query_site = google_query + " site:www.superprof.cl"

#Por cada url revisa si termina en html, si es asi, ingresa a la pagina, lo hace un total de n veces indicado en el if
for i in search(google_query_site, start = 0, pause = 1):
    if n >= 10:
        break
    else:
        if i.endswith('.html'):
            print(i)
            n+=1
            get_name(i)

import requests
import json
import threading
import time
import os
import flag
import math
import re
from datetime import datetime
from flask import Flask, render_template, request
import pycountry

app = Flask(__name__)
data_file = "dataransom.json"
data = []

def actualizar_datos(json_lastweek, json_historical, js_file, json_dump):
    # 1. Leer los archivos JSON
    with open(json_lastweek, 'r', encoding='utf-8') as f:
        lastweek_data = json.load(f)

    with open(json_historical, 'r', encoding='utf-8') as f:
        historical_data = json.load(f)

    # 2. Contar ocurrencias de cada país en lastweek.json
    lastweek_counts = {}
    for entry in lastweek_data:
        country = entry.get("country")
        if country:
            lastweek_counts[country] = lastweek_counts.get(country, 0) + 1

    # 3. Contar ocurrencias de cada país en historical.json
    historical_counts = {}
    for entry in historical_data:
        country = entry.get("country")
        if country:
            historical_counts[country] = historical_counts.get(country, 0) + 1

    # 4. Cargar el archivo JavaScript y extraer el objeto JSON
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # Buscar las llaves del JSON dentro del archivo JS
    json_start = js_content.find('{')
    json_end = js_content.rfind('}') + 1
    json_text = js_content[json_start:json_end]

    # Parsear el JSON que se encuentra dentro del JS
    data_js = json.loads(json_text)

    # 5. Actualizar los valores para cada país encontrado en lastweek_counts o historical_counts
    all_countries = set(lastweek_counts.keys()) | set(historical_counts.keys())
    for country in all_countries:
        lw_count = lastweek_counts.get(country, 0)
        hist_count = historical_counts.get(country, 0)

        # Si el país no existe en el objeto JS, crearlo
        if country not in data_js["values"]:
            data_js["values"][country] = {
                "totalatacks": 0,
                "lastweekatacks": 0
            }

        # Sumar ocurrencias históricas
        data_js["values"][country]["totalatacks"] = hist_count
        # Actualizar ocurrencias de la última semana (sobrescribir)
        data_js["values"][country]["lastweekatacks"] = lw_count

        data_js["values"][country]["country_name"] = get_country_name(country)

    # 6. Convertir de nuevo el diccionario actualizado a cadena para guardarlo en JS
    updated_js_content = f'var svgMapDataGPD = {json.dumps(data_js, indent=2)};'

    # 7. Guardar el contenido actualizado en el archivo JS
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(updated_js_content)

    with open(json_dump, 'w', encoding='utf-8') as f:
        json.dump(data_js, f, indent=2)

    print("Archivo JavaScript actualizado correctamente.")


def schedule_data_fetching():
    while True:
        actualizar_datos("latest_200.json", "dataransom.json", "static/gdp.js", "static/data.json")
        time.sleep(3600)  # Fetch data every hour


def get_country_name(country_code):
    country = pycountry.countries.get(alpha_2=country_code.upper())
    return country.name if country else country_code

@app.route('/')
def index():
    global data
    try:
        with open("latest_200.json", "r") as f:
            data = json.load(f)
            # Convertir las cadenas de fecha a objetos datetime para ordenarlas
            for item in data:
                item["discovered"] = datetime.strptime(item["discovered"], "%Y-%m-%d %H:%M:%S.%f")
            data = sorted(data, key=lambda x: x["discovered"], reverse=True)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []



    group_filter = request.args.get('group-filter', '')
    country_filter = request.args.get('country-filter', '')
    discovered_order = request.args.get('discovered-order', 'desc')  # por defecto descendente

    # Filtrar los datos
    filtered_data = data
    if group_filter:
        filtered_data = [item for item in filtered_data if item['group_name'] == group_filter]
    if country_filter:
        filtered_data = [item for item in filtered_data if item['country'] == country_filter]

    # Ordenar los datos
    if discovered_order == 'asc':
        filtered_data.sort(key=lambda x: x['discovered'])
    else:
        filtered_data.sort(key=lambda x: x['discovered'], reverse=True)


    # Obtener listas únicas de grupos y países para los dropdowns
    groups = sorted(set(item['group_name'] for item in data))
    countries = sorted(set(item['country'] for item in data))

    return render_template("index.html", data=filtered_data, groups=groups, countries=countries, get_country_name=get_country_name)


@app.route('/all-victims')
def all_victims():
    global data
    try:
        with open("dataransom.json", "r") as f:
            data = json.load(f)
            # Convertir las cadenas de fecha a objetos datetime para ordenarlas
            for item in data:
                item["discovered"] = datetime.strptime(item["discovered"], "%Y-%m-%d %H:%M:%S.%f")
            data = sorted(data, key=lambda x: x["discovered"], reverse=True)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    group_filter = request.args.get('group-filter', '')
    country_filter = request.args.get('country-filter', '')
    discovered_order = request.args.get('discovered-order', 'desc')  # por defecto descendente

    # Filtrar los datos
    filtered_data = data
    if group_filter:
        filtered_data = [item for item in filtered_data if item['group_name'] == group_filter]
    if country_filter:
        filtered_data = [item for item in filtered_data if item['country'] == country_filter]

    # Ordenar los datos
    if discovered_order == 'asc':
        filtered_data.sort(key=lambda x: x['discovered'])
    else:
        filtered_data.sort(key=lambda x: x['discovered'], reverse=True)

    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 500  # Número máximo de elementos por página
    total_items = len(filtered_data)
    total_pages = math.ceil(total_items / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = filtered_data[start:end]

    # Obtener listas únicas de grupos y países para los dropdowns
    groups = sorted(set(item['group_name'] for item in data))
    countries = sorted(set(item['country'] for item in data))

    return render_template("all_victims.html", data=page_data, page=page, total_pages=total_pages, groups=groups, countries=countries, get_country_name=get_country_name, 
        max=max, min=min, range=range)

# Nueva ruta para mostrar la lista de grupos
@app.route('/groups')
def groups():
    try:
        with open("groups.json", "r") as f:
            groups_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        groups_data = []

    # Pasar solo los nombres de los grupos a la plantilla
    return render_template("groups.html", groups=groups_data)


# Nueva ruta para mostrar la lista de grupos
@app.route('/Breaches')
def Breaches():

    return render_template("Breaches.html")

# Nueva ruta para mostrar la lista de grupos
@app.route('/disclaimer')
def Disclaimer():

    return render_template("Disclaimer.html")

# Nueva ruta para mostrar la lista de grupos
@app.route('/leads')
def Leads():

    return render_template("Leads.html")

# Nueva ruta para mostrar la lista de grupos
@app.route('/stealer')
def StealerPaquets():

    return render_template("StealerPaquets.html")

# Nueva ruta para mostrar la lista de grupos
@app.route('/notableprojects')
def notable():

    return render_template("notable.html")

# Nueva ruta para mostrar la lista de grupos
@app.route('/countries')
def countries():
# Diccionario de países sin URLs de banderas
    return render_template("countries.html", get_country_name=get_country_name)

    
# Nueva ruta para mostrar los detalles de un grupo específico
@app.route('/groups/<group_name>')
def group_detail(group_name):
    try:
        with open("groups.json", "r") as f:
            groups_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        groups_data = []

    # Encontrar el grupo con el nombre dado
    group = next((g for g in groups_data if g["name"].lower() == group_name.lower()), None)

    if not group:
        return "Group not found", 404

        
    for item in group.get("targets", []):
        
        item['discovered'] = datetime.strptime(item['discovered'], '%Y-%m-%d %H:%M:%S.%f')   

    
    country_filter = request.args.get('country-filter', '')
    discovered_order = request.args.get('discovered-order', 'desc')  # por defecto descendente

    # Filtrar los datos
    filtered_data = group.get("targets", [])
    if country_filter:
        filtered_data = [item for item in filtered_data if item['country'] == country_filter]

    # Ordenar los datos
    if discovered_order == 'asc':
        filtered_data.sort(key=lambda x: x['discovered'])
    else:
        filtered_data.sort(key=lambda x: x['discovered'], reverse=True)

    countries = sorted(set(item['country'] for item in group.get("targets", [])))

    # Pasar el grupo encontrado a la plantilla
    return render_template("group_detail.html", group=group, data=filtered_data, get_country_name=get_country_name, countries=countries)

# Nueva ruta para mostrar los detalles de un grupo específico
@app.route('/country/<country>')
def country_detail(country):
    # 1. Cargamos el archivo 'all_countries.json', que es un diccionario:
    #    { "Mexico": [ lista_de_posts ], "Spain": [ lista_de_posts ], ... }
    try:
        with open("all_countries.json", "r", encoding="utf-8") as f:
            country_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        country_data = {}  # si no existe o está vacío, usamos dict vacío

    # 2. Obtenemos la lista de posts para el país solicitado.
    #    Usamos get(country, []) para que, si no existe la clave, devuelva una lista vacía.
    posts_for_country = country_data.get(country, [])
    if not posts_for_country:
        return "Country not found", 404

    # 3. Convertir strings de fecha 'discovered' a objetos datetime (si la info lo permite).
    #    Ajustar el formato según el que tengas guardado.
    for item in posts_for_country:
        discovered_str = item.get('discovered')
        if discovered_str:
            item['discovered'] = datetime.strptime(discovered_str, '%Y-%m-%d %H:%M:%S.%f')


    discovered_order = request.args.get('discovered-order', 'desc')  # Orden descendente por defecto
    group_filter = request.args.get('group-filter', '')

    filtered_data = posts_for_country
    if group_filter:
        filtered_data = [item for item in filtered_data if item['group_name'] == group_filter]

    # 4b. Ordenar los datos por fecha
    #     Solo ordenamos si item['discovered'] es datetime; si es string podrías necesitar otro criterio
    if discovered_order == 'asc':
        filtered_data.sort(key=lambda x: x['discovered'] if isinstance(x['discovered'], datetime) else None)
    else:
        filtered_data.sort(key=lambda x: x['discovered'] if isinstance(x['discovered'], datetime) else None, 
                           reverse=True)


    return render_template(
        "country_detail.html",
        country=country,                  # Nombre del país recibido en la URL
        data=filtered_data,               # Lista final de posts filtrados y ordenados
        get_country_name=get_country_name
    )


@app.route('/search_results', methods=['GET'])
def search_results():
    """
    Lee 'q' del query string, busca en 'dataransom.json',
    y renderiza 'results.html' con las entradas que coincidan.
    Ordena primero por score (mayor a menor), y luego por fecha (más nuevo a más antiguo).
    Además, formatea fechas de '2025-02-22 17:20:21.809152' a '2025-02-22'.
    """
    query = request.args.get('q', '').lower().strip()

    # Si no hay término de búsqueda, devolvemos una lista vacía
    if not query:
        return render_template('results.html', results=[])

    # Cargar datos desde JSON
    with open('dataransom.json', encoding='utf-8') as file:
        data = json.load(file)

    min_match_length = 4  # Mínimo de caracteres para búsqueda en título

    # Generamos fragmentos de longitud 'min_match_length' para búsqueda en el título
    if len(query) < min_match_length:
        title_search_terms = [query]
    else:
        title_search_terms = [
            query[i : i + min_match_length]
            for i in range(len(query) - min_match_length + 1)
        ]

    # Creamos las expresiones regulares para el título (búsqueda parcial)
    title_regex_patterns = [
        re.compile(re.escape(term), re.IGNORECASE)
        for term in title_search_terms
    ]

    # Expresión regular para búsqueda exacta en la descripción (palabra completa)
    description_regex = re.compile(
        r'\b' + re.escape(query) + r'\b',
        re.IGNORECASE
    )

    results = []

    for entry in data:
        post_title = entry.get('post_title', '')
        description = entry.get('description', '')
        
        # Fecha completa (ejemplo: "2025-02-22 17:20:21.809152")
        post_date_str = entry.get('published', '')

        # Parseamos la fecha si está disponible
        post_date_dt = None
        try:
            # Ajusta el formato de strptime si tu cadena difiere
            # "%Y-%m-%d %H:%M:%S.%f" funciona para "2025-02-22 17:20:21.809152"
            post_date_dt = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S.%f")
            # Guardamos la versión formateada (solo fecha) para mostrarla luego
            entry['post_date_str'] = post_date_dt.strftime("%Y-%m-%d")
        except ValueError:
            # Si no coincide el formato, opcionalmente manejar excepción
            entry['post_date_str'] = post_date_str  # dejar la original o vacía

        # Contamos coincidencias parciales en el título
        title_match_count = 0
        for pattern in title_regex_patterns:
            title_match_count += len(pattern.findall(post_title))

        # Contamos coincidencias exactas en la descripción
        description_match_count = len(description_regex.findall(description))

        # Score total para la entrada
        total_score = title_match_count + description_match_count

        if total_score > 0:
            entry['_score'] = total_score
            entry['_post_date_dt'] = post_date_dt  # Para ordenar por fecha real
            results.append(entry)

    # Ordenar de mayor a menor score y, luego, por fecha/hora descendente
    results.sort(
        key=lambda x: (
            x['_score'],
            x['_post_date_dt'] if x['_post_date_dt'] else datetime.min
        ),
        reverse=True
    )


    return render_template('results.html', results=results,  get_country_name=get_country_name)

@app.template_filter('datetimeformat')
def datetimeformat_filter(value, format='%Y-%m-%d'):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f').strftime(format)

@app.template_filter('url_truncate')
def url_truncate_filter(url, max_length=25):
    return url if len(url) <= max_length else f"{url[:max_length//2]}...{url[-max_length//2:]}"


if __name__ == '__main__':
    # Start the data fetching in a separate thread
    threading.Thread(target=schedule_data_fetching, daemon=True).start()
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
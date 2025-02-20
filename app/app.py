import requests
import json
import threading
import time
import os
import flag
import math
from datetime import datetime
from flask import Flask, render_template, request
import pycountry

app = Flask(__name__)
data_file = "dataransom.json"
data = []

country_flags = {
    "AF": '🇦🇫',
    "AX": '🇦🇽',
    "AL": '🇦🇱',
    "DZ": '🇩🇿',
    "AS": '🇦🇸',
    "AD": '🇦🇩',
    "AO": '🇦🇴',
    "AI": '🇦🇮',
    "AQ": '🇦🇶',
    "AG": '🇦🇬',
    "AR": '🇦🇷',
    "AM": '🇦🇲',
    "AW": '🇦🇼',
    "AU": '🇦🇺',
    "AT": '🇦🇹',
    "AZ": '🇦🇿',
    "BS": '🇧🇸',
    "BH": '🇧🇭',
    "BD": '🇧🇩',
    "BB": '🇧🇧',
    "BY": '🇧🇾',
    "BE": '🇧🇪',
    "BZ": '🇧🇿',
    "BJ": '🇧🇯',
    "BM": '🇧🇲',
    "BT": '🇧🇹',
    "BO": '🇧🇴',
    "BA": '🇧🇦',
    "BW": '🇧🇼',
    "BR": '🇧🇷',
    "IO": '🇮🇴',
    "VG": '🇻🇬',
    "BN": '🇧🇳',
    "BG": '🇧🇬',
    "BF": '🇧🇫',
    "BI": '🇧🇮',
    "KH": '🇰🇭',
    "CM": '🇨🇲',
    "CA": '🇨🇦',
    "CV": '🇨🇻',
    "BQ": '🇧🇶',
    "KY": '🇰🇾',
    "CF": '🇨🇫',
    "TD": '🇹🇩',
    "CL": '🇨🇱',
    "CN": '🇨🇳',
    "CX": '🇨🇽',
    "CC": '🇨🇨',
    "CO": '🇨🇴',
    "KM": '🇰🇲',
    "CG": '🇨🇬',
    "CK": '🇨🇰',
    "CR": '🇨🇷',
    "HR": '🇭🇷',
    "CU": '🇨🇺',
    "CW": '🇨🇼',
    "CY": '🇨🇾',
    "CZ": '🇨🇿',
    "CD": '🇨🇩',
    "DK": '🇩🇰',
    "DJ": '🇩🇯',
    "DM": '🇩🇲',
    "DO": '🇩🇴',
    "EC": '🇪🇨',
    "EG": '🇪🇬',
    "SV": '🇸🇻',
    "GQ": '🇬🇶',
    "ER": '🇪🇷',
    "EE": '🇪🇪',
    "ET": '🇪🇹',
    "FK": '🇫🇰',
    "FO": '🇫🇴',
    "FM": '🇫🇲',
    "FJ": '🇫🇯',
    "FI": '🇫🇮',
    "FR": '🇫🇷',
    "GF": '🇬🇫',
    "PF": '🇵🇫',
    "TF": '🇹🇫',
    "GA": '🇬🇦',
    "GM": '🇬🇲',
    "GE": '🇬🇪',
    "DE": '🇩🇪',
    "GH": '🇬🇭',
    "GI": '🇬🇮',
    "GR": '🇬🇷',
    "GL": '🇬🇱',
    "GD": '🇬🇩',
    "GP": '🇬🇵',
    "GU": '🇬🇺',
    "GT": '🇬🇹',
    "GN": '🇬🇳',
    "GW": '🇬🇼',
    "GY": '🇬🇾',
    "HT": '🇭🇹',
    "HN": '🇭🇳',
    "HK": '🇭🇰',
    "HU": '🇭🇺',
    "IS": '🇮🇸',
    "IN": '🇮🇳',
    "ID": '🇮🇩',
    "IR": '🇮🇷',
    "IQ": '🇮🇶',
    "IE": '🇮🇪',
    "IM": '🇮🇲',
    "IL": '🇮🇱',
    "IT": '🇮🇹',
    "CI": '🇨🇮',
    "JM": '🇯🇲',
    "JP": '🇯🇵',
    "JE": '🇯🇪',
    "JO": '🇯🇴',
    "KZ": '🇰🇿',
    "KE": '🇰🇪',
    "KI": '🇰🇮',
    "XK": '🇽🇰',
    "KW": '🇰🇼',
    "KG": '🇰🇬',
    "LA": '🇱🇦',
    "LV": '🇱🇻',
    "LB": '🇱🇧',
    "LS": '🇱🇸',
    "LR": '🇱🇷',
    "LY": '🇱🇾',
    "LI": '🇱🇮',
    "LT": '🇱🇹',
    "LU": '🇱🇺',
    "MO": '🇲🇴',
    "MK": '🇲🇰',
    "MG": '🇲🇬',
    "MW": '🇲🇼',
    "MY": '🇲🇾',
    "MV": '🇲🇻',
    "ML": '🇲🇱',
    "MT": '🇲🇹',
    "MH": '🇲🇭',
    "MQ": '🇲🇶',
    "MR": '🇲🇷',
    "MU": '🇲🇺',
    "YT": '🇾🇹',
    "MX": '🇲🇽',
    "MD": '🇲🇩',
    "MC": '🇲🇨',
    "MN": '🇲🇳',
    "ME": '🇲🇪',
    "MS": '🇲🇸',
    "MA": '🇲🇦',
    "MZ": '🇲🇿',
    "MM": '🇲🇲',
    "NA": '🇳🇦',
    "NR": '🇳🇷',
    "NP": '🇳🇵',
    "NL": '🇳🇱',
    "NC": '🇳🇨',
    "NZ": '🇳🇿',
    "NI": '🇳🇮',
    "NE": '🇳🇪',
    "NG": '🇳🇬',
    "NU": '🇳🇺',
    "NF": '🇳🇫',
    "KP": '🇰🇵',
    "MP": '🇲🇵',
    "NO": '🇳🇴',
    "OM": '🇴🇲',
    "PK": '🇵🇰',
    "PW": '🇵🇼',
    "PS": '🇵🇸',
    "PA": '🇵🇦',
    "PG": '🇵🇬',
    "PY": '🇵🇾',
    "PE": '🇵🇪',
    "PH": '🇵🇭',
    "PN": '🇵🇳',
    "PL": '🇵🇱',
    "PT": '🇵🇹',
    "PR": '🇵🇷',
    "QA": '🇶🇦',
    "RE": '🇷🇪',
    "RO": '🇷🇴',
    "RU": '🇷🇺',
    "RW": '🇷🇼',
    "SH": '🇸🇭',
    "KN": '🇰🇳',
    "LC": '🇱🇨',
    "PM": '🇵🇲',
    "VC": '🇻🇨',
    "WS": '🇼🇸',
    "SM": '🇸🇲',
    "ST": '🇸🇹',
    "SA": '🇸🇦',
    "SN": '🇸🇳',
    "RS": '🇷🇸',
    "SC": '🇸🇨',
    "SL": '🇸🇱',
    "SG": '🇸🇬',
    "SX": '🇸🇽',
    "SK": '🇸🇰',
    "SI": '🇸🇮',
    "SB": '🇸🇧',
    "SO": '🇸🇴',
    "ZA": '🇿🇦',
    "GS": '🇬🇸',
    "KR": '🇰🇷',
    "SS": '🇸🇸',
    "ES": '🇪🇸',
    "LK": '🇱🇰',
    "SD": '🇸🇩',
    "SR": '🇸🇷',
    "SJ": '🇸🇯',
    "SZ": '🇸🇿',
    "SE": '🇸🇪',
    "CH": '🇨🇭',
    "SY": '🇸🇾',
    "TW": '🇹🇼',
    "TJ": '🇹🇯',
    "TZ": '🇹🇿',
    "TH": '🇹🇭',
    "TL": '🇹🇱',
    "TG": '🇹🇬',
    "TK": '🇹🇰',
    "TO": '🇹🇴',
    "TT": '🇹🇹',
    "TN": '🇹🇳',
    "TR": '🇹🇷',
    "TM": '🇹🇲',
    "TC": '🇹🇨',
    "TV": '🇹🇻',
    "UG": '🇺🇬',
    "UA": '🇺🇦',
    "AE": '🇦🇪',
    "GB": '🇬🇧',
    "US": '🇺🇸',
    "UM": '🇺🇲',
    "VI": '🇻🇮',
    "UY": '🇺🇾',
    "UZ": '🇺🇿',
    "VU": '🇻🇺',
    "VA": '🇻🇦',
    "VE": '🇻🇪',
    "VN": '🇻🇳',
    "WF": '🇼🇫',
    "EH": '🇪🇭',
    "YE": '🇾🇪',
    "ZM": '🇿🇲',
    "ZW": '🇿🇼',
}

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

    # Convertir los códigos de país a emojis de bandera
    for item in data:
        country_code = item.get("country")
        if country_code:
            item["country_flag"] = country_flags.get(country_code, '')  # Usa el diccionario para obtener la bandera
        else:
            item["country_flag"] = ''



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

    # Convertir los códigos de país a emojis de bandera
    for item in data:
        country_code = item.get("country")
        if country_code:
            item["country_flag"] = country_flags.get(country_code, '')  # Usa el diccionario para obtener la bandera
        else:
            item["country_flag"] = ''


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

        # Convertir los códigos de país a emojis de bandera
    for item in group.get("targets", []):
        
        item['discovered'] = datetime.strptime(item['discovered'], '%Y-%m-%d %H:%M:%S.%f')   

        country_code = item["country"]
        if country_code:
            item["country_flag"] = country_flags.get(country_code, '')  # Usa el diccionario para obtener la bandera
        else:
            item["country_flag"] = ''

    
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

@app.route('/your_view_function')
def your_view_function():
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

    return render_template('your_template.html', data=filtered_data, groups=groups, countries=countries)



if __name__ == '__main__':
    # Start the data fetching in a separate thread
    #app.run(debug=True)
    app.run(host='127.0.0.1', port=5000)


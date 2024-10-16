import requests
import json
import threading
import time
import os
import flag
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)
data_file = "dataransom.json"
data = []


def update_groups_json():

    # Leer el archivo groups.json si existe, de lo contrario usar una lista vacía
    if os.path.exists('groups.json'):
        with open('groups.json', 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Convertir los datos existentes a un conjunto de tuplas (name, fqdn) para facilitar la comparación
    existing_entries = {(entry['name'], location['Source Links']) for entry in existing_data for location in entry['locations']}

    # Procesar los nuevos datos y añadir sólo los nuevos
    for item in new_data:
        name = item.get('name')
        locations = item.get('locations', [])

        # Filtrar y preparar las nuevas ubicaciones
        new_locations = [
            {'Source Links': loc['fqdn']}
            for loc in locations
            if (name, loc['fqdn']) not in existing_entries
        ]

        # Si hay nuevas ubicaciones, añadir el item actualizado a los datos existentes
        if new_locations:
            existing_data.append({
                'name': name,
                'locations': new_locations
            })

    # Guardar los datos actualizados en groups.json
    sorted_groups = sorted(existing_data, key=lambda x: (not x['name'][0].isdigit(), x['name']))
    with open('groups.json', 'w', encoding='utf-8') as file:
        json.dump(sorted_groups, file, indent=4, ensure_ascii=False)
    print("Archivo groups.json actualizado exitosamente.")



def fetch_and_update_data():
    """Fetch new data from the API and update the local file with the latest 200 entries."""
    global data

    try:

        # Load existing data
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # Create a list of existing post URLs to avoid duplicates
        existing_urls = {item["post_url"] for item in existing_data} # cambiar esto porque si no los que no tienen link no los pone

        # Filter out existing entries and assign ID
        new_entries = [
            {**item, "id": len(existing_data) + idx + 1} 
            for idx, item in enumerate(new_data) 
            if item["post_url"] not in existing_urls
        ]

        if new_entries:
            existing_data.extend(new_entries)
            with open(data_file, "w") as f:
                json.dump(existing_data, f, indent=4)
            print(f"Added {len(new_entries)} new entries.")
        else:
            print("No new entries found.")

        data = existing_data
        
        # Update the latest 200 entries file
        latest_data = sorted(data, key=lambda x: datetime.strptime(x["discovered"], "%Y-%m-%d %H:%M:%S.%f"), reverse=True)[:200]
        with open("latest_200.json", "w") as f:
            json.dump(latest_data, f, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")


def schedule_data_fetching():
    while True:
        fetch_and_update_data()
        time.sleep(3600)  # Fetch data every hour


def updated_groups_json():
    while True:
        update_groups_json()
        time.sleep(76250)  # Fetch data every x


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
        if item["country"] == '':
            item["country"] = item["country"]
        else:
            item["country"] = flag.flag(item["country"])

    return render_template("index.html", data=data)


@app.route('/all-victims')
def all_victims():
    global data
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
            for item in data:
                item["discovered"] = datetime.strptime(item["discovered"], "%Y-%m-%d %H:%M:%S.%f")
            data = sorted(data, key=lambda x: x["discovered"], reverse=True)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []


            # Convertir los códigos de país a emojis de bandera
    for item in data:
        if item["country"] == '':
            item["country"] = item["country"]
        else:
            item["country"] = flag.flag(item["country"])

    return render_template("all_victims.html", data=data)

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

    # Pasar el grupo encontrado a la plantilla
    return render_template("group_detail.html", group=group)

if __name__ == '__main__':
    # Start the data fetching in a separate thread
    threading.Thread(target=schedule_data_fetching, daemon=True).start()
    threading.Thread(target=updated_groups_json, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)


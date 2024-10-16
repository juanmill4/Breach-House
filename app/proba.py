import requests
import json
import os




def update_groups_json():
    # Descargar el archivo JSON desde la URL
    try:
        response = requests.get("https://data.ransomware.live/groups.json")
        response.raise_for_status()  # Asegurarse de que la solicitud fue exitosa
        new_data = response.json()
    except requests.RequestException as e:
        print(f"Error al descargar el JSON: {e}")
        return

    # Leer el archivo groups.json si existe, de lo contrario usar una lista vacía
    if os.path.exists('groups.json'):
        with open('groups.json', 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Convertir los datos existentes a un conjunto de tuplas (name, fqdn) para facilitar la comparación
    existing_entries = {(entry['name'], location['fqdn']) for entry in existing_data for location in entry['locations']}

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
    with open('groups.json', 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
    print("Archivo groups.json actualizado exitosamente.")


update_groups_json()

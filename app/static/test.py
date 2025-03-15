import pycountry

def generate_country_flags():
    country_flags = {
        country.alpha_2: f"https://flagcdn.com/w160/{country.alpha_2.lower()}.png"
        for country in pycountry.countries
    }
    
    js_code = "const countryFlags = {\n"
    for code, url in sorted(country_flags.items()):
        js_code += f"    {code}: '{url}',\n"
    js_code += "};"
    
    return js_code

# Generar y guardar el código en un archivo
if __name__ == "__main__":
    js_code = generate_country_flags()
    print(js_code)

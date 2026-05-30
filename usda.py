import os
import requests

BASE_URL = 'https://api.nal.usda.gov/fdc/v1'


def lookup_fdc_id(fdc_id):
    api_key = os.environ.get('USDA_API_KEY')
    if not api_key:
        raise RuntimeError('USDA_API_KEY is not set in environment')

    resp = requests.get(
        f'{BASE_URL}/food/{fdc_id}',
        params={'api_key': api_key},
        timeout=10,
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    food = resp.json()

    label = food.get('labelNutrients') or {}
    serving_size = food.get('servingSize') or 100

    def per_100g(nutrient_key):
        val = label.get(nutrient_key, {}).get('value')
        if val is None:
            return None
        return round(val / serving_size * 100, 4)

    return {
        'name': food.get('description', ''),
        'upc': food.get('gtinUpc', ''),
        'serving_size': serving_size,
        'serving_unit': food.get('servingSizeUnit', 'g'),
        'kcal': per_100g('calories'),
        'protein': per_100g('protein'),
        'fat': per_100g('fat'),
        'carbs': per_100g('carbohydrates'),
        'fiber': per_100g('fiber'),
    }

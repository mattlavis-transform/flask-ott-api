from decouple import RepositoryEmpty
from flask import Flask, request, jsonify
from flask import json
from flask_caching import Cache
import os

from classes.application import Application
from classes.goods_nomenclature import GoodsNomenclature

config = {
    "DEBUG": True,           # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "JSON_SORT_KEYS": False
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

# Default route
@app.route('/', methods=['GET'])
def home():
    return 'Online Tariff Flask API'

# Test DB
@app.route('/db', methods=['GET'])
def db():
    DATABASE_URL = os.getenv('DATABASE_URL')
    return DATABASE_URL

# Gets a commodity code
@app.route('/commodities/<commodity>.json', methods=['GET'])
@cache.cached()
def show_commodity(commodity):
    gn = GoodsNomenclature(commodity)
    gn.get_ancestors_and_descendants()
    results = gn.get_commodity_json()
    return jsonify(results)

# Gets a heading
@app.route('/headings/<heading_id>.json', methods=['GET'])
@cache.cached()
def show_heading(heading_id):
    gn = GoodsNomenclature(heading_id)
    gn.get_ancestors_and_descendants()
    results = gn.get_heading_json()
    return jsonify(results)

# Measure type series
@app.route('/measure_types', methods=['GET'])
def measure_types():
    ret = Application.get_measure_types()
    return jsonify(ret)

# Measure types
@app.route('/measure_type_series', methods=['GET'])
def measure_type_series():
    ret = Application.get_measure_type_series()
    return jsonify(ret)

# Certificate types
@app.route('/certificate_types', methods=['GET'])
def certificate_types():
    ret = Application.get_certificate_types()
    return jsonify(ret)

# Additional code types
@app.route('/additional_code_types', methods=['GET'])
def additional_code_types():
    ret = Application.get_additional_code_types()
    return jsonify(ret)

# Footnote types
@app.route('/footnote_types', methods=['GET'])
def footnote_types():
    ret = Application.get_footnote_types()
    return jsonify(ret)

# Gets Meursing measures
@app.route('/meursing/<additional_code_id>/<geographical_area_id>', methods=['GET'])
@cache.cached()
def get_meursing_measures(additional_code_id, geographical_area_id):
    results = Application.get_meursing_measures(additional_code_id, geographical_area_id)
    return jsonify(results)

# Gets Meursing additional codes
@app.route('/meursing_codes', methods=['GET'])
@cache.cached()
def get_meursing_codes():
    results = Application.get_meursing_codes()
    return jsonify(results)

# Gets valid Meursing additional codes as list
@app.route('/meursing_code_list', methods=['GET'])
@cache.cached()
def get_meursing_code_list():
    results = Application.get_meursing_code_list()
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from xml_compare import parse_xml_from_string, flatten_elements, compare_xml

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Route for landing page
@app.route('/')
def landing():
    return render_template('landing.html')
# Route for comparison interface
@app.route('/compare')
def compare_page():
    return render_template('index.html')


# API route for comparing pasted XML
@app.route('/api/compare', methods=['POST'])
def compare_xml_data():
    data = request.get_json()
    xml1, xml2 = data.get('xml1'), data.get('xml2')

    root1, error1 = parse_xml_from_string(xml1)
    root2, error2 = parse_xml_from_string(xml2)

    if error1 or error2:
        return jsonify({'error': error1 or error2}), 400

    flat1 = flatten_elements(root1)
    flat2 = flatten_elements(root2)

    differences = compare_xml(flat1, flat2)
    return jsonify(differences)

if __name__ == '__main__':
    app.run(debug=True)

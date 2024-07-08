from flask import Flask, render_template_string, request, jsonify
import pickle
import pandas as pd
import stats_calculator 

app = Flask(__name__)

with open('wikidata_stats.pickle', 'rb') as f:
    data = pickle.load(f)


label_to_id = {data[item]['entity']['label']: item for item in data if 'entity' in data[item] and 'label' in data[item]['entity']}

def serialize_data(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: serialize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_data(item) for item in obj]
    else:
        return obj

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Prove</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <style>
        .list-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
        }
        .list-item {
            cursor: pointer;
            padding: 5px;
        }
        .list-item:hover {
            background-color: #f0f0f0;
        }
    </style>
    <script>
        $(document).ready(function(){
            function displayData(label) {
                $.get("/get_data", {label: label}, function(data){
                    $("#data-display").html(data);
                });
            }
            $(".list-item").click(function(){
                displayData($(this).text());
            });
            $("#search-input").on("keyup", function() {
                var value = $(this).val().toLowerCase();
                $(".list-item").filter(function() {
                    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                });
            });
        });
    </script>
</head>
<body>
    <h1>Prove</h1>
    <div style="display: flex;">
        <div style="width: 30%; padding-right: 20px;">
            <h2>Wikidata items</h2>
            <input type="text" id="search-input" placeholder="Search items...">
            <div class="list-container">
                <ul>
                    {% for label in labels %}
                    <li class="list-item">{{ label }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        <div style="width: 70%;">
            <h2>Result Display</h2>
            <div id="data-display"></div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, labels=label_to_id.keys())

@app.route('/get_data')
def get_data():
    label = request.args.get('label', '')
    item_id = label_to_id.get(label)
    if item_id and item_id in data:
        result = serialize_data(data[item_id]['entity']['label'])
        result_values = [data[item_id]['entity']['label']]
        result_values += stats_calculator.stats(data[item_id]['entity'])
        result_values += stats_calculator.entailmentResult(data[item_id]['result'])
        html_content = stats_calculator.format_to_html(result_values)
        return html_content
    return jsonify({'error': 'Data not found'})

if __name__ == '__main__':
    app.run(debug=True)
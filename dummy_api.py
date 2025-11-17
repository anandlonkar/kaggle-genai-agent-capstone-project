from flask import Flask, send_file

app = Flask(__name__)

@app.route('/api/get_smart_meter_data', methods=['GET'])
def get_smart_meter_data():
    """
    This endpoint returns a sample smart meter data file.
    """
    try:
        return send_file(
            'C:\\code\\googlexkaggle\\Capstone\\smartmeterdata\\10443720000055536-20241101-20251031.csv',
            mimetype='text/csv',
            as_attachment=True,
            download_name='smart_meter_data.csv'
        )
    except FileNotFoundError:
        return "File not found.", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)

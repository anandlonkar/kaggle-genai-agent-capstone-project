import requests
from flask import Flask, Response, stream_with_context

app = Flask(__name__)

DUMMY_API_URL = "http://127.0.0.1:5001/api/get_smart_meter_data"

@app.route('/mcp/meter_data/<string:meter_id>', methods=['GET'])
def get_meter_data(meter_id):
    """
    MCP endpoint to get meter data.
    It calls the dummy API and streams the response.
    The meter_id is ignored for now as we have only one data file.
    """
    try:
        # Make a request to the dummy API
        # Using stream=True to handle large files without loading them into memory
        response = requests.get(DUMMY_API_URL, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Stream the content from the dummy API to the client
        return Response(stream_with_context(response.iter_content(chunk_size=1024)),
                        content_type=response.headers['Content-Type'])

    except requests.exceptions.RequestException as e:
        return f"Error fetching data from dummy API: {e}", 502

if __name__ == '__main__':
    # Running on a different port than the dummy_api
    app.run(debug=True, port=5002)

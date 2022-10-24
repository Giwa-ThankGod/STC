from flask import Flask, jsonify
from jose import jwt

app = Flask(__name__)

@app.route('/public', methods=['GET'])
def public():
    return jsonify({
        'message': 'Public Endpoint',
        "success": True,
    })

if __name__ == '__main__':
    app.run(debug=True)


import json
from flask import request,Flask, Response
from flask_cors import CORS
import operations
app = Flask(__name__)

@app.route('/orders', methods=['GET'])
def get_orders():
    result = operations.get_orders(request.values.get('email'))
    return Response(json.dumps(result), mimetype='application/json', status=200)

@app.route('/getnextorder', methods=['GET'])
def get_next_order():
    result = operations.get_next_order(request.values.get('email'))
    return Response(json.dumps(result), mimetype='application/json', status=200)

@app.route('/user', methods=['GET'])
def get_user():
    result = operations.get_user(request.values.get('email'))
    if result:
        return Response(json.dumps(result), mimetype='application/json', status=200)
    else:
        return Response({}, mimetype='application/json', status=404)


@app.route('/hello', methods=['GET'])
def hello():
    return Response({"Hello world"}, mimetype='application/json', status=200)

@app.route('/user', methods=['POST'])
def add_or_update_user():
    body = json.loads(request.data)
    result = operations.add_or_update_user(body)
    return Response(json.dumps({}), mimetype='application/json', status=200)

@app.route('/changestatus', methods=['POST'])
def change_order_status():
    body = json.loads(request.data)
    result = operations.change_order_status(body['id'])
    return Response(json.dumps({}), mimetype='application/json', status=200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=83)

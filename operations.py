import mysql.connector
import os
cnx = None

def get_connection():
    global cnx

    if not cnx:
        cnx = mysql.connector.connect(user = 'root', password='Admin@123', host='localhost', database = 'systeam_ecommerce',
                              auth_plugin='mysql_native_password')
    return cnx


def get_orders(email):

    cursor = get_connection().cursor()

    cursor.execute("SELECT * FROM orders join order_details on orders.order_id = order_details.order_id")

    rows = cursor.fetchall()

    processed_orders =[]
    result = []
    for row in rows:
        order_id = row[0]
        if order_id not in processed_orders:
            order = {'order_id': order_id}
            order['total_amount'] = row[1]
            order['created_on'] = str(row[2])
            order['status'] = row[3]
            order['products'] = []
            result.append(order)
            processed_orders.append(order_id)

    for row in rows:
        order_id = row[0]
        product = {}
        product['product_name'] = row[8]
        product['product_id'] = row[6]
        product['quantity'] = row[9]
        product['unit_cost'] = row[10]

        for i in range(len(result)):
            if result[i]['order_id'] == order_id:
                result[i]['products'].append(product)
    return result


def get_user(email):
    cursor = get_connection().cursor()
    cursor.execute("SELECT role FROM users where email = '"+email+"'")
    rows = cursor.fetchall()

    if len(rows) < 1:
        return None
    else:
        return {'role': rows[0][0]}


def change_order_status(id):
    pass
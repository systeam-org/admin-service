import mysql.connector
from stompest.config import StompConfig
from stompest.sync import Stomp
from stompest.protocol import StompSpec
import socket
import Constants

import os
cnx = None

def get_connection():
    global cnx

    try:
        cnx = mysql.connector.connect(user=Constants.LOCAL_DATABASE_USER,
                                      password=Constants.LOCAL_DATABASE_PASSWORD,
                                      host=Constants.LOCAL_DATABASE_ENDPOINT,
                                      database=Constants.LOCAL_DATABASE_NAME,
                                      auth_plugin='mysql_native_password')
    except:
        cnx = mysql.connector.connect(user=Constants.PRODUCTION_DATABASE_USER,
                                      password=Constants.PRODUCTION_DATABASE_PASSWORD,
                                      host=Constants.PRODUCTION_DATABASE_ENDPOINT,
                                      database=Constants.PRODUCTION_DATABASE_NAME,
                                      auth_plugin='mysql_native_password')
    cnx.autocommit = True
    return cnx

def isOpen(dns,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((dns, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

def get_orders(email):
    conn = get_connection()
    cursor = conn.cursor()

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
    conn.close()
    return result


def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users where email = '"+email+"'")
    rows = cursor.fetchall()

    conn.close()
    if len(rows) < 1:
        return None
    else:
        return {'role': rows[0][0]}

def get_next_order(email):
    role = get_user(email).get('role')
    conn = get_connection()

    returnid = None
    if role == 'OrderAdmin':
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM next_order where  status= 'Ordered'")
        rows = cursor.fetchall()
        returnid = None
        if len(rows) < 1:
            amq_conf = None
            queue = '/queue/ordered'

            #if isOpen('activemq.default', 61612):
            amq_conf = StompConfig('tcp://activemq-service.default:61613')
            #else:
            #    amq_conf = StompConfig('tcp://localhost:30012')

            try:
                client = Stomp(amq_conf)
                client.connect()
                client.subscribe(queue, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
                if client.canRead(timeout=2):
                    frame = client.receiveFrame()

                    cursor = conn.cursor()

                    sql = "Insert into next_order (status, order_id) values (%s,%s)"
                    values = ( 'Ordered', int(frame.body.decode()))
                    row = cursor.execute(sql, values)
                    conn.commit()
                    client.ack(frame)
                    returnid = int(frame.body.decode())
                else:
                    returnid = None
                client.disconnect()
            except:
                print("something went wrong")
                returnid = None
        else:
            returnid = rows[0][0]
    elif role == 'ShipmentAdmin':
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM next_order where  status= 'ReadyToShip'")
        rows = cursor.fetchall()

        returnid = None
        if len(rows) < 1:
            amq_conf = None
            queue = '/queue/readytoship'

            #if isOpen('activemq.default', 61612):
            amq_conf = StompConfig('tcp://activemq-service.default:61613')
            #else:
            #    amq_conf = StompConfig('tcp://localhost:30012')

            try:
                client = Stomp(amq_conf)
                client.connect()
                client.subscribe(queue, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
                if client.canRead(timeout=2):
                    frame = client.receiveFrame()

                    cursor = conn.cursor()

                    sql = "Insert into next_order (status, order_id) values (%s,%s)"
                    values = ( 'ReadyToShip', int(frame.body.decode()))
                    row = cursor.execute(sql, values)
                    conn.commit()
                    client.ack(frame)
                    returnid = int(frame.body.decode())
                else:
                    returnid = None
                client.disconnect()
            except:
                print("something went wrong")
                returnid = None
        else:
            returnid = rows[0][0]
    elif role == 'DeliveryAdmin':
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM next_order where  status= 'Shipped'")
        rows = cursor.fetchall()

        returnid = None
        if len(rows) < 1:
            amq_conf = None
            queue = '/queue/shipped'

            #if isOpen('activemq.default', 61612):
            amq_conf = StompConfig('tcp://activemq-service.default:61613')
            #else:
            #    amq_conf = StompConfig('tcp://localhost:30012')

            try:
                client = Stomp(amq_conf)
                client.connect()
                client.subscribe(queue, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
                if client.canRead(timeout=2):
                    frame = client.receiveFrame()

                    cursor = conn.cursor()

                    sql = "Insert into next_order (status, order_id) values (%s,%s)"
                    values = ( 'Shipped', int(frame.body.decode()))
                    row = cursor.execute(sql, values)
                    conn.commit()
                    client.ack(frame)
                    returnid = int(frame.body.decode())
                else:
                    returnid = None
                client.disconnect()
            except:
                print("something went wrong")
                returnid = None
        else:
            returnid = rows[0][0]


    if returnid:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders join order_details on orders.order_id = order_details.order_id where orders.order_id = " + str(returnid) + "")
        rows = cursor.fetchall()
        print(rows)
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
        conn.close()
        return result
    else:
        conn.close()
        return []
def change_order_status(id):
    conn= get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM orders where  order_id = "+str(id)+"")
    rows = cursor.fetchall()

    status = rows[0][0]
    next_status= None
    if status == 'Ordered':
        next_status = 'ReadyToShip'
        queue = '/queue/readytoship'

    elif status == 'ReadyToShip':
        next_status = 'Shipped'
        queue = '/queue/shipped'

    elif status == 'Shipped':
        next_status = 'Delivered'

    if status=='Delivered':
        return True
    if next_status == 'ReadyToShip' or next_status == 'Shipped':
            amq_conf = None
            #if isOpen('activemq.default', 61612):
            amq_conf = StompConfig('tcp://activemq-service.default:61613')
            #else:
            #    amq_conf = StompConfig('tcp://localhost:30012')
            try:
                client = Stomp(amq_conf)
                client.connect()
                client.send(queue, str(id).encode())
                client.disconnect()
            except:
                print("something went wrong")
    sql = "Update systeam_ecommerce.orders SET status = '"+next_status+"' where order_id = " +str(id)+ ""
    rows = cursor.execute(sql)

    sql = "Delete from systeam_ecommerce.next_order where status = '" + status+ "'"
    rows = cursor.execute(sql)

    conn.commit()
    conn.close()
    return True

# -*- coding: utf-8 -*-
import socket, netstream
connected = False
sock = None

serialID = 0            #server向客户端发回的序列ID号
isSet = False

def connect():
    global connected, sock
    #if connected:
    #    return connected
    #connect server
    host = "127.0.0.1"
    port = 9234
    sock = socket.socket()
    try: 
        sock.connect((host, port))
    except:
        connected = False
        return connected
    
    connected = True

    #gameScene.schedule(receiveServer)
    receiveServer()
    return connected

#始终接收服务端消息
def receiveServer():
    global connected, serialID
    if not connected:
        return
    data = netstream.read(sock)
    if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
        return

    #客户端SID
    if 'sid' in data:
        serialID = data['sid']
        print 'sid :', data['sid']

    if 'notice_content' in data:
        import game_controller
        game_controller.showContent(data['notice_content']) #showContent is from game_controller


def get_send_data():
    send_data = {}
    send_data['sid'] = serialID
    return send_data

#向server请求公告
def request_notice():
    send_data = get_send_data()
    send_data['notice'] = 'request notice'
    netstream.send(sock, send_data)
    receiveServer()

def sendServer(message):
    global sock, serialID
    send_data = get_send_data()
    message['sid'] = send_data['sid']

    netstream.send(sock, message)
    tmp = netstream.read(sock)
    if isinstance(tmp, int):
        return 'Read from Server wrong, reenter and try'
    else:
        return tmp['FUNC']

def closeSock():
    if sock != None:
        # sock.shutdown(socket.SHUT_RDWR)
        sock.close()

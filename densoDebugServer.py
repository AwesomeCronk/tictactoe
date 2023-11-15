import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('10.1.0.9', 6000))

sock.listen(1)

while True:
    conn, addr = sock.accept()
    print('<Connection from {}>'.format(addr))

    try:
        while True:
            print(conn.recv(1024).decode(), end='')
    finally:
        print('<Closing connection>')
        conn.close()

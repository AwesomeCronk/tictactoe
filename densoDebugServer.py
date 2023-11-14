import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('0.0.0.0', 6000))

sock.listen(1)
sock.settimeout(5)

while True:
    try: conn, addr = sock.accept()
    except socket.timeout:
        continue
    print('<Connection from {}>'.format(addr))

    while True:
        try: print(conn.recv(1024).decode(), end='')
        except socket.timeout:
            print('<Timed out, closing connection>')
            conn.close()
            break

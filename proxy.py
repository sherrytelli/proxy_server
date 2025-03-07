#!/usr/bin/env python3
import os
import socket
import sys
from urllib.parse import urlparse

BACKLOG = 10 #maximum pending connections
MAX_CONN = 100 #maximum connections that proxy can handle

def send_error(conn, status, message):
    response = f"HTTP/1.0 {status} {message}\r\n" \
               "Content-Type: text/html\r\n\r\n" \
               f"<html><body><h1>{status} {message}</h1></body></html>\r\n"
    conn.sendall(response.encode())

def parse_request(request):
    # parse the first line of the HTTP request.
    request_line = request.splitlines()[0]
    print(f"request recieved: {request_line}\n")
    method, url, protocol = request_line.split()
    return method, url, protocol

def parse_url(url):
    # expect an absolute URL like http://hostname[:port]/path
    parsed = urlparse(url)
    if parsed.scheme != "http":
        return None, None, None
    hostname = parsed.hostname
    port = parsed.port if parsed.port else 80
    path = parsed.path if parsed.path else "/"
    return hostname, port, path

def validate_hostname(hostname):
    # try to resolve the hostname; if resolution fails, return False.
    try:
        socket.getaddrinfo(hostname, None)
        return True
    except socket.gaierror:
        return False

def forward_request(client_conn, method, url, protocol):
    hostname, port, path = parse_url(url)
    if not hostname or not validate_hostname(hostname):
        send_error(client_conn, 400, "Bad Request")
        return

    #build the request to the origin server
    request = f"GET {path} HTTP/1.0\r\n"
    request += f"Host: {hostname}\r\n"
    request += "Connection: close\r\n\r\n"

    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_sock.connect((hostname, port))
    remote_sock.sendall(request.encode())

    while True:
        data = remote_sock.recv(8192)
        if not data:
            break
        client_conn.sendall(data)
    remote_sock.close()

def handle_client(client_conn):
    request = client_conn.recv(8192).decode()
    if not request:
        return

    method, url, protocol = parse_request(request)
    if not (method and url and protocol):
        send_error(client_conn, 400, "Bad Request")
        return

    if method.upper() != "GET":
        send_error(client_conn, 501, "Not Implemented")
        return

    forward_request(client_conn, method, url, protocol)
    client_conn.close()

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python proxy.py listening_port")
        sys.exit(1)

    port = sys.argv[1]
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind(('', int(port)))
    listen_sock.listen(BACKLOG)
    print(f"Proxy listening on port {port}...")
    
    conn_num = 0

    while True:
        client_conn, client_addr = listen_sock.accept()
        conn_num += 1
        
        if(conn_num >= MAX_CONN):
            client_conn.close()
            continue
        
        pid = os.fork()
        if pid == 0:
            listen_sock.close()
            handle_client(client_conn)
            client_conn.close()
            os._exit(0)
        else:
            client_conn.close()

    listen_sock.close()

if __name__ == '__main__':
    main()
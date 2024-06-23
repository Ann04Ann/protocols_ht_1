import socket
from dnslib import DNSRecord, RR
import pickle
import time
import threading

CACHE_FILE = 'cache.pkl'
TTL_CHECK_INTERVAL = 60
UDP_IP = "127.0.0.1"
UDP_PORT = 53


dns_cache = {}

def load_cache():
    try:
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def save_cache():
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(dns_cache, f)

def check_ttl():
    global dns_cache
    while True:
        time.sleep(TTL_CHECK_INTERVAL)
        current_time = int(time.time())
        dns_cache = {k: v for k, v in dns_cache.items() if v[1] > current_time}

def query_dns(question):

    server = ('8.8.8.8', 53)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # Время ожидания ответа от сервера
    try:
        sock.sendto(question.pack(), server)
        data, _ = sock.recvfrom(4096)
        return DNSRecord.parse(data)
    except socket.timeout:
        return None

def process_request(data):
    request = DNSRecord.parse(data)
    reply = request.reply()
    qname = str(request.q.qname)


    cached = dns_cache.get(qname, None)
    current_time = int(time.time())

    if cached and cached[1] > current_time:
        reply.add_answer(*cached[0])
    else:

        response = query_dns(request)
        if response:

            for rr in response.rr + response.auth + response.ar:
                dns_cache[str(rr.rname)] = ([rr], int(time.time()) + rr.ttl)

            reply = response

    return reply.pack()

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(512)
        reply_data = process_request(data)
        if reply_data:
            sock.sendto(reply_data, addr)

if __name__ == "__main__":
    dns_cache = load_cache()
    ttl_thread = threading.Thread(target=check_ttl, daemon=True)
    ttl_thread.start()

    try:
        start_server()
    except KeyboardInterrupt:
        save_cache()

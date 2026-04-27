import argparse
import requests
import threading
import sys
from queue import Queue
from banner import banner

# --------------------------------------------------
# Directorios / Fuzzing
def dir_scan(url, wordlist, threads):
    def worker():
        while not q.empty():
            word = q.get()
            test_url = url.rstrip('/') + '/' + word.strip()
            try:
                r = requests.get(test_url, timeout=3)
                if r.status_code in [200, 301, 302, 403]:
                    print(f"[{r.status_code}] {test_url}")
            except:
                pass
            q.task_done()

    q = Queue()
    with open(wordlist, 'r') as f:
        for line in f:
            q.put(line)

    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# --------------------------------------------------
# DNS discovery
def dns_scan(domain, wordlist, threads):
    import socket
    def worker():
        while not q.empty():
            sub = q.get().strip()
            target = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(target)
                print(f"[FOUND] {target} -> {ip}")
            except:
                pass
            q.task_done()

    q = Queue()
    with open(wordlist, 'r') as f:
        for line in f:
            q.put(line)

    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# --------------------------------------------------
# S3 Bucket discovery
def s3_scan(bucket_name):
    import boto3
    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        print(f"[S3 OPEN] {bucket_name} -> {response.get('Contents', [])}")
    except:
        pass

# --------------------------------------------------
# TFTP discovery
def tftp_scan(ip, wordlist):
    from tftpy import TftpClient
    for word in open(wordlist, 'r'):
        try:
            client = TftpClient(ip, 69)
            client.download(word.strip(), f"/tmp/{word.strip()}", timeout=2)
            print(f"[TFTP] {ip}/{word.strip()}")
        except:
            pass

# --------------------------------------------------
# Virtual Host
def vhost_scan(url, wordlist, threads):
    def worker():
        while not q.empty():
            host = q.get().strip()
            try:
                r = requests.get(url, headers={"Host": host}, timeout=4)
                if r.status_code == 200:
                    print(f"[VHOST] {host} -> {url}")
            except:
                pass
            q.task_done()
    q = Queue()
    with open(wordlist, 'r') as f:
        for line in f:
            q.put(line)
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# --------------------------------------------------
# MAIN
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Mxmbuster - Multi-mode brute-forcing")
    parser.add_argument("-u", "--url", help="Target URL (http://ejemplo.com)")
    parser.add_argument("-d", "--domain", help="Domain for DNS")
    parser.add_argument("-w", "--wordlist", help="Ruta de wordlist")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Hilos")
    parser.add_argument("-m", "--mode", required=True, choices=["dir", "dns", "vhost", "s3", "gcs", "tftp", "fuzz"], help="Modo de escaneo")
    parser.add_argument("-b", "--bucket", help="Bucket name (S3/GCS)")
    parser.add_argument("--tftp-ip", help="IP de servidor TFTP")
    args = parser.parse_args()

    if args.mode == "dir" and args.url and args.wordlist:
        dir_scan(args.url, args.wordlist, args.threads)
    elif args.mode == "dns" and args.domain and args.wordlist:
        dns_scan(args.domain, args.wordlist, args.threads)
    elif args.mode == "s3" and args.bucket:
        s3_scan(args.bucket)
    elif args.mode == "tftp" and args.tftp_ip and args.wordlist:
        tftp_scan(args.tftp_ip, args.wordlist)
    elif args.mode == "vhost" and args.url and args.wordlist:
        vhost_scan(args.url, args.wordlist, args.threads)
    else:
        print("[!] Faltan parámetros. Usa --help")

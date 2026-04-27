import argparse
import requests
import threading
import sys
import socket
import time
from queue import Queue
from datetime import datetime
import os
import json
from banner import banner, R, G, Y, B, M, C, W, RS

# Variables globales para resultados
found_items = []
output_file = None
wildcard_ip = None

# ============================================================
# Guardar resultados
def save_result(data, category):
    global found_items
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    found_items.append({
        "timestamp": timestamp,
        "category": category,
        "data": data
    })
    print(f"{G}[+] {category}: {data}{RS}")
    
    if output_file:
        with open(output_file, 'a') as f:
            f.write(f"[{timestamp}] {category}: {data}\n")

# ============================================================
# Detectar wildcard en DNS
def has_wildcard(domain):
    global wildcard_ip
    test_sub = f"wildcard-test-{int(time.time())}.{domain}"
    try:
        ip = socket.gethostbyname(test_sub)
        wildcard_ip = ip
        print(f"{Y}[!] Wildcard detectado en: {domain} -> {ip}{RS}")
        return True
    except:
        print(f"{G}[+] Sin wildcard detectado en {domain}{RS}")
        return False

# ============================================================
# DNS con wildcard filtering
def dns_scan(domain, wordlist, threads):
    global wildcard_ip
    print(f"{C}[*] Iniciando DNS enumeration en {domain}{RS}")
    
    if has_wildcard(domain):
        print(f"{Y}[!] Filtrando resultados con wildcard IP: {wildcard_ip}{RS}")
    
    def worker():
        while not q.empty():
            sub = q.get().strip()
            target = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(target)
                if wildcard_ip and ip == wildcard_ip:
                    pass  # Falso positivo por wildcard
                else:
                    save_result(f"{target} → {ip}", "DNS_SUBDOMAIN")
            except:
                pass
            q.task_done()
    
    q = Queue()
    with open(wordlist, 'r') as f:
        lines = f.readlines()
        for line in lines:
            q.put(line)
    
    print(f"{Y}[*] Usando {threads} hilos con wordlist de {len(lines)} palabras{RS}")
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# ============================================================
# Directory busting
def dir_scan(url, wordlist, threads):
    print(f"{C}[*] Iniciando directory busting en {url}{RS}")
    
    def worker():
        while not q.empty():
            word = q.get().strip()
            test_url = url.rstrip('/') + '/' + word
            try:
                r = requests.get(test_url, timeout=3, allow_redirects=False)
                if r.status_code in [200, 201, 301, 302, 403, 401]:
                    size = len(r.content)
                    save_result(f"{test_url} [{r.status_code}] - {size} bytes", "DIRECTORY")
            except:
                pass
            q.task_done()
    
    q = Queue()
    with open(wordlist, 'r') as f:
        lines = f.readlines()
        for line in lines:
            q.put(line)
    
    print(f"{Y}[*] Usando {threads} hilos con wordlist de {len(lines)} palabras{RS}")
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# ============================================================
# Virtual Host
def vhost_scan(url, wordlist, threads):
    print(f"{C}[*] Iniciando virtual host enumeration en {url}{RS}")
    
    def worker():
        while not q.empty():
            host = q.get().strip()
            try:
                r = requests.get(url, headers={"Host": host}, timeout=4)
                if r.status_code == 200:
                    size = len(r.content)
                    save_result(f"{host} → {url} [{size} bytes]", "VIRTUAL_HOST")
            except:
                pass
            q.task_done()
    
    q = Queue()
    with open(wordlist, 'r') as f:
        lines = f.readlines()
        for line in lines:
            q.put(line)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# ============================================================
# S3 Bucket (mejorado)
def s3_scan(bucket_name):
    print(f"{C}[*] Verificando bucket S3: {bucket_name}{RS}")
    try:
        import boto3
        from botocore.exceptions import ClientError
        s3 = boto3.client('s3')
        try:
            response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                save_result(f"{bucket_name} → {len(files)} archivos: {files[:5]}", "S3_BUCKET_OPEN")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"{R}[-] Bucket no existe: {bucket_name}{RS}")
            else:
                print(f"{Y}[!] Bucket existe pero no es público: {bucket_name}{RS}")
    except Exception as e:
        print(f"{R}[-] Error: {e}{RS}")

# ============================================================
# GCS Bucket (soporte real)
def gcs_scan(bucket_name):
    print(f"{C}[*] Verificando bucket GCS: {bucket_name}{RS}")
    try:
        import google.cloud.storage
        from google.cloud.storage import Client
        client = Client.create_anonymous_client()
        bucket = client.bucket(bucket_name)
        try:
            blobs = list(bucket.list_blobs(max_results=10))
            if blobs:
                files = [blob.name for blob in blobs]
                save_result(f"gs://{bucket_name} → {len(blobs)} archivos: {files[:5]}", "GCS_BUCKET_OPEN")
            else:
                print(f"{Y}[!] Bucket existe pero vacío: {bucket_name}{RS}")
        except Exception:
            print(f"{Y}[!] Bucket no público o no existe: {bucket_name}{RS}")
    except ImportError:
        print(f"{R}[-] Instala: pip install google-cloud-storage{RS}")
    except Exception as e:
        print(f"{R}[-] Error GCS: {e}{RS}")

# ============================================================
# TFTP
def tftp_scan(ip, wordlist):
    print(f"{C}[*] Escaneando TFTP en {ip}{RS}")
    from tftpy import TftpClient
    for word in open(wordlist, 'r'):
        word = word.strip()
        try:
            client = TftpClient(ip, 69)
            client.download(word, f"/tmp/mxmbuster_{word}", timeout=2)
            save_result(f"tftp://{ip}/{word}", "TFTP_FILE")
        except:
            pass

# ============================================================
# Fuzzing personalizado
def fuzz_scan(url, wordlist, threads, param=None):
    print(f"{C}[*] Iniciando fuzzing en {url}{RS}")
    
    def worker():
        while not q.empty():
            word = q.get().strip()
            if param:
                test_url = url.replace("FUZZ", word) if "FUZZ" in url else f"{url}?{param}={word}"
            else:
                test_url = url.rstrip('/') + '/' + word
            
            try:
                r = requests.get(test_url, timeout=3)
                if r.status_code in [200, 403, 500]:
                    size = len(r.content)
                    save_result(f"{test_url} [{r.status_code}] - {size}b", "FUZZ")
            except:
                pass
            q.task_done()
    
    q = Queue()
    with open(wordlist, 'r') as f:
        lines = f.readlines()
        for line in lines:
            q.put(line)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    q.join()

# ============================================================
# MAIN
if __name__ == "__main__":
    banner()
    
    parser = argparse.ArgumentParser(description="Mxmbuster - Herramienta multipropósito para pentesting")
    parser.add_argument("-u", "--url", help="URL objetivo (http://ejemplo.com)")
    parser.add_argument("-d", "--domain", help="Dominio para DNS")
    parser.add_argument("-w", "--wordlist", help="Wordlist personalizada")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Número de hilos")
    parser.add_argument("-m", "--mode", required=True, 
                       choices=["dir", "dns", "vhost", "s3", "gcs", "tftp", "fuzz"], 
                       help="Modo de escaneo")
    parser.add_argument("-b", "--bucket", help="Nombre del bucket (S3/GCS)")
    parser.add_argument("--tftp-ip", help="IP del servidor TFTP")
    parser.add_argument("-p", "--param", help="Parámetro para fuzzing (ej: id)")
    parser.add_argument("-o", "--output", help="Archivo de salida para resultados")
    parser.add_argument("--no-save", action="store_true", help="No guardar resultados")
    
    args = parser.parse_args()
    
    # Configurar archivo de salida
    if not args.no_save:
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"mxmbuster_{args.mode}_{timestamp}.txt"
        print(f"{G}[+] Resultados se guardarán en: {output_file}{RS}")
    
    # Ejecutar según modo
    try:
        if args.mode == "dir" and args.url and args.wordlist:
            dir_scan(args.url, args.wordlist, args.threads)
        elif args.mode == "dns" and args.domain and args.wordlist:
            dns_scan(args.domain, args.wordlist, args.threads)
        elif args.mode == "vhost" and args.url and args.wordlist:
            vhost_scan(args.url, args.wordlist, args.threads)
        elif args.mode == "s3" and args.bucket:
            s3_scan(args.bucket)
        elif args.mode == "gcs" and args.bucket:
            gcs_scan(args.bucket)
        elif args.mode == "tftp" and args.tftp_ip and args.wordlist:
            tftp_scan(args.tftp_ip, args.wordlist)
        elif args.mode == "fuzz" and args.url and args.wordlist:
            fuzz_scan(args.url, args.wordlist, args.threads, args.param)
        else:
            print(f"{R}[!] Faltan parámetros. Usa --help para más info{RS}")
            sys.exit(1)
        
        # Resumen final
        print(f"\n{C}════════════════════════════════════════════════════{RS}")
        print(f"{G}[+] Escaneo completado! Encontrados: {len(found_items)} items{RS}")
        if output_file and not args.no_save:
            print(f"{G}[+] Resultados guardados en: {output_file}{RS}")
        print(f"{C}════════════════════════════════════════════════════{RS}")
        
        # Guardar JSON también
        if output_file and not args.no_save:
            json_file = output_file.replace('.txt', '.json')
            with open(json_file, 'w') as f:
                json.dump(found_items, f, indent=2)
            print(f"{G}[+] Backup JSON guardado en: {json_file}{RS}")
            
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Interrupción detectada. Guardando resultados parciales...{RS}")
        if output_file and found_items:
            with open(output_file, 'a') as f:
                f.write(f"\n[INTERRUMPIDO] {datetime.now()}\n")
            print(f"{G}[+] Resultados parciales guardados{RS}")

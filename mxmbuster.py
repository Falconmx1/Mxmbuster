#!/usr/bin/env python3
import argparse
import requests
import threading
import sys
import socket
import time
import subprocess
from queue import Queue
from datetime import datetime
import os
import json
from banner import banner, R, G, Y, B, M, C, W, RS

# Variables globales
found_items = []
output_file = None
wildcard_ip = None

# ============================================================
def save_result(data, category, severity="INFO", metadata=None):
    global found_items
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    colores = {
        "CRITICAL": f"{R}[!]{RS}",
        "HIGH": f"{R}[+]{RS}",
        "MEDIUM": f"{Y}[~]{RS}",
        "INFO": f"{G}[+]{RS}"
    }
    prefix = colores.get(severity, f"{G}[+]{RS}")
    
    item = {
        "timestamp": timestamp,
        "category": category,
        "severity": severity,
        "data": data,
        "metadata": metadata or {}
    }
    found_items.append(item)
    
    print(f"{prefix} {category}: {data}{RS}")
    
    if output_file:
        with open(output_file, 'a') as f:
            f.write(f"[{timestamp}] [{severity}] {category}: {data}\n")

# ============================================================
# 1. CASSANDRA DB ENUMERATION
def cassandra_scan(target, port=9042, wordlist=None):
    print(f"{C}[*] Escaneando Cassandra en {target}:{port}{RS}")
    try:
        from cassandra.cluster import Cluster
        from cassandra.auth import PlainTextAuthProvider
        
        # Sin autenticación
        try:
            cluster = Cluster([target], port=port, connect_timeout=3)
            session = cluster.connect()
            rows = session.execute("SELECT release_version FROM system.local")
            for row in rows:
                save_result(f"cassandra://{target}:{port} - SIN AUTH | Versión: {row.release_version}", 
                          "CASSANDRA_OPEN", "CRITICAL")
                
                # Listar keyspaces
                keyspaces = session.execute("SELECT keyspace_name FROM system_schema.keyspaces")
                ks_list = [k.keyspace_name for k in keyspaces][:5]
                save_result(f"  → Keyspaces: {ks_list}", "CASSANDRA_KEYSPACES", "HIGH")
            cluster.shutdown()
            return True
        except:
            pass
        
        # Con wordlist
        if wordlist and os.path.exists(wordlist):
            print(f"{C}[*] Probando credenciales en Cassandra{RS}")
            with open(wordlist, 'r') as f:
                for line in f:
                    if ':' in line:
                        user, pwd = line.strip().split(':', 1)
                        try:
                            auth = PlainTextAuthProvider(username=user, password=pwd)
                            cluster = Cluster([target], port=port, auth_provider=auth, connect_timeout=3)
                            session = cluster.connect()
                            save_result(f"cassandra://{user}:{pwd}@{target}:{port} - CREDENCIALES VÁLIDAS", 
                                      "CASSANDRA_CREDZ", "CRITICAL")
                            cluster.shutdown()
                            return True
                        except:
                            pass
    except ImportError:
        print(f"{R}[-] pip install cassandra-driver{RS}")
    except Exception as e:
        print(f"{Y}[!] Cassandra error: {e}{RS}")
    return False

# ============================================================
# 2. ELASTICSEARCH DISCOVERY
def elasticsearch_scan(target, port=9200):
    print(f"{C}[*] Escaneando Elasticsearch en {target}:{port}{RS}")
    try:
        # Información del cluster
        r = requests.get(f"http://{target}:{port}/", timeout=3)
        if r.status_code == 200:
            data = r.json()
            save_result(f"elasticsearch://{target}:{port} - {data.get('version', {}).get('number', 'unknown')}", 
                       "ELASTICSEARCH_OPEN", "HIGH")
            
            # Nodes
            nodes = requests.get(f"http://{target}:{port}/_nodes", timeout=3)
            if nodes.status_code == 200:
                node_data = nodes.json()
                node_count = len(node_data.get('nodes', {}))
                save_result(f"  → {node_count} nodos activos", "ELASTICSEARCH_NODES", "MEDIUM")
            
            # Indices
            indices = requests.get(f"http://{target}:{port}/_cat/indices?h=index", timeout=3)
            if indices.status_code == 200:
                idx_list = indices.text.strip().split('\n')[:10]
                if idx_list and idx_list[0]:
                    save_result(f"  → Índices: {idx_list}", "ELASTICSEARCH_INDICES", "HIGH")
            
            # Health check
            health = requests.get(f"http://{target}:{port}/_cluster/health", timeout=3)
            if health.status_code == 200:
                health_data = health.json()
                save_result(f"  → Estado: {health_data.get('status', 'unknown')}", "ELASTICSEARCH_STATUS", "INFO")
            
            return True
        else:
            print(f"{Y}[!] Elasticsearch no disponible{RS}")
    except:
        print(f"{Y}[!] No se pudo conectar a Elasticsearch{RS}")
    return False

# ============================================================
# 3. MEMCACHED SCANNING
def memcached_scan(target, port=11211):
    print(f"{C}[*] Escaneando Memcached en {target}:{port}{RS}")
    try:
        import memcache
        
        # Conectar
        mc = memcache.Client([f"{target}:{port}"], timeout=3)
        mc.set('test_mxmbuster', 'test_value', time=10)
        
        if mc.get('test_mxmbuster') == b'test_value':
            save_result(f"memcached://{target}:{port} - ACCESIBLE", "MEMCACHED_OPEN", "HIGH")
            
            # Stats
            stats = mc.get_stats()
            if stats:
                for server, stat_data in stats:
                    items = stat_data.get('curr_items', '0')
                    uptime = stat_data.get('uptime', '0')
                    save_result(f"  → {items} items | uptime: {uptime}s", "MEMCACHED_STATS", "MEDIUM")
            
            # Slabs
            slabs = mc.get_slabs()
            if slabs:
                save_result(f"  → {len(slabs)} slabs encontrados", "MEMCACHED_SLABS", "MEDIUM")
            
            mc.delete('test_mxmbuster')
            return True
        else:
            print(f"{Y}[!] Memcached no responde{RS}")
    except ImportError:
        print(f"{R}[-] pip install python-memcached{RS}")
    except Exception as e:
        print(f"{Y}[!] Memcached error: {e}{RS}")
    return False

# ============================================================
# 4. POSTGRESQL WEAK AUTH
def postgresql_scan(target, port=5432, wordlist=None):
    print(f"{C}[*] Escaneando PostgreSQL en {target}:{port}{RS}")
    try:
        import psycopg2
        
        # Intentar usuarios comunes
        default_users = ['postgres', 'admin', 'postgresql', 'user', 'test']
        for user in default_users:
            try:
                conn = psycopg2.connect(
                    host=target, port=port, user=user, password=user,
                    connect_timeout=3, database='postgres'
                )
                save_result(f"postgresql://{user}:{user}@{target}:{port} - CREDENCIALES POR DEFECTO", 
                          "POSTGRESQL_DEFAULT", "CRITICAL")
                conn.close()
                return True
            except:
                pass
            
            try:
                conn = psycopg2.connect(
                    host=target, port=port, user=user, password='password',
                    connect_timeout=3, database='postgres'
                )
                save_result(f"postgresql://{user}:password@{target}:{port} - CREDENCIALES DÉBILES", 
                          "POSTGRESQL_WEAK", "HIGH")
                conn.close()
                return True
            except:
                pass
        
        # Wordlist brute force
        if wordlist and os.path.exists(wordlist):
            print(f"{C}[*] Forzando credenciales PostgreSQL{RS}")
            with open(wordlist, 'r') as f:
                for line in f:
                    if ':' in line:
                        user, pwd = line.strip().split(':', 1)
                        try:
                            conn = psycopg2.connect(
                                host=target, port=port, user=user, password=pwd,
                                connect_timeout=2, database='postgres'
                            )
                            save_result(f"postgresql://{user}:{pwd}@{target}:{port} - CREDENCIALES VÁLIDAS", 
                                      "POSTGRESQL_CREDZ", "CRITICAL")
                            conn.close()
                            return True
                        except:
                            pass
    except ImportError:
        print(f"{R}[-] pip install psycopg2-binary{RS}")
    except Exception as e:
        print(f"{Y}[!] PostgreSQL error: {e}{RS}")
    return False

# ============================================================
# 5. MYSQL BRUTE FORCE
def mysql_scan(target, port=3306, wordlist=None):
    print(f"{C}[*] Escaneando MySQL en {target}:{port}{RS}")
    try:
        import mysql.connector
        from mysql.connector import errorcode
        
        # Probar root sin password
        try:
            conn = mysql.connector.connect(
                host=target, port=port, user='root', password='',
                connect_timeout=3
            )
            save_result(f"mysql://root:@ {target}:{port} - SIN CONTRASEÑA", "MYSQL_NO_PASS", "CRITICAL")
            conn.close()
            return True
        except:
            pass
        
        # Credenciales comunes
        common_creds = [
            ('root', 'root'), ('admin', 'admin'), ('root', '123456'),
            ('root', 'password'), ('user', 'user'), ('test', 'test')
        ]
        
        for user, pwd in common_creds:
            try:
                conn = mysql.connector.connect(
                    host=target, port=port, user=user, password=pwd,
                    connect_timeout=3
                )
                save_result(f"mysql://{user}:{pwd}@{target}:{port} - CREDENCIALES COMUNES", 
                          "MYSQL_COMMON", "HIGH")
                conn.close()
                return True
            except:
                pass
        
        # Wordlist brute force
        if wordlist and os.path.exists(wordlist):
            print(f"{C}[*] Forzando credenciales MySQL{RS}")
            with open(wordlist, 'r') as f:
                for line in f:
                    if ':' in line:
                        user, pwd = line.strip().split(':', 1)
                        try:
                            conn = mysql.connector.connect(
                                host=target, port=port, user=user, password=pwd,
                                connect_timeout=2
                            )
                            save_result(f"mysql://{user}:{pwd}@{target}:{port} - CREDENCIALES VÁLIDAS", 
                                      "MYSQL_CREDZ", "CRITICAL")
                            conn.close()
                            return True
                        except:
                            pass
    except ImportError:
        print(f"{R}[-] pip install mysql-connector-python{RS}")
    except Exception as e:
        print(f"{Y}[!] MySQL error: {e}{RS}")
    return False

# ============================================================
# MONGODB (ya existente)
def mongodb_scan(target, port=27017, wordlist=None):
    print(f"{C}[*] Escaneando MongoDB en {target}:{port}{RS}")
    try:
        from pymongo import MongoClient
        
        # Sin auth
        try:
            client = MongoClient(target, port, serverSelectionTimeoutMS=3000)
            client.server_info()
            save_result(f"mongodb://{target}:{port} - SIN AUTENTICACIÓN", "MONGODB_OPEN", "CRITICAL")
            
            dbs = client.list_database_names()
            save_result(f"  → Bases de datos: {dbs}", "MONGODB_DBS", "HIGH")
            client.close()
            return True
        except:
            pass
        
        # Wordlist
        if wordlist and os.path.exists(wordlist):
            with open(wordlist, 'r') as f:
                for line in f:
                    if ':' in line:
                        user, pwd = line.strip().split(':', 1)
                        try:
                            client = MongoClient(f"mongodb://{user}:{pwd}@{target}:{port}/", 
                                               serverSelectionTimeoutMS=3000)
                            client.server_info()
                            save_result(f"mongodb://{user}:{pwd}@{target}:{port} - CREDENCIALES", 
                                      "MONGODB_CREDZ", "CRITICAL")
                            client.close()
                            return True
                        except:
                            pass
    except:
        pass
    return False

# ============================================================
# REDIS (ya existente)
def redis_scan(target, port=6379, wordlist=None):
    print(f"{C}[*] Escaneando Redis en {target}:{port}{RS}")
    try:
        import redis
        
        # Sin auth
        try:
            r = redis.Redis(host=target, port=port, socket_connect_timeout=3, decode_responses=True)
            r.ping()
            save_result(f"redis://{target}:{port} - SIN AUTENTICACIÓN", "REDIS_OPEN", "CRITICAL")
            
            info = r.info()
            save_result(f"  → Versión: {info.get('redis_version', 'unknown')}", "REDIS_INFO", "MEDIUM")
            
            keys = r.keys('*')
            if keys:
                save_result(f"  → {len(keys)} keys encontradas", "REDIS_KEYS", "HIGH")
            r.close()
            return True
        except:
            pass
        
        # Wordlist
        if wordlist and os.path.exists(wordlist):
            with open(wordlist, 'r') as f:
                for password in f:
                    password = password.strip()
                    try:
                        r = redis.Redis(host=target, port=port, password=password, socket_connect_timeout=3)
                        r.ping()
                        save_result(f"redis://:{password}@{target}:{port} - CONTRASEÑA VÁLIDA", 
                                  "REDIS_CREDZ", "CRITICAL")
                        r.close()
                        return True
                    except:
                        pass
    except:
        pass
    return False

# ============================================================
# OTROS MÓDULOS (DNS, DIR, VHOST, S3, GCS, TFTP, FUZZ)
def dns_scan(domain, wordlist, threads):
    global wildcard_ip
    print(f"{C}[*] DNS enumeration: {domain}{RS}")
    
    def has_wildcard(d):
        global wildcard_ip
        test = f"wildcard-{int(time.time())}.{d}"
        try:
            ip = socket.gethostbyname(test)
            wildcard_ip = ip
            print(f"{Y}[!] Wildcard IP: {ip}{RS}")
            return True
        except:
            return False
    
    has_wildcard(domain)
    
    def worker():
        while not q.empty():
            sub = q.get().strip()
            target = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(target)
                if wildcard_ip and ip == wildcard_ip:
                    pass
                else:
                    save_result(f"{target} → {ip}", "DNS_SUBDOMAIN", "MEDIUM")
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

def dir_scan(url, wordlist, threads):
    print(f"{C}[*] Directory busting: {url}{RS}")
    def worker():
        while not q.empty():
            word = q.get().strip()
            test_url = url.rstrip('/') + '/' + word
            try:
                r = requests.get(test_url, timeout=3)
                if r.status_code in [200, 301, 302, 403]:
                    save_result(f"{test_url} [{r.status_code}]", "DIRECTORY", "MEDIUM")
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

def vhost_scan(url, wordlist, threads):
    print(f"{C}[*] Virtual host enumeration: {url}{RS}")
    def worker():
        while not q.empty():
            host = q.get().strip()
            try:
                r = requests.get(url, headers={"Host": host}, timeout=4)
                if r.status_code == 200:
                    save_result(f"{host} → {url}", "VIRTUAL_HOST", "MEDIUM")
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

def s3_scan(bucket):
    try:
        import boto3
        s3 = boto3.client('s3')
        s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        save_result(f"s3://{bucket} - ACCESIBLE", "S3_OPEN", "HIGH")
    except:
        print(f"{Y}[!] S3 no accesible{RS}")

def gcs_scan(bucket):
    try:
        from google.cloud import storage
        client = storage.Client.create_anonymous_client()
        bucket_obj = client.bucket(bucket)
        list(bucket_obj.list_blobs(max_results=1))
        save_result(f"gs://{bucket} - ACCESIBLE", "GCS_OPEN", "HIGH")
    except:
        print(f"{Y}[!] GCS no accesible{RS}")

def tftp_scan(ip, wordlist):
    from tftpy import TftpClient
    with open(wordlist, 'r') as f:
        for word in f:
            word = word.strip()
            try:
                client = TftpClient(ip, 69)
                client.download(word, f"/tmp/{word}", timeout=2)
                save_result(f"tftp://{ip}/{word}", "TFTP_FILE", "MEDIUM")
            except:
                pass

def fuzz_scan(url, wordlist, threads, param=None):
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
                    save_result(f"{test_url} [{r.status_code}]", "FUZZ", "MEDIUM")
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

# ============================================================
# MAIN
if __name__ == "__main__":
    banner()
    
    parser = argparse.ArgumentParser(description="Mxmbuster v4.0 - Herramienta definitiva de pentesting")
    parser.add_argument("-m", "--mode", required=True,
                       choices=["dir", "dns", "vhost", "s3", "gcs", "tftp", "fuzz",
                               "mongodb", "redis", "cassandra", "elasticsearch", 
                               "memcached", "postgresql", "mysql"],
                       help="Modo de escaneo")
    parser.add_argument("-t", "--target", help="IP o dominio objetivo")
    parser.add_argument("-u", "--url", help="URL para web modes")
    parser.add_argument("-d", "--domain", help="Dominio para DNS")
    parser.add_argument("-w", "--wordlist", help="Wordlist personalizada")
    parser.add_argument("--threads", type=int, default=20, help="Hilos (default: 20)")
    parser.add_argument("--port", type=int, help="Puerto personalizado")
    parser.add_argument("-o", "--output", help="Archivo de salida")
    parser.add_argument("--no-save", action="store_true", help="No guardar")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
    
    args = parser.parse_args()
    
    # Modo interactivo
    if args.interactive:
        print(f"{G}[+] Modo interactivo activado{RS}")
        print(f"{Y}[?] Próximamente: python3 interactive.py{RS}")
        print(f"{C}[*] Ejecutando modo normal por ahora...{RS}")
    
    if not args.no_save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = args.output or f"mxmbuster_{args.mode}_{timestamp}.txt"
        print(f"{G}[+] Resultados → {output_file}{RS}")
    
    try:
        # Web modes
        if args.mode == "dir" and args.url and args.wordlist:
            dir_scan(args.url, args.wordlist, args.threads)
        elif args.mode == "dns" and args.domain and args.wordlist:
            dns_scan(args.domain, args.wordlist, args.threads)
        elif args.mode == "vhost" and args.url and args.wordlist:
            vhost_scan(args.url, args.wordlist, args.threads)
        elif args.mode == "fuzz" and args.url and args.wordlist:
            fuzz_scan(args.url, args.wordlist, args.threads, getattr(args, 'param', None))
        
        # Cloud
        elif args.mode == "s3" and args.target:
            s3_scan(args.target)
        elif args.mode == "gcs" and args.target:
            gcs_scan(args.target)
        elif args.mode == "tftp" and args.target and args.wordlist:
            tftp_scan(args.target, args.wordlist)
        
        # Databases
        elif args.mode == "mongodb" and args.target:
            port = args.port or 27017
            mongodb_scan(args.target, port, args.wordlist)
        elif args.mode == "redis" and args.target:
            port = args.port or 6379
            redis_scan(args.target, port, args.wordlist)
        elif args.mode == "cassandra" and args.target:
            port = args.port or 9042
            cassandra_scan(args.target, port, args.wordlist)
        elif args.mode == "elasticsearch" and args.target:
            port = args.port or 9200
            elasticsearch_scan(args.target, port)
        elif args.mode == "memcached" and args.target:
            port = args.port or 11211
            memcached_scan(args.target, port)
        elif args.mode == "postgresql" and args.target:
            port = args.port or 5432
            postgresql_scan(args.target, port, args.wordlist)
        elif args.mode == "mysql" and args.target:
            port = args.port or 3306
            mysql_scan(args.target, port, args.wordlist)
        else:
            print(f"{R}[!] Faltan parámetros para {args.mode}{RS}")
            sys.exit(1)
        
        # Resumen
        print(f"\n{C}{'='*60}{RS}")
        print(f"{G}[+] Escaneo completado! Total hallazgos: {len(found_items)}{RS}")
        
        critical = sum(1 for x in found_items if x['severity'] == 'CRITICAL')
        high = sum(1 for x in found_items if x['severity'] == 'HIGH')
        if critical > 0:
            print(f"{R}[!] CRÍTICOS: {critical}{RS}")
        if high > 0:
            print(f"{R}[+] ALTOS: {high}{RS}")
        
        if output_file and not args.no_save:
            # Guardar JSON
            json_file = output_file.replace('.txt', '.json')
            with open(json_file, 'w') as f:
                json.dump(found_items, f, indent=2)
            print(f"{G}[+] JSON: {json_file}{RS}")
            
            # Intentar generar PDF/HTML
            try:
                from report_generator import generate_report
                report_file = generate_report(found_items, args.mode)
                print(f"{G}[+] Reporte: {report_file}{RS}")
            except:
                print(f"{Y}[!] Report Generator no disponible{RS}")
        
        print(f"{C}{'='*60}{RS}")
        
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Interrupción! Resultados guardados{RS}")

#!/usr/bin/env python3
import os
import sys
import readline
from datetime import datetime
from banner import banner, R, G, Y, B, M, C, W, RS

# Colores para el prompt
def colorful_input(prompt, color=G):
    return input(f"{color}{prompt}{RS}")

def interactive_menu():
    banner()
    
    print(f"{C}{'═'*60}{RS}")
    print(f"{G}🐙 Mxmbuster Modo Interactivo v4.0{RS}")
    print(f"{C}{'═'*60}{RS}")
    
    print(f"""
{Y}┌─────────────────────────────────────────────────────────┐
│  📋 Módulos disponibles:                                  │
├─────────────────────────────────────────────────────────┤
│  {G}1. Web Directory Busting{RS}      │  {M}8.  MongoDB{RS}                    │
│  {G}2. DNS Subdomain Discovery{RS}    │  {M}9.  Redis{RS}                     │
│  {G}3. Virtual Host Detection{RS}     │  {M}10. Cassandra{RS}                 │
│  {G}4. S3 Buckets{RS}                 │  {M}11. Elasticsearch{RS}             │
│  {G}5. GCS Buckets{RS}                │  {M}12. Memcached{RS}                 │
│  {G}6. TFTP Discovery{RS}             │  {M}13. PostgreSQL{RS}                │
│  {G}7. Fuzzing{RS}                    │  {M}14. MySQL{RS}                     │
│                                      {R}0. Exit{RS}                         │
└─────────────────────────────────────────────────────────┘
    """)
    
    while True:
        choice = colorful_input(f"{C}[Mxmbuster]{Y} Selecciona módulo (0-14): {RS}", Y)
        
        if choice == "0":
            print(f"{G}[+] Hasta luego, compa... Nos vemos en la siguiente intrusión 👊{RS}")
            sys.exit(0)
        
        # Módulo 1: Directory
        elif choice == "1":
            url = colorful_input(f"{C}[?] URL objetivo (ej: http://ejemplo.com): {RS}")
            wordlist = colorful_input(f"{C}[?] Wordlist path (default: wordlists/common.txt): {RS}") or "wordlists/common.txt"
            threads = colorful_input(f"{C}[?] Hilos (default 20): {RS}") or "20"
            
            cmd = f"python3 mxmbuster.py -m dir -u {url} -w {wordlist} -t {threads} -o interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 2: DNS
        elif choice == "2":
            domain = colorful_input(f"{C}[?] Dominio objetivo (ej: ejemplo.com): {RS}")
            wordlist = colorful_input(f"{C}[?] Wordlist DNS (default: wordlists/dns.txt): {RS}") or "wordlists/dns.txt"
            threads = colorful_input(f"{C}[?] Hilos (default 20): {RS}") or "20"
            
            cmd = f"python3 mxmbuster.py -m dns -d {domain} -w {wordlist} -t {threads} -o dns_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 8: MongoDB
        elif choice == "8":
            target = colorful_input(f"{C}[?] IP/Dominio MongoDB: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 27017): {RS}") or "27017"
            wordlist = colorful_input(f"{C}[?] Wordlist credenciales (opcional): {RS}")
            
            cmd = f"python3 mxmbuster.py -m mongodb --target {target} --port {port}"
            if wordlist:
                cmd += f" -w {wordlist}"
            cmd += f" -o mongodb_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 9: Redis
        elif choice == "9":
            target = colorful_input(f"{C}[?] IP/Dominio Redis: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 6379): {RS}") or "6379"
            wordlist = colorful_input(f"{C}[?] Wordlist contraseñas (opcional): {RS}")
            
            cmd = f"python3 mxmbuster.py -m redis --target {target} --port {port}"
            if wordlist:
                cmd += f" -w {wordlist}"
            cmd += f" -o redis_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 10: Cassandra
        elif choice == "10":
            target = colorful_input(f"{C}[?] IP/Dominio Cassandra: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 9042): {RS}") or "9042"
            wordlist = colorful_input(f"{C}[?] Wordlist credenciales (opcional): {RS}")
            
            cmd = f"python3 mxmbuster.py -m cassandra --target {target} --port {port}"
            if wordlist:
                cmd += f" -w {wordlist}"
            cmd += f" -o cassandra_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 11: Elasticsearch
        elif choice == "11":
            target = colorful_input(f"{C}[?] IP/Dominio Elasticsearch: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 9200): {RS}") or "9200"
            
            cmd = f"python3 mxmbuster.py -m elasticsearch --target {target} --port {port} -o elastic_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 12: Memcached
        elif choice == "12":
            target = colorful_input(f"{C}[?] IP/Dominio Memcached: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 11211): {RS}") or "11211"
            
            cmd = f"python3 mxmbuster.py -m memcached --target {target} --port {port} -o memcached_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 13: PostgreSQL
        elif choice == "13":
            target = colorful_input(f"{C}[?] IP/Dominio PostgreSQL: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 5432): {RS}") or "5432"
            wordlist = colorful_input(f"{C}[?] Wordlist credenciales (opcional): {RS}")
            
            cmd = f"python3 mxmbuster.py -m postgresql --target {target} --port {port}"
            if wordlist:
                cmd += f" -w {wordlist}"
            cmd += f" -o postgres_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        # Módulo 14: MySQL
        elif choice == "14":
            target = colorful_input(f"{C}[?] IP/Dominio MySQL: {RS}")
            port = colorful_input(f"{C}[?] Puerto (default 3306): {RS}") or "3306"
            wordlist = colorful_input(f"{C}[?] Wordlist credenciales (opcional): {RS}")
            
            cmd = f"python3 mxmbuster.py -m mysql --target {target} --port {port}"
            if wordlist:
                cmd += f" -w {wordlist}"
            cmd += f" -o mysql_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            print(f"{G}[+] Ejecutando: {cmd}{RS}")
            os.system(cmd)
            input(f"{Y}[!] Presiona Enter para continuar...{RS}")
        
        else:
            print(f"{R}[!] Opción inválida{RS}")

if __name__ == "__main__":
    interactive_menu()

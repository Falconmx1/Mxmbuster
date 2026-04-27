# 🦍 Mxmbuster v3.0

[![Version](https://img.shields.io/badge/version-3.0.0-red)](https://github.com/Falconmx1/Mxmbuster)

> **"De la calle a la nube, encontrando todo lo que esconden"**

## 🔥 Nuevos modos en v3.0

- 🍃 **MongoDB Discovery** - Bases de datos abiertas + credenciales débiles
- 📀 **Redis Enumeration** - Servidores Redis expuestos + comandos peligrosos

## 🎯 Ejemplos MongoDB & Redis

```bash
# MongoDB sin autenticación
python3 mxmbuster.py -m mongodb --target 192.168.1.100

# MongoDB con fuerza bruta
python3 mxmbuster.py -m mongodb --target 10.0.0.5 -w wordlists/mongodb.txt

# Redis enumeration
python3 mxmbuster.py -m redis --target 192.168.1.200

# Redis con wordlist
python3 mxmbuster.py -m redis --target 10.0.0.10 -w wordlists/redis.txt

# Puertos personalizados
python3 mxmbuster.py -m mongodb --target ejemplo.com --mongodb-port 27018
python3 mxmbuster.py -m redis --target ejemplo.com --redis-port 6380

🚀 EJEMPLOS DE USO FINAL

# Escaneo completo de todo
python3 mxmbuster.py -m mongodb --target 10.0.0.1 -w wordlists/mongodb.txt
python3 mxmbuster.py -m cassandra --target db.ejemplo.com --port 9042
python3 mxmbuster.py -m elasticsearch --target logs.ejemplo.com
python3 mxmbuster.py -m memcached --target cache.ejemplo.com
python3 mxmbuster.py -m postgresql --target postgres.ejemplo.com -w wordlists/postgres.txt
python3 mxmbuster.py -m mysql --target mysql.ejemplo.com -w wordlists/mysql.txt

# Modo interactivo
python3 interactive.py

# Generar reporte (automático al final)
python3 mxmbuster.py -m redis --target 192.168.1.100 -o resultados.txt
# Genera: resultados.txt, resultados.json, report_redis_20240101_120000.html

# Escaneo con todos los módulos de bases de datos
for db in mongodb redis cassandra elasticsearch memcached postgresql mysql; do
    python3 mxmbuster.py -m $db --target objetivo.com
done

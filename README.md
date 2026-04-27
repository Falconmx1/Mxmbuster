# 🦍 Mxmbuster v3.0

[![Version](https://img.shields.io/badge/version-3.0.0-red)](https://github.com/tuusuario/Mxmbuster)

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

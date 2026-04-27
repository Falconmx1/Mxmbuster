# 🦍 Mxmbuster

[![Version](https://img.shields.io/badge/version-1.0.0-red)](https://github.com/Falconmx1/Mxmbuster)

> **"Rompiendo muros, encontrando caminos"**  
Herramienta ofensiva para pentesting y bug bounty.

![meme](https://media.tenor.com/3bTxoK7OyPkAAAAC/mexico.gif)

## 🔥 Características

- 🌐 Web Directory/File Busting
- 🧠 DNS Subdomain Discovery (wildcard support)
- 🏢 Virtual Host Detection
- ☁️ S3 + GCS open buckets
- 📁 TFTP enumeration
- 🧬 Fuzzing personalizable
- ⚡ Multi-threading con control de concurrencia
- 🐳 Docker ready

## 🚀 Instalación

```bash
git clone https://github.com/Falconmx1/Mxmbuster
cd Mxmbuster
pip install -r requirements.txt

📦 Usar con Docker
docker build -t mxmbuster .
docker run --rm mxmbuster --help

🎯 Ejemplos de uso
# DNS con detección de wildcard + guardado automático
python3 mxmbuster.py -d ejemplo.com -w wordlists/dns.txt -m dns -t 50

# Guardar resultados en archivo específico
python3 mxmbuster.py -u https://ejemplo.com -w wordlists/common.txt -m dir -o results.txt

# GCS bucket enumeration
python3 mxmbuster.py -b mi-bucket -m gcs

# Fuzzing con parámetro personalizado
python3 mxmbuster.py -u https://ejemplo.com/page?FUZZ=1 -w wordlists/common.txt -m fuzz

# S3 bucket check
python3 mxmbuster.py -b vulnerable-bucket -m s3

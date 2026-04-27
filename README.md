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

🎯 Ejemplos
# Directorios
python3 mxmbuster.py -u https://ejemplo.com -w wordlists/common.txt -t 50 -m dir

# Subdominios
python3 mxmbuster.py -d ejemplo.com -w wordlists/dns.txt -m dns

# Virtual Host
python3 mxmbuster.py -u https://ejemplo.com -w wordlists/vhost.txt -m vhost

🔧 Modos disponibles

dir, dns, vhost, s3, gcs, tftp, fuzz

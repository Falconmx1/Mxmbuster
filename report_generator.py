#!/usr/bin/env python3
import json
from datetime import datetime
import os

def generate_report(found_items, mode):
    """Genera reporte en HTML y PDF (si está disponible)"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"report_{mode}_{timestamp}.html"
    
    # Generar HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Mxmbuster Report - {mode}</title>
        <style>
            body {{
                font-family: 'Courier New', monospace;
                background: #0a0e27;
                color: #00ff41;
                margin: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: #0f1235;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #00ff41;
            }}
            h1 {{
                color: #ff3366;
                text-align: center;
                border-bottom: 2px solid #ff3366;
                padding-bottom: 10px;
            }}
            .critical {{
                background: #ff0000;
                color: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }}
            .high {{
                background: #ff6600;
                color: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }}
            .medium {{
                background: #ffcc00;
                color: black;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }}
            .info {{
                background: #0066cc;
                color: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }}
            .stats {{
                background: #1a1f4e;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                border-left: 4px solid #00ff41;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #00ff41;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #ff3366;
                color: white;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Mxmbuster Security Report</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Mode:</strong> {mode}</p>
            <p><strong>Total Findings:</strong> {len(found_items)}</p>
            
            <div class="stats">
                <h3>📊 Statistics</h3>
    """
    
    # Estadísticas por severidad
    critical = sum(1 for x in found_items if x['severity'] == 'CRITICAL')
    high = sum(1 for x in found_items if x['severity'] == 'HIGH')
    medium = sum(1 for x in found_items if x['severity'] == 'MEDIUM')
    info = sum(1 for x in found_items if x['severity'] == 'INFO')
    
    html_content += f"""
                <p>🔴 Critical: {critical}</p>
                <p>🟠 High: {high}</p>
                <p>🟡 Medium: {medium}</p>
                <p>🔵 Info: {info}</p>
            </div>
            
            <h2>📋 Detailed Findings</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Severity</th>
                    <th>Category</th>
                    <th>Data</th>
                </tr>
    """
    
    for item in found_items:
        severity_class = item['severity'].lower()
        html_content += f"""
                <tr>
                    <td>{item['timestamp']}</td>
                    <td class="{severity_class}">{item['severity']}</td>
                    <td>{item['category']}</td>
                    <td>{item['data']}</td>
                </tr>
        """
    
    html_content += f"""
            </table>
            
            <div class="footer">
                <p>🚀 Mxmbuster v4.0 - Hecho con sangre, sudor y frijolitos 🇲🇽</p>
                <p>⚠️ Este reporte es para fines de pruebas de seguridad autorizadas</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Guardar HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"{G}[+] Reporte HTML generado: {html_file}{RS}")
    
    # Intentar generar PDF (requiere wkhtmltopdf o weasyprint)
    try:
        import weasyprint
        pdf_file = html_file.replace('.html', '.pdf')
        weasyprint.HTML(string=html_content).write_pdf(pdf_file)
        print(f"{G}[+] Reporte PDF generado: {pdf_file}{RS}")
        return pdf_file
    except ImportError:
        print(f"{Y}[!] Instala weasyprint para PDF: pip install weasyprint{RS}")
    except Exception as e:
        print(f"{Y}[!] No se pudo generar PDF: {e}{RS}")
    
    return html_file

if __name__ == "__main__":
    # Test
    test_data = [
        {"timestamp": "2024-01-01 12:00:00", "severity": "CRITICAL", "category": "MONGODB_OPEN", "data": "mongodb://localhost:27017"},
        {"timestamp": "2024-01-01 12:00:01", "severity": "HIGH", "category": "REDIS_OPEN", "data": "redis://localhost:6379"}
    ]
    generate_report(test_data, "test")

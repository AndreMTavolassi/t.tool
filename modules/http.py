import urllib.request
import urllib.error
import ssl

def check_http_status(target_ip, ports):
    """
    Verifica rapidamente a resposta HTTP/HTTPS das portas abertas.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    results = {}
    for port in ports:
        protocol = "https" if port in [443, 8443] else "http"
        url = f"{protocol}://{target_ip}:{port}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 't.tool-scanner/1.0'})
            with urllib.request.urlopen(req, timeout=3, context=ctx) as response:
                results[port] = {
                    "url": url,
                    "status_code": response.getcode(),
                    "server": response.headers.get('Server', 'Unknown')
                }
                print(f"[+] Serviço HTTP ativo na porta {port}: {response.getcode()} ({response.headers.get('Server', 'Unknown')})")
        except urllib.error.HTTPError as e:
            results[port] = {"url": url, "status_code": e.code, "server": e.headers.get('Server', 'Unknown')}
            print(f"[!] Resposta HTTP na porta {port}: Código {e.code}")
        except Exception:
            pass
            
    return results
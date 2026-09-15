import urllib.request
import urllib.error
import ssl

def check_http_status(target, http_ports):
    """
    Verifica o status HTTP/HTTPS das portas identificadas.
    """
    # Desabilita verificação de certificado SSL para alvos com certificados autoassinados
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for port in http_ports:
        protocol = "https" if port in [443, 8443] else "http"
        url = f"{protocol}://{target}:{port}"
        
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (t.tool-recon)'}
            )
            with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                server = response.headers.get('Server', 'Desconhecido')
                print(f"[+] Serviço HTTP ativo na porta {port}: {response.status} (Server: {server})")
        except urllib.error.HTTPError as e:
            server = e.headers.get('Server', 'Desconhecido')
            print(f"[+] Serviço HTTP ativo na porta {port}: {e.code} (Server: {server})")
        except urllib.error.URLError as e:
            print(f"[-] Falha ao conectar em {url}: {e.reason}")
        except Exception as e:
            print(f"[-] Erro inesperado ao verificar {url}: {e}")
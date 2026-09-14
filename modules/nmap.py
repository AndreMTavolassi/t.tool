import subprocess

def run_nmap(target, ports, args, output_xml_path):
    """
    Executa o Nmap no sistema e salva o resultado em formato XML.
    """
    cmd = ["nmap", "-p", str(ports)] + args.split() + ["-oX", output_xml_path, target]
    print(f"[+] Executando Nmap: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Varredura Nmap concluída com sucesso.")
        return output_xml_path
    except FileNotFoundError:
        print("[-] Erro: 'nmap' não encontrado. Instale com: sudo apt install nmap")
        return None
    except subprocess.CalledProcessError as e:
        print(f"[-] Erro ao executar Nmap: {e}")
        return None
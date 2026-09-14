#!/usr/bin/env python3
import os
import sys
import argparse

# 1. COLOQUE O BANNER AQUI (logo abaixo dos imports)
BANNER = r"""
  ████████╗   ████████╗ ██████╗  ██████╗ ██╗     
  ╚══██╔══╝   ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
     ██║  █████╗ ██║   ██║   ██║██║   ██║██║     
     ██║  ╚════╝ ██║   ██║   ██║██║   ██║██║     
     ██║         ██║   ╚██████╔╝╚██████╔╝███████╗
     ╚═╝         ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""

def print_banner():
    # Cor Ciano no terminal Linux
    CYAN = "\033[1;36m"
    RESET = "\033[0m"
    print(f"{CYAN}{BANNER}{RESET}")

def main():
    # 2. CHAME A FUNÇÃO LOGO NO INÍCIO DA FUNÇÃO MAIN
    print_banner()
    
    # Restante da sua lógica do código aqui...
    print("[*] Iniciando t.tool...")

if __name__ == "__main__":
    main()

try:
    import yaml
except ImportError:
    yaml = None

from modules.nmap import run_nmap
from modules.gobuster import run_gobuster
from modules.http import check_http_status
from parsers.nmap_xml import parse_nmap_xml

def load_config(config_path="config/config.yaml"):
    if not os.path.exists(config_path):
        print(f"[-] Configuração não encontrada em {config_path}. Usando padrões.")
        return {}
    
    if yaml is not None:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {
            "target": "127.0.0.1",
            "output_dir": "output",
            "wordlists": {"web": "config/wordlists/common.txt"},
            "nmap": {"ports": "21,22,80,443,8080", "arguments": "-sV -sC -T4"},
            "gobuster": {"threads": 10}
        }

def main():
    parser = argparse.ArgumentParser(description="t.tool - Automação de Reconhecimento e Fuzzing")
    parser.add_argument("-t", "--target", help="IP ou Host Alvo", default=None)
    parser.add_argument("-p", "--ports", help="Portas a escanear", default=None)
    args = parser.parse_args()

    config = load_config()

    # Define o alvo:
    # 1º Tenta pegar da linha de comando (-t / --target)
    # 2º Se não foi passado, solicita ao usuário via prompt
    target = args.target
    if not target:
        target = input("Digite o IP ou Host alvo: ").strip()

    # Validação simples para evitar execução vazia caso o usuário apenas dê Enter
    while not target:
        print("[-] O campo de alvo não pode ficar vazio.")
        target = input("Digite o IP ou Host alvo: ").strip()

    ports = args.ports if args.ports else config.get("nmap", {}).get("ports", "80,443")
    nmap_args = config.get("nmap", {}).get("arguments", "-sV")
    output_dir = config.get("output_dir", "output")
    wordlist = config.get("wordlists", {}).get("web", "config/wordlists/common.txt")
    threads = config.get("gobuster", {}).get("threads", 10)

    os.makedirs(output_dir, exist_ok=True)
    xml_output = os.path.join(output_dir, f"nmap_{target.replace('.', '_')}.xml")

    print(f"\n=== [ t.tool :: Iniciando Reconhecimento em {target} ] ===")

    # 1. Executar Nmap
    run_nmap(target, ports, nmap_args, xml_output)

    # 2. Parse do XML do Nmap
    if os.path.exists(xml_output):
        nmap_data = parse_nmap_xml(xml_output)
        print(f"[+] Portas abertas encontradas: {[p['port'] for p in nmap_data['open_ports']]}")
        
        # 3. Teste HTTP nas portas identificadas
        if nmap_data["http_ports"]:
            print(f"[+] Verificando serviços HTTP nas portas: {nmap_data['http_ports']}")
            check_http_status(target, nmap_data["http_ports"])

            # 4. Fuzzing Web com Gobuster
            for http_port in nmap_data["http_ports"]:
                proto = "https" if http_port in [443, 8443] else "http"
                target_url = f"{proto}://{target}:{http_port}"
                print(f"\n--- Iniciando Fuzzing Web em {target_url} ---")
                
                if os.path.exists(wordlist):
                    gobuster_output = run_gobuster(target_url, wordlist, threads)
                    print(gobuster_output)
                else:
                    print(f"[-] Wordlist não encontrada em: {wordlist}")
        else:
            print("[-] Nenhuma porta HTTP/Web detectada.")

    print("=== [ Reconhecimento Concluído ] ===")

if __name__ == "__main__":
    main()
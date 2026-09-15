#!/usr/bin/env python3
import os
import sys
import argparse

BANNER = r"""
  ████████╗   ████████╗ ██████╗  ██████╗ ██╗     
  ╚══██╔══╝   ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
     ██║  █████╗ ██║   ██║   ██║██║   ██║██║     
     ██║  ╚════╝ ██║   ██║   ██║██║   ██║██║     
     ██║         ██║   ╚██████╔╝╚██████╔╝███████╗
     ╚═╝         ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""

try:
    import yaml
except ImportError:
    yaml = None

from modules.nmap import run_nmap
from modules.gobuster import run_gobuster
from modules.http import check_http_status
from parsers.nmap_xml import parse_nmap_xml

def print_banner():
    # Cores ANSI para o terminal Linux
    CYAN = "\033[1;36m"
    WHITE_BOLD = "\033[1;37m"
    RESET = "\033[0m"
    
    # Exibe a arte ASCII em ciano
    print(f"{CYAN}{BANNER}{RESET}")
    # Exibe a descrição em branco negrito logo abaixo
    print(f"{WHITE_BOLD} Automatic Port Scan & Fuzzing | Input the target IP{RESET}\n")

def load_config(config_path=None):
    # Obtém o caminho absoluto da pasta raiz do projeto para evitar erros de caminho relativo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if config_path is None:
        config_path = os.path.join(base_dir, "config", "config.yaml")
        
    default_wordlist = os.path.join(base_dir, "config", "wordlists", "common.txt")
    default_output = os.path.join(base_dir, "output")

    if not os.path.exists(config_path):
        print(f"[-] Configuração não encontrada em {config_path}. Usando padrões absolutos.")
        return {
            "target": "127.0.0.1",
            "output_dir": default_output,
            "wordlists": {"web": default_wordlist},
            "nmap": {"ports": "21,22,80,443,8080", "arguments": "-sV -sC -T4"},
            "gobuster": {"threads": 10}
        }
    
    if yaml is not None:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
            
            # Converte wordlist para caminho absoluto dinâmico
            w_path = cfg.get("wordlists", {}).get("web", "config/wordlists/common.txt")
            if not os.path.isabs(w_path):
                w_path = os.path.join(base_dir, w_path)
            
            if "wordlists" not in cfg:
                cfg["wordlists"] = {}
            cfg["wordlists"]["web"] = w_path

            # Converte diretório de saída para caminho absoluto
            out_p = cfg.get("output_dir", "output")
            if not os.path.isabs(out_p):
                out_p = os.path.join(base_dir, out_p)
            cfg["output_dir"] = out_p

            return cfg
    
    return {
        "target": "127.0.0.1",
        "output_dir": default_output,
        "wordlists": {"web": default_wordlist},
        "nmap": {"ports": "21,22,80,443,8080", "arguments": "-sV -sC -T4"},
        "gobuster": {"threads": 10}
    }

def main():
    # 1. Exibe o banner ASCII e descrição
    print_banner()

    parser = argparse.ArgumentParser(description="t.tool - Automação de Reconhecimento e Fuzzing")
    parser.add_argument("-t", "--target", help="IP ou Host Alvo", default=None)
    parser.add_argument("-p", "--ports", help="Portas a escanear", default=None)
    args = parser.parse_args()

    config = load_config()

    # 2. Define o alvo via CLI ou prompt interativo
    target = args.target
    if not target:
        target = input("Digite o IP ou Host alvo: ").strip()

    while not target:
        print("[-] O campo de alvo não pode ficar vazio.")
        target = input("Digite o IP ou Host alvo: ").strip()

    ports = args.ports if args.ports else config.get("nmap", {}).get("ports", "80,443")
    nmap_args = config.get("nmap", {}).get("arguments", "-sV")
    output_dir = config.get("output_dir")
    wordlist = config.get("wordlists", {}).get("web")
    threads = config.get("gobuster", {}).get("threads", 10)

    os.makedirs(output_dir, exist_ok=True)
    xml_output = os.path.join(output_dir, f"nmap_{target.replace('.', '_')}.xml")

    print(f"\n=== [ t.tool :: Iniciando Reconhecimento em {target} ] ===")

    # 3. Executar Nmap
    run_nmap(target, ports, nmap_args, xml_output)

    # 4. Parse do XML do Nmap
    if os.path.exists(xml_output):
        nmap_data = parse_nmap_xml(xml_output)
        print(f"[+] Portas abertas encontradas: {[p['port'] for p in nmap_data['open_ports']]}")
        
        # 5. Teste HTTP nas portas identificadas
        if nmap_data["http_ports"]:
            print(f"[+] Verificando serviços HTTP nas portas: {nmap_data['http_ports']}")
            check_http_status(target, nmap_data["http_ports"])

            # 6. Fuzzing Web com Gobuster
            for http_port in nmap_data["http_ports"]:
                proto = "https" if http_port in [443, 8443] else "http"
                target_url = f"{proto}://{target}:{http_port}"
                print(f"\n--- Iniciando Fuzzing Web em {target_url} ---")
                
                if os.path.exists(wordlist):
                    gobuster_output = run_gobuster(target_url, wordlist, threads)
                    print(gobuster_output)
                else:
                    print(f"[-] Wordlist não encontrada no caminho: {wordlist}")
        else:
            print("[-] Nenhuma porta HTTP/Web detectada.")

    print("\n=== [ Reconhecimento Concluído ] ===")

if __name__ == "__main__":
    main()
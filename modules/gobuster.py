import subprocess

def run_gobuster(target_url, wordlist, threads=10):
    """
    Executa o Gobuster para fuzzing / brute-force de diretórios web.
    """
    cmd = [
        "gobuster", "dir",
        "-u", target_url,
        "-w", wordlist,
        "-t", str(threads),
        "-q"
    ]
    print(f"[+] Executando Gobuster: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Fuzzing com Gobuster concluído.")
        return result.stdout
    except FileNotFoundError:
        print("[-] Erro: 'gobuster' não encontrado. Instale com: sudo apt install gobuster")
        return ""
    except subprocess.CalledProcessError as e:
        print(f"[-] Erro na execução do Gobuster: {e}")
        return e.output
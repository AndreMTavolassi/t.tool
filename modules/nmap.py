import subprocess
import shlex

def run_nmap(target, ports, arguments, output_file):
    """
    Executa o Nmap contra o alvo especificado salvando o resultado em XML.
    """
    # Converte a string de argumentos em uma lista para o subprocess
    extra_args = shlex.split(arguments)
    
    cmd = ["nmap", "-p", str(ports)] + extra_args + ["-oX", output_file, target]
    
    print(f"[+] Executando Nmap: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Varredura Nmap concluída com sucesso.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[-] Erro ao executar o Nmap: {e}")
        if e.stderr:
            print(f"[-] Detalhes: {e.stderr}")
        return None
import xml.etree.ElementTree as ET

def parse_nmap_xml(xml_file):
    """
    Analisa o XML gerado pelo Nmap para extrair portas abertas e serviços Web.
    """
    parsed_result = {
        "ip": None,
        "open_ports": [],
        "http_ports": []
    }

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for host in root.findall('host'):
            addr = host.find('address')
            if addr is not None:
                parsed_result["ip"] = addr.get('addr')

            ports = host.find('ports')
            if ports is not None:
                for port in ports.findall('port'):
                    state = port.find('state')
                    if state is not None and state.get('state') == 'open':
                        port_id = int(port.get('portid'))
                        service = port.find('service')
                        service_name = service.get('name') if service is not None else ''

                        parsed_result["open_ports"].append({
                            "port": port_id,
                            "service": service_name,
                            "protocol": port.get('protocol')
                        })

                        if 'http' in service_name.lower() or port_id in [80, 443, 8080, 8443]:
                            parsed_result["http_ports"].append(port_id)

    except Exception as e:
        print(f"[-] Erro ao realizar o parse do XML ({xml_file}): {e}")

    return parsed_result
from DNS import cabecalhoDNS, perguntaDNS, registroDNS
from io import BytesIO
import socket, select
import struct
import random


def cria_requisicao(dominio):
    id = random.randint(0, 65535)
    cabecalho = cabecalhoDNS(id=id)
    pergunta = perguntaDNS(nome=codifica_nome(dominio))
    return cabecalho.to_bytes() + pergunta.to_bytes()


def envia_requisicao(requisicao, servidorDNS):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(requisicao, (servidorDNS, 53))

    try:
        # Monitora o socket verificando se ele esta pronto para realizar a leitura,
        # ou seja, ter dados disponiveis para serem lidos, com timeout de 2 segundos.
        ready = select.select([sock], [], [], 2)

        if ready[0]:
            resposta, _ = sock.recvfrom(1024)
            print("Resposta recebida:", resposta)
            return resposta
        else:
            print("Timeout. Tentando novamente...")
            return envia_requisicao(requisicao, servidorDNS)

    except socket.timeout:
        print("Timeout. Tentando novamente...")
        return envia_requisicao(requisicao, servidorDNS)

    finally:
        sock.close()


def codifica_nome(nome):
    nome_bytes = b""
    for part in nome.encode("ascii").split(b"."):
        nome_bytes += bytes([len(part)]) + part
    return nome_bytes + b"\x00"


def decodifica_nome(reader):
    parts = []
    while (length := reader.read(1)[0]) != 0:
        if length & 0b1100_0000:
            parts.append(decodifica_nome_comp(length, reader))
            break
        else:
            parts.append(reader.read(length))
    return b".".join(parts)


def decodifica_nome_comp(length, reader):
    pointer_bytes = bytes([length & 0b0011_1111]) + reader.read(1)
    pointer = struct.unpack("!H", pointer_bytes)[0]
    current_pos = reader.tell()
    reader.seek(pointer)
    result = decodifica_nome(reader)
    reader.seek(current_pos)
    return result


def interpreta_cabecalho(reader):
    items = struct.unpack("!HHHHHH", reader.read(12))
    return cabecalhoDNS(*items)


def interpreta_pergunta(reader):
    nome = decodifica_nome(reader)
    return perguntaDNS(nome)


def interpreta_resposta(resposta):
    reader = BytesIO(resposta)
    cabecalho = interpreta_cabecalho(reader)
    pergunta = interpreta_pergunta(reader)
    print(f"{cabecalho}\n{pergunta}")
    # interpretar registro NS


# req = cria_requisicao("unb.br")
# resposta = envia_requisicao(req, "8.8.8.8")

# exemplo de resposta
resposta = b"\xe7\x81\x81\x80\x00\x01\x00\x03\x00\x00\x00\x00\x03unb\x02br\x00\x00\x02\x00\x01\xc0\x0c\x00\x02\x00\x01\x00\x00\x01\xda\x00\x07\x04dns3\xc0\x0c\xc0\x0c\x00\x02\x00\x01\x00\x00\x01\xda\x00\x07\x04dns1\xc0\x0c\xc0\x0c\x00\x02\x00\x01\x00\x00\x01\xda\x00\x07\x04dns2\xc0\x0c"
interpreta_resposta(resposta)

from DNS import CabecalhoDNS, PerguntaDNS
from sys import argv
import socket, select
import struct
import random


def cria_requisicao(dominio):
    id = random.randint(0, 65535)
    cabecalho = CabecalhoDNS(id=id)
    pergunta = PerguntaDNS(nome=codifica_nome(dominio))
    return cabecalho.to_bytes() + pergunta.to_bytes()


def envia_requisicao(requisicao, servidorDNS, tentativa):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(requisicao, (servidorDNS, 53))

    if tentativa == 3:
        print(f"Nao foi possível coletar entrada NS para {argv[1]}")
        sock.close()
        exit()

    try:
        # Monitora o socket verificando se ele esta pronto para realizar a leitura,
        # ou seja, ter dados disponiveis para serem lidos, com timeout de 2 segundos.
        ready = select.select([sock], [], [], 2)

        if ready[0]:
            resposta, _ = sock.recvfrom(1024)
            return resposta
        else:
            tentativa += 1
            return envia_requisicao(requisicao, servidorDNS, tentativa)

    except socket.timeout:
        tentativa += 1
        return envia_requisicao(requisicao, servidorDNS, tentativa)

    finally:
        sock.close()


def codifica_nome(nome):
    nome_bytes = b""
    for part in nome.encode("ascii").split(b"."):
        nome_bytes += bytes([len(part)]) + part
    return nome_bytes + b"\x00"


def decodifica_nome(resposta, offset):
    nome = ""
    while True:
        tamanho = resposta[offset]
        if tamanho == 0:
            offset += 1
            break
        if tamanho >= 192:  # caso tenha compressao
            pointer = struct.unpack("!H", resposta[offset : offset + 2])[0] & 0x3FFF
            nome_parte, _ = decodifica_nome(resposta, pointer)
            nome += nome_parte
            offset += 2
            break
        else:
            nome += resposta[offset + 1 : offset + 1 + tamanho].decode("utf-8") + "."
            offset += tamanho + 1
    return nome, offset


def interpreta_resposta(resposta):
    cabecalho = struct.unpack("!6H", resposta[:12])
    flags = cabecalho[1]
    qtd_perguntas = cabecalho[2]
    qtd_respostas = cabecalho[3]
    rcode = flags & 0xF

    # Response Code 3: Name error (domain name referenced in the query does not exist)
    if rcode == 3:
        print(f"Dominio {argv[1]} nao encontrado")
        exit()

    # Pula as perguntas
    offset = 12
    for _ in range(qtd_perguntas):
        while resposta[offset] != 0:
            offset += 1
        offset += 5

    # Interpreta as respostas
    ns_list = []
    for _ in range(qtd_respostas):
        _, offset = decodifica_nome(resposta, offset)
        rr_tipo, _, _, rd_tamanho = struct.unpack(
            "!2HIH", resposta[offset : offset + 10]
        )
        offset += 10
        if rr_tipo == 2:  # NS
            ns_nome, offset = decodifica_nome(resposta, offset)
            ns_list.append(ns_nome)
        else:
            offset += rd_tamanho
    return ns_list


if len(argv) < 3:
    print("Exemplo de uso: python main.py unb.br 8.8.8.8")
    exit()

dominio = argv[1]
servidor_dns = argv[2]

req = cria_requisicao(dominio)
resposta = envia_requisicao(req, servidor_dns, 1)

ns_list = interpreta_resposta(resposta)

if not ns_list:
    print(f"Dominio {dominio} nao possui entrada NS")

for i in ns_list:
    print(f"{dominio} <> {i}")

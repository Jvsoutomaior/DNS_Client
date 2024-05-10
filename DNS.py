from dataclasses import dataclass
import dataclasses
import struct


@dataclass
class cabecalhoDNS:
    id: int
    flags: int = 1 << 8     # Consulta recursiva (0x0100)
    qtd_perguntas: int = 1
    qtd_respostas: int = 0
    qtd_autoridades: int = 0
    qtd_adicionais: int = 0

    def to_bytes(self):
        campos = dataclasses.astuple(self)
        return struct.pack("!HHHHHH", *campos)


@dataclass
class perguntaDNS:
    nome: bytes
    tipo: int = 2       # RFC 1035: NS -> an authoritative name server
    classe: int = 1     # RFC 1035: IN -> the Internet

    def to_bytes(self):
        return self.nome + struct.pack("!HH", self.tipo, self.classe)


@dataclass
class registroDNS:
    nome: bytes
    ttl: int
    dados: bytes
    tipo: int = 2       # RFC 1035: NS -> an authoritative name server
    classe: int = 1     # RFC 1035: IN -> the Internet

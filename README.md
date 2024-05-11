# Camada de Aplicação: Cliente DNS

Cliente para o protocolo DNS que realiza consultas do tipo NS.

### Ambiente de desenvolvimento
O cliente foi desenvolvido no sistema Ubuntu 22.04 e utilizando Python 3.10.12

### Como executar
Basta executar o seguinte comando no mesmo diretório que o `main.py`, substituindo `<dominio>` e `<servidor DNS>` a seu critério:

```
$ python3 main.py <dominio> <servidor DNS>
```

exemplo:

```
$ python3 main.py unb.br 8.8.8.8
```

### Instruções de uso
O cliente te retornará os nomes dos servidores retornados pela sua consulta. Para o exemplo acima:
```
$ python3 main.py unb.br 8.8.8.8
unb.br <> dns2.unb.br.
unb.br <> dns1.unb.br.
unb.br <> dns3.unb.br.
```

### Limitações
Não há limitações conhecidas
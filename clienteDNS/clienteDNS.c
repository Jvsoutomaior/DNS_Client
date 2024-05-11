#include<stdio.h>
#include<string.h>
#include<stdint.h>
#include<stdlib.h>
#include<time.h>
#include<unistd.h>
#include<sys/socket.h>
#include<arpa/inet.h>

#define TYPE_NS 2
#define CLASS_IN 1
#define NAME_SIZE 255
#define UDP_MESSAGE 512
#define UDP_PORT 53

uint16_t get_id_16bits();

typedef struct PAYLOAD_UDP {
    //Header
    uint16_t id;
    uint16_t flags;
    uint16_t qd_count;
    uint16_t an_count;
    uint16_t ns_count;
    uint16_t ar_count;

    //Question
    char* Q_name;
    uint16_t Q_type;
    uint16_t Q_class;

    //Answer, Authority and Additional
    uint16_t answerRRs;
    uint16_t authorityRRs;
    uint16_t additionalRRs;   
} PAYLOAD_UDP;

int main(unsigned int argc, char** argv) {

    if (argc != 3) {
        printf("Parâmetros Inválidos\n");
        return 1;
    }

    char* server_ip = malloc(20*sizeof(char));
    char* name = malloc(NAME_SIZE*sizeof(char));

    memcpy(name, argv[1], strlen(argv[1])+1); // + 1 para pegar o '\0'
    memcpy(server_ip, argv[2], strlen(argv[2])+1);

    PAYLOAD_UDP new_request;

    // Configurando Header
    new_request.id = get_id_16bits();
    new_request.flags = 0x0100;
    new_request.qd_count = 0x0001; // Deverá indicar apenas 1 consulta
    new_request.an_count = 0x0000;
    new_request.ns_count = 0x0000;
    new_request.ar_count = 0x0000;

    // Configurando Question
    new_request.Q_name = name;
    new_request.Q_type = TYPE_NS;
    new_request.Q_class = CLASS_IN;

    // Configurando Answer RRs, Authority RRs, Additional RRs
    new_request.answerRRs = 0x0000;
    new_request.authorityRRs = 0x0000;
    new_request.additionalRRs = 0x0000;

    unsigned char message[sizeof(PAYLOAD_UDP)];
    memcpy(message, &new_request, sizeof(PAYLOAD_UDP));

    // Criando socket
    struct sockaddr_in si_other;
    socklen_t slen = sizeof(si_other);
    int socket_cliente;

    // Configurando abertura do socket UDP
    if ((socket_cliente = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Erro na abertura do socket");
        exit(1);
    }

    // Configurando a estrutura de dados sockaddr_in
    memset((char *) &si_other, 0, sizeof(si_other));
    si_other.sin_family = AF_INET;
    si_other.sin_port = htons(UDP_PORT);
    
    // Configurando inet
    if (inet_aton(server_ip, &si_other.sin_addr) == 0) {
        fprintf(stderr, "Falha no inet_aton()\n");
        exit(1);
    }

    // 3 tentativas. Se não der certo, exibir mensagem de erro
    unsigned char buffer[UDP_MESSAGE];
    for (int i = 0; i<3; i++){
        
        // Envia a mensagem
        if (sendto(socket_cliente, message, sizeof(message) , 0 , (struct sockaddr *) &si_other, slen)==-1) {
            fprintf(stderr, "Falha no sendto()\n");
            exit(1);
        }

        // Recebe resposta do servidor DNS
        memset(buffer,'\0', UDP_MESSAGE); // Limpa buffer
        if (recvfrom(socket_cliente, buffer, UDP_MESSAGE, 0, (struct sockaddr *) &si_other, &slen) == -1)
        {
            fprintf(stderr, "Erro no recvfrom()\n");
        }

        printf("Resposta:\n");
        for (int j=0; j<sizeof(buffer); j++) {
            printf("%c ", buffer[i]);
        }
        printf("\n");
    }

    close(socket_cliente);
    return 0;
}

uint16_t get_id_16bits() {
    uint16_t numero_16_bits;

    srand(time(NULL));

    numero_16_bits = (uint16_t)rand();

    return numero_16_bits;
}
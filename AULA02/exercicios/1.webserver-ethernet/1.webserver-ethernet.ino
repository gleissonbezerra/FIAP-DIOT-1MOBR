#include <SPI.h>
#include <Ethernet.h>
 
// Entre com os dados do MAC para o dispositivo.
// Lembre-se que o ip depende de sua rede local
byte mac[] = { 
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
//IPAddress ip(10,10,2,102);
 
// Inicializando a biblioteca Ehternet
// 80 é a porta que será usada. (padrão http)
EthernetServer server(80);

//Varial para mostrar a atualização da pagina
 
void setup() {
 // Abrindo a comunicação serial para monitoramento.
  Serial.begin(9600);

  // Inicia a conexão Ethernet e o servidor:
  //Ethernet.begin(mac, ip);
  Ethernet.begin(mac);

  server.begin();
  Serial.print("Servidor iniciado em: ");
  Serial.println(Ethernet.localIP());
}
 
void loop() {
  // Aguardando novos clientes;
  EthernetClient client = server.available();
  if (client) {
    Serial.println("Novo Cliente");
    // Uma solicitação http termina com uma linha em branco
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        // Se tiver chegado ao fim da linha (recebeu um novo 
        // Caractere) e a linha estiver em branco, o pedido http terminou,
        // Para que você possa enviar uma resposta
        if (c == '\n' && currentLineIsBlank) {
          
          // Envia um cabeçalho de resposta HTTP padrão
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");  // a conexão será fechada após a conclusão da resposta
          client.println("Refresh: 5");  // Atualização automática no browser
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          
          client.println("Hello World!!!");
          client.println("<br />");       
          client.print("Time: ");
          client.println((int)(millis()/1000));

          client.println("</html>");
          break;
        }
        
        if (c == '\n') {
          // Você está começando uma nova linha
          currentLineIsBlank = true;
        } 
        else if (c != '\r') {
          // Você recebeu um caracter na linha atual.
          currentLineIsBlank = false;
        }
      }
    }
    // Dar tempo ao navegador para receber os dados
    delay(1);
    // Fecha a conexão:
    client.stop();
    Serial.println("Cliente desconectado");
  }
}

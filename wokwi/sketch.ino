// Desligamento de aparelhos em tempestade - versao para simulacao no Wokwi
// O Wokwi nao tem DHT11 nem higrometro: usa DHT22 e um potenciometro no A1.
// Le o DHT11 e o higrometro, manda as leituras para o Raspberry Pi pela
// USB serial e aciona rele, LEDs e buzzer conforme o comando recebido.
// Se o Raspberry parar de responder, entra em modo seguro e decide sozinho.
//
// Protocolo (9600 baud, uma mensagem por linha):
//   Arduino -> Raspberry: T:24.0;U:78;C:310
//   Raspberry -> Arduino: N:0..2 (nivel de risco) e R:0/1 (aparelhos off/on)

#include <DHT.h>

// ---------- Pinos ----------
#define PINO_CHUVA      A1
#define PINO_DHT         2
#define PINO_BUZZER      6
#define PINO_RELE        8
#define PINO_LED_VERDE   9
#define PINO_LED_AMAR   10
#define PINO_LED_VERM   11

// ---------- Ajustes da montagem ----------
#define TIPO_DHT DHT22

// O higrometro marca perto de 1023 seco e o valor cai quando molha.
// Invertendo, o C enviado sobe com a chuva (0 = seco, 1023 = encharcado).
#define INVERTER_CHUVA false  // potenciometro: girar ao maximo = chuva

// Alguns modulos de rele ligam com LOW. Se os aparelhos ficarem desligados
// quando deveriam estar ligados (e ao contrario), troque para true.
#define RELE_ATIVO_EM_LOW false

// ---------- Tempos e limites ----------
const unsigned long INTERVALO_LEITURA = 2000;   // envia leituras a cada 2 s
const unsigned long TEMPO_SEM_RASP    = 10000;  // 10 s sem comando = modo seguro
const int LIMITE_CHUVA_SEGURO = 500;            // so usado no modo seguro (escala do C)

DHT dht(PINO_DHT, TIPO_DHT);

unsigned long ultimaLeitura = 0;
unsigned long ultimoComando = 0;
int nivel = 0;              // 0 normal, 1 atencao, 2 tempestade
bool aparelhosLigados = true;
bool modoSeguro = false;
String buffer = "";

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(PINO_BUZZER, OUTPUT);
  pinMode(PINO_RELE, OUTPUT);
  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_AMAR, OUTPUT);
  pinMode(PINO_LED_VERM, OUTPUT);

  autoteste();
  aplicarSaidas();
  ultimoComando = millis();
}

void loop() {
  lerComandos();

  if (millis() - ultimaLeitura >= INTERVALO_LEITURA) {
    ultimaLeitura = millis();
    enviarLeituras();
  }

  // Modo seguro: sem o Raspberry, decide so pela chuva
  if (millis() - ultimoComando > TEMPO_SEM_RASP) {
    modoSeguro = true;
    nivel = (lerChuva() >= LIMITE_CHUVA_SEGURO) ? 2 : 0;
    aparelhosLigados = (nivel != 2);
    aplicarSaidas();
  }

  tocarBuzzer();
}

// Pisca os LEDs em sequencia e da um bipe curto, para conferir a montagem
void autoteste() {
  int leds[] = {PINO_LED_VERDE, PINO_LED_AMAR, PINO_LED_VERM};
  for (int i = 0; i < 3; i++) {
    digitalWrite(leds[i], HIGH);
    delay(250);
    digitalWrite(leds[i], LOW);
  }
  tone(PINO_BUZZER, 1500, 100);
  delay(150);
}

int lerChuva() {
  int v = analogRead(PINO_CHUVA);
  return INVERTER_CHUVA ? 1023 - v : v;
}

// Manda uma linha com as leituras para o Raspberry Pi
void enviarLeituras() {
  float temp = dht.readTemperature();
  float umid = dht.readHumidity();

  // Falha no DHT: manda -1 e o Raspberry ignora esse sinal
  if (isnan(temp) || isnan(umid)) {
    temp = -1;
    umid = -1;
  }

  Serial.print("T:");  Serial.print(temp, 1);
  Serial.print(";U:"); Serial.print(umid, 0);
  Serial.print(";C:"); Serial.println(lerChuva());
}

// Junta os caracteres recebidos ate o fim da linha
void lerComandos() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processarComando(buffer);
      buffer = "";
    } else if (c != '\r') {
      buffer += c;
      if (buffer.length() > 20) buffer = "";  // linha estranha, descarta
    }
  }
}

void processarComando(String cmd) {
  if (cmd.startsWith("N:")) {
    nivel = constrain(cmd.substring(2).toInt(), 0, 2);
  } else if (cmd.startsWith("R:")) {
    aparelhosLigados = (cmd.substring(2).toInt() == 1);
  } else {
    return;  // comando desconhecido
  }
  ultimoComando = millis();
  modoSeguro = false;
  aplicarSaidas();
}

// LEDs mostram o nivel; o rele segue o comando de ligar/desligar
void aplicarSaidas() {
  digitalWrite(PINO_LED_VERDE, nivel == 0);
  digitalWrite(PINO_LED_AMAR,  nivel == 1);
  digitalWrite(PINO_LED_VERM,  nivel == 2);

  // LED da casa no contato NO: rele energizado = casa com energia
  bool energizar = aparelhosLigados;
  if (RELE_ATIVO_EM_LOW) energizar = !energizar;
  digitalWrite(PINO_RELE, energizar ? HIGH : LOW);
}

// Bipe intermitente so no nivel de tempestade
void tocarBuzzer() {
  if (nivel == 2 && (millis() / 500) % 2 == 0) {
    tone(PINO_BUZZER, 1000);
  } else {
    noTone(PINO_BUZZER);
  }
}

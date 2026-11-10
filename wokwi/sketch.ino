// Desligamento de aparelhos em tempestade - firmware do Arduino
// Le os sensores, envia ao Raspberry Pi pela serial e aciona os atuadores
// conforme o nivel de risco recebido. Sem comunicacao, entra em modo seguro.

#include <DHT.h>

// ---------- Pinos ----------
#define PINO_LDR       A0   // sensor de luminosidade (saida analogica)
#define PINO_CHUVA     A1   // higrometro usado como sensor de chuva
#define PINO_DHT        2   // DHT11 no prototipo (DHT22 no Wokwi)
#define PINO_BUZZER     6
#define PINO_RELE       8
#define PINO_LED_VERDE  9
#define PINO_LED_AMAR  10
#define PINO_LED_VERM  11

// No Wokwi so existe DHT22; na placa real, trocar para DHT11
#define TIPO_DHT DHT22
DHT dht(PINO_DHT, TIPO_DHT);

// ---------- Configuracao ----------
const unsigned long INTERVALO_LEITURA = 2000;   // envia leituras a cada 2 s
const unsigned long TEMPO_SEM_RASP    = 10000;  // 10 s sem comando = modo seguro
const int LIMITE_CHUVA = 600;                   // acima disso, considera chuva

unsigned long ultimaLeitura = 0;
unsigned long ultimoComando = 0;
int nivel = 0;            // 0 normal, 1 atencao, 2 tempestade
bool releLigado = true;   // aparelhos ligados por padrao
String buffer = "";

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(PINO_BUZZER, OUTPUT);
  pinMode(PINO_RELE, OUTPUT);
  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_AMAR, OUTPUT);
  pinMode(PINO_LED_VERM, OUTPUT);

  aplicarSaidas();
  ultimoComando = millis();
}

void loop() {
  lerComandos();

  // Envia as leituras no formato L:620;T:24;U:78;C:310
  if (millis() - ultimaLeitura >= INTERVALO_LEITURA) {
    ultimaLeitura = millis();
    enviarLeituras();
  }

  // Modo seguro: sem o Raspberry, decide so pela chuva
  if (millis() - ultimoComando > TEMPO_SEM_RASP) {
    int chuva = analogRead(PINO_CHUVA);
    nivel = (chuva > LIMITE_CHUVA) ? 2 : 0;
    releLigado = (nivel != 2);
    aplicarSaidas();
  }

  tocarBuzzer();
}

// Le os sensores e manda uma linha para o Raspberry Pi
void enviarLeituras() {
  int luz = analogRead(PINO_LDR);
  int chuva = analogRead(PINO_CHUVA);
  float temp = dht.readTemperature();
  float umid = dht.readHumidity();

  // Falha no DHT: envia -1 para o Raspberry tratar
  if (isnan(temp) || isnan(umid)) {
    temp = -1;
    umid = -1;
  }

  Serial.print("L:"); Serial.print(luz);
  Serial.print(";T:"); Serial.print(temp, 1);
  Serial.print(";U:"); Serial.print(umid, 0);
  Serial.print(";C:"); Serial.println(chuva);
}

// Recebe comandos do Raspberry: N:0..2 (nivel) e R:0/1 (rele)
void lerComandos() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processarComando(buffer);
      buffer = "";
    } else if (c != '\r') {
      buffer += c;
    }
  }
}

void processarComando(String cmd) {
  if (cmd.startsWith("N:")) {
    nivel = constrain(cmd.substring(2).toInt(), 0, 2);
  } else if (cmd.startsWith("R:")) {
    releLigado = (cmd.substring(2).toInt() == 1);
  } else {
    return;  // comando desconhecido
  }
  ultimoComando = millis();
  aplicarSaidas();
}

// Atualiza LEDs e rele conforme o estado atual
void aplicarSaidas() {
  digitalWrite(PINO_LED_VERDE, nivel == 0);
  digitalWrite(PINO_LED_AMAR,  nivel == 1);
  digitalWrite(PINO_LED_VERM,  nivel == 2);
  digitalWrite(PINO_RELE, releLigado ? HIGH : LOW);
}

// Bipe intermitente apenas no nivel de tempestade
void tocarBuzzer() {
  if (nivel == 2 && (millis() / 500) % 2 == 0) {
    tone(PINO_BUZZER, 1000);
  } else {
    noTone(PINO_BUZZER);
  }
}

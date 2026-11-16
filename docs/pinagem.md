# Pinagem

Montagem com duas protoboards pequenas: uma para o Arduino e outra para o Raspberry Pi com o LCD.

## Arduino Uno

Alimentação da protoboard: **5V → trilha +** e **GND → trilha −**.

| Componente | Pino do componente | Liga em |
| --- | --- | --- |
| Relé HW-482 | S | D8 |
| | + | trilha + |
| | − | trilha − |
| Relé (bornes) | COM | trilha + (5V) |
| | NO | resistor 220 Ω → perna longa do LED verde da casa |
| | NC | sem ligação |
| LED verde da casa | perna curta | trilha − |
| DHT11 (grade virada para você, da esquerda para a direita) | 1 VCC | trilha + |
| | 2 DATA | D2 |
| | 3 | sem ligação |
| | 4 GND | trilha − |
| | resistor 10 kΩ | entre o pino 1 e o pino 2 |
| Higrômetro HW-103 | VCC | trilha + |
| | GND | trilha − |
| | DO | sem ligação |
| | AO | A1 |
| Sonda HW-080 | 2 fios | nos 2 pinos do outro lado do HW-103, em qualquer ordem |
| Buzzer | + (perna longa) | D6 |
| | outra perna | trilha − |
| LED verde (nível normal) | perna longa | resistor 220 Ω → D9 |
| | perna curta | trilha − |
| LED amarelo (atenção) | perna longa | resistor 220 Ω → D10 |
| | perna curta | trilha − |
| LED vermelho (tempestade) | perna longa | resistor 220 Ω → D11 |
| | perna curta | trilha − |
| Cabo USB | | porta USB do Raspberry Pi |

O A0 fica livre.

## Raspberry Pi 4 e LCD 16x2

Numeração física do conector de 40 pinos. O pino 1 fica na ponta do conector mais longe das portas USB. Os ímpares ficam na fileira de dentro e os pares na fileira da borda.

| Pino do Raspberry | Liga em |
| --- | --- |
| 2 (5V) | trilha + da protoboard do LCD |
| 6 (GND) | trilha − da protoboard do LCD |
| 37 | LCD 4 (RS) |
| 35 | LCD 6 (E) |
| 33 | LCD 11 (D4) |
| 31 | LCD 12 (D5) |
| 29 | LCD 13 (D6) |
| 23 | LCD 14 (D7) |
| USB | cabo do Arduino |

| Pino do LCD | Liga em |
| --- | --- |
| 1 VSS | trilha − |
| 2 VDD | trilha + |
| 3 V0 | resistor 1 kΩ → trilha − |
| 4 RS | pino 37 |
| 5 RW | trilha − |
| 6 E | pino 35 |
| 7 a 10 | sem ligação |
| 11 D4 | pino 33 |
| 12 D5 | pino 31 |
| 13 D6 | pino 29 |
| 14 D7 | pino 23 |
| 15 A | resistor 220 Ω → trilha + |
| 16 K | trilha − |

Observações:

- O RW precisa ficar no GND, para o LCD nunca mandar 5V para o GPIO do Raspberry.
- Se o texto ficar fraco, troque o resistor do V0 por 2,2 kΩ. Se aparecerem quadrados pretos, use 470 Ω.
- Nunca ligue um pino do Arduino direto em um GPIO do Raspberry. Os dois conversam só pelo cabo USB.

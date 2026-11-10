# Circuito no Wokwi

Simulação do lado do Arduino no [Wokwi](https://wokwi.com). Para abrir, crie um projeto novo com Arduino Uno e cole o conteúdo de `diagram.json` e `sketch.ino` nas abas de mesmo nome. Depois, adicione a biblioteca **DHT sensor library** no Library Manager.

## Ligações

| Componente | Pino do Arduino |
| --- | --- |
| Módulo LDR (saída AO) | A0 |
| Higrômetro / sensor de chuva | A1 |
| DHT11 (DHT22 no Wokwi) | D2 |
| Buzzer | D6 |
| Relé (entrada IN) | D8 |
| LED verde (220 Ω) | D9 |
| LED amarelo (220 Ω) | D10 |
| LED vermelho (220 Ω) | D11 |

Todos os módulos são alimentados pelo 5V e GND do Arduino. No relé, o COM vai no 5V e o NO liga a carga de teste (um LED com resistor de 220 Ω), que representa os aparelhos.

## Diferenças para a montagem real

- O Wokwi não tem DHT11, então a simulação usa o DHT22. Na placa, basta trocar `DHT22` por `DHT11` no `sketch.ino`.
- O Wokwi não tem higrômetro. Um potenciômetro no A1 faz o papel dele: girando para o máximo, simula chuva.
- O Raspberry Pi 4 e o LCD 16x2 não existem no Wokwi e não aparecem nesta simulação.

## Comunicação serial (9600 baud)

O Arduino envia a cada 2 segundos:

```
L:620;T:24.0;U:78;C:310
```

E recebe do Raspberry Pi:

- `N:0`, `N:1` ou `N:2` para o nível de risco (normal, atenção, tempestade)
- `R:0` ou `R:1` para desligar ou ligar o relé

Se ficar 10 segundos sem receber comando, o Arduino entra em modo seguro e decide sozinho pela leitura de chuva.

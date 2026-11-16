# Divisão de tarefas

Cada integrante faz o commit da própria parte, pela própria conta do GitHub.

## Luiz Eduardo Treméa (líder)

Núcleo do Raspberry Pi e documentação.

| Arquivo | O que faz |
| --- | --- |
| `raspberry/config.py` | Porta serial, pinos do LCD e valores iniciais dos limites |
| `raspberry/serial_arduino.py` | Conversa com o Arduino pela USB e interpreta as mensagens |
| `raspberry/risco.py` | Regra de pontos de risco e decisão de ligar ou desligar os aparelhos |
| `raspberry/lcd.py` | Mensagens no LCD 16x2 |
| `raspberry/coletor.py` | Programa principal, que junta tudo |
| `README.md`, `docs/` | Documentação, pinagem e diagrama |

## Bruno Benetti

Hardware e firmware do Arduino.

| Arquivo | O que faz |
| --- | --- |
| `arduino/firmware/firmware.ino` | Lê os sensores, envia pela serial, aciona relé, LEDs e buzzer, e entra em modo seguro sem o Raspberry |
| `wokwi/` | Simulação do circuito do Arduino |
| Montagem | Circuito na protoboard, conforme `docs/pinagem.md` |

## Patrick Marques

Interface web, dados e testes.

| Arquivo | O que faz |
| --- | --- |
| `raspberry/banco.py` | Banco SQLite: leituras, eventos e configuração |
| `raspberry/web/` | Site em Flask: painel, gráficos, controle e limites |
| `raspberry/simulador.py` | Arduino falso para testar sem hardware |
| `raspberry/tests/` | Testes automáticos (pytest) |
| Roteiro de testes | Cenários de falha para a aula 7 |

## Como as partes se encaixam

- O firmware (Bruno) e o `serial_arduino.py` (Luiz) seguem o mesmo protocolo: `T:24.0;U:78;C:310` de ida e `N:2` / `R:0` de volta.
- O `coletor.py` (Luiz) grava no banco pelo `banco.py` (Patrick).
- O site (Patrick) lê o banco e grava as mudanças de modo, relé e limites; o coletor aplica no ciclo seguinte.
- Com o `simulador.py`, o Patrick consegue desenvolver o site sem o Arduino montado.

"""Mostra o estado do sistema no LCD 16x2.

Fora do Raspberry (ou sem o LCD ligado) só imprime no terminal.
"""
import config
from risco import NOMES


class Display:
    def __init__(self):
        self.lcd = None
        self.ultimo = None
        try:
            import RPi.GPIO as GPIO
            from RPLCD.gpio import CharLCD

            self.lcd = CharLCD(
                numbering_mode=GPIO.BOARD,
                cols=16,
                rows=2,
                pin_rs=config.LCD_RS,
                pin_e=config.LCD_E,
                pins_data=config.LCD_DADOS,
                compat_mode=True,
            )
            self.lcd.clear()
        except (ImportError, RuntimeError) as erro:
            print(f"LCD indisponível ({erro}), mostrando no terminal")

    def escrever(self, linha1, linha2=""):
        # O LCD não mostra acentos: as mensagens são escritas sem eles
        texto = (linha1[:16].ljust(16), linha2[:16].ljust(16))
        if texto == self.ultimo:
            return  # nada mudou, evita a tela piscar
        self.ultimo = texto
        if self.lcd:
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string(texto[0])
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(texto[1])
        else:
            print(f"[LCD] {texto[0]} | {texto[1]}")

    def mostrar_estado(self, nivel, aparelhos_ligados):
        self.escrever(f"Risco {NOMES[nivel]}", f"Aparelhos: {'ON' if aparelhos_ligados else 'OFF'}")

    def mostrar_offline(self):
        self.escrever("Arduino offline", "Verifique o USB")

    def fechar(self):
        if self.lcd:
            self.lcd.close(clear=True)

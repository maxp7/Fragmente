#include <Keyboard.h>
int x;

boolean buttonWasUp = true;   // переменные для считывания нажатия на кнопки

void setup() {
   pinMode(2, INPUT_PULLUP);   // подключаем тактовые кнопки
   Keyboard.begin();
   Serial.begin(9600);
}

void loop() {
   boolean buttonIsUp = digitalRead(2);   // узнаем текущее состояние кнопок


   if (buttonWasUp && !buttonIsUp) {
     delay(10);
     if (!buttonIsUp) { 
     Keyboard.press(' ');               // Нажимаем клавишу 
     delay(10);                        // Пауза для имитации нажатия клавиши
     Keyboard.releaseAll(); }
   }
   
}                                                                                    

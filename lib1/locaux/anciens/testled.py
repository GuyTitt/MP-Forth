Voici un exemple de code MicroPython utilisant `uasyncio` pour faire clignoter 3 LEDs connectées aux GPIO 7, 8, et 9, chacune avec un rythme différent, en utilisant des tâches séparées :

```python
import uasyncio as asyncio
from machine import Pin

# Définition des LEDs
led1 = Pin(7, Pin.OUT)
led2 = Pin(8, Pin.OUT)
led3 = Pin(9, Pin.OUT)

async def blink_led(led, delay_on, delay_off):
    while True:
        led.value(1)  # LED allumée
        await asyncio.sleep(delay_on)
        led.value(0)  # LED éteinte
        await asyncio.sleep(delay_off)

async def main():
    # Création des tâches pour chaque LED avec des rythmes différents
    task1 = asyncio.create_task(blink_led(led1, 0.5, 0.5))
    task2 = asyncio.create_task(blink_led(led2, 0.2, 0.8))
    task3 = asyncio.create_task(blink_led(led3, 1.0, 1.0))
    await asyncio.gather(task1, task2, task3)

asyncio.run(main())
```

### Explication :
- Chaque tâche `blink_led` contrôle une LED, en l’allumant et en l’éteignant selon des délais donnés.
- `asyncio.create_task()` lance ces tâches en parallèle.
- `asyncio.gather()` attend que toutes les tâches soient en cours d’exécution indéfiniment.

### Usage :
- Connectez vos LEDs aux GPIO 7, 8, et 9 avec des résistances en série.
- Chargez ce script sur votre microcontroller MicroPython.
- Les LEDs clignoteront indépendamment avec des rythmes différents.

Souhaitez-vous que je vous envoie le fichier `.py` prêt à être déployé ?
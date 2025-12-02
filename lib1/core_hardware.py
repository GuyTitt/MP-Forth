# début du "core_hardware" version "2"
version = ('core_hardware.py', 2)

"""
Vocabulaire spécifique ESP32-S3
- GPIO (entrées/sorties TOR)
- TIME (gestion du temps)
- NEOPIXEL (LED RGB WS2812)
"""

try:
    __core_hw_done
except NameError:
    __core_hw_done = False

if not __core_hw_done:
    from memoire import mem
    from dictionnaire import create
    from piles import piles
    import uasyncio as asyncio
    
    try:
        from machine import Pin
        from neopixel import NeoPixel
        import time
        import utime
        HW_AVAILABLE = True
    except ImportError:
        HW_AVAILABLE = False
        print("Warning: machine/neopixel non disponibles (simulation)")

    from core_primitives import dispatch

    # Opcodes GPIO
    OP_PIN_OUT     = 400
    OP_PIN_IN      = 401
    OP_PIN_HIGH    = 402
    OP_PIN_LOW     = 403
    OP_PIN_READ    = 404
    OP_PIN_TOGGLE  = 405
    OP_PIN_PULLUP  = 406
    OP_PIN_PULLDOWN= 407

    # Opcodes TIME
    OP_MS          = 410
    OP_US          = 411
    OP_TICKS_MS    = 414
    OP_TICKS_US    = 415
    OP_TICKS_DIFF  = 416

    # Opcodes NEOPIXEL
    OP_NEO_INIT    = 420
    OP_NEO_SET     = 421
    OP_NEO_WRITE   = 422
    OP_NEO_FILL    = 423
    OP_NEO_CLEAR   = 424

    pins = {}
    neopixels = {}  # Stocke les objets NeoPixel

    # ================================================
    # PRIMITIVES GPIO
    # ================================================
    
    async def prim_pin_out():
        """PIN-OUT ( pin -- ) Configure pin en sortie"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            try:
                pins[pin_num] = Pin(pin_num, Pin.OUT)
            except Exception as e:
                print(f"? Erreur GPIO {pin_num}: {e}")
        else:
            print(f"[SIM] GPIO{pin_num} → OUTPUT")

    async def prim_pin_in():
        """PIN-IN ( pin -- ) Configure pin en entrée"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            try:
                pins[pin_num] = Pin(pin_num, Pin.IN)
            except Exception as e:
                print(f"? Erreur GPIO {pin_num}: {e}")
        else:
            print(f"[SIM] GPIO{pin_num} → INPUT")

    async def prim_pin_high():
        """PIN-HIGH ( pin -- ) Met pin à HIGH"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            if pin_num in pins:
                pins[pin_num].value(1)
            else:
                print(f"? GPIO{pin_num} non configuré")
        else:
            print(f"[SIM] GPIO{pin_num} → HIGH")

    async def prim_pin_low():
        """PIN-LOW ( pin -- ) Met pin à LOW"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            if pin_num in pins:
                pins[pin_num].value(0)
            else:
                print(f"? GPIO{pin_num} non configuré")
        else:
            print(f"[SIM] GPIO{pin_num} → LOW")

    async def prim_pin_read():
        """PIN-READ ( pin -- value ) Lit l'état du pin"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            if pin_num in pins:
                val = pins[pin_num].value()
                await piles.push(val)
            else:
                print(f"? GPIO{pin_num} non configuré")
                await piles.push(0)
        else:
            print(f"[SIM] GPIO{pin_num} READ → 0")
            await piles.push(0)

    async def prim_pin_toggle():
        """PIN-TOGGLE ( pin -- ) Inverse l'état du pin"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            if pin_num in pins:
                current = pins[pin_num].value()
                pins[pin_num].value(1 - current)
            else:
                print(f"? GPIO{pin_num} non configuré")
        else:
            print(f"[SIM] GPIO{pin_num} TOGGLE")

    async def prim_pin_pullup():
        """PIN-PULLUP ( pin -- ) Configure avec pull-up"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            try:
                pins[pin_num] = Pin(pin_num, Pin.IN, Pin.PULL_UP)
            except Exception as e:
                print(f"? Erreur GPIO {pin_num}: {e}")
        else:
            print(f"[SIM] GPIO{pin_num} → INPUT PULL-UP")

    async def prim_pin_pulldown():
        """PIN-PULLDOWN ( pin -- ) Configure avec pull-down"""
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            try:
                pins[pin_num] = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
            except Exception as e:
                print(f"? Erreur GPIO {pin_num}: {e}")
        else:
            print(f"[SIM] GPIO{pin_num} → INPUT PULL-DOWN")

    # ================================================
    # PRIMITIVES TIME
    # ================================================
    
    async def prim_ms():
        """MS ( n -- ) Pause en millisecondes"""
        ms = await piles.pop()
        if HW_AVAILABLE:
            await asyncio.sleep_ms(ms)
        else:
            print(f"[SIM] SLEEP {ms}ms")

    async def prim_us():
        """US ( n -- ) Pause en microsecondes"""
        us = await piles.pop()
        if HW_AVAILABLE:
            time.sleep_us(us)
        else:
            print(f"[SIM] SLEEP {us}µs")

    async def prim_ticks_ms():
        """TICKS-MS ( -- n ) Timestamp en millisecondes"""
        if HW_AVAILABLE:
            await piles.push(utime.ticks_ms())
        else:
            await piles.push(0)

    async def prim_ticks_us():
        """TICKS-US ( -- n ) Timestamp en microsecondes"""
        if HW_AVAILABLE:
            await piles.push(utime.ticks_us())
        else:
            await piles.push(0)

    async def prim_ticks_diff():
        """TICKS-DIFF ( t1 t2 -- diff ) Différence entre timestamps"""
        t2 = await piles.pop()
        t1 = await piles.pop()
        if HW_AVAILABLE:
            diff = utime.ticks_diff(t2, t1)
            await piles.push(diff)
        else:
            await piles.push(t2 - t1)

    # ================================================
    # PRIMITIVES NEOPIXEL
    # ================================================
    
    async def prim_neo_init():
        """NEO-INIT ( pin n -- ) Initialise n LEDs NeoPixel sur pin
        Exemple: 48 1 NEO-INIT  ( 1 LED sur GPIO48 pour LilyGO T-Display-S3 )
        """
        n_leds = await piles.pop()
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            try:
                pin = Pin(pin_num, Pin.OUT)
                neopixels[pin_num] = NeoPixel(pin, n_leds)
                print(f"NeoPixel initialisé: GPIO{pin_num}, {n_leds} LED(s)")
            except Exception as e:
                print(f"? Erreur NeoPixel {pin_num}: {e}")
        else:
            print(f"[SIM] NeoPixel GPIO{pin_num}: {n_leds} LEDs")

    async def prim_neo_set():
        """NEO-SET ( pin led r g b -- ) Définit couleur RGB d'une LED
        Exemple: 48 0 255 0 0 NEO-SET  ( LED 0 en rouge )
        """
        b = await piles.pop()
        g = await piles.pop()
        r = await piles.pop()
        led = await piles.pop()
        pin_num = await piles.pop()
        
        if HW_AVAILABLE:
            if pin_num in neopixels:
                try:
                    neopixels[pin_num][led] = (r, g, b)
                except Exception as e:
                    print(f"? Erreur NEO-SET: {e}")
            else:
                print(f"? NeoPixel GPIO{pin_num} non initialisé")
        else:
            print(f"[SIM] NEO[{pin_num}][{led}] = RGB({r},{g},{b})")

    async def prim_neo_write():
        """NEO-WRITE ( pin -- ) Affiche les changements
        Exemple: 48 NEO-WRITE
        """
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            if pin_num in neopixels:
                neopixels[pin_num].write()
            else:
                print(f"? NeoPixel GPIO{pin_num} non initialisé")
        else:
            print(f"[SIM] NEO[{pin_num}] WRITE")

    async def prim_neo_fill():
        """NEO-FILL ( pin r g b -- ) Remplit toutes les LEDs
        Exemple: 48 0 255 0 NEO-FILL  ( Tout en vert )
        """
        b = await piles.pop()
        g = await piles.pop()
        r = await piles.pop()
        pin_num = await piles.pop()
        
        if HW_AVAILABLE:
            if pin_num in neopixels:
                neopixels[pin_num].fill((r, g, b))
                neopixels[pin_num].write()
            else:
                print(f"? NeoPixel GPIO{pin_num} non initialisé")
        else:
            print(f"[SIM] NEO[{pin_num}] FILL RGB({r},{g},{b})")

    async def prim_neo_clear():
        """NEO-CLEAR ( pin -- ) Éteint toutes les LEDs
        Exemple: 48 NEO-CLEAR
        """
        pin_num = await piles.pop()
        if HW_AVAILABLE:
            if pin_num in neopixels:
                neopixels[pin_num].fill((0, 0, 0))
                neopixels[pin_num].write()
            else:
                print(f"? NeoPixel GPIO{pin_num} non initialisé")
        else:
            print(f"[SIM] NEO[{pin_num}] CLEAR")

    # ================================================
    # ENREGISTREMENT DISPATCH
    # ================================================
    
    dispatch.update({
        OP_PIN_OUT:      prim_pin_out,
        OP_PIN_IN:       prim_pin_in,
        OP_PIN_HIGH:     prim_pin_high,
        OP_PIN_LOW:      prim_pin_low,
        OP_PIN_READ:     prim_pin_read,
        OP_PIN_TOGGLE:   prim_pin_toggle,
        OP_PIN_PULLUP:   prim_pin_pullup,
        OP_PIN_PULLDOWN: prim_pin_pulldown,
        OP_MS:           prim_ms,
        OP_US:           prim_us,
        OP_TICKS_MS:     prim_ticks_ms,
        OP_TICKS_US:     prim_ticks_us,
        OP_TICKS_DIFF:   prim_ticks_diff,
        OP_NEO_INIT:     prim_neo_init,
        OP_NEO_SET:      prim_neo_set,
        OP_NEO_WRITE:    prim_neo_write,
        OP_NEO_FILL:     prim_neo_fill,
        OP_NEO_CLEAR:    prim_neo_clear,
    })

    # ================================================
    # CRÉATION MOTS DICTIONNAIRE
    # ================================================
    
    def c(name, opcode):
        create(name, opcode)
        print(name, end=" ")

    print("\nVocabulaire Hardware ESP32-S3:")
    print("  GPIO:", end=" ")
    c("PIN-OUT", OP_PIN_OUT)
    c("PIN-IN", OP_PIN_IN)
    c("PIN-HIGH", OP_PIN_HIGH)
    c("PIN-LOW", OP_PIN_LOW)
    c("PIN-READ", OP_PIN_READ)
    c("PIN-TOGGLE", OP_PIN_TOGGLE)
    c("PIN-PULLUP", OP_PIN_PULLUP)
    c("PIN-PULLDOWN", OP_PIN_PULLDOWN)
    
    print("\n  TIME:", end=" ")
    c("MS", OP_MS)
    c("US", OP_US)
    c("TICKS-MS", OP_TICKS_MS)
    c("TICKS-US", OP_TICKS_US)
    c("TICKS-DIFF", OP_TICKS_DIFF)
    
    print("\n  NEOPIXEL:", end=" ")
    c("NEO-INIT", OP_NEO_INIT)
    c("NEO-SET", OP_NEO_SET)
    c("NEO-WRITE", OP_NEO_WRITE)
    c("NEO-FILL", OP_NEO_FILL)
    c("NEO-CLEAR", OP_NEO_CLEAR)
    print()

    print(f"core_hardware.py v{version[1]} chargé – GPIO, Time & NeoPixel")
    __core_hw_done = True

# fin du "core_hardware" version "2"
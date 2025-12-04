\ ============================================================================
\ APPS/3LEDS.V - Application 3 LEDs clignotantes multitâche
\ Version 1.0
\ ============================================================================
\ Fait clignoter 3 LEDs à des fréquences différentes en parallèle
\ Utilise le système de tâches coopératives
\ 
\ Connexions:
\   LED1 -> GPIO 2  (500ms on/off)
\   LED2 -> GPIO 3  (300ms on/off)
\   LED3 -> GPIO 4  (1000ms on/off)
\
\ Nécessite: stdlib_minimal.v + esp32.v + applicatif.v

\ ============================================================================
\ CONFIGURATION
\ ============================================================================

2 CONSTANT LED1-PIN
3 CONSTANT LED2-PIN
4 CONSTANT LED3-PIN

500 CONSTANT LED1-PERIOD
300 CONSTANT LED2-PERIOD
1000 CONSTANT LED3-PERIOD

\ ============================================================================
\ TÂCHES
\ ============================================================================

: LED1-TASK ( -- )
  \ Tâche LED1: clignotement 500ms
  LED1-PIN LED-INIT
  BEGIN
    LED1-PIN LED-ON
    LED1-PERIOD SLEEP
    LED1-PIN LED-OFF
    LED1-PERIOD SLEEP
  AGAIN
;

: LED2-TASK ( -- )
  \ Tâche LED2: clignotement 300ms
  LED2-PIN LED-INIT
  BEGIN
    LED2-PIN LED-ON
    LED2-PERIOD SLEEP
    LED2-PIN LED-OFF
    LED2-PERIOD SLEEP
  AGAIN
;

: LED3-TASK ( -- )
  \ Tâche LED3: clignotement 1000ms
  LED3-PIN LED-INIT
  BEGIN
    LED3-PIN LED-ON
    LED3-PERIOD SLEEP
    LED3-PIN LED-OFF
    LED3-PERIOD SLEEP
  AGAIN
;

\ ============================================================================
\ INITIALISATION ET LANCEMENT
\ ============================================================================

VARIABLE TCB1
VARIABLE TCB2
VARIABLE TCB3

: 3LEDS-INIT ( -- )
  \ Crée les 3 tâches
  256 TASK-CREATE TCB1 !
  256 TASK-CREATE TCB2 !
  256 TASK-CREATE TCB3 !
  
  \ Active les tâches
  ' LED1-TASK TCB1 @ TASK-ACTIVATE
  ' LED2-TASK TCB2 @ TASK-ACTIVATE
  ' LED3-TASK TCB3 @ TASK-ACTIVATE
  
  \ Démarre avec tâche 1
  TCB1 @ CURRENT-TASK !
;

: 3LEDS-RUN ( -- )
  \ Lance l'application
  3LEDS-INIT
  ." 3 LEDs clignotantes actives" CR
  ." GPIO 2, 3, 4 - Appuyez sur une touche pour arreter" CR
  
  \ Boucle principale
  BEGIN
    PAUSE
    \ KEY? UNTIL  \ Arrêt sur touche (si KEY? disponible)
  AGAIN
;

\ ============================================================================
\ AIDE
\ ============================================================================

: 3LEDS-HELP ( -- )
  CR
  ." ========================================" CR
  ." APPLICATION: 3 LEDs clignotantes" CR
  ." ========================================" CR
  ." " CR
  ." Utilisation:" CR
  ."   3LEDS-RUN     - Lance l'application" CR
  ."   3LEDS-INIT    - Initialise sans lancer" CR
  ."   3LEDS-HELP    - Affiche cette aide" CR
  ." " CR
  ." Configuration:" CR
  ."   LED1: GPIO 2  -> 500ms" CR
  ."   LED2: GPIO 3  -> 300ms" CR
  ."   LED3: GPIO 4  -> 1000ms" CR
  ." " CR
;

\ Afficher aide au chargement
3LEDS-HELP

\ ============================================================================
\ FIN APPS/3LEDS.V
\ ============================================================================
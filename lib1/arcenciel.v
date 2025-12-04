\ ============================================================================
\ APPS/ARCENCIEL.V - Application arc-en-ciel NeoPixel
\ Version 1.0
\ ============================================================================
\ Fait varier les couleurs d'une LED NeoPixel en arc-en-ciel
\ Utilise le système de tâches coopératives
\ 
\ Connexion:
\   NeoPixel -> GPIO 48 (carte LilyGO T-Display-S3)
\
\ Nécessite: stdlib_minimal.v + esp32.v + applicatif.v

\ ============================================================================
\ CONFIGURATION
\ ============================================================================

48 CONSTANT NEO-PIN
1 CONSTANT NEO-COUNT

\ ============================================================================
\ CONVERSION HSV -> RGB (simplifié)
\ ============================================================================

: HSV>RGB ( h s v -- r g b )
  \ Convertit HSV en RGB
  \ h: 0-359 (teinte), s: 0-255 (saturation), v: 0-255 (valeur)
  \ Algorithme simplifié pour arc-en-ciel
  
  >R >R                      ( h ) ( R: v s )
  
  \ Diviser en 6 secteurs (60° chacun)
  60 /MOD                    ( secteur reste ) ( R: v s )
  SWAP                       ( reste secteur )
  
  \ Calculer composantes selon secteur
  CASE
    0 OF  R> R> DROP DROP 255 0 0 ENDOF         \ Rouge -> Jaune
    1 OF  R> R> DROP DROP 255 255 0 ENDOF       \ Jaune -> Vert
    2 OF  R> R> DROP DROP 0 255 0 ENDOF         \ Vert -> Cyan
    3 OF  R> R> DROP DROP 0 255 255 ENDOF       \ Cyan -> Bleu
    4 OF  R> R> DROP DROP 0 0 255 ENDOF         \ Bleu -> Magenta
    5 OF  R> R> DROP DROP 255 0 255 ENDOF       \ Magenta -> Rouge
    DROP R> R> DROP DROP 255 0 0                \ Par défaut: rouge
  ENDCASE
;

\ ============================================================================
\ ANIMATION ARC-EN-CIEL
\ ============================================================================

VARIABLE HUE

: RAINBOW-STEP ( -- )
  \ Avance d'un pas dans l'arc-en-ciel
  HUE @ 255 255 HSV>RGB      ( r g b )
  NEO-PIN 0 ROT ROT ROT      ( pin led r g b )
  NEO-SET
  NEO-PIN NEO-WRITE
  
  \ Incrémenter teinte
  HUE @ 10 +                 ( new-hue )
  DUP 360 >= IF DROP 0 THEN  ( new-hue wrapped )
  HUE !
;

: RAINBOW-TASK ( -- )
  \ Tâche arc-en-ciel: variation continue
  NEO-PIN NEO-COUNT NEO-INIT
  0 HUE !
  
  BEGIN
    RAINBOW-STEP
    50 SLEEP                 \ 50ms entre étapes
  AGAIN
;

\ ============================================================================
\ INITIALISATION ET LANCEMENT
\ ============================================================================

VARIABLE RAINBOW-TCB

: RAINBOW-INIT ( -- )
  \ Crée la tâche arc-en-ciel
  256 TASK-CREATE RAINBOW-TCB !
  ' RAINBOW-TASK RAINBOW-TCB @ TASK-ACTIVATE
  RAINBOW-TCB @ CURRENT-TASK !
;

: RAINBOW-RUN ( -- )
  \ Lance l'application
  RAINBOW-INIT
  ." Arc-en-ciel NeoPixel actif" CR
  ." GPIO 48 - Variation continue" CR
  
  \ Boucle principale
  BEGIN
    PAUSE
  AGAIN
;

\ ============================================================================
\ VARIANTES
\ ============================================================================

: RAINBOW-FAST ( -- )
  \ Arc-en-ciel rapide (25ms)
  NEO-PIN NEO-COUNT NEO-INIT
  0 HUE !
  BEGIN
    RAINBOW-STEP
    25 SLEEP
  AGAIN
;

: RAINBOW-SLOW ( -- )
  \ Arc-en-ciel lent (100ms)
  NEO-PIN NEO-COUNT NEO-INIT
  0 HUE !
  BEGIN
    RAINBOW-STEP
    100 SLEEP
  AGAIN
;

: RAINBOW-PULSE ( -- )
  \ Pulsation arc-en-ciel
  NEO-PIN NEO-COUNT NEO-INIT
  0 HUE !
  
  BEGIN
    \ Variation intensité
    0 255 DO
      HUE @ 255 I HSV>RGB
      NEO-PIN 0 ROT ROT ROT NEO-SET
      NEO-PIN NEO-WRITE
      10 SLEEP
    10 +LOOP
    
    255 0 DO
      HUE @ 255 I HSV>RGB
      NEO-PIN 0 ROT ROT ROT NEO-SET
      NEO-PIN NEO-WRITE
      10 SLEEP
    -10 +LOOP
    
    \ Changer teinte
    HUE @ 30 + DUP 360 >= IF DROP 0 THEN HUE !
  AGAIN
;

\ ============================================================================
\ AIDE
\ ============================================================================

: RAINBOW-HELP ( -- )
  CR
  ." ========================================" CR
  ." APPLICATION: Arc-en-ciel NeoPixel" CR
  ." ========================================" CR
  ." " CR
  ." Utilisation:" CR
  ."   RAINBOW-RUN    - Lance arc-en-ciel standard" CR
  ."   RAINBOW-FAST   - Arc-en-ciel rapide" CR
  ."   RAINBOW-SLOW   - Arc-en-ciel lent" CR
  ."   RAINBOW-PULSE  - Pulsation colorée" CR
  ."   RAINBOW-INIT   - Initialise sans lancer" CR
  ."   RAINBOW-HELP   - Affiche cette aide" CR
  ." " CR
  ." Configuration:" CR
  ."   NeoPixel: GPIO 48 (LilyGO T-Display-S3)" CR
  ."   1 LED RGB WS2812" CR
  ." " CR
;

\ Afficher aide au chargement
RAINBOW-HELP

\ ============================================================================
\ FIN APPS/ARCENCIEL.V
\ ============================================================================
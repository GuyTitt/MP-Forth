\ ============================================================================
\ ESP32.V - Bibliothèque matériel ESP32-S3
\ Version 1.1
\ ============================================================================
\ Accès direct aux registres ESP32-S3 (memory-mapped)
\ Nécessite: stdlib_minimal.v

\ ============================================================================
\ REGISTRES GPIO ESP32-S3 (adresses fixes)
\ ============================================================================

HEX
60004004 CONSTANT GPIO_OUT_REG
60004008 CONSTANT GPIO_OUT_W1TS_REG
6000400C CONSTANT GPIO_OUT_W1TC_REG
60004020 CONSTANT GPIO_ENABLE_REG
60004024 CONSTANT GPIO_ENABLE_W1TS
60004028 CONSTANT GPIO_ENABLE_W1TC
60004044 CONSTANT GPIO_IN_REG
DECIMAL

\ ============================================================================
\ GPIO - Fonctions de base
\ ============================================================================

: PIN-OUT ( pin -- )
  1 SWAP LSHIFT
  GPIO_ENABLE_W1TS !
;

: PIN-HIGH ( pin -- )
  1 SWAP LSHIFT
  GPIO_OUT_W1TS_REG !
;

: PIN-LOW ( pin -- )
  1 SWAP LSHIFT
  GPIO_OUT_W1TC_REG !
;

: PIN-TOGGLE ( pin -- )
  DUP 1 SWAP LSHIFT
  GPIO_OUT_REG @ AND 
  IF PIN-LOW ELSE PIN-HIGH THEN
;

: PIN-IN ( pin -- )
  1 SWAP LSHIFT
  GPIO_ENABLE_W1TC !
;

: PIN-READ ( pin -- flag )
  1 SWAP LSHIFT
  GPIO_IN_REG @ AND 0<>
;

\ ============================================================================
\ TIME - Gestion du temps (simplifié)
\ ============================================================================

VARIABLE TICK-COUNT
0 TICK-COUNT !

: TICKS-MS ( -- n )
  TICK-COUNT @
;

: MS ( n -- )
  0 DO
    1000 0 DO LOOP
  LOOP
;

\ ============================================================================
\ NEOPIXEL - Placeholders (timing assembleur requis)
\ ============================================================================

: NEO-INIT ( pin n-leds -- )
  2DROP
;

: NEO-SET ( pin led r g b -- )
  2DROP 2DROP DROP
;

: NEO-WRITE ( pin -- )
  DROP
;

: NEO-CLEAR ( pin -- )
  DROP
;

\ ============================================================================
\ FIN ESP32.V
\ ============================================================================
\ ============================================================================
\ APPLICATIF.V - Utilitaires généraux
\ Version 1.1
\ ============================================================================
\ Nécessite: stdlib_minimal.v + esp32.v

\ ============================================================================
\ LED - Fonctions utilitaires
\ ============================================================================

: LED-INIT ( pin -- )
  DUP PIN-OUT
  PIN-LOW
;

: LED-ON ( pin -- )
  PIN-HIGH
;

: LED-OFF ( pin -- )
  PIN-LOW
;

: BLINK ( pin n delay -- )
  >R >R
  DUP LED-INIT
  R> 0 DO
    DUP PIN-HIGH
    R@ MS
    DUP PIN-LOW
    R@ MS
  LOOP
  DROP
  R> DROP
;

\ ============================================================================
\ BOUTON - Gestion entrées
\ ============================================================================

: BUTTON-INIT ( pin -- )
  PIN-IN
;

: BUTTON-PRESSED? ( pin -- flag )
  PIN-READ 0=
;

: BUTTON-WAIT ( pin -- )
  BEGIN
    DUP BUTTON-PRESSED?
  UNTIL
  DROP
;

\ ============================================================================
\ MULTITÂCHE - Simplifié (version de base)
\ ============================================================================

VARIABLE TASK-LIST
VARIABLE CURRENT-TASK

: TASK-CREATE ( size -- tcb-addr )
  0
;

: TASK-ACTIVATE ( xt tcb -- )
  2DROP
;

: PAUSE ( -- )
  \ Placeholder
;

: SLEEP ( ms -- )
  MS
;

\ ============================================================================
\ FIN APPLICATIF.V
\ ============================================================================
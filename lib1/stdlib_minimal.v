\ ============================================================================
\ STDLIB_MINIMAL.V - Bibliothèque minimale Forth ESP32-S3
\ Version 1.1
\ ============================================================================
\ Construit UNIQUEMENT sur les 21 primitives de base
\ Primitives: DUP DROP SWAP OVER ROT + - * / < = @ ! C@ C! >R R> EMIT .

\ ============================================================================
\ NIVEAU 0 - MOTS ESSENTIELS (construits sur 21 primitives)
\ ============================================================================

\ --- Comparaisons dérivées ---
: > ( n1 n2 -- flag ) SWAP < ;
: 0= ( n -- flag ) 0 = ;
: 0< ( n -- flag ) 0 < ;
: 0> ( n -- flag ) 0 > ;
: <> ( n1 n2 -- flag ) = 0= ;

\ --- Arithmétique étendue ---
: 1+ ( n -- n+1 ) 1 + ;
: 1- ( n -- n-1 ) 1 - ;
: 2+ ( n -- n+2 ) 2 + ;
: 2- ( n -- n-2 ) 2 - ;
: 2* ( n -- n*2 ) 2 * ;
: 2/ ( n -- n/2 ) 2 / ;
: NEGATE ( n -- -n ) 0 SWAP - ;
: ABS ( n -- |n| ) DUP 0< IF NEGATE THEN ;
: MIN ( n1 n2 -- min ) 2DUP < IF DROP ELSE SWAP DROP THEN ;
: MAX ( n1 n2 -- max ) 2DUP > IF DROP ELSE SWAP DROP THEN ;
: MOD ( n1 n2 -- reste ) 2DUP / * - ;
: /MOD ( n1 n2 -- reste quotient ) 2DUP MOD >R / R> SWAP ;

\ --- Pile avancée ---
: NIP ( a b -- b ) SWAP DROP ;
: TUCK ( a b -- b a b ) SWAP OVER ;
: 2DUP ( a b -- a b a b ) OVER OVER ;
: 2DROP ( a b -- ) DROP DROP ;
: 2SWAP ( a b c d -- c d a b ) >R ROT >R ROT R> R> ;
: ?DUP ( n -- 0 | n n ) DUP 0= IF ELSE DUP THEN ;

\ --- Logique bit à bit (simplifiée pour booléens) ---
: AND ( n1 n2 -- n3 ) 0= SWAP 0= OR 0= ;
: OR ( n1 n2 -- n3 ) 0= SWAP 0= AND 0= ;
: NOT ( n -- flag ) 0= ;
: INVERT ( n -- flag ) 0= ;
: XOR ( n1 n2 -- n3 ) OVER OVER = 0= ;

\ --- Shift (simulé avec * et /) ---
: LSHIFT ( x n -- x<<n ) 0 DO 2* LOOP ;
: RSHIFT ( x n -- x>>n ) 0 DO 2/ LOOP ;

\ --- Pile retour ---
: R@ ( -- n ) R> DUP >R ;

\ --- Mémoire étendue ---
: +! ( n addr -- ) DUP @ ROT + SWAP ! ;
: CELL+ ( addr -- addr+4 ) 4 + ;
: CELLS ( n -- n*4 ) 4 * ;

\ --- Mémoire compilateur (placeholders - seront implémentés en Python) ---
: HERE ( -- addr ) 0 ;
: ALLOT ( n -- ) DROP ;
: , ( n -- ) DROP ;
: C, ( c -- ) DROP ;

\ --- I/O étendu ---
: CR ( -- ) 10 EMIT ;
: SPACE ( -- ) 32 EMIT ;
: SPACES ( n -- ) 0 DO SPACE LOOP ;

\ --- Comparaisons non-signées (simplifiées) ---
: U< ( u1 u2 -- flag ) < ;
: U> ( u1 u2 -- flag ) > ;

\ ============================================================================
\ NIVEAU 1 - VOCABULAIRE GÉNÉRAL FORTH
\ ============================================================================

\ --- Comparaisons dérivées ---
: <= ( n1 n2 -- flag ) > 0= ;
: >= ( n1 n2 -- flag ) < 0= ;
: 0<> ( n -- flag ) 0= 0= ;
: U<= ( u1 u2 -- flag ) U> 0= ;
: U>= ( u1 u2 -- flag ) U< 0= ;

\ --- Constantes booléennes ---
: TRUE ( -- -1 ) 0 1- ;
: FALSE ( -- 0 ) 0 ;

\ --- Logique étendue ---
: NAND ( x1 x2 -- x3 ) AND 0= ;
: NOR ( x1 x2 -- x3 ) OR 0= ;

\ --- Structures de contrôle avancées ---
: UNLOOP ( -- ) R> R> R> 2DROP >R ;
: LEAVE ( -- ) R> R> R> 2DROP >R >R ;

\ --- Mathématiques ---
: */ ( n1 n2 n3 -- n1*n2/n3 ) >R * R> / ;

\ --- Affichage (simplifiés) ---
: U. ( u -- ) . ;
: .R ( n width -- ) SWAP . DROP ;

\ --- Bases numériques ---
VARIABLE BASE
10 BASE !

: HEX ( -- ) 16 BASE ! ;
: DECIMAL ( -- ) 10 BASE ! ;
: BINARY ( -- ) 2 BASE ! ;

\ ============================================================================
\ NIVEAU 2 - UTILITAIRES SIMPLES
\ ============================================================================

\ --- Mathématiques ---
: SQRT ( n -- racine )
  DUP 0= IF EXIT THEN
  DUP 2/ 
  BEGIN 
    2DUP 2DUP / + 2/ 
    2DUP > 
  WHILE 
    NIP 
  REPEAT 
  DROP ;

: GCD ( a b -- pgcd )
  BEGIN 
    ?DUP 
  WHILE 
    TUCK MOD 
  REPEAT ;

: FIB ( n -- fib[n] )
  DUP 2 < IF DROP 1 EXIT THEN
  0 1 ROT 0 DO OVER + SWAP LOOP DROP ;

\ ============================================================================
\ FIN STDLIB_MINIMAL.V
\ ============================================================================
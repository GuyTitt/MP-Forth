\ ============================================================================
\ STDLIB.V - Bibliothèque standard Forth ESP32-S3
\ Version 1.0
\ ============================================================================
\ version = ('stdlib.v', 1.0)
\ Ce fichier contient toutes les définitions Forth standard organisées
\ par niveau et par catégorie. Ces mots peuvent remplacer les implémentations
\ MicroPython pour un système Forth pur.
\ ============================================================================

\ ============================================================================
\ NIVEAU 1 - MOTS DE BASE (construits sur les primitives)
\ ============================================================================

\ ----------------------------------------------------------------------------
\ Manipulation de pile avancée
\ ----------------------------------------------------------------------------

: ?DUP ( n -- 0 | n n )
  \ Duplique si non-zéro
  DUP 0= IF ELSE DUP THEN ;

: 2SWAP ( a b c d -- c d a b )
  \ Échange deux paires
  ROT >R ROT R> ;

: 2OVER ( a b c d -- a b c d a b )
  \ Copie la deuxième paire sur le dessus
  >R >R 2DUP R> R> 2SWAP ;

: 2ROT ( a b c d e f -- c d e f a b )
  \ Rotation de trois paires
  >R >R 2SWAP R> R> 2SWAP ;

: PICK ( xu...x1 x0 u -- xu...x1 x0 xu )
  \ Copie le u-ième élément
  1+ 4 * SP@ + @ ;

: ROLL ( xu...x1 x0 u -- xu-1...x1 x0 xu )
  \ Retire et remonte le u-ième élément
  DUP >R PICK SP@ DUP 4 + R> 4 * MOVE DROP ;

\ ----------------------------------------------------------------------------
\ Arithmétique avancée
\ ----------------------------------------------------------------------------

: */ ( n1 n2 n3 -- n1*n2/n3 )
  \ Multiplication puis division
  */MOD NIP ;

: */MOD ( n1 n2 n3 -- reste quotient )
  \ Multiplication puis division avec modulo
  >R M* R> FM/MOD ;

: /MOD ( n1 n2 -- reste quotient )
  \ Division avec reste
  >R S>D R> FM/MOD ;

: ABS ( n -- |n| )
  \ Valeur absolue
  DUP 0< IF NEGATE THEN ;

: WITHIN ( n lo hi -- flag )
  \ Vrai si lo <= n < hi
  OVER - >R - R> U< ;

: ALIGNED ( addr -- a-addr )
  \ Aligne adresse sur 4 octets
  3 + 3 INVERT AND ;

: ALIGN ( -- )
  \ Aligne HERE
  HERE ALIGNED HERE - ALLOT ;

\ ----------------------------------------------------------------------------
\ Comparaisons
\ ----------------------------------------------------------------------------

: 0<> ( n -- flag )
  \ Différent de zéro
  0= 0= ;

: <= ( n1 n2 -- flag )
  \ Inférieur ou égal
  > 0= ;

: >= ( n1 n2 -- flag )
  \ Supérieur ou égal
  < 0= ;

: U> ( u1 u2 -- flag )
  \ Supérieur non signé
  SWAP U< ;

: U<= ( u1 u2 -- flag )
  \ Inférieur ou égal non signé
  U> 0= ;

: U>= ( u1 u2 -- flag )
  \ Supérieur ou égal non signé
  U< 0= ;

\ ----------------------------------------------------------------------------
\ Logique
\ ----------------------------------------------------------------------------

: TRUE ( -- -1 )
  -1 ;

: FALSE ( -- 0 )
  0 ;

: NAND ( x1 x2 -- x3 )
  AND NOT ;

: NOR ( x1 x2 -- x3 )
  OR NOT ;

\ ============================================================================
\ NIVEAU 2 - STRUCTURES DE CONTRÔLE AVANCÉES
\ ============================================================================

\ ----------------------------------------------------------------------------
\ Boucles conditionnelles
\ ----------------------------------------------------------------------------

: ?DO ( limit index -- ) IMMEDIATE
  \ DO qui ne s'exécute pas si index=limit
  POSTPONE 2DUP POSTPONE = 
  POSTPONE IF 
  POSTPONE 2DROP 
  HERE 0 ,
  POSTPONE ELSE 
  POSTPONE DO ;

: LEAVE ( -- )
  \ Sort immédiatement d'une boucle DO
  R> R> 2DROP R> DROP ;

: UNLOOP ( -- )
  \ Nettoie la pile de retour (limite et index)
  R> R> R> 2DROP >R ;

\ ----------------------------------------------------------------------------
\ Structures CASE/ENDCASE
\ ----------------------------------------------------------------------------

: CASE ( -- case-sys ) IMMEDIATE
  0 ;

: OF ( -- of-sys ) IMMEDIATE
  POSTPONE OVER POSTPONE = 
  POSTPONE IF POSTPONE DROP ;

: ENDOF ( -- endof-sys ) IMMEDIATE
  POSTPONE ELSE ;

: ENDCASE ( case-sys -- ) IMMEDIATE
  POSTPONE DROP 
  BEGIN ?DUP WHILE POSTPONE THEN REPEAT ;

\ ============================================================================
\ NIVEAU 3 - ENTRÉES/SORTIES ET FORMATAGE
\ ============================================================================

\ ----------------------------------------------------------------------------
\ Affichage formaté
\ ----------------------------------------------------------------------------

: U. ( u -- )
  \ Affiche nombre non signé
  0 <# #S #> TYPE SPACE ;

: .R ( n width -- )
  \ Affiche nombre aligné à droite
  >R DUP ABS 0 <# #S ROT SIGN #> 
  R> OVER - SPACES TYPE ;

: U.R ( u width -- )
  \ Affiche non signé aligné à droite
  >R 0 <# #S #> R> OVER - SPACES TYPE ;

: HEX ( -- )
  \ Passe en base 16
  16 BASE ! ;

: DECIMAL ( -- )
  \ Passe en base 10
  10 BASE ! ;

: BINARY ( -- )
  \ Passe en base 2
  2 BASE ! ;

: OCTAL ( -- )
  \ Passe en base 8
  8 BASE ! ;

\ ----------------------------------------------------------------------------
\ Chaînes de caractères
\ ----------------------------------------------------------------------------

: ." ( "text<quote>" -- ) IMMEDIATE
  \ Affiche une chaîne
  [CHAR] " PARSE TYPE ;

: S" ( "text<quote>" -- c-addr u ) IMMEDIATE
  \ Compile une chaîne
  [CHAR] " PARSE 
  STATE @ IF 
    POSTPONE SLITERAL 
  THEN ;

: ABORT" ( flag "text<quote>" -- ) IMMEDIATE
  \ Abandonne si flag vrai avec message
  POSTPONE IF 
  [CHAR] " PARSE 
  POSTPONE TYPE 
  POSTPONE ABORT 
  POSTPONE THEN ;

\ ============================================================================
\ NIVEAU 4 - MOTS HARDWARE ESP32-S3
\ ============================================================================

\ ----------------------------------------------------------------------------
\ GPIO - Macros de haut niveau
\ ----------------------------------------------------------------------------

: LED-INIT ( pin -- )
  \ Initialise un pin comme LED
  DUP PIN-OUT PIN-LOW ;

: LED-ON ( pin -- )
  \ Allume une LED
  PIN-HIGH ;

: LED-OFF ( pin -- )
  \ Éteint une LED
  PIN-LOW ;

: BUTTON-INIT ( pin -- )
  \ Initialise un pin comme bouton avec pull-up
  PIN-PULLUP ;

: BUTTON-PRESSED? ( pin -- flag )
  \ Vrai si bouton pressé (active-low)
  PIN-READ 0= ;

: BUTTON-WAIT ( pin -- )
  \ Attend appui sur bouton
  BEGIN DUP BUTTON-PRESSED? UNTIL DROP ;

\ ----------------------------------------------------------------------------
\ Temporisation et clignotement
\ ----------------------------------------------------------------------------

: BLINK ( pin times delay -- )
  \ Fait clignoter une LED
  >R >R 
  DUP LED-INIT 
  R> 0 DO 
    DUP LED-ON R@ MS 
    DUP LED-OFF R@ MS 
  LOOP 
  DROP R> DROP ;

: CLIGNOTE ( pin tempo-bas tempo-haut duree-bas duree-haut n-cycles -- )
  \ Clignotement avancé avec temporisation et durées configurables
  \ 
  \ Paramètres:
  \   pin        : numéro GPIO
  \   tempo-bas  : délai initial avec signal BAS (ms), 0 = skip
  \   tempo-haut : délai initial avec signal HAUT (ms), 0 = skip
  \   duree-bas  : durée signal BAS dans un cycle (ms)
  \   duree-haut : durée signal HAUT dans un cycle (ms)
  \   n-cycles   : nombre de cycles (≤0 = infini)
  \
  \ Exemple: 2 1000 500 300 200 10 CLIGNOTE
  \   GPIO2: attend 1s BAS, puis 500ms HAUT, puis 10 cycles de 300ms BAS + 200ms HAUT
  \
  \ Pile ordre: pin tempo-bas tempo-haut duree-bas duree-haut n-cycles
  
  \ Sauvegarder paramètres sur pile retour
  >R >R >R >R >R     ( R: n-cycles duree-haut duree-bas tempo-haut tempo-bas )
  
  \ Initialiser pin
  DUP LED-INIT       ( pin )
  
  \ Tempo initiale BAS
  R@ ?DUP IF         ( pin tempo-bas )
    OVER LED-OFF     ( pin tempo-bas )
    MS               ( pin )
  THEN
  R> DROP            ( pin ) ( R: n-cycles duree-haut duree-bas tempo-haut )
  
  \ Tempo initiale HAUT
  R@ ?DUP IF         ( pin tempo-haut )
    OVER LED-ON      ( pin tempo-haut )
    MS               ( pin )
  THEN
  R> DROP            ( pin ) ( R: n-cycles duree-haut duree-bas )
  
  \ Préparer cycles
  R> R> R>           ( pin duree-bas duree-haut n-cycles )
  
  \ Boucle principale
  DUP 0<= IF         ( pin duree-bas duree-haut n-cycles )
    \ Cycles infinis
    DROP             ( pin duree-bas duree-haut )
    BEGIN
      2 PICK LED-OFF ( pin duree-bas duree-haut )
      OVER MS        ( pin duree-bas duree-haut )
      2 PICK LED-ON  ( pin duree-bas duree-haut )
      DUP MS         ( pin duree-bas duree-haut )
    KEY? UNTIL       ( Stop avec une touche )
    2DROP DROP       ( -- )
  ELSE
    \ Cycles finis
    0 DO             ( pin duree-bas duree-haut )
      2 PICK LED-OFF ( pin duree-bas duree-haut )
      OVER MS        ( pin duree-bas duree-haut )
      2 PICK LED-ON  ( pin duree-bas duree-haut )
      DUP MS         ( pin duree-bas duree-haut )
    LOOP
    2DROP DROP       ( -- )
  THEN ;

\ Exemples d'utilisation CLIGNOTE:
\ 
\ Clignotement simple 10 fois (300ms BAS, 200ms HAUT):
\   2 0 0 300 200 10 CLIGNOTE
\
\ Avec temporisation initiale (1s BAS, 500ms HAUT):
\   2 1000 500 300 200 10 CLIGNOTE
\
\ Clignotement infini (arrêt par touche):
\   2 0 0 500 500 0 CLIGNOTE
\
\ SOS en morse (... --- ...):
\   : SOS-DIT  2 0 0 100 100 1 CLIGNOTE 100 MS ;
\   : SOS-DAH  2 0 0 300 100 1 CLIGNOTE 100 MS ;
\   : SOS  
\     3 0 DO SOS-DIT LOOP  500 MS
\     3 0 DO SOS-DAH LOOP  500 MS
\     3 0 DO SOS-DIT LOOP  2000 MS ;
\   : SOS-INFINI  BEGIN SOS KEY? UNTIL ;

: PULSE ( pin duration -- )
  \ Impulsion HIGH pendant duration ms
  OVER LED-ON SWAP MS LED-OFF ;

\ ----------------------------------------------------------------------------
\ NeoPixel - Macros couleurs
\ ----------------------------------------------------------------------------

: NEO-RED ( pin led -- )
  \ LED rouge
  255 0 0 NEO-SET ;

: NEO-GREEN ( pin led -- )
  \ LED verte
  0 255 0 NEO-SET ;

: NEO-BLUE ( pin led -- )
  \ LED bleue
  0 0 255 NEO-SET ;

: NEO-YELLOW ( pin led -- )
  \ LED jaune
  255 255 0 NEO-SET ;

: NEO-CYAN ( pin led -- )
  \ LED cyan
  0 255 255 NEO-SET ;

: NEO-MAGENTA ( pin led -- )
  \ LED magenta
  255 0 255 NEO-SET ;

: NEO-WHITE ( pin led -- )
  \ LED blanche
  255 255 255 NEO-SET ;

: NEO-RAINBOW ( pin n-leds delay -- )
  \ Arc-en-ciel animé
  >R >R DUP 
  BEGIN 
    R@ 0 DO 
      OVER I 
      I 360 R@ */ 255 * 360 / \ Hue to RGB (simplifié)
      128 128 NEO-SET 
    LOOP 
    DUP NEO-WRITE 
    R@ MS 
    KEY? UNTIL 
  R> R> 2DROP DROP ;

\ ============================================================================
\ NIVEAU 5 - UTILITAIRES ET ALGORITHMES
\ ============================================================================

\ ----------------------------------------------------------------------------
\ Mathématiques
\ ----------------------------------------------------------------------------

: SQRT ( n -- racine )
  \ Racine carrée par Newton-Raphson
  DUP 2/ 
  BEGIN 
    2DUP DUP 
    / + 2/ 
    2DUP > 
  WHILE 
    NIP 
  REPEAT 
  DROP ;

: GCD ( a b -- pgcd )
  \ Plus grand commun diviseur (Euclide)
  BEGIN 
    ?DUP 
  WHILE 
    TUCK MOD 
  REPEAT ;

: LCM ( a b -- ppcm )
  \ Plus petit commun multiple
  2DUP GCD 
  >R * R> / ;

: RANDOM ( n -- random )
  \ Nombre aléatoire [0..n-1]
  TICKS-MS SWAP MOD ;

\ ----------------------------------------------------------------------------
\ Fibonacci (exemples)
\ ----------------------------------------------------------------------------

: FIB-RECURSIVE ( n -- fib[n] )
  \ Version récursive (lente!)
  DUP 2 < IF 
    DROP 1 
  ELSE 
    DUP 1- RECURSE 
    SWAP 2- RECURSE 
    + 
  THEN ;

: FIB ( n -- fib[n] )
  \ Version itérative (rapide)
  0 1 ROT 0 DO OVER + SWAP LOOP DROP ;

: FIB-SEQUENCE ( n -- )
  \ Affiche séquence de Fibonacci
  0 1 ROT 0 DO 
    DUP . 
    OVER + SWAP 
  LOOP 
  2DROP ;

\ ----------------------------------------------------------------------------
\ Tri et recherche
\ ----------------------------------------------------------------------------

: BUBBLE-SORT ( addr n -- )
  \ Tri à bulles d'un tableau
  1- 0 DO 
    DUP I CELLS + 
    DUP @ SWAP CELL+ @ < IF 
      DUP @ OVER CELL+ @ 
      OVER CELL+ ! SWAP ! 
    THEN 
  LOOP DROP ;

: BINARY-SEARCH ( addr n key -- index|-1 )
  \ Recherche dichotomique
  >R 0 SWAP 
  BEGIN 
    2DUP > 
  WHILE 
    2DUP + 2/ 
    DUP CELLS 3 PICK + @ 
    R@ = IF 
      R> 2DROP NIP EXIT 
    THEN 
    R@ < IF 
      1+ SWAP DROP 
    ELSE 
      NIP 
    THEN 
  REPEAT 
  R> 3DROP -1 ;

\ ============================================================================
\ NIVEAU 6 - MULTITÂCHE (voir guide pour explications)
\ ============================================================================

\ Note: Le multitâche coopératif nécessite une gestion avancée
\ Voir guide_pedagogique.md pour l'architecture complète

VARIABLE TASK-LIST    \ Liste chaînée des tâches
VARIABLE CURRENT-TASK \ Tâche active

\ Structure d'une tâche (32 octets):
\ +0  : LINK (4) -> prochaine tâche
\ +4  : SP (4)   -> pointeur pile données
\ +8  : RP (4)   -> pointeur pile retour  
\ +12 : STATUS (4) -> 0=prête, 1=suspendue, 2=terminée
\ +16 : IP (4)   -> instruction pointer
\ +20 : délai (4) -> ticks réveil
\ +24 : nom (8)  -> nom tâche (2 cells)

: TASK ( size "name" -- task-addr )
  \ Crée une nouvelle tâche
  CREATE 
    HERE 32 + ,     \ LINK
    HERE 8 + ,      \ SP (pile locale)
    HERE 4 + ,      \ RP
    0 ,             \ STATUS
    0 ,             \ IP
    0 ,             \ délai
    0 , 0 ,         \ nom
  ALLOT             \ Espace piles
  DOES> ;

: ACTIVATE ( xt task -- )
  \ Active une tâche avec son code
  SWAP OVER 16 + ! 
  0 OVER 12 + !   \ STATUS = prête
  TASK-LIST @ OVER ! 
  TASK-LIST ! ;

: PAUSE ( -- )
  \ Passe à la tâche suivante
  \ À implémenter avec sauvegarde contexte ;

: SLEEP ( ms -- )
  \ Suspend tâche pendant ms millisecondes
  TICKS-MS + CURRENT-TASK @ 20 + ! 
  PAUSE ;

\ ============================================================================
\ EXEMPLES D'UTILISATION
\ ============================================================================

\ Exemple 1: Clignotement LED simple
\ : DEMO-LED  2 LED-INIT  2 10 500 BLINK ;

\ Exemple 2: Bouton et LED
\ : DEMO-BUTTON
\   0 BUTTON-INIT  2 LED-INIT
\   BEGIN
\     0 BUTTON-PRESSED? IF 2 LED-ON ELSE 2 LED-OFF THEN
\   KEY? UNTIL ;

\ Exemple 3: NeoPixel RGB
\ : DEMO-NEO
\   48 1 NEO-INIT           ( Initialise GPIO48, 1 LED )
\   48 0 255 0 0 NEO-SET    ( Rouge )
\   48 NEO-WRITE            ( Affiche )
\   1000 MS
\   48 0 0 255 0 NEO-SET    ( Vert )
\   48 NEO-WRITE
\   1000 MS
\   48 NEO-CLEAR ;          ( Éteint )

\ Exemple 4: Fibonacci
\ : DEMO-FIB  20 0 DO I FIB . LOOP ;

\ ============================================================================
\ FIN DE STDLIB.V
\ ============================================================================
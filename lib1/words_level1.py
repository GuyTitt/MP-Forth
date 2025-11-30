# début du "words_level1" version "2"
version = ('words_level1.py', 2)

"""
NIVEAU 1 : Mots Forth définis à partir des primitives.
Ces définitions sont en Forth pur et seront compilées au démarrage.
"""

FORTH_WORDS_LEVEL1 = """
( ============================================================ )
( STACK MANIPULATION                                           )
( ============================================================ )
: ?DUP DUP IF DUP THEN ;
: -ROT ROT ROT ;
: 2SWAP >R -ROT R> -ROT ;
: 2OVER >R >R 2DUP R> R> 2SWAP ;

( ============================================================ )
( ARITHMETIC HELPERS                                           )
( ============================================================ )
: 1+ 1 + ;
: 1- 1 - ;
: 2+ 2 + ;
: 2- 2 - ;
: 2* 2 * ;
: 2/ 2 / ;
: /MOD 2DUP MOD -ROT / ;
: */ >R * R> / ;
: */MOD >R * R> /MOD ;

( ============================================================ )
( COMPARISON                                                   )
( ============================================================ )
: <> = 0= ;
: 0> 0 > ;
: 0<> 0= 0= ;
: >= < 0= ;
: <= > 0= ;
: WITHIN OVER - >R - R> U< ;

( ============================================================ )
( LOGIC                                                        )
( ============================================================ )
: TRUE -1 ;
: FALSE 0 ;
: INVERT NOT ;

( ============================================================ )
( MEMORY HELPERS                                               )
( ============================================================ )
: FILL ( addr n char -- )
  SWAP 0 DO 2DUP C! 1+ LOOP 2DROP ;
  
: ERASE ( addr n -- )
  0 FILL ;
  
: CMOVE ( src dest n -- )
  0 DO
    OVER C@ OVER C! 1+ SWAP 1+ SWAP
  LOOP 2DROP ;

( ============================================================ )
( CONSTANTS                                                    )
( ============================================================ )
: BL 32 ;
: CELL 4 ;
: CELLS CELL * ;

( ============================================================ )
( MISCELLANEOUS                                                )
( ============================================================ )
: NOOP ;
: ALIGNED ( n -- n' ) 3 + 3 INVERT AND ;
: ALIGN HERE @ ALIGNED HERE ! ;
: ALLOT ( n -- ) HERE +! ;

( ============================================================ )
( BOUNDS & RANGES                                              )
( ============================================================ )
: BOUNDS ( addr n -- addr+n addr ) OVER + SWAP ;
: MIN ( n1 n2 -- n ) 2DUP > IF SWAP THEN DROP ;
: MAX ( n1 n2 -- n ) 2DUP < IF SWAP THEN DROP ;
: ABS ( n -- |n| ) DUP 0< IF NEGATE THEN ;
: CLAMP ( n min max -- n' )
  ROT MIN MAX ;

( ============================================================ )
( PRINTING HELPERS                                             )
( ============================================================ )
: SPACES ( n -- )
  0 MAX 0 ?DO SPACE LOOP ;
  
: U. ( u -- )
  0 <# #S #> TYPE SPACE ;

( ============================================================ )
( CONDITIONALS                                                 )
( ============================================================ )
: UNLESS ( flag -- ) 0= IF ;

( ============================================================ )
( STRING HELPERS                                               )
( ============================================================ )
: COUNT ( addr -- addr+1 n ) DUP 1+ SWAP C@ ;

( ============================================================ )
( END LEVEL 1                                                  )
( ============================================================ )
"""

async def load_level1_words():
    """
    Charge et compile tous les mots de NIVEAU 1.
    Cette fonction sera appelée par main.py après init du système.
    """
    print("\n=== Chargement NIVEAU 1 : Mots Forth pur ===")
    
    # Pour l'instant, on affiche juste les définitions
    # L'utilisateur pourra les taper manuellement ou on ajoutera
    # un compilateur automatique plus tard
    
    lines = FORTH_WORDS_LEVEL1.strip().split('\n')
    definitions = [l.strip() for l in lines if l.strip() and not l.strip().startswith('(')]
    
    print(f"{len(definitions)} définitions disponibles")
    print("Ces mots peuvent être définis en tapant les lignes dans le REPL")
    print("\nExemple rapide :")
    print("  : 1+ 1 + ;")
    print("  : 2* 2 * ;")
    print("  : ?DUP DUP IF DUP THEN ;")

print(f"words_level1.py v{version[1]} chargé – {len(FORTH_WORDS_LEVEL1.split(chr(10)))} lignes de définitions")
# fin du "words_level1" version "2"
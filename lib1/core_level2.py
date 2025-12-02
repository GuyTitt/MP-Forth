# début du "core_level2" version "1"
version = ('core_level2.py', 1)

"""
Mots Forth de niveau 2 - Définitions compilées standard

Ces mots sont définis en termes des primitives de base.
Ils sont compilés dans le dictionnaire au démarrage.
"""

try:
    __core_level2_done
except NameError:
    __core_level2_done = False

if not __core_level2_done:
    from memoire import mem
    from dictionnaire import create_colon_word, align_here
    
    def compile_word(opcodes):
        """Helper pour compiler une séquence d'opcodes"""
        for opc in opcodes:
            mem.wpoke(mem.here, opc)
            mem.here += 4

    def compile_lit(value):
        """Helper pour compiler LIT + valeur"""
        mem.wpoke(mem.here, 21)  # OP_LIT
        mem.here += 4
        mem.wpoke(mem.here, value)
        mem.here += 4

    print("\nCréation mots Forth niveau 2:", end=" ")

    # ?DUP ( n -- 0 | n n )
    # Si n≠0 alors duplique, sinon laisse 0
    align_here()
    create_colon_word("?DUP", 0)
    compile_word([1, 115])  # DUP 0=
    # Si 0= est vrai (pile=0), on a déjà 0 sur la pile, fini
    # Sinon on duplique
    mem.wpoke(mem.here, 23)  # ZBRANCH (IF)
    mem.here += 4
    skip_addr = mem.here
    mem.here += 4
    compile_word([1])  # DUP
    mem.wpoke(skip_addr, mem.here)  # Patcher THEN
    mem.wpoke(mem.here, 0)  # EXIT
    mem.here += 4
    print("?DUP", end=" ")

    # */ ( n1 n2 n3 -- n1*n2/n3 )
    align_here()
    create_colon_word("*/", 0)
    compile_word([8, 9, 0])  # * / EXIT
    mem.here += 0
    print("*/", end=" ")

    # /MOD ( n1 n2 -- reste quotient )
    align_here()
    create_colon_word("/MOD", 0)
    compile_word([4, 4, 9, 3, 10, 0])  # OVER OVER / SWAP MOD EXIT
    mem.here += 0
    print("/MOD", end=" ")

    # WITHIN ( n lo hi -- flag )
    # Vrai si lo <= n < hi
    align_here()
    create_colon_word("WITHIN", 0)
    compile_word([4, 7, 4, 111, 5, 111, 42, 0])  # OVER - OVER < ROT < AND EXIT
    mem.here += 0
    print("WITHIN", end=" ")

    # PICK ( xu ... x1 x0 u -- xu ... x1 x0 xu )
    # Copie le u-ième élément sur le sommet
    # Note: implémentation simplifiée, à améliorer
    align_here()
    create_colon_word("PICK", 0)
    compile_lit(4)
    compile_word([8, 13, 0])  # * @ EXIT
    mem.here += 0
    print("PICK", end=" ")

    # ROLL ( xu ... x1 x0 u -- xu-1 ... x1 x0 xu )
    # Rotation de u éléments
    # Note: implémentation simplifiée
    align_here()
    create_colon_word("ROLL", 0)
    compile_word([0])  # EXIT (TODO: implémenter)
    mem.here += 0
    print("ROLL", end=" ")

    # 2SWAP ( a b c d -- c d a b )
    align_here()
    create_colon_word("2SWAP", 0)
    compile_word([5, 4, 5, 0])  # ROT OVER ROT EXIT
    mem.here += 0
    print("2SWAP", end=" ")

    # 2OVER ( a b c d -- a b c d a b )
    align_here()
    create_colon_word("2OVER", 0)
    compile_lit(3)
    compile_word([13])  # PICK
    compile_lit(3)
    compile_word([13, 0])  # PICK EXIT
    mem.here += 0
    print("2OVER", end=" ")

    # ABS ( n -- |n| )
    align_here()
    create_colon_word("ABS", 0)
    compile_word([1, 114])  # DUP 0<
    mem.wpoke(mem.here, 23)  # ZBRANCH (IF)
    mem.here += 4
    skip_addr = mem.here
    mem.here += 4
    compile_word([11])  # NEGATE
    mem.wpoke(skip_addr, mem.here)
    mem.wpoke(mem.here, 0)  # EXIT
    mem.here += 4
    print("ABS", end=" ")

    # S>D ( n -- d )
    # Conversion simple vers double
    align_here()
    create_colon_word("S>D", 0)
    compile_word([1, 114])  # DUP 0<
    mem.wpoke(mem.here, 23)  # ZBRANCH
    mem.here += 4
    skip_addr = mem.here
    mem.here += 4
    compile_lit(-1)
    mem.wpoke(mem.here, 22)  # BRANCH
    mem.here += 4
    skip2 = mem.here
    mem.here += 4
    mem.wpoke(skip_addr, mem.here)
    compile_lit(0)
    mem.wpoke(skip2, mem.here)
    mem.wpoke(mem.here, 0)  # EXIT
    mem.here += 4
    print("S>D", end=" ")

    # M* ( n1 n2 -- d )
    # Multiplication avec résultat double
    align_here()
    create_colon_word("M*", 0)
    compile_word([8, 115, 0])  # * 0= EXIT (simplifié)
    mem.here += 0
    print("M*", end=" ")

    # UM* ( u1 u2 -- ud )
    # Multiplication non signée
    align_here()
    create_colon_word("UM*", 0)
    compile_word([8, 115, 0])  # * 0= EXIT (simplifié)
    mem.here += 0
    print("UM*", end=" ")

    # FM/MOD ( d n -- r q )
    # Division floor avec modulo
    align_here()
    create_colon_word("FM/MOD", 0)
    compile_word([2, 9, 3, 10, 0])  # DROP / SWAP MOD EXIT (simplifié)
    mem.here += 0
    print("FM/MOD", end=" ")

    # SM/REM ( d n -- r q )
    # Division symétrique
    align_here()
    create_colon_word("SM/REM", 0)
    compile_word([2, 9, 3, 10, 0])  # DROP / SWAP MOD EXIT (simplifié)
    mem.here += 0
    print("SM/REM", end=" ")

    # UM/MOD ( ud u -- ur uq )
    # Division non signée
    align_here()
    create_colon_word("UM/MOD", 0)
    compile_word([2, 9, 3, 10, 0])  # DROP / SWAP MOD EXIT (simplifié)
    mem.here += 0
    print("UM/MOD", end=" ")

    print(f"\ncore_level2.py v{version[1]} chargé – 15 mots niveau 2 définis")
    __core_level2_done = True

# fin du "core_level2" version "1"
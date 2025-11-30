# Guide Pédagogique Forth ESP32-S3

( version 1.0)

## Table des matières
1. [Introduction à Forth](#introduction)
2. [Architecture mémoire](#architecture-mémoire)
3. [Structure d'un mot primitif](#mot-primitif)
4. [Structure d'un mot compilé](#mot-compilé)
5. [Le dictionnaire](#dictionnaire)
6. [Compilation vs Interprétation](#compilation-interprétation)
7. [Transcodage vers assembleur](#transcodage-assembleur)
8. [Exemples pratiques](#exemples)

---

## 1. Introduction à Forth

Forth est un **langage basé sur une pile** (stack-based) inventé par Charles Moore en 1970.

### Caractéristiques
- **Notation postfixe** : `2 3 +` au lieu de `2 + 3`
- **Pas de syntaxe** : tout est des mots séparés par des espaces
- **Extensible** : on définit de nouveaux mots avec `:` et `;`
- **Compilation incrémentale** : chaque mot est compilé immédiatement

### Exemple simple
```forth
: SQUARE DUP * ;    ( Définir un mot SQUARE )
5 SQUARE .          ( Utiliser : affiche 25 )
```

---

## 2. Architecture mémoire

La RAM de l'ESP32-S3 (512KB) est organisée ainsi :

```
┌─────────────────────────────────────────┐
│ 0x00000 - 0x0FFFF : Dictionnaire/Code   │ 64KB
│ 0x10000 - 0x1FFFF : Data Stack          │ 64KB
│ 0x20000 - 0x2FFFF : Return Stack        │ 64KB
│ 0x30000 - 0x7FFFF : Heap                │ 320KB
└─────────────────────────────────────────┘
```

### Pointeurs clés
- `here` : prochaine adresse libre pour le dictionnaire
- `sp` : sommet de la pile de données (Data Stack)
- `rp` : sommet de la pile de retour (Return Stack)
- `ip` : pointeur d'instruction (Instruction Pointer)
- `latest` : dernier mot défini (chaînage du dictionnaire)

---

## 3. Structure d'un mot primitif

Un **mot primitif** est une opération de base (comme `DUP`, `+`, etc.) dont le code est géré par Python (puis assembleur).

```
┌────────────────────────────────────────────┐
│ STRUCTURE D'UN MOT PRIMITIF                │
├────────────────────────────────────────────┤
│ +0x00 : LINK (4 bytes)                     │  → Adresse du mot précédent
│ +0x04 : FLAGS|LENGTH (1 byte)             │  → bit 7=immediate, bits 6-0=longueur
│ +0x05 : NAME (N bytes)                    │  → Nom en ASCII majuscules
│ +align: CODE (4 bytes)                     │  → Opcode < 100
└────────────────────────────────────────────┘
```

### Exemple : Le mot `DUP` (opcode 1)
```
Adresse   | Contenu       | Description
----------|---------------|----------------------------
0x0118    | 0x0000010C    | LINK → mot précédent (EXIT)
0x011C    | 0x03          | FLAGS = 0, LENGTH = 3
0x011D    | 'D' (0x44)    | 
0x011E    | 'U' (0x55)    | Nom = "DUP"
0x011F    | 'P' (0x50)    | 
0x0120    | 0x00000001    | CODE = opcode 1 (OP_DUP)
```

---

## 4. Structure d'un mot compilé

Un **mot compilé** (défini avec `:`) contient du bytecode Forth.

```
┌────────────────────────────────────────────┐
│ STRUCTURE D'UN MOT COMPILÉ                 │
├────────────────────────────────────────────┤
│ +0x00 : LINK (4 bytes)                     │
│ +0x04 : FLAGS|LENGTH (1 byte)             │
│ +0x05 : NAME (N bytes)                    │
│ +align: CODE (4 bytes)                     │  → Adresse >= 0x1000
│                                            │
│ @ CODE:                                    │
│   +0x00: OP_LIT (21)                       │
│   +0x04: 42                                │
│   +0x08: OP_DUP (1)                        │
│   +0x0C: OP_MUL (8)                        │
│   +0x10: OP_EXIT (0)                       │
└────────────────────────────────────────────┘
```

### Exemple : `: SQUARE DUP * ;`
```
Adresse   | Contenu       | Description
----------|---------------|----------------------------
Header:
0x1000    | 0x00000438    | LINK → mot précédent
0x1004    | 0x06          | LENGTH = 6
0x1005-0A | "SQUARE"      | Nom
0x100C    | 0x00001010    | CODE → 0x1010

Bytecode @ 0x1010:
0x1010    | 0x00000001    | OP_DUP
0x1014    | 0x00000008    | OP_MUL
0x1018    | 0x00000000    | OP_EXIT
```

---

## 5. Le dictionnaire

Le dictionnaire est une **liste chaînée** de tous les mots définis.

```
      latest
         ↓
    ┌────────┐      ┌────────┐      ┌────────┐
    │ SQUARE │ ───> │  DUP   │ ───> │  EXIT  │ ───> NULL
    │ 0x1000 │      │ 0x0118 │      │ 0x010C │
    └────────┘      └────────┘      └────────┘
```

### Recherche d'un mot
```python
def find(name):
    addr = latest
    while addr != 0:
        if mot_à_addr(addr) == name:
            return code_addr
        addr = link_à_addr(addr)
    return None
```

---

## 6. Compilation vs Interprétation

### Mode Interprétation (state = 0)
```forth
ok> 5 DUP * .
25 ok>
```
1. `5` → empiler sur data stack
2. `DUP` → exécuter primitive `OP_DUP`
3. `*` → exécuter primitive `OP_MUL`
4. `.` → exécuter primitive `OP_DOT`

### Mode Compilation (state = 1)
```forth
ok> : SQUARE DUP * ;
ok>
```
1. `:` → passer en mode compilation, créer header
2. `DUP` → écrire `OP_DUP` dans le bytecode
3. `*` → écrire `OP_MUL` dans le bytecode
4. `;` → écrire `OP_EXIT`, revenir en mode interprétation

---

## 7. Transcodage vers assembleur

### Exemple : Primitive `DUP`

**Python (actuel)**
```python
async def prim_dup():
    x = await piles.pop()
    await piles.push(x)
    await piles.push(x)
```

**Xtensa Assembly (cible ESP32)**
```asm
; Registres:
;   a12 = SP (stack pointer)
;   a13 = RP (return pointer)
;   a14 = IP (instruction pointer)

prim_dup:
    l32i  a2, a12, 0        ; charger TOS dans a2
    addi  a12, a12, -4      ; décrémenter SP
    s32i  a2, a12, 0        ; push première copie
    addi  a12, a12, -4      ; décrémenter SP
    s32i  a2, a12, 0        ; push deuxième copie
    ret.n                   ; retour
```

### Boucle d'interprétation

**Python (actuel)**
```python
while True:
    opc = mem.wpeek(mem.ip)
    mem.ip += 4
    if opc == 0:
        break
    func = dispatch[opc]
    await func()
```

**Xtensa Assembly (cible)**
```asm
interpret_loop:
    l32i  a2, a14, 0        ; charger opcode @ IP
    addi  a14, a14, 4       ; IP += 4
    beqz  a2, exit_loop     ; si opcode == 0, sortir
    
    ; Dispatch vers primitive
    slli  a3, a2, 2         ; opcode * 4
    l32r  a4, dispatch_table
    add   a4, a4, a3        ; adresse de la primitive
    l32i  a4, a4, 0         ; charger adresse fonction
    callx0 a4               ; appeler primitive
    
    j     interpret_loop    ; boucler

exit_loop:
    ret.n
```

---

## 8. Exemples pratiques

### Exemple 1 : Fibonacci récursif
```forth
: FIB ( n -- fib )
  DUP 2 < IF EXIT THEN
  DUP 1- RECURSE
  SWAP 2 - RECURSE
  + ;

10 FIB .  ( affiche 55 )
```

### Exemple 2 : Boucle avec DO/LOOP
```forth
: EVENS ( n -- )
  0 DO
    I 2 MOD 0= IF I . THEN
  LOOP ;

10 EVENS  ( affiche: 0 2 4 6 8 )
```

### Exemple 3 : IF/THEN/ELSE
```forth
: ABS ( n -- |n| )
  DUP 0< IF NEGATE THEN ;

-5 ABS .  ( affiche: 5 )
```

---

## Annexes

### A. Table des opcodes primitifs

| Opcode | Nom | Description |
|--------|-----|-------------|
| 0 | EXIT | Fin d'exécution |
| 1 | DUP | Dupliquer TOS |
| 2 | DROP | Supprimer TOS |
| 3 | SWAP | Échanger les 2 premiers |
| 6 | + | Addition |
| 7 | - | Soustraction |
| 8 | * | Multiplication |
| 21 | LIT | Push literal |
| 23 | 0BRANCH | Branche si TOS=0 |

### B. Registres Xtensa ESP32

| Registre | Usage |
|----------|-------|
| a0 | Return address |
| a1 | Stack pointer (system) |
| a2-a7 | Arguments / return values |
| a8-a15 | Callee-saved |
| a12 | SP (Forth data stack) |
| a13 | RP (Forth return stack) |
| a14 | IP (Forth instruction pointer) |

---

**Version** : 1.0  
**Auteur** : Système Forth ESP32-S3  
**Date** : 2025
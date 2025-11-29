# début du "tests" version "5"
from memoire import mem
from piles import piles
import uasyncio as asyncio

async def assert_eq(actual, expected, msg):
    """Tester une égalité"""
    if actual == expected:
        print(f"  ✓ {msg}")
        return True
    else:
        print(f"  ✗ {msg} → attendu {expected}, obtenu {actual}")
        return False

async def run_all_tests():
    """Suite de tests complète"""
    print("\n" + "="*70)
    print(" SUITE DE TESTS – FORTH ESP32-S3")
    print("="*70 + "\n")
    
    # Réinitialiser la pile
    mem.sp = mem.SP0
    mem.rp = mem.RP0
    
    # Test 1 : push / pop basique
    print("Test 1 : Push/Pop basique")
    await piles.push(42)
    result = await piles.pop()
    await assert_eq(result, 42, "push(42) / pop() = 42")
    
    # Test 2 : DUP
    print("\nTest 2 : DUP")
    mem.sp = mem.SP0
    await piles.push(5)
    x = await piles.pop()
    await piles.push(x)
    await piles.push(x)
    result = await piles.pop()
    await assert_eq(result, 5, "DUP: première copie = 5")
    result = await piles.pop()
    await assert_eq(result, 5, "DUP: deuxième copie = 5")
    
    # Test 3 : ADD
    print("\nTest 3 : ADD")
    mem.sp = mem.SP0
    await piles.push(3)
    await piles.push(4)
    a = await piles.pop()
    b = await piles.pop()
    await piles.push(b + a)
    result = await piles.pop()
    await assert_eq(result, 7, "3 + 4 = 7")
    
    # Test 4 : SUB
    print("\nTest 4 : SUB")
    mem.sp = mem.SP0
    await piles.push(10)
    await piles.push(3)
    b = await piles.pop()
    a = await piles.pop()
    await piles.push(a - b)
    result = await piles.pop()
    await assert_eq(result, 7, "10 - 3 = 7")
    
    # Test 5 : MUL
    print("\nTest 5 : MUL")
    mem.sp = mem.SP0
    await piles.push(6)
    await piles.push(7)
    a = await piles.pop()
    b = await piles.pop()
    await piles.push(a * b)
    result = await piles.pop()
    await assert_eq(result, 42, "6 * 7 = 42")
    
    # Test 6 : SWAP
    print("\nTest 6 : SWAP")
    mem.sp = mem.SP0
    await piles.push(10)
    await piles.push(20)
    a = await piles.pop()
    b = await piles.pop()
    await piles.push(a)
    await piles.push(b)
    result_b = await piles.pop()
    result_a = await piles.pop()
    await assert_eq(result_a, 20, "SWAP: premier élément = 20")
    await assert_eq(result_b, 10, "SWAP: deuxième élément = 10")
    
    # Test 7 : Underflow
    print("\nTest 7 : Underflow detection")
    mem.sp = mem.SP0
    try:
        await piles.pop()
        print("  ✗ Underflow non détecté !")
    except IndexError as e:
        print(f"  ✓ Underflow détecté correctement")
    
    print("\n" + "="*70)
    print(" TOUS LES TESTS RÉUSSI !")
    print("="*70 + "\n")

version = ('tests.py', 5)
print(f"tests.py v{version[1]} – chargé")
# fin du "tests" version "5"
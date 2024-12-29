#!/usr/bin/env python3
from game_config import GameConfig

def test_config_validation():
    print("\nTesting configuration validation...")
    
    # Test 1: Try to set dealer_hits_soft_17 to False (should raise ValueError)
    print("\nTest 1: Setting dealer_hits_soft_17 to False")
    try:
        config = GameConfig(dealer_hits_soft_17=False)
        print("FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"PASS: Correctly raised ValueError: {str(e)}")
    
    # Test 2: Try to set allow_surrender to False (should raise ValueError)
    print("\nTest 2: Setting allow_surrender to False")
    try:
        config = GameConfig(allow_surrender=False)
        print("FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"PASS: Correctly raised ValueError: {str(e)}")
    
    # Test 3: Try invalid num_decks (should raise ValueError)
    print("\nTest 3: Setting invalid num_decks")
    try:
        config = GameConfig(num_decks=9)
        print("FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"PASS: Correctly raised ValueError: {str(e)}")
    
    # Test 4: Valid configuration (should succeed)
    print("\nTest 4: Setting valid configuration")
    try:
        config = GameConfig(
            dealer_hits_soft_17=True,
            allow_surrender=True,
            num_decks=6,
            blackjack_payout=1.5,
            max_splits=3
        )
        print("PASS: Valid configuration accepted")
    except Exception as e:
        print(f"FAIL: Valid configuration raised exception: {str(e)}")

if __name__ == "__main__":
    test_config_validation()

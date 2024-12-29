#!/usr/bin/env python3
from game_config import GameConfig

def test_config_logging():
    print("\nTesting configuration state logging...")
    
    # Test 1: Create configuration with verbose logging enabled
    print("\nTest 1: Configuration initialization logging")
    config = GameConfig(
        dealer_hits_soft_17=True,
        allow_surrender=True,
        num_decks=6,
        blackjack_payout=1.5,
        max_splits=3,
        verbose_logging=True
    )
    
    # Test 2: Modify a critical parameter
    print("\nTest 2: Parameter modification logging")
    try:
        config.dealer_hits_soft_17 = True  # This should log the change
        print("PASS: Successfully logged parameter change")
    except Exception as e:
        print(f"FAIL: Error during parameter modification: {str(e)}")
    
    # Test 3: Create configuration from preset
    print("\nTest 3: Preset configuration logging")
    vegas_config = GameConfig.vegas_strip()
    vegas_config.verbose_logging = True
    vegas_config._log_config_state("Vegas Strip Configuration")

if __name__ == "__main__":
    test_config_logging()

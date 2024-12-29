from dataclasses import dataclass
from typing import List
from game_engine import HandResult

@dataclass
class Statistics:
    """
    Tracks and reports statistics for blackjack simulation.
    Includes game outcomes, bankroll tracking, and special hand counters.
    """
    def __init__(self):
        # Game outcome counters
        self.hands_played: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.pushes: int = 0
        self.blackjacks: int = 0
        self.surrenders: int = 0
        self.busts: int = 0
        
        # Special hand counters
        self.split_hands: int = 0
        self.doubled_hands: int = 0
        
        # Configuration
        self.config = None
        self.verbose_logging = False
    
    # Bankroll tracking
    total_profit: float = 0.0
    high_water_mark: float = 0.0
    low_water_mark: float = float('inf')
    initial_bankroll: float = 0.0
    current_bankroll: float = 0.0
    
    def __post_init__(self):
        """Initialize bankroll tracking values after instance creation."""
        self.low_water_mark = self.initial_bankroll
        self.high_water_mark = self.initial_bankroll
        self.current_bankroll = self.initial_bankroll
    
    def update(self, result: HandResult, current_bankroll: float):
        """
        Update statistics based on the result of a hand.
        
        Args:
            result: The result of the hand just played
            current_bankroll: Current bankroll after the hand
        """
        # Update basic counters
        self.hands_played += 1
        self.total_profit += result.net_profit
        self.current_bankroll = current_bankroll
        
        # Update bankroll watermarks
        self.high_water_mark = max(self.high_water_mark, current_bankroll)
        self.low_water_mark = min(self.low_water_mark, current_bankroll)
        
        # Update game outcomes
        if result.is_blackjack:
            self.blackjacks += 1
            self.wins += 1
        elif result.is_surrender:
            self.surrenders += 1
            self.losses += 1
        elif result.is_bust:
            self.busts += 1
            self.losses += 1
        elif result.is_push:
            self.pushes += 1
        elif result.net_profit > 0:
            self.wins += 1
        elif result.net_profit < 0:
            self.losses += 1
            
        # Count special hands
        for hand in result.final_hands:
            if hand.is_doubled:
                self.doubled_hands += 1
            if hand.is_split:
                self.split_hands += 1
            
        # Update verbose_logging from config if available
        self.verbose_logging = self.config.verbose_logging if self.config else False
        
        # Log split hand details if verbose logging is enabled
        if self.verbose_logging and any(h.is_split for h in result.final_hands):
            print("\nSplit hand details:")
            for i, hand in enumerate(result.final_hands):
                if hand.is_split:
                    print(f"Split hand {i+1}: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
    
    def print_progress(self, hands_played: int):
        """
        Print progress statistics for the current batch of hands.
        Displays a summary of current session statistics.
        
        Args:
            hands_played: Number of hands completed in the current session
        """
        print(f"\nProgress Update - {hands_played} hands completed")
        print("-" * 60)
        
        # Bankroll status
        print("Current Bankroll Status:")
        print(f"  Current Balance: ${self.current_bankroll:.2f}")
        print(f"  Session High:    ${self.high_water_mark:.2f}")
        print(f"  Session Low:     ${self.low_water_mark:.2f}")
        
        # Basic statistics
        print("\nCurrent Statistics:")
        print(f"  Win Rate:      {self.wins/hands_played*100:.1f}%")
        print(f"  Blackjack Rate: {self.blackjacks/hands_played*100:.1f}%")
        
        # Special hands summary
        print("\nSpecial Hands:")
        print(f"  Split Hands:   {self.split_hands}")
        print(f"  Doubled Hands: {self.doubled_hands}")

    def print_final_results(self):
        """
        Print comprehensive final statistics for the session.
        Includes detailed breakdowns of hand outcomes, special hands,
        and bankroll performance.
        """
        print("\nFinal Game Statistics")
        print("=" * 60)
        
        # Basic game statistics
        print(f"Total Hands Played: {self.hands_played}")
        
        # Hand outcomes
        print("\nHand Outcomes:")
        total_hands = self.hands_played
        print(f"  Wins:      {self.wins:5d} ({self.wins/total_hands*100:.1f}%)")
        print(f"  Losses:    {self.losses:5d} ({self.losses/total_hands*100:.1f}%)")
        print(f"  Pushes:    {self.pushes:5d} ({self.pushes/total_hands*100:.1f}%)")
        print(f"  Blackjacks: {self.blackjacks:4d} ({self.blackjacks/total_hands*100:.1f}%)")
        print(f"  Surrenders: {self.surrenders:4d} ({self.surrenders/total_hands*100:.1f}%)")
        print(f"  Busts:      {self.busts:4d} ({self.busts/total_hands*100:.1f}%)")
        
        # Special hands statistics
        print("\nSpecial Hands:")
        print(f"  Split Hands:   {self.split_hands:4d} ({self.split_hands/total_hands*100:.1f}%)")
        print(f"  Doubled Hands: {self.doubled_hands:4d} ({self.doubled_hands/total_hands*100:.1f}%)")
        
        # Bankroll performance
        print("\nBankroll Performance")
        print("-" * 60)
        print(f"Initial Bankroll:  ${self.initial_bankroll:.2f}")
        print(f"Final Bankroll:    ${self.current_bankroll:.2f}")
        print(f"Session High:      ${self.high_water_mark:.2f}")
        print(f"Session Low:       ${self.low_water_mark:.2f}")
        print(f"Net Profit/Loss:   ${self.current_bankroll-self.initial_bankroll:.2f}")
        roi = ((self.current_bankroll-self.initial_bankroll)/self.initial_bankroll)*100
        print(f"Return on Investment: {roi:+.1f}%")
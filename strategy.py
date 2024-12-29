import csv
from typing import Dict, List, Optional
from card_manager import Card, Hand
from game_config import GameConfig


class Strategy:
    # Action types
    STAND = 'S'  # Stand
    HIT = 'H'  # Hit
    DOUBLE = 'D'  # Double (or hit if unable to double)
    SPLIT = 'P'  # Split
    SURRENDER = 'X'  # Surrender (or hit if not allowed)
    DOUBLE_OR_STAND = 'B'  # Double (or stand if not allowed)
    SURRENDER_OR_STAND = 'U'  # Surrender (or stand if not allowed)
    SURRENDER_OR_SPLIT = 'Q'  # Surrender (or split if not allowed)

    # Card value mapping for strategy lookups
    TEN_VALUE_RANKS = {'10', 'J', 'Q', 'K',
                       'T'}  # Using set for faster lookups

    @staticmethod
    def normalize_card_value(rank: str) -> str:
        """
        Convert ten-value cards to 'T' for strategy lookups.
        This ensures consistent handling of 10, J, Q, K as the same value.
        """
        if rank in Strategy.TEN_VALUE_RANKS:
            return 'T'
        return str(rank).upper()  # Ensure consistent case

    def __init__(self,
                 strategy_file: str,
                 config: Optional['GameConfig'] = None):
        """
        Initialize strategy from file or use default conservative strategy
        Args:
            strategy_file: Path to the strategy CSV file
            config: Game configuration instance containing rule settings
        """
        print("\nDEBUG - Strategy Constructor Input:")
        print(f"config parameter is None: {config is None}")
        if config is not None:
            print(f"Input config object id: {id(config)}")
            print(f"Input config class: {config.__class__.__name__}")
            print("Complete config state:")
            print(f"  dealer_hits_soft_17: {config.dealer_hits_soft_17}")
            print(f"  allow_surrender: {config.allow_surrender}")
            print(f"  num_decks: {config.num_decks}")
            print(f"  blackjack_payout: {config.blackjack_payout}")
            print(f"  max_splits: {config.max_splits}")
            print(f"  allow_resplit_aces: {config.allow_resplit_aces}")
            print(f"  double_after_split: {config.double_after_split}")
            print(f"  verbose_logging: {config.verbose_logging}")
            print(f"  strategy_file: {config.strategy_file}")
        else:
            print("Creating new vegas_strip config in Strategy")

        # Use the provided config or create a new vegas_strip config
        if config is not None:
            # Store a reference to the existing config
            self.config = config
        else:
            # Create a new vegas_strip config if none provided
            self.config = GameConfig.vegas_strip()

        # Ensure critical parameters are explicitly set
        self.config.dealer_hits_soft_17 = True
        self.config.allow_surrender = True

        print("\nDEBUG - Strategy After Config Assignment:")
        print(f"Using config object id: {id(self.config)}")
        print(f"Config class: {self.config.__class__.__name__}")
        print(
            f"self.config.dealer_hits_soft_17 = {self.config.dealer_hits_soft_17}"
        )
        print(f"self.config.allow_surrender = {self.config.allow_surrender}")

        if self.config.verbose_logging:
            print("\nStrategy configuration loaded with settings:")
            print(f"Allow surrender: {self.config.allow_surrender}")
            print(f"Allow resplit aces: {self.config.allow_resplit_aces}")
            print(f"Dealer hits soft 17: {self.config.dealer_hits_soft_17}")
            print(f"Number of decks: {self.config.num_decks}")
            print(f"Blackjack payout: {self.config.blackjack_payout}:1\n")

        # Load strategy after initializing logging
        self.strategy_matrix = self._load_strategy(strategy_file)

    def _load_strategy(self, filename: str) -> Dict[str, Dict[str, str]]:
        """Load strategy from CSV file or return default if file not found"""
        strategy = {}
        try:
            with open(filename, 'r') as f:
                # Skip empty lines and read header
                header = None
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith(
                            '#'):  # Skip comments and empty lines
                        continue

                    row = next(csv.reader([line]))
                    if not row:
                        continue

                    if header is None:
                        # Normalize header values (dealer cards)
                        header = [
                            self.normalize_card_value(h) for h in row[1:]
                        ]
                        if self.config.verbose_logging:
                            print(f"Strategy loader: dealer cards = {header}")
                        continue

                    # First column is the player's hand
                    player_total = row[0].strip()

                    # Convert dealer card values and create mapping
                    actions = {}
                    for i, dealer_card in enumerate(header):
                        if i + 1 < len(
                                row
                        ):  # Ensure we have an action for this dealer card
                            action = row[i + 1].strip().upper()
                            if action in [
                                    'S', 'H', 'D', 'P', 'X', 'B', 'U', 'Q'
                            ]:
                                actions[dealer_card] = action
                                if self.config.verbose_logging:
                                    print(
                                        f"Strategy loaded: {player_total} vs {dealer_card} -> {action}"
                                    )
                            else:
                                print(
                                    f"Warning: Invalid action '{action}' in strategy file at line {line_num} for hand {player_total} vs dealer {dealer_card}"
                                )
                                continue

                    if actions:  # Only add if we have valid actions
                        strategy[player_total] = actions
                        if self.config.verbose_logging:
                            print(
                                f"Strategy loader: Added rules for hand {player_total}: {actions}"
                            )

        except FileNotFoundError:
            print(
                "Strategy file not found, using default conservative strategy")
            strategy = self._default_strategy()

        if self.config.verbose_logging:
            print("\nLoaded strategy matrix:")
            for hand, actions in strategy.items():
                print(f"{hand}: {actions}")

        return strategy

    def _default_strategy(self) -> Dict[str, Dict[str, str]]:
        """Returns a conservative default strategy if no file is found"""
        return {
            # Hard totals
            '21': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            '20': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            '19': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            '18': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            '17': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            '16': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '15': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '14': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '13': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '12': {
                '2': 'H',
                '3': 'H',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '11': {
                '2': 'D',
                '3': 'D',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'D',
                '8': 'D',
                '9': 'D',
                'T': 'D',
                'A': 'D'
            },
            '10': {
                '2': 'D',
                '3': 'D',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'D',
                '8': 'D',
                '9': 'D',
                'T': 'H',
                'A': 'H'
            },
            '9': {
                '2': 'H',
                '3': 'D',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '8': {
                '2': 'H',
                '3': 'H',
                '4': 'H',
                '5': 'H',
                '6': 'H',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            # Soft totals
            'A9': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            'A8': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            'A7': {
                '2': 'S',
                '3': 'D',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'S',
                '8': 'S',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            'A6': {
                '2': 'H',
                '3': 'D',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            'A5': {
                '2': 'H',
                '3': 'H',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            'A4': {
                '2': 'H',
                '3': 'H',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            'A3': {
                '2': 'H',
                '3': 'H',
                '4': 'H',
                '5': 'D',
                '6': 'D',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            'A2': {
                '2': 'H',
                '3': 'H',
                '4': 'H',
                '5': 'D',
                '6': 'D',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            # Pairs
            'AA': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'P',
                '8': 'P',
                '9': 'P',
                'T': 'P',
                'A': 'P'
            },
            'TT': {
                '2': 'S',
                '3': 'S',
                '4': 'S',
                '5': 'S',
                '6': 'S',
                '7': 'S',
                '8': 'S',
                '9': 'S',
                'T': 'S',
                'A': 'S'
            },
            '99': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'S',
                '8': 'P',
                '9': 'P',
                'T': 'S',
                'A': 'S'
            },
            '88': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'P',
                '8': 'P',
                '9': 'P',
                'T': 'P',
                'A': 'P'
            },
            '77': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'P',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '66': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '55': {
                '2': 'D',
                '3': 'D',
                '4': 'D',
                '5': 'D',
                '6': 'D',
                '7': 'D',
                '8': 'D',
                '9': 'D',
                'T': 'H',
                'A': 'H'
            },
            '44': {
                '2': 'H',
                '3': 'H',
                '4': 'H',
                '5': 'P',
                '6': 'P',
                '7': 'H',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '33': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'P',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            },
            '22': {
                '2': 'P',
                '3': 'P',
                '4': 'P',
                '5': 'P',
                '6': 'P',
                '7': 'P',
                '8': 'H',
                '9': 'H',
                'T': 'H',
                'A': 'H'
            }
        }

    def get_action(self, hand: Hand, dealer_upcard: Card) -> str:
        """
        Returns the appropriate action for the given hand and dealer upcard.
        """
        # Always stand on split aces that have received their one card
        if hand.is_split_aces and len(hand.cards) > 1:
            if self.config.verbose_logging:
                print("Standing on split Ace (one-card rule)")
            return self.STAND

        dealer_key = self.normalize_card_value(dealer_upcard.rank)
        hand_value = hand.best_value()
        is_soft = hand.is_soft()

        if self.config.verbose_logging:
            print(f"\nStrategy Decision:")
            print(f"  Player Hand: {[str(c) for c in hand.cards]}")
            print(
                f"  Hand Value: {hand_value} ({'soft' if is_soft else 'hard'})"
            )
            print(f"  Dealer Upcard: {dealer_upcard}")

        # Always stand on natural blackjack or hard 20
        if hand.is_blackjack() or (hand_value == 20 and not is_soft):
            return self.STAND

        # Get the base action from the strategy matrix
        action = self._get_base_action(hand, dealer_key)

        # Convert complex actions based on available options
        return self._resolve_action(action, hand)

    def _normalize_hand_key(self, hand: Hand) -> str:
        """Normalize hand representation for strategy lookup"""
        # Handle pairs
        if hand.can_split():
            rank = self.normalize_card_value(hand.cards[0].rank)
            return f"{rank}{rank}"

        # Handle Ace combinations
        if len(hand.get_values()) > 1:  # Hand contains an Ace
            for card in hand.cards:
                if card.rank == 'A':
                    other_cards = [c for c in hand.cards if c != card]
                    if len(other_cards) == 1:
                        other_rank = self.normalize_card_value(
                            other_cards[0].rank)
                        return f"A{other_rank}"
                    other_sum = sum(min(c.value) for c in other_cards)
                    return f"A{other_sum}"

        # Handle hard totals
        return str(hand.best_value())

    def _get_base_action(self, hand: Hand, dealer_key: str) -> str:
        """Get the raw action from the strategy matrix"""
        key = self._normalize_hand_key(hand)
        if key not in self.strategy_matrix:
            # If no specific rule found, use hard total
            key = str(hand.best_value())

        return self.strategy_matrix[key][dealer_key]

    def _resolve_action(self, action: str, hand: Hand) -> str:
        """
        Resolve complex actions based on hand state and available options.
        """
        if self.config.verbose_logging:
            print(
                f"Resolving action: {action} for hand {[str(c) for c in hand.cards]}"
            )

        # Simple actions require no resolution
        if action in [self.STAND, self.HIT, self.SPLIT]:
            return action

        # Handle complex actions
        if action == self.DOUBLE_OR_STAND:  # B
            # Double if possible, otherwise stand
            can_double = len(hand.cards) == 2 and not hand.is_split
            resolved = self.DOUBLE if can_double else self.STAND
            if self.config.verbose_logging:
                print(
                    f"DOUBLE_OR_STAND resolved to {resolved} (can_double: {can_double})"
                )
            return resolved

        if action == self.SURRENDER_OR_STAND:  # U
            # Surrender if possible, otherwise stand
            can_surrender = len(
                hand.cards) == 2 and self.config.allow_surrender
            resolved = self.SURRENDER if can_surrender else self.STAND
            if self.config.verbose_logging:
                print(
                    f"SURRENDER_OR_STAND resolved to {resolved} (can_surrender: {can_surrender})"
                )
            return resolved

        if action == self.SURRENDER_OR_SPLIT:  # Q
            # Try surrender first, then split, finally hit
            can_surrender = len(
                hand.cards) == 2 and self.config.allow_surrender
            can_split = hand.can_split()
            resolved = self.SURRENDER if can_surrender else self.SPLIT if can_split else self.HIT
            if self.config.verbose_logging:
                print(
                    f"SURRENDER_OR_SPLIT resolved to {resolved} (can_surrender: {can_surrender}, can_split: {can_split})"
                )
            return resolved

        if action == self.DOUBLE:  # D
            # Double if possible, otherwise hit
            can_double = len(
                hand.cards) == 2  # and not hand.is_split #WBW DEBUG
            resolved = self.DOUBLE if can_double else self.HIT
            if self.config.verbose_logging:
                print(
                    f"DOUBLE resolved to {resolved} (can_double: {can_double})"
                )
            return resolved

        if action == self.SURRENDER:  # X
            # Surrender if possible, otherwise hit
            can_surrender = len(
                hand.cards) == 2 and self.config.allow_surrender
            resolved = self.SURRENDER if can_surrender else self.HIT
            if self.config.verbose_logging:
                print(
                    f"SURRENDER resolved to {resolved} (can_surrender: {can_surrender})"
                )
            return resolved

        if action == self.SPLIT:  # P
            can_split = hand.can_split()
            resolved = self.SPLIT if can_split else self.HIT
            if self.config.verbose_logging:
                print(f"SPLIT resolved to {resolved} (can_split: {can_split})")
            return resolved

        # Default to hit for unknown actions
        if self.config.verbose_logging:
            print(f"Unknown action {action}, defaulting to HIT")
        return self.HIT

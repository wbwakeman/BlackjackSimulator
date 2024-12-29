class GameConfig:
    def __init__(self,
                 dealer_hits_soft_17: bool = True,   # Default: Dealer MUST hit soft 17
                 num_decks: int = 6,                 # Default: 6 decks
                 allow_surrender: bool = True,       # Default: Late surrender IS allowed
                 blackjack_payout: float = 1.5,      # Default: 3:2 payout
                 max_splits: int = 3,                # Default: Up to 3 splits
                 allow_resplit_aces: bool = True,    # Default: Can resplit aces
                 double_after_split: bool = True,    # Default: Can double after split
                 verbose_logging: bool = False,      # Default: No verbose logging
                 strategy_file: str = 'basic_strategy.csv',
                 test_scenario: str = None):        # Default: No test scenario
        """
        Initialize game configuration with specified rules.
        All parameters have defaults matching Vegas Strip rules.

        Args:
            dealer_hits_soft_17: Whether dealer must hit on soft 17 (Default: True for Vegas Strip)
            num_decks: Number of decks in play (Default: 6 for Vegas Strip)
            allow_surrender: Whether late surrender is allowed (Default: True for Vegas Strip)
            blackjack_payout: Payout ratio for blackjack (Default: 1.5 for 3:2)
            max_splits: Maximum number of times a hand can be split (Default: 3)
            allow_resplit_aces: Whether aces can be re-split (Default: True)
            double_after_split: Whether doubling is allowed after splitting (Default: True)
            verbose_logging: Whether to enable detailed hand-by-hand logging
            strategy_file: Path to the strategy file to use

        Raises:
            ValueError: If any parameter values are invalid
            TypeError: If any parameter types are incorrect
        """
        # Initialize all parameters with defaults first
        # Non-critical parameters (public)
        self.verbose_logging = bool(verbose_logging)
        self.allow_resplit_aces = bool(allow_resplit_aces)
        self.double_after_split = bool(double_after_split)
        self.strategy_file = str(strategy_file)

        # Critical parameters (private with validation)
        self._dealer_hits_soft_17 = True  # Must always be True
        self._allow_surrender = True      # Must always be True
        self._num_decks = 6              # Default: 6 decks
        self._blackjack_payout = 1.5     # Default: 3:2 payout
        self._max_splits = 3             # Default: 3 splits allowed

        # Validate and set critical parameters
        self.dealer_hits_soft_17 = dealer_hits_soft_17  # Must be True
        self.allow_surrender = allow_surrender          # Must be True
        self.num_decks = num_decks                     # Must be 1-8
        self.blackjack_payout = blackjack_payout       # Must be > 1.0
        self.max_splits = max_splits                   # Must be 1-4

        if self.verbose_logging:
            print("\nDEBUG - GameConfig initialized with parameters:")
            print(f"Object ID: {id(self)}")
            print(f"dealer_hits_soft_17: {self._dealer_hits_soft_17}")
            print(f"allow_surrender: {self._allow_surrender}")
            print(f"num_decks: {self._num_decks}")
            print(f"blackjack_payout: {self._blackjack_payout}")
            print(f"max_splits: {self._max_splits}")
            print(f"allow_resplit_aces: {self.allow_resplit_aces}")
            print(f"double_after_split: {self.double_after_split}")
            print(f"strategy_file: {self.strategy_file}")

        # Log configuration state after initialization
        self._log_config_state("GameConfig initialized")

    @property
    def dealer_hits_soft_17(self) -> bool:
        """Whether dealer must hit on soft 17. This must always be True."""
        return self._dealer_hits_soft_17

    @dealer_hits_soft_17.setter
    def dealer_hits_soft_17(self, value: bool):
        """Set dealer_hits_soft_17 to True regardless of input value."""
        if not isinstance(value, bool):
            raise TypeError("dealer_hits_soft_17 must be a boolean")
        if not value:
            raise ValueError("dealer_hits_soft_17 must be True")
        old_value = self._dealer_hits_soft_17
        self._dealer_hits_soft_17 = True  # Always set to True
        if self.verbose_logging:
            if old_value != self._dealer_hits_soft_17:
                print(f"\nDEBUG - Configuration change:")
                print(f"  dealer_hits_soft_17: {old_value} -> {self._dealer_hits_soft_17}")
            print(f"  (Object ID: {id(self)})")

    @property
    def allow_surrender(self) -> bool:
        """Whether surrender is allowed. This must always be True."""
        return self._allow_surrender

    @allow_surrender.setter
    def allow_surrender(self, value: bool):
        """Set allow_surrender to True regardless of input value."""
        if not isinstance(value, bool):
            raise TypeError("allow_surrender must be a boolean")
        if not value:
            raise ValueError("allow_surrender must be True")
        old_value = self._allow_surrender
        self._allow_surrender = True  # Always set to True
        if self.verbose_logging:
            if old_value != self._allow_surrender:
                print(f"\nDEBUG - Configuration change:")
                print(f"  allow_surrender: {old_value} -> {self._allow_surrender}")
            print(f"  (Object ID: {id(self)})")

    @property
    def num_decks(self) -> int:
        """Number of decks in play (1-8)."""
        return self._num_decks

    @num_decks.setter
    def num_decks(self, value: int):
        """Set num_decks with validation."""
        if not isinstance(value, int):
            raise TypeError("num_decks must be an integer")
        if not 1 <= value <= 8:
            raise ValueError("num_decks must be between 1 and 8")
        old_value = self._num_decks
        self._num_decks = value
        if self.verbose_logging and old_value != self._num_decks:
            print(f"\nDEBUG - Configuration change:")
            print(f"  num_decks: {old_value} -> {self._num_decks}")
            print(f"  (Object ID: {id(self)})")

    @property
    def blackjack_payout(self) -> float:
        """Blackjack payout ratio (must be > 1.0)."""
        return self._blackjack_payout

    @blackjack_payout.setter
    def blackjack_payout(self, value: float):
        """Set blackjack_payout with validation."""
        if not isinstance(value, (int, float)):
            raise TypeError("blackjack_payout must be a number")
        value = float(value)
        if value <= 1.0:
            raise ValueError("blackjack_payout must be greater than 1.0")
        old_value = self._blackjack_payout
        self._blackjack_payout = value
        if self.verbose_logging and old_value != self._blackjack_payout:
            print(f"\nDEBUG - Configuration change:")
            print(f"  blackjack_payout: {old_value} -> {self._blackjack_payout}")
            print(f"  (Object ID: {id(self)})")

    @property
    def max_splits(self) -> int:
        """Maximum number of splits allowed (1-4)."""
        return self._max_splits

    @max_splits.setter
    def max_splits(self, value: int):
        """Set max_splits with validation."""
        if not isinstance(value, int):
            raise TypeError("max_splits must be an integer")
        if not 1 <= value <= 4:
            raise ValueError("max_splits must be between 1 and 4")
        old_value = self._max_splits
        self._max_splits = value
        if self.verbose_logging and old_value != self._max_splits:
            print(f"\nDEBUG - Configuration change:")
            print(f"  max_splits: {old_value} -> {self._max_splits}")
            print(f"  (Object ID: {id(self)})")

    @classmethod
    def vegas_strip(cls) -> 'GameConfig':
        """Las Vegas Strip rules - Updated 2024 configuration"""
        print("\nDEBUG - Creating Vegas Strip Configuration")
        # Create a new instance with explicit True values for critical parameters
        config = cls(
            dealer_hits_soft_17=True,     # Dealer MUST hit on soft 17
            num_decks=6,                  # Standard: Six deck game
            allow_surrender=True,         # Late surrender IS allowed
            blackjack_payout=1.5,         # Standard: 3:2 payout for blackjack
            max_splits=3,                 # Standard: Can split up to 3 times
            allow_resplit_aces=True,      # Standard: Can resplit aces
            double_after_split=True,      # Standard: Can double after splitting
            verbose_logging=False,        # Standard: No verbose logging by default
            strategy_file='basic_strategy.csv'
        )

        # Force the critical parameters to True explicitly after creation
        config.dealer_hits_soft_17 = True
        config.allow_surrender = True

        print(f"\nDEBUG - Vegas Strip Config Created:")
        print(f"Object ID: {id(config)}")
        print(f"dealer_hits_soft_17: {config.dealer_hits_soft_17}")
        print(f"allow_surrender: {config.allow_surrender}")
        print(f"num_decks: {config.num_decks}")
        print(f"blackjack_payout: {config.blackjack_payout}")
        print(f"max_splits: {config.max_splits}")
        print(f"allow_resplit_aces: {config.allow_resplit_aces}")
        print(f"double_after_split: {config.double_after_split}")
        return config

    def _log_config_state(self, event: str):
        """Log the current state of all configuration parameters."""
        if self.verbose_logging:
            print(f"\nDEBUG - {event}:")
            print(f"Object ID: {id(self)}")
            print("Critical Parameters:")
            print(f"  dealer_hits_soft_17: {self._dealer_hits_soft_17}")
            print(f"  allow_surrender: {self._allow_surrender}")
            print(f"  num_decks: {self._num_decks}")
            print(f"  blackjack_payout: {self._blackjack_payout}")
            print(f"  max_splits: {self._max_splits}")
            print("Non-critical Parameters:")
            print(f"  allow_resplit_aces: {getattr(self, 'allow_resplit_aces', None)}")
            print(f"  double_after_split: {getattr(self, 'double_after_split', None)}")
            print(f"  strategy_file: {getattr(self, 'strategy_file', None)}")
            print("-------------------")

    @classmethod
    def downtown_vegas(cls) -> 'GameConfig':
        """Downtown Las Vegas rules"""
        return cls(
            dealer_hits_soft_17=True,  # Dealer must hit on soft 17
            num_decks=2,              # Double deck game
            allow_surrender=True,      # Late surrender allowed
            blackjack_payout=1.5,     # 3:2 payout for blackjack
            max_splits=3,             # Can split up to 3 times
            allow_resplit_aces=True,  # Can resplit aces
            double_after_split=True,  # Can double after splitting
            verbose_logging=True      # Enable detailed logging
        )

    @classmethod
    def single_deck(cls) -> 'GameConfig':
        """Single deck rules"""
        return cls(
            dealer_hits_soft_17=True,   # Dealer hits on soft 17
            num_decks=1,               # Single deck game
            allow_surrender=False,      # No surrender allowed
            blackjack_payout=1.2,      # 6:5 payout for blackjack
            max_splits=2,              # Can split up to 2 times
            allow_resplit_aces=False,  # Cannot resplit aces
            double_after_split=False   # Cannot double after splitting
        )

    @classmethod
    def atlantic_city(cls) -> 'GameConfig':
        """Atlantic City rules"""
        return cls(
            dealer_hits_soft_17=True,   # Dealer hits on soft 17 (modified for consistency)
            num_decks=8,               # Eight deck game
            allow_surrender=True,       # Late surrender allowed
            blackjack_payout=1.5,      # 3:2 payout for blackjack
            max_splits=3,              # Can split up to 3 times
            allow_resplit_aces=False,  # Cannot resplit aces
            double_after_split=True    # Can double after splitting
        )

    @classmethod
    def european(cls) -> 'GameConfig':
        """European rules"""
        return cls(
            dealer_hits_soft_17=True,   # Dealer hits on soft 17 (modified for consistency)
            num_decks=6,               # Six deck game
            allow_surrender=False,      # No surrender allowed
            blackjack_payout=1.5,      # 3:2 payout for blackjack
            max_splits=3,              # Can split up to 3 times
            allow_resplit_aces=False,  # Cannot resplit aces
            double_after_split=False   # Cannot double after splitting
        )

    @classmethod
    def wcent(cls) -> 'GameConfig':
        """Wcent casino rules"""
        return cls(
            dealer_hits_soft_17=True,   # Dealer hits on soft 17 (modified for consistency)
            num_decks=4,               # Four deck game
            allow_surrender=False,      # No surrender allowed
            blackjack_payout=2.0,      # 2:1 payout for blackjack
            max_splits=3,              # Can split up to 3 times
            allow_resplit_aces=True,  # Can resplit aces
            double_after_split=True,   # Can double after splitting
            verbose_logging=False      # Standard: No verbose logging by default
        )
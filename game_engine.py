from dataclasses import dataclass
from typing import List, Optional
from card_manager import Card, Deck, Hand, Suit
from strategy import Strategy

@dataclass
class HandResult:
    net_profit: float
    is_blackjack: bool
    is_surrender: bool
    is_bust: bool
    is_push: bool
    final_hands: List[Hand]
    dealer_hand: Hand

from game_config import GameConfig


class BlackjackGame:
    def __init__(self, config: Optional['GameConfig'] = None):
        """Initialize game with Vegas Strip rules by default."""
        # Create a new instance of GameConfig with vegas_strip rules if no config provided
        # Ensure we're using the vegas_strip defaults when no config is provided
        if config is None:
            self.config = GameConfig.vegas_strip()
        else:
            # Use the provided config and ensure critical parameters are set
            self.config = config
            
        # Always ensure critical parameters are set correctly
        self.config.dealer_hits_soft_17 = True
        self.config.allow_surrender = True
            
        print("\nDEBUG - Starting BlackjackGame initialization...")
        
        # Initialize deck with test scenario
        self.deck = Deck(self.config.num_decks, self.config)
        print("\nDEBUG - Deck initialized, setting up test scenario...")
        
        # Set up perfect double-after-split scenario:
        # Deal order matches actual dealing sequence in play_hand method
        print("\nDEBUG - Configuring test deck sequence...")
        test_sequence = [
            # Double down cards (dealt last)
            Card('T', Suit.SPADES),    # Second split hand double
            Card('T', Suit.HEARTS),    # First split hand double
            # Post-split cards
            Card('3', Suit.DIAMONDS),  # Second split hand gets 3
            Card('3', Suit.CLUBS),     # First split hand gets 3
            # Initial deal sequence (dealt first)
            Card('T', Suit.CLUBS),     # Dealer's hole card
            Card('8', Suit.SPADES),    # Player's second card
            Card('6', Suit.DIAMONDS),  # Dealer's up card
            Card('8', Suit.HEARTS),    # Player's first card
        ]
        
        # Import and load test scenarios
        from test_scenarios import TestScenarios
        test_sequence = TestScenarios.get_scenario(self.config.test_scenario if hasattr(self.config, 'test_scenario') else None)
        self.deck.cards = test_sequence
        self.deck.is_test_deck = True  # Mark as test deck to prevent reset/shuffle
        if self.config.verbose_logging:
            print("\nDEBUG - Test deck setup for 8,8 vs 6:")
            for i, card in enumerate(self.deck.cards):
                print(f"  Position {i+1}: {card}")
        
        if self.config.verbose_logging:
            print("\nDEBUG - Test scenario setup:")
            print(f"Double after split allowed: {self.config.double_after_split}")
            print("Test deck contents:")
            for i, card in enumerate(self.deck.cards):
                print(f"  Card {i+1}: {card}")
            print("\nDeck initialized with 8,8 vs 6 split scenario\n")
        self.strategy = Strategy(self.config.strategy_file, self.config)
        
        # Debug print configuration values
        print("\nDEBUG - BlackjackGame Initialization:")
        print(f"Input config is None: {config is None}")
        if config is None:
            print("Creating new Vegas Strip config")
        else:
            print(f"Using provided config with id: {id(config)}")
        print(f"Final config.dealer_hits_soft_17 = {self.config.dealer_hits_soft_17}")
        print(f"Final config.allow_surrender = {self.config.allow_surrender}")
        print(f"Config object id: {id(self.config)}")
        
        # Print configuration if verbose logging is enabled
        if self.config.verbose_logging:
            print("\nGame initialized with rules:")
            print(f"Dealer {'hits' if self.config.dealer_hits_soft_17 else 'stands'} on soft 17")
            print(f"Late surrender {'allowed' if self.config.allow_surrender else 'not allowed'}")
            print(f"Blackjack pays {self.config.blackjack_payout:.2f}:1")
            print(f"Number of decks: {self.config.num_decks}\n")
        
        # Print configuration if verbose logging is enabled
        if self.config.verbose_logging:
            print("\nGame initialized with rules:")
            print(f"Dealer {'hits' if self.config.dealer_hits_soft_17 else 'stands'} on soft 17")
            print(f"Late surrender {'allowed' if self.config.allow_surrender else 'not allowed'}")
            print(f"Blackjack pays {self.config.blackjack_payout:.2f}:1")
            print(f"Number of decks: {self.config.num_decks}\n")

    def deal_initial_hands(self, bet: float) -> tuple[Hand, Hand]:
        player_hand = Hand(bet)
        dealer_hand = Hand(0)  # Dealer doesn't bet

        if self.config.verbose_logging:
            print("\nDealing initial hands:")

        # Deal cards alternately
        for i in range(2):
            # Deal to player
            card = self.deck.deal()
            player_hand.add_card(card)
            if self.config.verbose_logging:
                print(f"  Player card {i+1}: {card}")

            # Deal to dealer
            card = self.deck.deal()
            dealer_hand.add_card(card)
            if self.config.verbose_logging:
                print(f"  Dealer card {i+1}: {card}")

        if self.config.verbose_logging:
            print(f"\nInitial hands:")
            print(f"  Player: {[str(c) for c in player_hand.cards]}")
            print(f"  Dealer: {[str(c) for c in dealer_hand.cards]}")

        return player_hand, dealer_hand

    def play_hand(self, bet: float) -> HandResult:
        # Reset deck if less than 25% of cards remain
        if self.deck.cards_remaining() < (52 * self.deck.num_decks) // 4:
            self.deck.reset()

        self.split_hand_count = 0  # Reset split hand counter for new hand
        
        if self.config.verbose_logging:
            print("\nStarting new hand with bet: ${:.2f}".format(bet))
            
        player_hand, dealer_hand = self.deal_initial_hands(bet)
        final_hands = []

        # Always check dealer blackjack first - hand ends immediately if dealer has blackjack
        if dealer_hand.is_blackjack():
            if self.config.verbose_logging:
                print(f"\n Initial player hand: {[str(c) for c in player_hand.cards]}, dealer hand: {[str(c) for c in dealer_hand.cards]}")
                print(f"Dealer has blackjack with {[str(c) for c in dealer_hand.cards]}")
            # Only check player blackjack for push, otherwise dealer wins immediately
            if player_hand.is_blackjack():
                if self.config.verbose_logging:
                    print("Player also has blackjack - Push")
                return HandResult(0, True, False, False, True, [player_hand], dealer_hand)
            if self.config.verbose_logging:
                print("Dealer wins with blackjack")
                print("Result: L")
            return HandResult(-bet, False, False, False, False, [player_hand], dealer_hand)

        # If dealer doesn't have blackjack, check for player blackjack
        if player_hand.is_blackjack():
            return HandResult(bet * self.config.blackjack_payout, True, False, False, False,
                              [player_hand], dealer_hand)

        # Play out all hands (including splits)
        hands_to_play = [player_hand]
        while hands_to_play:
            current_hand = hands_to_play.pop(0)

            # Handle splitting aces special case
            is_split_aces = (current_hand.is_split and
                             len(current_hand.cards) == 1 and
                             current_hand.cards[0].rank == 'A')

            result = self.play_single_hand(current_hand, dealer_hand, hands_to_play,
                                           is_split_aces)

            if result.is_surrender:
                surrender_loss = -(current_hand.bet / 2)  # Half bet loss on surrender
                if self.config.verbose_logging:
                    print(f"\nPlayer surrenders with {[str(c) for c in current_hand.cards]} vs dealer {dealer_hand.cards[0]}")
                    print(f"Original bet: ${current_hand.bet:.2f}")
                    print(f"Surrender loss (half bet): -${abs(surrender_loss):.2f}")
                    print(f"Result: L (Surrender)")
                    print(f"Net Loss: -${abs(surrender_loss):.2f}")
                return HandResult(surrender_loss, False, True, False, False,
                                  [current_hand], dealer_hand)

            if not result.is_bust:
                final_hands.append(current_hand)

        # If all hands busted, return total loss
        if not final_hands:
            total_bet = sum(h.bet for h in [player_hand] +
                            [h for h in hands_to_play if h != player_hand])
            if self.config.verbose_logging:
                print(f"\nAll hands busted. Total loss: ${total_bet}")
            return HandResult(-total_bet, False, False, True, False,
                               [player_hand], dealer_hand)

        # Play dealer hand
        self.play_dealer_hand(dealer_hand)
        
        # Calculate results
        total_profit = 0
        dealer_value = dealer_hand.best_value()
        dealer_busted = dealer_hand.is_bust()

        if self.config.verbose_logging:
            if dealer_busted:
                print(f"\nDealer busts with hand: {[str(c) for c in dealer_hand.cards]} ({dealer_value})")
            else:
                print(f"\nDealer stands with hand: {[str(c) for c in dealer_hand.cards]} ({dealer_value})")

        for hand in final_hands:
            hand_value = hand.best_value()

            if dealer_busted:
                total_profit += hand.bet
            elif hand_value > dealer_value:
                total_profit += hand.bet
            elif hand_value < dealer_value:
                total_profit -= hand.bet
            # Push - no profit/loss

        # Print detailed outcome if verbose logging is enabled
        if self.config.verbose_logging:
            print(f"\nFinal Outcome:")
            print(f"Player hand(s):")
            for idx, hand in enumerate(final_hands, 1):
                hand_result = "Win" if dealer_busted or hand.best_value() > dealer_value else "Loss" if hand.best_value() < dealer_value else "Push"
                is_soft = "soft" if hand.is_soft() else "hard"
                print(f"  Hand {idx}: {[str(c) for c in hand.cards]}")
                print(f"    Value: {hand.best_value()} ({is_soft})")
                print(f"    Initial Bet: ${hand.bet:.2f}")
                if hand.is_doubled:
                    print(f"    Doubled to: ${hand.bet*2:.2f}")
                print(f"    Result: {hand_result}")
                    
                # Calculate and display monetary outcome
                if hand_result == "Win":
                    profit = hand.bet * (1.5 if hand.is_blackjack() else 1)
                    print(f"    Net Profit: +${profit:.2f}")
                elif hand_result == "Loss":
                    if hand.is_surrender:
                        print(f"    Surrendered - Loss: -${hand.bet/2:.2f}")
                    else:
                        print(f"    Net Loss: -${hand.bet:.2f}")
                else:  # Push
                    print(f"    Net Result: $0.00")
            print(f"\nDealer hand: {[str(c) for c in dealer_hand.cards]}")
            print(f"  Value: {dealer_value}{' (Busted)' if dealer_busted else ''}")
            result = 'W' if total_profit > 0 else 'L' if total_profit < 0 else 'P'
            outcome = f"+${total_profit:.2f}" if total_profit > 0 else f"-${abs(total_profit):.2f}" if total_profit < 0 else "$0.00"
            print(f"\nTotal Outcome: {result}, Net Result: {outcome}")
            if len(final_hands) > 1:
                print("\nSplit hand details:")
                for i, hand in enumerate(final_hands, 1):
                    print(f"Split hand {i}: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")

        return HandResult(total_profit, False, False, False, False,
                           final_hands, dealer_hand)

    def play_single_hand(self, hand: Hand, dealer_hand: Hand,
                         hands_to_play: List[Hand], is_split_aces: bool = False) -> HandResult:
        if self.config.verbose_logging:
            if hand.is_split:
                self.split_hand_count += 1
                print(f"\nPlaying split hand {self.split_hand_count}: {[str(c) for c in hand.cards]}, dealer hand: {[str(c) for c in dealer_hand.cards]}")
            else:
                print(f"\nInitial player hand: {[str(c) for c in hand.cards]}, dealer hand: {[str(c) for c in dealer_hand.cards]}")
        
        # First check for surrender before any other actions
        action = self.strategy.get_action(hand, dealer_hand.cards[0])
        if action in ['R', 'X']:  # Both X and R indicate surrender attempt
            can_surrender = len(hand.cards) == 2 and self.config.allow_surrender
            if can_surrender:
                hand.is_surrender = True  # Mark the hand as surrendered
                surrender_loss = -(hand.bet / 2)  # Half bet loss on surrender
                if self.config.verbose_logging:
                    print(f"\nPlayer surrenders with {[str(c) for c in hand.cards]} vs dealer {dealer_hand.cards[0]}")
                    print(f"Original bet: ${hand.bet:.2f}")
                    print(f"Surrender loss (half bet): -${abs(surrender_loss):.2f}")
                    print(f"Result: L (Surrender)")
                    print(f"Net Loss: -${abs(surrender_loss):.2f}")
                return HandResult(surrender_loss, False, True, False, False,
                                  [hand], dealer_hand)
            elif self.config.verbose_logging:
                print("Cannot surrender - continuing with basic strategy")

        # Check if we've reached maximum splits
        if hand.is_split and len(hands_to_play) >= self.config.max_splits:
            if self.config.verbose_logging:
                print(f"Maximum splits ({self.config.max_splits}) reached, continuing with current hand")
            return self._play_current_hand(hand, dealer_hand, is_split_aces)

        while True:
            # Split aces get only one card - always
            if is_split_aces:
                if len(hand.cards) == 1:
                    # Deal one card to the ace
                    while True:
                        card = self.deck.deal()
                        if card is None:
                            self.deck.reset()
                            continue
                        hand.add_card(card)
                        break
                    if self.config.verbose_logging:
                        print(f"\nSplit Ace received one card: {card}")
                        print(f"Final split Ace hand: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                        print("Standing on split Ace (one-card rule)")
                    break
                elif len(hand.cards) > 1:
                    if self.config.verbose_logging:
                        print("Standing on split Ace (one-card rule)")
                    break

            action = self.strategy.get_action(hand, dealer_hand.cards[0])
            if self.config.verbose_logging:
                print(f"Hand: {[str(c) for c in hand.cards]} (Value: {hand.best_value()}), Dealer shows: {dealer_hand.cards[0]}")
                print(f"Strategy suggests: {action}")

            if action == 'S':  # Stand
                if self.config.verbose_logging:
                    print(f"Standing with {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                break

            elif action == 'H':  # Hit
                while True:
                    card = self.deck.deal()
                    if card is None:
                        self.deck.reset()
                        continue
                    hand.add_card(card)
                    break
                if self.config.verbose_logging:
                    print(f"Player hits, receives: {card}")
                    print(f"New hand: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                if hand.is_bust():
                    if self.config.verbose_logging:
                        print(f"Player busts with {[str(c) for c in hand.cards]}")
                    return HandResult(0, False, False, True, False, [], dealer_hand)

            elif action == 'D':  # Double
                if self.config.verbose_logging:
                    print("\nDEBUG - Double Down Evaluation Started:")
                    print(f"Initial hand state:")
                    print(f"  Cards: {[str(c) for c in hand.cards]}")
                    print(f"  Value: {hand.best_value()}")
                    print(f"  Is split hand: {hand.is_split}")
                    print(f"  Has exactly 2 cards: {len(hand.cards) == 2}")
                    print(f"  Current bet: ${hand.bet:.2f}")
                    if hand.is_split:
                        print(f"  Double after split setting: {self.config.double_after_split}")
                        print(f"  Is split aces: {is_split_aces}")

                # Check if doubling is allowed
                can_double = len(hand.cards) == 2  # Must have exactly 2 cards
                reasons_not_allowed = []

                if not can_double:
                    reasons_not_allowed.append("must have exactly 2 cards")
                elif is_split_aces:
                    can_double = False
                    reasons_not_allowed.append("cannot double split aces")
                elif hand.is_split and not self.config.double_after_split:
                    can_double = False
                    reasons_not_allowed.append("double after split not allowed")

                # Final decision logging
                if self.config.verbose_logging:
                    print("\nDouble Down Decision:")
                    print(f"  Can double: {can_double}")
                    if not can_double:
                        print(f"  Reasons not allowed: {', '.join(reasons_not_allowed)}")
                    else:
                        print("  All validation checks passed - proceeding with double down")
                
                if can_double:
                    # Execute double down
                    if self.config.verbose_logging:
                        print("\nExecuting double down:")
                        print(f"Original bet: ${hand.bet:.2f}")
                        
                    # Double the bet
                    hand.is_doubled = True
                    hand.bet *= 2
                    
                    if self.config.verbose_logging:
                        print(f"Doubled bet to: ${hand.bet:.2f}")
                    
                    # Deal exactly one card
                    card = self.deck.deal()
                    if card is not None:
                        hand.add_card(card)
                        if self.config.verbose_logging:
                            print(f"Received card: {card}")
                            print(f"Final hand: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                    
                    # Check for bust
                    if hand.is_bust():
                        if self.config.verbose_logging:
                            print(f"Busted with {[str(c) for c in hand.cards]}")
                        return HandResult(0, False, False, True, False, [], dealer_hand)
                    
                    return HandResult(0, False, False, False, False, [hand], dealer_hand)
                else:
                    # Convert to hit if double down not allowed
                    if self.config.verbose_logging:
                        print("\nDouble down not allowed, converting to hit")
                        print(f"Current hand: {[str(c) for c in hand.cards]}")
                    
                    card = self.deck.deal()
                    if card is not None:
                        hand.add_card(card)
                        if self.config.verbose_logging:
                            print(f"Hit received: {card}")
                            print(f"New hand: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                    
                    if hand.is_bust():
                        if self.config.verbose_logging:
                            print(f"Busted with {[str(c) for c in hand.cards]}")
                        return HandResult(0, False, False, True, False, [], dealer_hand)
                    continue

            elif action == 'P' and hand.can_split():  # Split
                if len(hands_to_play) >= self.config.max_splits:
                    if self.config.verbose_logging:
                        print(f"Maximum splits ({self.config.max_splits}) reached, continuing with current hand")
                    continue
                    
                if self.config.verbose_logging:
                    print(f"\nSplitting pair of {hand.cards[0].rank}'s")
                
                # Create new hand with same bet
                if self.config.verbose_logging:
                    print("\nDEBUG - Executing Split:")
                    print(f"Original hand: {[str(c) for c in hand.cards]}")

                new_hand = Hand(hand.bet)
                new_hand.is_split = True
                split_card = hand.cards.pop()
                new_hand.add_card(split_card)
                hand.is_split = True

                if self.config.verbose_logging:
                    print(f"After split - First hand: {[str(c) for c in hand.cards]}")
                    print(f"After split - Second hand: {[str(c) for c in new_hand.cards]}")

                # Deal one card to each split hand
                card = self.deck.deal()
                if card:
                    hand.add_card(card)
                    if self.config.verbose_logging:
                        print(f"First split hand received: {card}")
                        print(f"Complete first hand: {[str(c) for c in hand.cards]}")

                card = self.deck.deal()
                if card:
                    new_hand.add_card(card)
                    if self.config.verbose_logging:
                        print(f"Second split hand received: {card}")
                        print(f"Complete second hand: {[str(c) for c in new_hand.cards]}")
                
                if self.config.verbose_logging:
                    print(f"First split hand: {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                    print(f"Second split hand: {[str(c) for c in new_hand.cards]} (Value: {new_hand.best_value()})")

                hands_to_play.append(new_hand)

                # Handle split aces - allow resplitting and enforce one-card rule
                if split_card.rank == 'A':
                    if self.config.verbose_logging:
                        print("\nAces split detected - one card will be dealt to each split Ace")
                        print(f"First Ace: {hand.cards[0]}")
                        print(f"Second Ace: {new_hand.cards[0]}")
                    is_split_aces = True
                    # Mark both hands as split aces for one-card rule enforcement
                    hand.is_split_aces = True
                    new_hand.is_split_aces = True
                    
                    # Cards have already been dealt to split hands earlier in the code
                    # Just need to ensure no more cards are dealt
                    if len(hand.cards) > 1 and len(new_hand.cards) > 1:
                        break
                    
                continue
            
            # If no valid action was taken, default to standing
            else:
                if self.config.verbose_logging:
                    print(f"No valid action available, standing with {[str(c) for c in hand.cards]} (Value: {hand.best_value()})")
                break
            
            if hand.is_bust():
                if self.config.verbose_logging:
                    print(f"Player busts with {[str(c) for c in hand.cards]}")
                return HandResult(0, False, False, True, False, [], dealer_hand)
        return self._play_current_hand(hand, dealer_hand, is_split_aces)


    def _play_current_hand(self, hand: Hand, dealer_hand: Hand, is_split_aces: bool = False) -> HandResult:
        while True:
            # Split aces get only one card
            if is_split_aces and len(hand.cards) > 1:
                break

            action = self.strategy.get_action(hand, dealer_hand.cards[0])
            if self.config.verbose_logging:
                print(f"Player hand: {hand.best_value()}, Dealer card: {dealer_hand.cards[0].rank}, Action: {action}")

            if action == 'S':  # Stand
                break

            elif action == 'H':  # Hit
                # Hit - get another card
                while True:
                    card = self.deck.deal()
                    if card is None:
                        self.deck.reset()
                        continue
                    hand.add_card(card)
                    break
                if self.config.verbose_logging:
                    print(f"Player hits: {[str(c) for c in hand.cards]}")
                if hand.is_bust():
                    return HandResult(0, False, False, True, False, [], dealer_hand)

            elif action == 'D' and len(hand.cards) == 2 and not hand.is_split:  # Double
                hand.is_doubled = True
                hand.bet *= 2
                # Double down - get one more card and double bet
                while True:
                    card = self.deck.deal()
                    if card is None:
                        self.deck.reset()
                        continue
                    hand.add_card(card)
                    break
                break

            elif action == 'R' and self.config.allow_surrender and len(hand.cards) == 2:  # Surrender
                hand.is_surrender = True #Added this line
                return HandResult(0, False, True, False, False, [], dealer_hand)
        return HandResult(0, False, False, False, False, [], dealer_hand)


    def play_dealer_hand(self, hand: Hand):
        while True:
            value = hand.best_value()
            if value > 21:  # Dealer busts
                break
            if value > 17:  # Stand on anything above 17
                break
            if value == 17:  # On 17, check if dealer hits soft 17
                if not (self.config.dealer_hits_soft_17 and hand.is_soft()):
                    break
                if self.config.verbose_logging:
                    print(f"Dealer hits on soft 17: {[str(c) for c in hand.cards]}")

            # Deal next card
            while True:
                card = self.deck.deal()
                if card is None:
                    self.deck.reset()
                    continue
                hand.add_card(card)
                break
            
            if self.config.verbose_logging:
                print(f"Dealer draws: {card}")
                print(f"Dealer hand: {[str(c) for c in hand.cards]} (Value: {value})")
from card_manager import Card, Suit
from typing import List, Dict


class TestScenarios:

    @staticmethod
    def get_scenario(name: str) -> List[Card]:
        scenarios = {
            "split_8s": [
                Card('4', Suit.SPADES),  # 3-Dealer's draw card
                Card('T', Suit.SPADES),  # 3-Dealer's hole card
                Card('3', Suit.HEARTS),  # 3-Player's second card
                Card('6', Suit.DIAMONDS),  # 3-Dealer's up card
                Card('8',
                     Suit.CLUBS),  # 3-Player's first card (test no split dbl)
                Card('7', Suit.SPADES),  # 2-Dealer's bust card
                #Card('T', Suit.SPADES),  # 2-Player's dbl card (if alt strat)
                Card('T', Suit.SPADES),  # 2-Dealer's hole card
                Card('A', Suit.HEARTS),  # 2-Player's second card
                Card('6', Suit.DIAMONDS),  # 2-Dealer's up card
                Card('8', Suit.CLUBS),  # 2-Player's first card (test S19 dbl)
                Card('6', Suit.CLUBS),  # Dealer's bust card
                Card('T', Suit.SPADES),  # Second split hand double
                Card('T', Suit.HEARTS),  # First split hand double
                Card('3', Suit.DIAMONDS),  # Second split hand gets 3
                Card('3', Suit.CLUBS),  # First split hand gets 3
                Card('T', Suit.CLUBS),  # Dealer's hole card
                Card('8', Suit.SPADES),  # Player's second card
                Card('6', Suit.DIAMONDS),  # Dealer's up card
                Card('8', Suit.HEARTS),  # Player's first card
            ],
            "double_after_split": [
                Card('Q', Suit.HEARTS),  # Dealer's hole card
                Card('K',
                     Suit.DIAMONDS),  # Double down card for second split hand
                Card('K',
                     Suit.SPADES),  # Double down card for first split hand
                Card('J', Suit.CLUBS),  # Second split hand receives Jack
                Card('4', Suit.HEARTS),  # First split hand receives 4
                Card('T', Suit.CLUBS),  # Dealer's hole card
                Card('7', Suit.DIAMONDS),  # Player's second card
                Card('6', Suit.SPADES),  # Dealer's up card
                Card('7', Suit.HEARTS),  # Player's first card
            ],
            "soft_17": [
                Card('6', Suit.HEARTS),  # Hit card
                Card('6', Suit.HEARTS),  # Hit card
                Card('7', Suit.DIAMONDS),  # Player's second card
                Card('6', Suit.CLUBS),  # Dealer's hole card
                Card('3', Suit.SPADES),  # Player's second card  
                Card('A', Suit.SPADES),  # Dealer's up card
                Card('T', Suit.SPADES),  # Player's first card
            ],
            "soft19v6": [
                Card('Q', Suit.HEARTS),  # Dealer's hole card
                Card('4', Suit.HEARTS),  # Player hit/double card
                Card('T', Suit.CLUBS),  # Dealer's hole card
                Card('A', Suit.DIAMONDS),  # Player's second card
                Card('6', Suit.SPADES),  # Dealer's up card
                Card('8', Suit.HEARTS),  # Player's first card
            ],
            "split_aces": [
                Card('Q', Suit.HEARTS),  # Dealer's hit card
                Card('J', Suit.CLUBS),  # Second split hand receives Jack
                Card('4', Suit.HEARTS),  # First split hand receives 4
                Card('T', Suit.CLUBS),  # Dealer's hole card
                Card('A', Suit.DIAMONDS),  # Player's second card
                Card('6', Suit.SPADES),  # Dealer's up card
                Card('A', Suit.HEARTS),  # Player's first card
            ]
        }
        return scenarios.get(name, [])

#!/usr/bin/env python3
import argparse
import sys
from game_engine import BlackjackGame
from game_config import GameConfig
from statistics import Statistics  # Import from local statistics.py


def parse_args():
    parser = argparse.ArgumentParser(
        description='Blackjack Simulation Program')
    parser.add_argument(
        '--rule_set',
        type=str,
        default='vegas_strip',
        choices=['vegas_strip', 'downtown_vegas', 'single_deck', 'atlantic_city', 'european'],
        help='Predefined casino rule set')
    parser.add_argument('--num_decks',
                        type=int,
                        choices=range(1, 9),
                        help='Override: Number of decks (1-8)')
    parser.add_argument('--blackjack_payout',
                        type=str,
                        choices=['3:2', '6:5', '2:1'],
                        help='Override: Blackjack payout ratio')
    parser.add_argument('--starting_stake',
                        type=float,
                        default=1000,
                        help='Starting bankroll amount')
    parser.add_argument('--standard_bet',
                        type=float,
                        default=10,
                        help='Standard bet amount')
    parser.add_argument('--num_hands',
                        type=int,
                        default=1000,
                        help='Number of hands to simulate')
    parser.add_argument('--strategy_file',
                        type=str,
                        default='basic_strategy.csv',
                        help='Path to strategy CSV file')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Enable detailed per-hand logging')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Enable debug mode - verify each hand')
    parser.add_argument('--test_scenario',
                        type=str,
                        choices=['split_8s', 'soft_17', 'double_after_split', 'soft19v6', 'split_aces'],
                        help='Run a specific test scenario in debug mode')

    args = parser.parse_args()

    if args.test_scenario and not args.debug:
        print("Warning: Test scenarios require debug mode. Enabling debug mode.")
        args.debug = True

    # Handle blackjack payout if provided
    if args.blackjack_payout:
        try:
            num, den = map(int, args.blackjack_payout.split(':'))
            args.blackjack_payout = num / den
        except ValueError:
            print(f"Invalid blackjack payout format: {args.blackjack_payout}")
            sys.exit(1)

    return args


def main():
    args = parse_args()
    stats = Statistics()
    stats.initial_bankroll = args.starting_stake
    stats.current_bankroll = args.starting_stake
    stats.high_water_mark = args.starting_stake
    stats.low_water_mark = args.starting_stake

    # Create game config based on selected rule set
    if args.rule_set == 'vegas_strip':
        config = GameConfig.vegas_strip()
    elif args.rule_set == 'downtown_vegas':
        config = GameConfig.downtown_vegas()
    elif args.rule_set == 'single_deck':
        config = GameConfig.single_deck()
    elif args.rule_set == 'atlantic_city':
        config = GameConfig.atlantic_city()
    elif args.rule_set == 'european':
        config = GameConfig.european()
    else:
        config = GameConfig()

    # Override config with any explicitly provided arguments
    if args.num_decks is not None:
        config.num_decks = args.num_decks
    if args.blackjack_payout is not None:
        config.blackjack_payout = args.blackjack_payout
    if args.strategy_file:
        config.strategy_file = args.strategy_file
    config.verbose_logging = args.verbose
    config.test_scenario = args.test_scenario

    # Critical parameters are always enforced
    config.dealer_hits_soft_17 = True
    config.allow_surrender = True

    # Pass config to statistics and initialize game
    stats.config = config

    game = BlackjackGame(config)

    print(f"\nStarting simulation with {args.num_hands} hands...")
    print(f"Rule set: {args.rule_set}")
    print(f"Initial bankroll: ${stats.initial_bankroll:.2f}")
    print(f"Number of decks: {config.num_decks}")
    print(f"Blackjack pays: {config.blackjack_payout:.2f}:1")
    print(
        f"Dealer {'hits' if config.dealer_hits_soft_17 else 'stands'} on soft 17"
    )
    print(
        f"Late surrender {'allowed' if config.allow_surrender else 'not allowed'}\n"
    )

    while stats.hands_played < args.num_hands and stats.current_bankroll >= args.standard_bet:
        if args.debug:
            print("\n" + "="*80)
            print("Starting hand #{} with bet: ${:.2f}".format(stats.hands_played + 1, args.standard_bet))
            print("="*80)
            
        result = game.play_hand(args.standard_bet)
        stats.current_bankroll += result.net_profit
        stats.update(result, stats.current_bankroll)

        if args.debug:
            print("\nDebug Review - Hand Summary:")
            print("-"*40)
            print("Initial bet: ${:.2f}".format(args.standard_bet))
            
            # Show all hands with complete details
            for i, hand in enumerate(result.final_hands, 1):
                print(f"\nPlayer hand {i}:")
                print(f"  Initial Cards: {[str(c) for c in hand.cards]}")
                print(f"  Final value: {hand.best_value()}")
                print(f"  Was split: {hand.is_split}")
                print(f"  Was doubled: {hand.is_doubled}")
                if hand.is_doubled:
                    print(f"  Initial bet: ${hand.bet/2:.2f}")
                    print(f"  Final bet: ${hand.bet:.2f}")
                else:
                    print(f"  Bet: ${hand.bet:.2f}")
                    
            print(f"\nDealer hand: {[str(c) for c in result.dealer_hand.cards]}")
            print(f"Dealer value: {result.dealer_hand.best_value()}")
            print(f"Net result: {'Win' if result.net_profit > 0 else 'Loss' if result.net_profit < 0 else 'Push'}")
            print(f"Amount: ${abs(result.net_profit):.2f}")
            
            # Show special conditions
            print("\nHand conditions:")
            if result.is_blackjack:
                print("  - Blackjack!")
            if result.is_surrender:
                print("  - Hand was surrendered")
            if result.is_bust:
                print("  - Hand was busted")
            if any(h.is_split for h in result.final_hands):
                print("  - Hand was split")
            if any(h.is_doubled for h in result.final_hands):
                print("  - Hand was doubled")

            response = input("\nWas the gameplay correct for this hand? (y/n): ")
            if response.lower() not in ['y', 'yes']:
                print("\nDebug mode: Stopping for gameplay verification.")
                print("\nFinal state of the hand:")
                print(f"  Total hands played: {stats.hands_played}")
                print(f"  Current bankroll: ${stats.current_bankroll:.2f}")
                print(f"  Session high: ${stats.high_water_mark:.2f}")
                print(f"  Session low: ${stats.low_water_mark:.2f}")
                print("\nFinal Statistics:")
                stats.print_final_results()
                sys.exit(0)  # Exit with success status since this is expected behavior
            print("\nContinuing to next hand...")

        if stats.hands_played % 5 == 0:
            stats.print_progress(stats.hands_played)

    # Print split hand details for verification if we have a result
    if result and len(result.final_hands) > 1:
        print("\nSplit hand detected:")
        for i, hand in enumerate(result.final_hands):
            print(f"Split hand {i+1}: {[str(c) for c in hand.cards]}")

    stats.print_final_results()


if __name__ == "__main__":
    main()

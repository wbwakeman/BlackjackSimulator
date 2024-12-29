#!/usr/bin/env python3
import argparse
import sys
from game_engine import BlackjackGame
from game_config import GameConfig
from statistics import Statistics
from session_statistics import SessionStatistics

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
                       help='Number of hands to simulate per session')
    parser.add_argument('--num_sessions',
                       type=int,
                       default=1,
                       help='Number of sessions to simulate')
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


def run_single_session(config: GameConfig, args, session_stats: SessionStatistics) -> float:
    """
    Run a single session of blackjack and return the final bankroll.

    Args:
        config: Game configuration
        args: Command line arguments
        session_stats: Session statistics tracker

    Returns:
        float: Final bankroll amount
    """
    stats = Statistics()
    stats.initial_bankroll = args.starting_stake
    stats.current_bankroll = args.starting_stake
    stats.high_water_mark = args.starting_stake
    stats.low_water_mark = args.starting_stake
    stats.config = config

    game = BlackjackGame(config)

    while stats.hands_played < args.num_hands and stats.current_bankroll >= args.standard_bet:
        if args.debug:
            print("\n" + "="*80)
            print(f"Starting hand #{stats.hands_played + 1} with bet: ${args.standard_bet:.2f}")
            print("="*80)

        result = game.play_hand(args.standard_bet)
        stats.current_bankroll += result.net_profit
        stats.update(result, stats.current_bankroll)

        # Update session statistics for time-series analysis
        session_stats.update_hand(stats.current_bankroll)

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
                sys.exit(0)

        if stats.hands_played % 100 == 0 and args.verbose:
            stats.print_progress(stats.hands_played)

    if args.verbose:
        stats.print_final_results()

    return stats.current_bankroll


def main():
    args = parse_args()

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

    # Critical parameters are always enforced
    config.dealer_hits_soft_17 = True
    config.allow_surrender = True

    # Initialize multi-session statistics
    session_stats = SessionStatistics(
        initial_bankroll=args.starting_stake,
        num_sessions=args.num_sessions,
        num_hands_per_session=args.num_hands
    )

    print(f"\nStarting multi-session simulation...")
    print(f"Rule set: {args.rule_set}")
    print(f"Sessions: {args.num_sessions}")
    print(f"Hands per session: {args.num_hands}")
    print(f"Initial bankroll: ${args.starting_stake:.2f}")
    print(f"Standard bet: ${args.standard_bet:.2f}")
    print(f"Number of decks: {config.num_decks}")
    print(f"Blackjack pays: {config.blackjack_payout:.2f}:1")
    print(f"Dealer {'hits' if config.dealer_hits_soft_17 else 'stands'} on soft 17")
    print(f"Late surrender {'allowed' if config.allow_surrender else 'not allowed'}\n")

    # Run all sessions
    for session in range(args.num_sessions):
        if args.verbose:
            print(f"\nStarting Session {session + 1}/{args.num_sessions}")
            print("-" * 60)

        final_bankroll = run_single_session(config, args, session_stats)
        session_stats.update_session(final_bankroll)

        if args.verbose:
            print(f"\nSession {session + 1} complete. Final bankroll: ${final_bankroll:.2f}")

    # Print final multi-session statistics
    session_stats.print_results()


if __name__ == "__main__":
    main()
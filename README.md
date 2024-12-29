# Blackjack Simulation Program

A configurable blackjack simulation program implementing comprehensive split hand support and customizable game rules. The system features a robust game rules engine supporting multiple casino rule profiles including Vegas Strip, Downtown Vegas, Single Deck, Atlantic City, and European variants.

## Quick Start

Run the simulation with default Vegas Strip rules:
```bash
python blackjack_sim.py
```

## Command Line Options

### Basic Settings
- `--rule_set`: Choose casino rules (default: 'vegas_strip')
  - Options: 'vegas_strip', 'downtown_vegas', 'single_deck', 'atlantic_city', 'european'
- `--num_hands`: Number of hands to simulate (default: 1000)
- `--starting_stake`: Initial bankroll amount (default: $1000)
- `--standard_bet`: Bet amount per hand (default: $10)
- `--strategy_file`: Path to custom strategy CSV file (default: 'basic_strategy.csv')
- `--verbose`: Enable detailed per-hand logging (default: False)
- `--debug`: Enable debug mode - verify each hand gameplay (default: False)
  - Shows detailed information for each hand including:
    - Initial cards and bet amounts
    - Final hand values and dealer cards
    - Split and double down decisions
    - Special conditions (blackjack, surrender, bust)
  - Program pauses after each hand for verification
  - Enter 'yes' to continue to next hand
  - Enter 'no' to exit with final statistics and debugging information

### Rule Overrides
- `--num_decks`: Override number of decks (1-8)
- `--blackjack_payout`: Set blackjack payout ('3:2' or '6:5' or '2:1')

Note: dealer_hits_soft_17 and allow_surrender are always set to True for consistent gameplay.

## Predefined Rule Sets

### Vegas Strip Rules (Default)
- 6 decks
- Dealer hits on soft 17 (Rule Change)
- Late surrender allowed (Rule Change)
- 3:2 blackjack payout
- Can split up to 3 times
- Can resplit aces
- Double after split allowed

### Downtown Vegas Rules
- 2 decks
- Dealer hits on soft 17
- Late surrender allowed
- 3:2 blackjack payout
- Can split up to 3 times
- Can resplit aces
- Double after split allowed
- Verbose logging enabled

### Single Deck Rules
- 1 deck
- Dealer hits on soft 17
- No surrender
- 6:5 blackjack payout
- Can split up to 2 times
- Cannot resplit aces
- No double after split

### Atlantic City Rules
- 8 decks
- Dealer stands on all 17s
- Late surrender allowed
- 3:2 blackjack payout
- Can split up to 3 times
- Cannot resplit aces
- Double after split allowed

### European Rules
- 6 decks
- Dealer hits on soft 17
- No surrender
- 3:2 blackjack payout
- Can split up to 3 times
- Cannot resplit aces
- No double after split

## Custom Strategy Files

You can use a custom basic strategy by providing a CSV file with the `--strategy_file` option. The CSV format should be:

```csv
Hand,2,3,4,5,6,7,8,9,T,A
5,H,H,H,H,H,H,H,H,H,H
6,H,H,H,H,H,H,H,H,H,H
...
```

### Action Codes
- H: Hit
- S: Stand
- D: Double down (hit if not allowed)
- P: Split
- X: Surrender (hit if not allowed)
- B: Double if allowed, otherwise stand
- U: Surrender if allowed, otherwise stand
- Q: Surrender if allowed, otherwise split

## Example Commands

Run 100 hands with Downtown Vegas rules:
```bash
python blackjack_sim.py --num_hands 100 --rule_set downtown_vegas
```

Use a custom strategy with verbose logging:
```bash
python blackjack_sim.py --strategy_file my_strategy.csv --verbose
```

High stakes simulation:
```bash
python blackjack_sim.py --starting_stake 10000 --standard_bet 100
```

Debug mode with verbose logging:
```bash
python blackjack_sim.py --num_hands 10 --verbose --debug --rule_set vegas_strip
```

Custom rules configuration:
```bash
python blackjack_sim.py --num_decks 2 --dealer_hits_on_soft_17 --allow_surrender --blackjack_payout 3:2
```

# Blackjack Simulation Program

A sophisticated blackjack simulation program featuring configurable game rules, multiple casino rule profiles, and comprehensive multi-session analysis capabilities. The system provides detailed statistics, time-series metrics, and bankroll tracking across multiple simulation sessions.

## Features

- **Configurable Game Rules Engine**
  - Multiple casino rule profiles (Vegas Strip, Downtown Vegas, Single Deck, Atlantic City, European)
  - Customizable deck count, blackjack payouts, and splitting rules
  - Parameter validation and inheritance framework

- **Multi-Session Analysis**
  - Comprehensive session statistics tracking
  - Bankroll distribution analysis
  - Time-series progression metrics
  - CSV export functionality

- **Advanced Game Features**
  - Split hand management with double-after-split support
  - Strategy engine for split and double-down decisions
  - Debug logging system

## Installation

```bash
git clone [repository-url]
cd blackjack-simulator
pip install -r requirements.txt
```

## Usage

Basic usage with default Vegas Strip rules:
```bash
python blackjack_sim.py --num_sessions 5 --num_hands 100 --starting_stake 1000 --standard_bet 10
```

### Command Line Arguments

- `--rule_set`: Casino rule set (`vegas_strip`, `downtown_vegas`, `single_deck`, `atlantic_city`, `european`)
- `--num_sessions`: Number of sessions to simulate (default: 1)
- `--num_hands`: Number of hands per session (default: 1000)
- `--starting_stake`: Initial bankroll amount (default: 1000)
- `--standard_bet`: Standard bet amount (default: 10)
- `--verbose`: Enable detailed hand-by-hand logging
- `--debug`: Enable debug mode with hand verification
- `--strategy_file`: Path to strategy CSV file (default: basic_strategy.csv)

### Rule Set Profiles

1. **Vegas Strip** (Default)
   - 6 decks
   - Dealer hits soft 17
   - Late surrender allowed
   - 3:2 blackjack payout
   - Double after split allowed
   - Up to 3 splits permitted

2. **Downtown Vegas**
   - 2 decks
   - Same core rules as Strip
   - More favorable deck penetration

3. **Single Deck**
   - 1 deck
   - 6:5 blackjack payout
   - Limited splitting options
   - No double after split

4. **Atlantic City**
   - 8 decks
   - Standard 3:2 payout
   - No resplit of aces

5. **European**
   - 6 decks
   - No surrender
   - Limited doubling options

## Analysis Features

### Time-Series Analysis
The program tracks and analyzes various metrics across sessions:

1. **Bankroll Progression**
   - Maximum drawdown percentage
   - Win/loss streaks
   - Bankroll volatility

2. **Session Performance**
   - Bankruptcy and doubling rates
   - Distribution of final bankrolls
   - High/low watermarks

### Sample Output

```
Multi-Session Simulation Results
============================================================
Total Sessions: 5
Initial Bankroll: $1,000.00
Hands per Session: 100

Session Outcomes:
  Bankruptcy Rate: 0.0% (0 sessions)
  Doubling Rate:   0.0% (0 sessions)

Final Bankroll Distribution:
  $800-$1,200:   5 sessions (100.0%)

Time-Series Analysis:
  Maximum Drawdown:     14.4%
  Longest Win Streak:   9 hands
  Longest Loss Streak:  6 hands
  Average Win Streak:   1.6 hands
  Average Loss Streak:  1.8 hands
  Bankroll Volatility:  0.9%

Summary Statistics:
  Average Final Bankroll: $1,041.00
  Best Session Result:    $1,165.00
  Worst Session Result:   $865.00
```

### Data Export
Session data is automatically exported to CSV files for external analysis, including:
- Hand-by-hand bankroll progression
- Session outcomes
- Time-series metrics

## Debug Mode
Enable debug mode to verify correct gameplay:
```bash
python blackjack_sim.py --debug --test_scenario split_8s
```

Available test scenarios:
- `split_8s`: Tests pair splitting
- `soft_17`: Tests dealer soft 17 behavior
- `double_after_split`: Tests doubling after split
- `soft19v6`: Tests soft total strategy
- `split_aces`: Tests ace splitting rules

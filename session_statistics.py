#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List, Dict
import csv
from datetime import datetime

@dataclass
class SessionStatistics:
    """
    Tracks statistics across multiple blackjack sessions.
    Analyzes patterns in bankroll outcomes and session results.
    """
    initial_bankroll: float
    num_sessions: int
    num_hands_per_session: int

    # Session outcome counters
    bankrupt_sessions: int = 0  # Sessions ending at $0
    doubled_sessions: int = 0   # Sessions where bankroll doubled
    completed_sessions: int = 0  # Total completed sessions

    # Bankroll distribution tracking
    bankroll_bins: Dict[str, int] = field(default_factory=dict)
    session_results: List[float] = field(default_factory=list)

    # Time series tracking
    current_session_history: List[float] = field(default_factory=list)
    all_session_histories: List[List[float]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize bankroll bins based on initial bankroll"""
        bin_size = self.initial_bankroll * 0.4  # Create bins of 40% of initial bankroll
        max_bin = self.initial_bankroll * 3     # Track up to 300% of initial bankroll

        current = 0
        while current < max_bin:
            next_level = min(current + bin_size, max_bin)
            bin_label = f"${current:,.0f}-${next_level:,.0f}"
            self.bankroll_bins[bin_label] = 0
            current = next_level

        # Add final bin for anything above max_bin
        self.bankroll_bins[f">${max_bin:,.0f}"] = 0

    def update_session(self, final_bankroll: float) -> None:
        """
        Update statistics based on a completed session's final bankroll.

        Args:
            final_bankroll: The final bankroll at session end
        """
        self.completed_sessions += 1
        self.session_results.append(final_bankroll)

        # Store the completed session history and reset for next session
        if self.current_session_history:
            self.all_session_histories.append(self.current_session_history)
            self.current_session_history = []

        # Track bankruptcy and doubling
        if final_bankroll <= 0:
            self.bankrupt_sessions += 1
        elif final_bankroll >= (self.initial_bankroll * 2):
            self.doubled_sessions += 1

        # Update bankroll distribution bins
        for bin_range, _ in self.bankroll_bins.items():
            if bin_range.startswith('>'): # Handle the overflow bin
                threshold = float(bin_range[1:].replace('$', '').replace(',', ''))
                if final_bankroll > threshold:
                    self.bankroll_bins[bin_range] += 1
                    break
            else:
                # Extract range values
                low, high = map(lambda x: float(x.replace('$', '').replace(',', '')), 
                              bin_range.split('-'))
                if low <= final_bankroll <= high:
                    self.bankroll_bins[bin_range] += 1
                    break

    def update_hand(self, current_bankroll: float) -> None:
        """
        Track bankroll after each hand for time series analysis.

        Args:
            current_bankroll: The current bankroll after the hand
        """
        self.current_session_history.append(current_bankroll)

    def analyze_time_series(self) -> Dict[str, float]:
        """
        Analyze time-series data for performance metrics.

        Returns:
            Dictionary containing calculated metrics
        """
        metrics = {
            'max_drawdown': 0.0,
            'longest_win_streak': 0,
            'longest_loss_streak': 0,
            'avg_win_streak': 0.0,
            'avg_loss_streak': 0.0,
            'volatility': 0.0
        }

        if not self.all_session_histories:
            return metrics

        # Calculate metrics across all sessions
        for history in self.all_session_histories:
            if not history:
                continue

            # Calculate drawdown
            peak = history[0]
            current_drawdown = 0.0
            for value in history:
                if value > peak:
                    peak = value
                current_drawdown = (peak - value) / peak * 100
                metrics['max_drawdown'] = max(metrics['max_drawdown'], current_drawdown)

            # Calculate streaks
            current_streak = 0
            current_sign = 0
            win_streaks = []
            loss_streaks = []

            for i in range(1, len(history)):
                diff = history[i] - history[i-1]
                if diff > 0:  # Win
                    if current_sign <= 0:  # New streak
                        if current_sign < 0:
                            loss_streaks.append(-current_streak)
                        current_streak = 1
                        current_sign = 1
                    else:
                        current_streak += 1
                elif diff < 0:  # Loss
                    if current_sign >= 0:  # New streak
                        if current_sign > 0:
                            win_streaks.append(current_streak)
                        current_streak = 1
                        current_sign = -1
                    else:
                        current_streak += 1

            # Add final streak
            if current_sign > 0:
                win_streaks.append(current_streak)
            elif current_sign < 0:
                loss_streaks.append(-current_streak)

            # Update streak metrics
            if win_streaks:
                metrics['longest_win_streak'] = max(metrics['longest_win_streak'], max(win_streaks))
                metrics['avg_win_streak'] = sum(win_streaks) / len(win_streaks)
            if loss_streaks:
                metrics['longest_loss_streak'] = max(metrics['longest_loss_streak'], -min(loss_streaks))
                metrics['avg_loss_streak'] = sum(abs(x) for x in loss_streaks) / len(loss_streaks)

            # Calculate volatility (standard deviation of returns)
            returns = [(history[i] - history[i-1]) / history[i-1] * 100 for i in range(1, len(history))]
            if returns:
                metrics['volatility'] = sum(abs(r) for r in returns) / len(returns)  # Average absolute return

        return metrics

    def export_session_data(self, filename: str = None) -> None:
        """
        Export session data to CSV file for external analysis.

        Args:
            filename: Optional custom filename, defaults to timestamp-based name
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blackjack_session_data_{timestamp}.csv"

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Session', 'Hand', 'Bankroll'])

            # Write data for each session
            for session_idx, history in enumerate(self.all_session_histories, 1):
                for hand_idx, bankroll in enumerate(history, 1):
                    writer.writerow([session_idx, hand_idx, f"{bankroll:.2f}"])

    def print_results(self) -> None:
        """Print comprehensive statistics across all sessions."""
        print("\nMulti-Session Simulation Results")
        print("=" * 60)

        # Basic session statistics
        print(f"Total Sessions: {self.completed_sessions}")
        print(f"Initial Bankroll: ${self.initial_bankroll:,.2f}")
        print(f"Hands per Session: {self.num_hands_per_session}")

        # Bankruptcy and doubling rates
        print("\nSession Outcomes:")
        bankruptcy_rate = (self.bankrupt_sessions / self.completed_sessions * 100)
        doubling_rate = (self.doubled_sessions / self.completed_sessions * 100)
        print(f"  Bankruptcy Rate: {bankruptcy_rate:.1f}% ({self.bankrupt_sessions} sessions)")
        print(f"  Doubling Rate:   {doubling_rate:.1f}% ({self.doubled_sessions} sessions)")

        # Distribution of final bankrolls
        print("\nFinal Bankroll Distribution:")
        for bin_range, count in self.bankroll_bins.items():
            percentage = (count / self.completed_sessions * 100)
            print(f"  {bin_range}: {count:3d} sessions ({percentage:.1f}%)")

        # Time-series analysis
        metrics = self.analyze_time_series()
        print("\nTime-Series Analysis:")
        print(f"  Maximum Drawdown:     {metrics['max_drawdown']:.1f}%")
        print(f"  Longest Win Streak:   {metrics['longest_win_streak']} hands")
        print(f"  Longest Loss Streak:  {metrics['longest_loss_streak']} hands")
        print(f"  Average Win Streak:   {metrics['avg_win_streak']:.1f} hands")
        print(f"  Average Loss Streak:  {metrics['avg_loss_streak']:.1f} hands")
        print(f"  Bankroll Volatility:  {metrics['volatility']:.1f}%")

        # Summary statistics
        if self.session_results:
            avg_final = sum(self.session_results) / len(self.session_results)
            print("\nSummary Statistics:")
            print(f"  Average Final Bankroll: ${avg_final:,.2f}")
            print(f"  Best Session Result:    ${max(self.session_results):,.2f}")
            print(f"  Worst Session Result:   ${min(self.session_results):,.2f}")

        # Export session data
        self.export_session_data()
        print("\nSession data exported to CSV file.")
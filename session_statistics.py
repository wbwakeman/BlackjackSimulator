#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import csv
from datetime import datetime
import os
import statistics as stats_lib  # Rename import to avoid conflict
try:
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

@dataclass
class SessionStatistics:
    """
    Tracks statistics across multiple blackjack sessions.
    Analyzes patterns in bankroll outcomes and session results.
    """
    initial_bankroll: float
    num_sessions: int
    num_hands_per_session: int
    quad_bins_threshold: Optional[float] = None  # New parameter for quad-bins feature

    # Session outcome counters
    bankrupt_sessions: int = 0
    doubled_sessions: int = 0
    completed_sessions: int = 0

    # Bankroll distribution tracking
    bankroll_bins: Dict[str, int] = field(default_factory=dict)
    session_results: List[float] = field(default_factory=list)
    quad_bins: Dict[str, List[float]] = field(default_factory=lambda: {
        'below_threshold': [],
        'below_initial': [],
        'above_initial': [],
        'above_threshold': []
    })

    # Time series tracking
    current_session_history: List[float] = field(default_factory=list)
    all_session_histories: List[List[float]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize bankroll bins based on initial bankroll"""
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)

        if self.quad_bins_threshold is not None:
            if not 0.0 <= self.quad_bins_threshold <= 1.0:
                raise ValueError("quad_bins_threshold must be between 0.0 and 1.0")
            return  # Skip regular bin creation when using quad bins

        # Create regular bins with initial bankroll as the central boundary
        bin_size = self.initial_bankroll * 0.2  # Create bins of 20% of initial bankroll
        lowest_bin = 0
        highest_bin = self.initial_bankroll * 2  # Track up to 200% of initial bankroll

        # Start with bins below initial bankroll
        current = lowest_bin
        while current < self.initial_bankroll:
            next_level = min(current + bin_size, self.initial_bankroll)
            bin_label = f"${current:,.0f}-${next_level:,.0f}"
            self.bankroll_bins[bin_label] = 0
            current = next_level

        # Add bins above initial bankroll
        current = self.initial_bankroll
        while current < highest_bin:
            next_level = min(current + bin_size, highest_bin)
            bin_label = f"${current:,.0f}-${next_level:,.0f}"
            self.bankroll_bins[bin_label] = 0
            current = next_level

        # Add final bin for anything above highest_bin
        self.bankroll_bins[f">${highest_bin:,.0f}"] = 0

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

        if self.quad_bins_threshold is not None:
            # Update quad bins
            threshold = self.quad_bins_threshold
            lower_threshold = self.initial_bankroll * (1 - threshold)
            upper_threshold = self.initial_bankroll * (1 + threshold)

            if final_bankroll < lower_threshold:
                self.quad_bins['below_threshold'].append(final_bankroll)
            elif final_bankroll < self.initial_bankroll:
                self.quad_bins['below_initial'].append(final_bankroll)
            elif final_bankroll <= upper_threshold:
                self.quad_bins['above_initial'].append(final_bankroll)
            else:
                self.quad_bins['above_threshold'].append(final_bankroll)
        else:
            # Update regular bankroll distribution bins
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

    def _generate_ascii_histogram(self, bin_data: Dict[str, int], max_width: int = 40) -> str:
        """Generate ASCII histogram visualization"""
        if not bin_data:
            return "No data available for histogram"

        max_count = max(bin_data.values())
        scale = max_width / (max_count if max_count > 0 else 1)

        # Calculate the maximum label length for alignment
        max_label_len = max(len(label) for label in bin_data.keys())

        histogram = []
        for label, count in bin_data.items():
            bar_width = int(count * scale)
            bar = '█' * bar_width
            # Pad the label to align all bars
            padded_label = f"{label:<{max_label_len}}"
            histogram.append(f"{padded_label} | {bar} ({count:2d} sessions)")

        return '\n'.join(histogram)

    def _calculate_quad_bins_stats(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistical metrics for quad bins"""
        stats_data = {}

        for bin_name, values in self.quad_bins.items():
            if values:
                mean_value = sum(values) / len(values)
                # Calculate standard deviation manually if needed
                if len(values) > 1:
                    variance = sum((x - mean_value) ** 2 for x in values) / (len(values) - 1)
                    std_dev = variance ** 0.5
                else:
                    std_dev = 0.0

                stats_data[bin_name] = {
                    'count': len(values),
                    'mean': mean_value,
                    'std': std_dev,
                    'percentage': (len(values) / self.completed_sessions * 100)
                }
            else:
                stats_data[bin_name] = {
                    'count': 0,
                    'mean': 0.0,
                    'std': 0.0,
                    'percentage': 0.0
                }

        return stats_data

    def _perform_statistical_tests(self) -> Dict[str, Optional[float]]:
        """Perform statistical significance tests between bins"""
        test_results = {}
        if not SCIPY_AVAILABLE:
            return {}

        bin_pairs = [
            ('below_threshold', 'below_initial'),
            ('below_initial', 'above_initial'),
            ('above_initial', 'above_threshold')
        ]

        for bin1, bin2 in bin_pairs:
            values1 = self.quad_bins[bin1]
            values2 = self.quad_bins[bin2]

            if len(values1) > 0 and len(values2) > 0:
                try:
                    statistic, pvalue = scipy_stats.mannwhitneyu(
                        values1, values2, alternative='two-sided'
                    )
                    test_results[f'{bin1}_vs_{bin2}'] = pvalue
                except ValueError:
                    test_results[f'{bin1}_vs_{bin2}'] = None
            else:
                test_results[f'{bin1}_vs_{bin2}'] = None

        return test_results

    def print_quad_bins_analysis(self) -> None:
        """Print quad-bins analysis with ASCII visualization"""
        if self.quad_bins_threshold is None:
            return

        threshold = self.quad_bins_threshold
        lower_threshold = self.initial_bankroll * (1 - threshold)
        upper_threshold = self.initial_bankroll * (1 + threshold)

        print(f"\nQuad-Bins Analysis (threshold: {threshold*100:.1f}%)")
        print("=" * 60)

        # Calculate statistics
        stats = self._calculate_quad_bins_stats()

        # Prepare histogram data with clear bankroll ranges
        hist_data = {
            f"< ${lower_threshold:,.2f}":
                len(self.quad_bins['below_threshold']),
            f"${lower_threshold:,.2f} - ${self.initial_bankroll:,.2f}":
                len(self.quad_bins['below_initial']),
            f"${self.initial_bankroll:,.2f} - ${upper_threshold:,.2f}":
                len(self.quad_bins['above_initial']),
            f"> ${upper_threshold:,.2f}":
                len(self.quad_bins['above_threshold'])
        }

        # Print distribution header
        print("\nBankroll Distribution:")
        print("-" * 60)
        print(self._generate_ascii_histogram(hist_data))

        # Print detailed statistics for each bin
        print("\nDetailed Statistics:")
        print("-" * 60)
        bin_labels = {
            'below_threshold': 'Significant Loss',
            'below_initial': 'Moderate Loss',
            'above_initial': 'Moderate Gain',
            'above_threshold': 'Significant Gain'
        }

        for bin_name, stats_data in stats.items():
            print(f"\n{bin_labels[bin_name]}:")
            print(f"  Count:     {stats_data['count']:3d} sessions ({stats_data['percentage']:5.1f}%)")
            if stats_data['count'] > 0:
                print(f"  Mean:      ${stats_data['mean']:,.2f}")
                print(f"  Std Dev:   ${stats_data['std']:,.2f}")

        # Print statistical significance tests if scipy is available
        if SCIPY_AVAILABLE:
            test_results = self._perform_statistical_tests()
            if test_results:
                print("\nStatistical Significance Tests:")
                print("-" * 60)
                for test_name, p_value in test_results.items():
                    if p_value is not None:
                        bin1, bin2 = test_name.split('_vs_')
                        print(f"  {bin_labels[bin1]} vs {bin_labels[bin2]}:")
                        print(f"    p-value: {p_value:.4f}")
                        print(f"    {'✓ Significant' if p_value < 0.05 else '✗ Not significant'} at α=0.05")
        else:
            print("\nNote: Statistical significance tests unavailable (scipy not installed)")

    def print_results(self) -> None:
        """Print comprehensive statistics across all sessions."""
        print("\nMulti-Session Simulation Results")
        print("=" * 60)

        # Basic session statistics
        print(f"Total Sessions: {self.completed_sessions}")
        print(f"Initial Bankroll: ${self.initial_bankroll:,.2f}")
        print(f"Hands per Session: {self.num_hands_per_session}")

        # Performance relative to initial bankroll
        sessions_above_initial = sum(1 for result in self.session_results if result > self.initial_bankroll)
        sessions_below_initial = sum(1 for result in self.session_results if result < self.initial_bankroll)
        print("\nPerformance vs Initial Bankroll:")
        print(f"  Sessions Above Initial: {sessions_above_initial} ({sessions_above_initial/self.completed_sessions*100:.1f}%)")
        print(f"  Sessions Below Initial: {sessions_below_initial} ({sessions_below_initial/self.completed_sessions*100:.1f}%)")

        # Bankruptcy and doubling rates
        print("\nSession Outcomes:")
        bankruptcy_rate = (self.bankrupt_sessions / self.completed_sessions * 100)
        doubling_rate = (self.doubled_sessions / self.completed_sessions * 100)
        print(f"  Bankruptcy Rate: {bankruptcy_rate:.1f}% ({self.bankrupt_sessions} sessions)")
        print(f"  Doubling Rate:   {doubling_rate:.1f}% ({self.doubled_sessions} sessions)")

        # Print quad-bins analysis if enabled
        if self.quad_bins_threshold is not None:
            self.print_quad_bins_analysis()
        else:
            # Distribution of final bankrolls (original format)
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

        for history in self.all_session_histories:
            if not history:
                continue

            # Calculate drawdown
            peak = history[0]
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
                    if current_sign <= 0:
                        if current_sign < 0:
                            loss_streaks.append(-current_streak)
                        current_streak = 1
                        current_sign = 1
                    else:
                        current_streak += 1
                elif diff < 0:  # Loss
                    if current_sign >= 0:
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

            # Calculate volatility (standard deviation of percentage returns)
            if len(history) > 1:
                returns = [(history[i] - history[i-1]) / history[i-1] * 100 for i in range(1, len(history))]
                if len(returns) > 1:
                    mean_return = sum(returns) / len(returns)
                    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
                    metrics['volatility'] = variance ** 0.5

        return metrics

    def export_session_data(self) -> None:
        """
        Export session data to CSV files for external analysis.
        Creates two CSV files in the logs directory:
        1. Session-level summary with aggregate statistics
        2. Hand-by-hand progression of bankroll
        """
        try:
            # Generate timestamp-based prefix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"blackjack_session_data_{timestamp}"

            # Ensure logs directory exists
            os.makedirs('logs', exist_ok=True)

            # Export detailed hand-by-hand data
            hands_file = os.path.join('logs', f"{prefix}_hands.csv")
            with open(hands_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Session', 'Hand', 'Bankroll', 'Change'])

                for session_idx, history in enumerate(self.all_session_histories, 1):
                    prev_bankroll = self.initial_bankroll
                    for hand_idx, bankroll in enumerate(history, 1):
                        change = bankroll - prev_bankroll
                        writer.writerow([
                            session_idx,
                            hand_idx,
                            f"{bankroll:.2f}",
                            f"{change:+.2f}"
                        ])
                        prev_bankroll = bankroll

            # Export session summary data
            summary_file = os.path.join('logs', f"{prefix}_summary.csv")
            with open(summary_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'Session',
                    'Final Bankroll',
                    'Net Profit/Loss',
                    'Peak Bankroll',
                    'Maximum Drawdown',
                    'Win Streak',
                    'Loss Streak'
                ])

                for session_idx, history in enumerate(self.all_session_histories, 1):
                    if history:
                        final_bankroll = history[-1]
                        net_change = final_bankroll - self.initial_bankroll
                        peak = max(history)

                        # Calculate max drawdown for this session
                        max_drawdown = 0
                        peak_so_far = history[0]
                        for value in history:
                            if value > peak_so_far:
                                peak_so_far = value
                            drawdown = (peak_so_far - value) / peak_so_far * 100
                            max_drawdown = max(max_drawdown, drawdown)

                        # Calculate streaks
                        current_streak = 0
                        max_win_streak = 0
                        max_loss_streak = 0
                        for i in range(1, len(history)):
                            if history[i] > history[i - 1]:  # Win
                                if current_streak > 0:
                                    current_streak += 1
                                else:
                                    current_streak = 1
                                max_win_streak = max(max_win_streak, current_streak)
                            elif history[i] < history[i - 1]:  # Loss
                                if current_streak < 0:
                                    current_streak -= 1
                                else:
                                    current_streak = -1
                                max_loss_streak = max(max_loss_streak, -current_streak)

                        writer.writerow([
                            session_idx,
                            f"{final_bankroll:.2f}",
                            f"{net_change:+.2f}",
                            f"{peak:.2f}",
                            f"{max_drawdown:.1f}%",
                            max_win_streak,
                            max_loss_streak
                        ])

            print(f"\nSession data exported to:")
            print(f"  Hand details: {hands_file}")
            print(f"  Session summary: {summary_file}")

        except IOError as e:
            print(f"\nError exporting session data: {str(e)}")
            return
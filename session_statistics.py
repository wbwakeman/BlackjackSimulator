#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List, Dict

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

        # Track bankruptcy and doubling
        if final_bankroll <= 0:
            self.bankrupt_sessions += 1
        elif final_bankroll >= (self.initial_bankroll * 2):
            self.doubled_sessions += 1

        # Update bankroll distribution bins
        for bin_range, _ in self.bankroll_bins.items():
            if bin_range.startswith('>'):  # Handle the overflow bin
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

        # Summary statistics
        if self.session_results:
            avg_final = sum(self.session_results) / len(self.session_results)
            print("\nSummary Statistics:")
            print(f"  Average Final Bankroll: ${avg_final:,.2f}")
            print(f"  Best Session Result:    ${max(self.session_results):,.2f}")
            print(f"  Worst Session Result:   ${min(self.session_results):,.2f}")
#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List, Dict
import matplotlib.pyplot as plt

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

    def plot_bankroll_distribution(self) -> None:
        """Create a visual representation of the bankroll distribution."""
        # Set figure style and size
        plt.figure(figsize=(12, 6))
        plt.style.use('default')  # Use default style instead of seaborn

        # Extract bin ranges and counts
        bins = list(self.bankroll_bins.keys())
        counts = list(self.bankroll_bins.values())

        # Create bar plot with enhanced styling
        bars = plt.bar(range(len(bins)), counts, 
                      color='lightblue', edgecolor='navy', alpha=0.7)
        plt.xticks(range(len(bins)), bins, rotation=45, ha='right')

        # Add custom title and labels with enhanced styling
        plt.title('Blackjack Session Results: Bankroll Distribution', 
                 fontsize=14, pad=20, weight='bold')
        plt.xlabel('Final Bankroll Range', fontsize=12, labelpad=10)
        plt.ylabel('Number of Sessions', fontsize=12, labelpad=10)

        # Add count labels on top of bars with improved positioning
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)

        # Add reference line for initial bankroll
        plt.axvline(x=len(bins)/3, color='red', linestyle='--', alpha=0.5,
                   label=f'Initial Bankroll (${self.initial_bankroll:,.0f})')

        # Add grid for better readability
        plt.grid(True, axis='y', linestyle='--', alpha=0.3)
        plt.legend()

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig('bankroll_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_bankroll_histogram(self) -> None:
        """Create a histogram of final bankrolls with enhanced visualization."""
        plt.figure(figsize=(12, 6))
        plt.style.use('default')  # Use default style instead of seaborn

        # Create histogram with enhanced styling
        n, bins, patches = plt.hist(self.session_results, bins=20, 
                                  color='lightgreen', edgecolor='darkgreen', 
                                  alpha=0.7, density=True)

        # Add mean and median lines
        mean_bankroll = sum(self.session_results) / len(self.session_results)
        median_bankroll = sorted(self.session_results)[len(self.session_results)//2]

        plt.axvline(mean_bankroll, color='red', linestyle='--', 
                   label=f'Mean (${mean_bankroll:,.2f})', linewidth=2)
        plt.axvline(median_bankroll, color='blue', linestyle='--',
                   label=f'Median (${median_bankroll:,.2f})', linewidth=2)
        plt.axvline(self.initial_bankroll, color='green', linestyle='--',
                   label=f'Initial (${self.initial_bankroll:,.2f})', linewidth=2)

        # Enhanced title and labels
        plt.title('Distribution of Final Bankrolls Across Sessions',
                 fontsize=14, pad=20, weight='bold')
        plt.xlabel('Final Bankroll ($)', fontsize=12, labelpad=10)
        plt.ylabel('Density', fontsize=12, labelpad=10)

        # Add grid and legend with improved styling
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend(fontsize=10, loc='upper right')

        # Adjust layout and save with high resolution
        plt.tight_layout()
        plt.savefig('bankroll_histogram.png', dpi=300, bbox_inches='tight')
        plt.close()

    def print_results(self) -> None:
        """Print comprehensive statistics across all sessions and generate visualizations."""
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

        # Generate visualizations
        self.plot_bankroll_distribution()
        self.plot_bankroll_histogram()
        print("\nVisualization files generated:")
        print("  - bankroll_distribution.png")
        print("  - bankroll_histogram.png")
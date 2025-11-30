#!/usr/bin/env python3
"""
Script to visualize epipolar loss results from JSON file.
Creates scientific statistical plots with mean, max, min, and variation metrics.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse


def load_results(json_path):
    """Load evaluation results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def extract_statistics(results):
    """
    Extract statistical metrics for each category.

    Args:
        results: Dictionary with evaluation results

    Returns:
        Dictionary mapping category names to statistics
    """
    stats_by_category = {}

    for category, category_results in results['categories'].items():
        # Extract valid epipolar errors
        errors = []
        for result in category_results:
            if result.get('score') is not None and result['score'] >= 0:
                error = result['metrics'].get('mean_epipolar_error')
                if error is not None and not np.isinf(error):
                    errors.append(error)

        if errors:
            stats = {
                'mean': np.mean(errors),
                'std': np.std(errors),
                'min': np.min(errors),
                'max': np.max(errors),
                'median': np.median(errors),
                'q25': np.percentile(errors, 25),
                'q75': np.percentile(errors, 75),
                'count': len(errors),
                'raw_data': errors
            }
        else:
            stats = {
                'mean': None,
                'std': None,
                'min': None,
                'max': None,
                'median': None,
                'q25': None,
                'q75': None,
                'count': 0,
                'raw_data': []
            }

        stats_by_category[category] = stats

    return stats_by_category


def create_visualizations(stats_by_category, output_dir='plots'):
    """
    Create comprehensive statistical visualizations.

    Args:
        stats_by_category: Dictionary with statistics for each category
        output_dir: Directory to save plots
    """
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Set style for scientific plots
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10

    categories = list(stats_by_category.keys())
    categories_with_data = [cat for cat in categories if stats_by_category[cat]['count'] > 0]

    if not categories_with_data:
        print("No valid data to visualize!")
        return

    # Color palette
    colors = sns.color_palette("Set2", len(categories_with_data))

    # Create a comprehensive figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. Bar plot with error bars (mean ± std)
    ax1 = fig.add_subplot(gs[0, :2])
    means = [stats_by_category[cat]['mean'] for cat in categories_with_data]
    stds = [stats_by_category[cat]['std'] for cat in categories_with_data]
    x_pos = np.arange(len(categories_with_data))

    bars = ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color=colors, edgecolor='black')
    ax1.set_xlabel('Category')
    ax1.set_ylabel('Mean Epipolar Error')
    ax1.set_title('Mean Epipolar Error by Category (with Standard Deviation)')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(categories_with_data, rotation=0)
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + std,
                f'{mean:.3f}',
                ha='center', va='bottom', fontsize=9)

    # 2. Box plot
    ax2 = fig.add_subplot(gs[0, 2])
    box_data = [stats_by_category[cat]['raw_data'] for cat in categories_with_data]
    bp = ax2.boxplot(box_data, labels=categories_with_data, patch_artist=True,
                     showmeans=True, meanline=True)

    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax2.set_ylabel('Epipolar Error')
    ax2.set_title('Distribution (Box Plot)')
    ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=0)

    # 3. Violin plot
    ax3 = fig.add_subplot(gs[1, :2])
    positions = np.arange(len(categories_with_data))
    parts = ax3.violinplot(box_data, positions=positions, showmeans=True, showmedians=True)

    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)

    ax3.set_xlabel('Category')
    ax3.set_ylabel('Epipolar Error')
    ax3.set_title('Error Distribution (Violin Plot)')
    ax3.set_xticks(positions)
    ax3.set_xticklabels(categories_with_data)
    ax3.grid(axis='y', alpha=0.3)

    # 4. Min/Max range visualization
    ax4 = fig.add_subplot(gs[1, 2])
    for i, cat in enumerate(categories_with_data):
        min_val = stats_by_category[cat]['min']
        max_val = stats_by_category[cat]['max']
        mean_val = stats_by_category[cat]['mean']

        # Plot range
        ax4.plot([i, i], [min_val, max_val], 'o-', linewidth=2, markersize=8,
                color=colors[i], alpha=0.7, label=cat)
        # Plot mean
        ax4.plot(i, mean_val, 's', markersize=10, color=colors[i],
                markeredgecolor='black', markeredgewidth=1.5)

    ax4.set_xlabel('Category')
    ax4.set_ylabel('Epipolar Error')
    ax4.set_title('Min/Max Range with Mean')
    ax4.set_xticks(np.arange(len(categories_with_data)))
    ax4.set_xticklabels(categories_with_data)
    ax4.grid(axis='y', alpha=0.3)
    ax4.legend(loc='upper right', fontsize=8)

    # 5. Statistical summary table
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')

    # Prepare table data
    table_data = []
    headers = ['Category', 'Count', 'Mean', 'Std', 'Min', 'Q25', 'Median', 'Q75', 'Max']

    for cat in categories_with_data:
        stats = stats_by_category[cat]
        row = [
            cat,
            f"{stats['count']}",
            f"{stats['mean']:.4f}",
            f"{stats['std']:.4f}",
            f"{stats['min']:.4f}",
            f"{stats['q25']:.4f}",
            f"{stats['median']:.4f}",
            f"{stats['q75']:.4f}",
            f"{stats['max']:.4f}"
        ]
        table_data.append(row)

    # Create table
    table = ax5.table(cellText=table_data, colLabels=headers,
                     cellLoc='center', loc='center',
                     colColours=['lightgray']*len(headers))
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Color code rows
    for i, color in enumerate(colors):
        for j in range(len(headers)):
            table[(i+1, j)].set_facecolor((*color, 0.3))

    ax5.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)

    # Save the comprehensive figure
    plt.savefig(f'{output_dir}/epipolar_comprehensive_analysis.png',
                bbox_inches='tight', dpi=300)
    print(f"Saved comprehensive analysis to {output_dir}/epipolar_comprehensive_analysis.png")

    # Create individual plots for better clarity

    # Individual plot 1: Bar chart with error bars
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color=colors, edgecolor='black')
    ax.set_xlabel('Category', fontsize=12)
    ax.set_ylabel('Mean Epipolar Error', fontsize=12)
    ax.set_title('Mean Epipolar Error by Category', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories_with_data, rotation=0)
    ax.grid(axis='y', alpha=0.3)

    for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std,
               f'{mean:.4f}\n±{std:.4f}',
               ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/epipolar_bar_chart.png', bbox_inches='tight', dpi=300)
    print(f"Saved bar chart to {output_dir}/epipolar_bar_chart.png")

    # Individual plot 2: Combined box and violin plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Box plot
    bp = ax1.boxplot(box_data, labels=categories_with_data, patch_artist=True,
                     showmeans=True, meanline=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax1.set_ylabel('Epipolar Error', fontsize=12)
    ax1.set_title('Distribution - Box Plot', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Violin plot
    parts = ax2.violinplot(box_data, positions=positions, showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
    ax2.set_xlabel('Category', fontsize=12)
    ax2.set_ylabel('Epipolar Error', fontsize=12)
    ax2.set_title('Distribution - Violin Plot', fontsize=14, fontweight='bold')
    ax2.set_xticks(positions)
    ax2.set_xticklabels(categories_with_data)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/epipolar_distributions.png', bbox_inches='tight', dpi=300)
    print(f"Saved distribution plots to {output_dir}/epipolar_distributions.png")

    plt.close('all')


def print_statistics(stats_by_category):
    """Print statistical summary to console."""
    print("\n" + "="*80)
    print("STATISTICAL SUMMARY")
    print("="*80)

    for category, stats in stats_by_category.items():
        print(f"\n{category.upper()}")
        print("-" * 40)
        if stats['count'] > 0:
            print(f"  Sample count: {stats['count']}")
            print(f"  Mean:         {stats['mean']:.6f}")
            print(f"  Std Dev:      {stats['std']:.6f}")
            print(f"  Min:          {stats['min']:.6f}")
            print(f"  Q25:          {stats['q25']:.6f}")
            print(f"  Median:       {stats['median']:.6f}")
            print(f"  Q75:          {stats['q75']:.6f}")
            print(f"  Max:          {stats['max']:.6f}")
        else:
            print("  No valid data")

    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Visualize epipolar loss results from JSON file'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='epipolar_results.json',
        help='Input JSON file with evaluation results (default: epipolar_results.json)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='plots',
        help='Output directory for plots (default: plots)'
    )

    args = parser.parse_args()

    # Load results
    print(f"Loading results from {args.input}...")
    results = load_results(args.input)

    # Extract statistics
    print("Extracting statistics...")
    stats_by_category = extract_statistics(results)

    # Print statistics to console
    print_statistics(stats_by_category)

    # Create visualizations
    print(f"\nCreating visualizations...")
    create_visualizations(stats_by_category, args.output_dir)

    print("\n✓ Visualization complete!")


if __name__ == '__main__':
    main()

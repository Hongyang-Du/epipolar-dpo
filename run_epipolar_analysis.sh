#!/bin/bash
# One-click script to run complete epipolar analysis pipeline

set -e  # Exit on error

echo "========================================"
echo "Epipolar Loss Analysis Pipeline"
echo "========================================"
echo ""

# Default parameters
BASE_DIR="i2v"
OUTPUT_JSON="epipolar_results.json"
PLOT_DIR="plots"
SAMPLING_RATE=15
DESCRIPTOR="sift"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --base-dir)
            BASE_DIR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_JSON="$2"
            shift 2
            ;;
        --plot-dir)
            PLOT_DIR="$2"
            shift 2
            ;;
        --sampling-rate)
            SAMPLING_RATE="$2"
            shift 2
            ;;
        --descriptor)
            DESCRIPTOR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --base-dir DIR        Base directory with video subfolders (default: i2v)"
            echo "  --output FILE         Output JSON file (default: epipolar_results.json)"
            echo "  --plot-dir DIR        Output directory for plots (default: plots)"
            echo "  --sampling-rate N     Frame sampling rate (default: 15)"
            echo "  --descriptor TYPE     Descriptor type: sift or lightglue (default: sift)"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Configuration:"
echo "  Base directory:   $BASE_DIR"
echo "  Output JSON:      $OUTPUT_JSON"
echo "  Plot directory:   $PLOT_DIR"
echo "  Sampling rate:    $SAMPLING_RATE"
echo "  Descriptor type:  $DESCRIPTOR"
echo ""

# Step 1: Run evaluation
echo "Step 1/2: Evaluating videos..."
echo "----------------------------------------"
python3 evaluate_i2v_videos.py \
    --base-dir "$BASE_DIR" \
    --output "$OUTPUT_JSON" \
    --sampling-rate "$SAMPLING_RATE" \
    --descriptor "$DESCRIPTOR"

if [ $? -ne 0 ]; then
    echo "Error: Evaluation failed!"
    exit 1
fi

echo ""
echo "✓ Evaluation completed successfully"
echo ""

# Step 2: Generate visualizations
echo "Step 2/2: Generating visualizations..."
echo "----------------------------------------"
python3 visualize_epipolar_results.py \
    --input "$OUTPUT_JSON" \
    --output-dir "$PLOT_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Visualization failed!"
    exit 1
fi

echo ""
echo "✓ Visualization completed successfully"
echo ""

# Summary
echo "========================================"
echo "Analysis Complete!"
echo "========================================"
echo ""
echo "Results saved to:"
echo "  - JSON data: $OUTPUT_JSON"
echo "  - Plots:     $PLOT_DIR/"
echo ""
echo "Generated plots:"
echo "  - $PLOT_DIR/epipolar_comprehensive_analysis.png"
echo "  - $PLOT_DIR/epipolar_bar_chart.png"
echo "  - $PLOT_DIR/epipolar_distributions.png"
echo ""

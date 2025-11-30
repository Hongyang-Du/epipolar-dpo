#!/bin/bash
#SBATCH --job-name=epipolar_eval
#SBATCH --output=logs/epipolar_eval_%j.out
#SBATCH --error=logs/epipolar_eval_%j.err
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=batch

# Print job information
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Start Time: $(date)"
echo "=========================================="
echo ""

# Load conda module
module load miniconda3/23.11.0s

# Activate conda environment
echo "Activating conda environment: epipolar-eval"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate epipolar-eval

# Verify environment
echo ""
echo "Python version:"
python --version
echo ""
echo "Installed packages:"
conda list | grep -E "numpy|opencv|torch|kornia|matplotlib"
echo ""

# Create output directories
mkdir -p logs
mkdir -p plots

# Change to script directory
cd /oscar/scratch/hdu15/epipolar-dpo

# Run the analysis pipeline
echo "=========================================="
echo "Starting Epipolar Loss Analysis"
echo "=========================================="
echo ""

# Configuration
BASE_DIR="i2v"
OUTPUT_JSON="epipolar_results.json"
PLOT_DIR="plots"
SAMPLING_RATE=15
DESCRIPTOR="sift"

echo "Configuration:"
echo "  Base directory:   $BASE_DIR"
echo "  Output JSON:      $OUTPUT_JSON"
echo "  Plot directory:   $PLOT_DIR"
echo "  Sampling rate:    $SAMPLING_RATE"
echo "  Descriptor type:  $DESCRIPTOR"
echo ""

# Step 1: Evaluate videos
echo "Step 1/2: Evaluating videos..."
echo "------------------------------------------"
python3 evaluate_i2v_videos.py \
    --base-dir "$BASE_DIR" \
    --output "$OUTPUT_JSON" \
    --sampling-rate "$SAMPLING_RATE" \
    --descriptor "$DESCRIPTOR"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Evaluation completed successfully"
    echo ""
else
    echo ""
    echo "✗ Evaluation failed!"
    exit 1
fi

# Step 2: Generate visualizations
echo "Step 2/2: Generating visualizations..."
echo "------------------------------------------"
python3 visualize_epipolar_results.py \
    --input "$OUTPUT_JSON" \
    --output-dir "$PLOT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Visualization completed successfully"
    echo ""
else
    echo ""
    echo "✗ Visualization failed!"
    exit 1
fi

# Summary
echo "=========================================="
echo "Analysis Complete!"
echo "=========================================="
echo ""
echo "Results saved to:"
echo "  - JSON data: $OUTPUT_JSON"
echo "  - Plots:     $PLOT_DIR/"
echo ""
echo "Generated plots:"
ls -lh $PLOT_DIR/*.png
echo ""
echo "End Time: $(date)"
echo "=========================================="

# Epipolar Analysis - Setup and Running Guide

## 📋 Overview

This guide will help you set up the conda environment and submit the epipolar loss analysis job to the SLURM cluster.

## 🔧 Step 1: Create Conda Environment

The conda environment is being created using the provided `environment.yml` file. This includes all necessary dependencies:

- Python 3.10
- OpenCV 4.9.0
- PyTorch 2.4.1 (CPU version)
- Kornia (for epipolar geometry)
- Matplotlib & Seaborn (for visualization)
- Transformers (for LightGlue if needed)
- And other dependencies

### Create the environment:

```bash
module load miniconda3/23.11.0s
conda env create -f environment.yml -y
```

This will create an environment named **`epipolar-eval`**.

### Verify the environment:

```bash
module load miniconda3/23.11.0s
conda activate epipolar-eval
python test_env.py
```

You should see checkmarks (✓) for all installed packages.

## 🚀 Step 2: Submit the Job to SLURM

Once the conda environment is ready, you can submit the analysis job:

```bash
sbatch submit_epipolar_analysis.sh
```

### Check job status:

```bash
# Check if job is running
squeue -u $USER

# View job output (real-time)
tail -f logs/epipolar_eval_<JOB_ID>.out

# View job errors (if any)
tail -f logs/epipolar_eval_<JOB_ID>.err
```

## 📊 Step 3: Monitor Progress

The job will:

1. **Evaluate all videos** in `i2v/` folder (cogvid, realestate, wan subfolders)
2. **Save results** to `epipolar_results.json`
3. **Generate visualizations** in `plots/` folder

Expected runtime: ~2-6 hours depending on number of videos and cluster load.

## 📁 Output Files

After completion, you'll find:

### JSON Results:
```
epipolar_results.json
```

### Visualization Plots:
```
plots/
├── epipolar_comprehensive_analysis.png  # Main analysis with all metrics
├── epipolar_bar_chart.png              # Bar chart with error bars
└── epipolar_distributions.png          # Box & violin plots
```

### Log Files:
```
logs/
├── epipolar_eval_<JOB_ID>.out  # Standard output
└── epipolar_eval_<JOB_ID>.err  # Error output (if any)
```

## ⚙️ Configuration Options

### Modify SLURM Resources

Edit `submit_epipolar_analysis.sh`:

```bash
#SBATCH --time=12:00:00      # Maximum runtime
#SBATCH --cpus-per-task=8    # Number of CPUs
#SBATCH --mem=32G            # Memory allocation
#SBATCH --partition=batch    # Partition to use
```

### Modify Evaluation Parameters

Edit the configuration section in `submit_epipolar_analysis.sh`:

```bash
SAMPLING_RATE=15      # Frame sampling rate (lower = faster but less accurate)
DESCRIPTOR="sift"     # Feature descriptor: "sift" or "lightglue"
```

## 🔍 Troubleshooting

### Problem: Conda environment creation fails

```bash
# Clean up and retry
conda env remove -n epipolar-eval
conda clean --all
conda env create -f environment.yml -y
```

### Problem: Job fails with memory error

Increase memory in `submit_epipolar_analysis.sh`:
```bash
#SBATCH --mem=64G
```

Or reduce workload by processing one category at a time:
```bash
# Modify evaluate_i2v_videos.py --base-dir parameter
python3 evaluate_i2v_videos.py --base-dir i2v/cogvid
```

### Problem: Permission denied

```bash
chmod +x run_epipolar_analysis.sh
chmod +x submit_epipolar_analysis.sh
chmod +x test_env.py
```

### Problem: Module not found

```bash
# Make sure you're in the correct conda environment
module load miniconda3/23.11.0s
conda activate epipolar-eval
which python  # Should show path in epipolar-eval environment
```

## 📝 Alternative: Interactive Testing

If you want to test on a few videos first before submitting the full job:

### Request an interactive node:

```bash
salloc --time=01:00:00 --cpus-per-task=4 --mem=16G
```

### Activate environment and test:

```bash
module load miniconda3/23.11.0s
conda activate epipolar-eval

# Test on a single category
python3 evaluate_i2v_videos.py --base-dir i2v/cogvid --output test_results.json

# Visualize test results
python3 visualize_epipolar_results.py --input test_results.json --output-dir test_plots
```

### Exit interactive session:

```bash
exit
```

## 📧 Job Completion

When the job completes successfully, you'll see in the log file:

```
========================================
Analysis Complete!
========================================

Results saved to:
  - JSON data: epipolar_results.json
  - Plots:     plots/

Generated plots:
-rw-r--r-- plots/epipolar_comprehensive_analysis.png
-rw-r--r-- plots/epipolar_bar_chart.png
-rw-r--r-- plots/epipolar_distributions.png

End Time: [timestamp]
========================================
```

## 🎯 Quick Start (TL;DR)

```bash
# 1. Wait for conda environment to finish creating (currently running)
# Check with: conda env list | grep epipolar-eval

# 2. Submit the job
sbatch submit_epipolar_analysis.sh

# 3. Monitor progress
squeue -u $USER
tail -f logs/epipolar_eval_*.out

# 4. View results when done
ls -lh epipolar_results.json plots/
```

## 📚 Additional Resources

- **Main Documentation**: [EPIPOLAR_ANALYSIS_README.md](EPIPOLAR_ANALYSIS_README.md)
- **Evaluation Script**: [evaluate_i2v_videos.py](evaluate_i2v_videos.py)
- **Visualization Script**: [visualize_epipolar_results.py](visualize_epipolar_results.py)
- **Core Evaluation Code**: [metrics/video_evaluation/epipolar.py](metrics/video_evaluation/epipolar.py)

## ✅ Checklist

- [ ] Conda environment `epipolar-eval` created successfully
- [ ] Test environment with `python test_env.py`
- [ ] Verify video files exist in `i2v/` subfolders
- [ ] `logs/` directory created
- [ ] Submit job with `sbatch submit_epipolar_analysis.sh`
- [ ] Monitor job progress
- [ ] Review results in `epipolar_results.json` and `plots/`

---

**Note**: The conda environment creation is currently running in the background. It may take 10-20 minutes to complete. You can check the status with:

```bash
conda env list | grep epipolar-eval
```

When you see `epipolar-eval` in the list, the environment is ready!

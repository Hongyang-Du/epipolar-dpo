#!/usr/bin/env python3
"""
Quick script to test if the conda environment is properly installed.
"""

print("Testing conda environment...")
print("=" * 60)

try:
    import numpy as np
    print(f"✓ NumPy {np.__version__}")
except Exception as e:
    print(f"✗ NumPy: {e}")

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__}")
except Exception as e:
    print(f"✗ OpenCV: {e}")

try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
except Exception as e:
    print(f"✗ PyTorch: {e}")

try:
    import kornia
    print(f"✓ Kornia {kornia.__version__}")
except Exception as e:
    print(f"✗ Kornia: {e}")

try:
    import matplotlib
    print(f"✓ Matplotlib {matplotlib.__version__}")
except Exception as e:
    print(f"✗ Matplotlib: {e}")

try:
    import seaborn as sns
    print(f"✓ Seaborn {sns.__version__}")
except Exception as e:
    print(f"✗ Seaborn: {e}")

try:
    from transformers import __version__
    print(f"✓ Transformers {__version__}")
except Exception as e:
    print(f"✗ Transformers: {e}")

try:
    from tqdm import __version__
    print(f"✓ tqdm {__version__}")
except Exception as e:
    print(f"✗ tqdm: {e}")

print("=" * 60)
print("Environment test complete!")

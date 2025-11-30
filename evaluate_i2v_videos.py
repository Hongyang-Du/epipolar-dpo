#!/usr/bin/env python3
"""
Script to evaluate epipolar loss for all videos in i2v folder.
Computes metrics for each video, saves results to JSON, and generates statistical visualizations.
"""

import os
import json
import glob
from pathlib import Path
from tqdm import tqdm
import argparse

from metrics.video_evaluation.epipolar import EpipolarEvaluator


def find_all_videos(base_dir='i2v'):
    """
    Find all video files in the i2v directory, organized by subfolder.

    Args:
        base_dir: Base directory containing video subfolders

    Returns:
        Dictionary mapping category names to lists of video paths
    """
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']
    videos_by_category = {}

    # Get all subdirectories
    base_path = Path(base_dir)
    if not base_path.exists():
        raise ValueError(f"Directory {base_dir} does not exist")

    # Iterate through subdirectories
    for subdir in sorted(base_path.iterdir()):
        if subdir.is_dir():
            category = subdir.name
            videos = []

            # Find all videos with supported extensions
            for ext in video_extensions:
                videos.extend(sorted(subdir.glob(ext)))

            if videos:
                videos_by_category[category] = [str(v) for v in videos]

    return videos_by_category


def evaluate_all_videos(videos_by_category, output_json='epipolar_results.json',
                        sampling_rate=15, descriptor_type='sift'):
    """
    Evaluate epipolar loss for all videos and save results to JSON.

    Args:
        videos_by_category: Dictionary mapping categories to video paths
        output_json: Path to save JSON results
        sampling_rate: Frame sampling rate for evaluation
        descriptor_type: Type of descriptor ('sift' or 'lightglue')

    Returns:
        Dictionary with all evaluation results
    """
    # Initialize evaluator with default parameters
    evaluator = EpipolarEvaluator(
        sampling_rate=sampling_rate,
        descriptor_type=descriptor_type,
        ratio_thresh=0.75,
        ransac_thresh=1.0,
        min_matches=20
    )

    all_results = {
        'config': {
            'sampling_rate': sampling_rate,
            'descriptor_type': descriptor_type,
            'ratio_thresh': 0.75,
            'ransac_thresh': 1.0,
            'min_matches': 20
        },
        'categories': {}
    }

    # Process each category
    for category, video_paths in videos_by_category.items():
        print(f"\n{'='*60}")
        print(f"Processing category: {category}")
        print(f"{'='*60}")

        category_results = []

        # Evaluate each video with progress bar
        for video_path in tqdm(video_paths, desc=f"Evaluating {category}"):
            try:
                score, metrics = evaluator.evaluate_video(video_path)

                # Add video filename and category to results
                result = {
                    'video_name': os.path.basename(video_path),
                    'video_path': video_path,
                    'category': category,
                    'score': float(score) if score is not None else None,
                    'metrics': metrics
                }

                category_results.append(result)

                # Print summary for this video
                if score >= 0:
                    print(f"  ✓ {os.path.basename(video_path)}: "
                          f"epipolar_error={metrics.get('mean_epipolar_error', 'N/A'):.4f}")
                else:
                    error_msg = metrics.get('error', 'Unknown error')
                    print(f"  ✗ {os.path.basename(video_path)}: {error_msg}")

            except Exception as e:
                print(f"  ✗ Error processing {video_path}: {str(e)}")
                category_results.append({
                    'video_name': os.path.basename(video_path),
                    'video_path': video_path,
                    'category': category,
                    'score': None,
                    'metrics': {'error': str(e)}
                })

        all_results['categories'][category] = category_results
        print(f"\nCompleted {category}: {len(category_results)} videos processed")

    # Save results to JSON
    with open(output_json, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_json}")
    print(f"{'='*60}")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate epipolar loss for all videos in i2v folder'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='i2v',
        help='Base directory containing video subfolders (default: i2v)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='epipolar_results.json',
        help='Output JSON file path (default: epipolar_results.json)'
    )
    parser.add_argument(
        '--sampling-rate',
        type=int,
        default=15,
        help='Frame sampling rate (default: 15)'
    )
    parser.add_argument(
        '--descriptor',
        type=str,
        default='sift',
        choices=['sift', 'lightglue'],
        help='Descriptor type (default: sift)'
    )

    args = parser.parse_args()

    # Find all videos organized by category
    print("Scanning for videos...")
    videos_by_category = find_all_videos(args.base_dir)

    total_videos = sum(len(videos) for videos in videos_by_category.values())
    print(f"\nFound {total_videos} videos across {len(videos_by_category)} categories:")
    for category, videos in videos_by_category.items():
        print(f"  - {category}: {len(videos)} videos")

    # Evaluate all videos
    print("\nStarting evaluation...")
    evaluate_all_videos(
        videos_by_category,
        output_json=args.output,
        sampling_rate=args.sampling_rate,
        descriptor_type=args.descriptor
    )


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Full VLM Pipeline Orchestrator: Q-Align → Filter → VLM → Prompt DNA"""
import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_step_1_qalign(limit: int = None):
    """Step 1: Run Q-Align scoring on all images"""
    print("\n" + "=" * 60)
    print("🔹 STEP 1: Q-Align Scoring")
    print("=" * 60)
    from vlm.qalign_scorer import run_qalign_scoring
    run_qalign_scoring(limit=limit)

def run_step_2_filter(min_score: float = 2.5, top_k: int = 10):
    """Step 2: Filter high-quality images"""
    print("\n" + "=" * 60)
    print("🔹 STEP 2: Filter High-Quality Images")
    print("=" * 60)
    from vlm.filter_high_quality import filter_and_select_top_k
    filter_and_select_top_k(top_k=top_k, min_score=min_score)

def run_step_3_vlm():
    """Step 3: Run VLM on filtered images"""
    print("\n" + "=" * 60)
    print("🔹 STEP 3: VLM Style Extraction")
    print("=" * 60)
    from vlm.run_vlm_pipeline import run_vlm_on_clusters
    run_vlm_on_clusters()

def run_step_4_prompt_dna():
    """Step 4: Generate Prompt DNA"""
    print("\n" + "=" * 60)
    print("🔹 STEP 4: Generate Prompt DNA")
    print("=" * 60)
    from vlm.generate_prompt_dna import generate_all_prompt_dna
    generate_all_prompt_dna()

def run_step_5_update_db():
    """Step 5: Update Supabase"""
    print("\n" + "=" * 60)
    print("🔹 STEP 5: Update Supabase")
    print("=" * 60)
    from vlm.update_supabase import update_qalign_scores_in_db, upload_cluster_meta
    update_qalign_scores_in_db()
    upload_cluster_meta()

def run_full_pipeline(limit: int = None, min_score: float = 2.5, top_k: int = 10, skip_qalign: bool = False, skip_vlm: bool = False):
    """Run the complete pipeline"""
    print("🚀 Starting Full VLM Pipeline")
    print(f"   Config: min_score={min_score}, top_k={top_k}, limit={limit}")
    if not skip_qalign: run_step_1_qalign(limit=limit)
    else: print("\n⏭️ Skipping Q-Align (--skip-qalign)")
    run_step_2_filter(min_score=min_score, top_k=top_k)
    if not skip_vlm: run_step_3_vlm()
    else: print("\n⏭️ Skipping VLM (--skip-vlm)")
    run_step_4_prompt_dna()
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 60)
    print("\nOutputs:")
    print("  📄 output/qalign_scores.json - Q-Align scores for all images")
    print("  📄 output/filtered_clusters.json - High-quality images per cluster")
    print("  📄 output/cluster_vlm_results.json - VLM analysis results")
    print("  📄 output/prompt_dna.json - Prompt DNA for generation")
    print("  📄 output/cluster_meta.json - Cluster metadata")
    print("\nNext: Run `python -m vlm.update_supabase --schema` to see SQL, then upload to DB")

def main():
    parser = argparse.ArgumentParser(description="Full VLM Pipeline", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
Examples:
  # Test with 100 images
  python -m vlm.run_full_pipeline --limit 100
  
  # Full run (80k images, ~10 hours for Q-Align)
  python -m vlm.run_full_pipeline
  
  # Skip Q-Align (if already done)
  python -m vlm.run_full_pipeline --skip-qalign
  
  # Run individual steps
  python -m vlm.qalign_scorer --limit 100
  python -m vlm.filter_high_quality
  python -m vlm.run_vlm_pipeline
  python -m vlm.generate_prompt_dna
""")
    parser.add_argument("--limit", type=int, default=None, help="Limit images for Q-Align (for testing)")
    parser.add_argument("--min-score", type=float, default=2.5, help="Q-Align minimum score (default: 2.5)")
    parser.add_argument("--top-k", type=int, default=10, help="Top-K images per cluster (default: 10)")
    parser.add_argument("--skip-qalign", action="store_true", help="Skip Q-Align step (use existing scores)")
    parser.add_argument("--skip-vlm", action="store_true", help="Skip VLM step (use existing results)")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4, 5], help="Run only specific step")
    args = parser.parse_args()
    if args.step:
        {1: lambda: run_step_1_qalign(args.limit), 2: lambda: run_step_2_filter(args.min_score, args.top_k), 3: run_step_3_vlm, 4: run_step_4_prompt_dna, 5: run_step_5_update_db}[args.step]()
    else:
        run_full_pipeline(limit=args.limit, min_score=args.min_score, top_k=args.top_k, skip_qalign=args.skip_qalign, skip_vlm=args.skip_vlm)

if __name__ == "__main__": main()




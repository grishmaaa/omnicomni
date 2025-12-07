#!/usr/bin/env python3
"""
OmniComni - AI Audio Scene Generator
Main entry point for generating audio dramas from topics
"""

import argparse
import sys
from pathlib import Path

from src.scene_generator import SceneGenerator
from src.audio_generator import AudioGenerator
from src.utils import (
    create_project_folder,
    save_project_metadata,
    print_scenes
)
import config


def main():
    """Main pipeline"""
    parser = argparse.ArgumentParser(
        description="Generate AI audio dramas from topics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "A mysterious signal from deep space"
  python main.py "The last library on Earth" --scenes 7
  python main.py "First contact with aliens" --output my_projects --verbose
        """
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="Topic to generate scenes about"
    )
    
    parser.add_argument(
        "--scenes", "-s",
        type=int,
        default=config.DEFAULT_NUM_SCENES,
        help=f"Number of scenes to generate (default: {config.DEFAULT_NUM_SCENES})"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=config.DEFAULT_MODEL,
        help=f"Model to use (default: {config.DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(config.OUTPUT_DIR),
        help=f"Output directory (default: {config.OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show debug information"
    )
    
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Generate scenes only, skip audio generation"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*70)
    print(" "*20 + "🎬 OMNICOMNI AUDIO GENERATOR 🎬")
    print("="*70 + "\n")
    
    try:
        # Step 1: Initialize scene generator
        print("📝 STEP 1: AI Scene Generation")
        print("-" * 70)
        
        scene_gen = SceneGenerator(model_name=args.model)
        scenes = scene_gen.generate_scenes(
            topic=args.topic,
            num_scenes=args.scenes,
            verbose=args.verbose
        )
        
        # Print generated scenes
        print_scenes(scenes)
        
        # Step 2: Generate audio (unless --no-audio)
        audio_files = []
        if not args.no_audio:
            print("🎵 STEP 2: Audio Generation")
            print("-" * 70)
            
            audio_gen = AudioGenerator(output_dir=args.output)
            audio_files = audio_gen.generate_audio_sync(
                scenes=scenes,
                topic=args.topic
            )
        
        # Step 3: Save project
        print("💾 STEP 3: Saving Project")
        print("-" * 70)
        
        project_folder = create_project_folder(Path(args.output), args.topic)
        save_project_metadata(
            project_folder=project_folder,
            topic=args.topic,
            scenes=scenes,
            audio_files=audio_files,
            model_name=args.model
        )
        
        # Summary
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📁 Project: {project_folder}")
        print(f"📝 Scenes: {len(scenes)}")
        if audio_files:
            print(f"🎵 Audio Files: {len(audio_files)}")
        print(f"\n💡 View your project at: {project_folder}")
        print("="*70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

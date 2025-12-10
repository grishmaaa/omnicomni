#!/bin/bash
# Complete Pipeline with Disk Management
# Optimized for limited disk space (14GB available)

set -e  # Exit on error

# Configuration
TOPIC="${1:-Northern Lights Adventure}"
echo "=================================================="
echo "OmniComni Pipeline - Disk-Optimized"
echo "Topic: $TOPIC"
echo "=================================================="

# Check initial disk space
echo -e "\n📊 Initial disk space:"
df -h | grep overlay

# ============================================================================
# STEP 1: Scene Generation + Audio (~3GB VRAM, ~3GB cache)
# ============================================================================
echo -e "\n\n🎬 STEP 1: Generating scenes and audio..."
python pipeline_manager.py --topic "$TOPIC"

# Find the output directory
OUTPUT_DIR=$(ls -td output/*_$(echo "$TOPIC" | tr ' ' '_' | tr '[:upper:]' '[:lower:]') 2>/dev/null | head -1)
SCENES_JSON="$OUTPUT_DIR/1_scripts/$(basename $OUTPUT_DIR | sed 's/^[0-9]*_//')_scenes.json"

echo "✅ Scenes and audio complete"
echo "   Output: $OUTPUT_DIR"
df -h | grep overlay

# ============================================================================
# STEP 2: Image Generation (~4GB VRAM, ~4GB cache)
# ============================================================================
echo -e "\n\n🖼️  STEP 2: Generating images..."

# Clear Llama cache to make room for SD
echo "Clearing LLM cache to free space..."
rm -rf ~/.cache/huggingface/hub/models--meta-llama*
df -h | grep overlay

python generate_images.py --input "$SCENES_JSON"

IMAGES_TOPIC=$(basename "$SCENES_JSON" .json)
echo "✅ Images complete"
echo "   Output: output/images/$IMAGES_TOPIC/"
df -h | grep overlay

# ============================================================================
# STEP 3: Video Generation (~8GB VRAM, ~7GB cache)
# ============================================================================
echo -e "\n\n🎥 STEP 3: Generating videos..."

# Clear SD cache to make room for SVD
echo "Clearing SD cache to free space..."
rm -rf ~/.cache/huggingface/hub/models--runwayml*
df -h | grep overlay

python generate_videos.py --topic "$IMAGES_TOPIC"

echo "✅ Videos complete"
echo "   Output: output/video/clips/$IMAGES_TOPIC/"
df -h | grep overlay

# ============================================================================
# STEP 4: Merge Video + Audio
# ============================================================================
echo -e "\n\n🔗 STEP 4: Merging videos with audio..."

python merge_scenes.py --topic "$IMAGES_TOPIC"

echo "✅ Merge complete"
echo "   Output: output/video/final/$IMAGES_TOPIC/"
df -h | grep overlay

# ============================================================================
# STEP 5: Concatenate Final Video
# ============================================================================
echo -e "\n\n✂️  STEP 5: Concatenating final video..."

python concat_scenes.py --topic "$IMAGES_TOPIC"

FINAL_VIDEO="output/video/complete/${IMAGES_TOPIC}_complete.mp4"

echo "✅ Concatenation complete"
echo "   Output: $FINAL_VIDEO"
df -h | grep overlay

# ============================================================================
# SUMMARY
# ============================================================================
echo -e "\n\n=================================================="
echo "🎉 PIPELINE COMPLETE!"
echo "=================================================="
echo "Topic: $TOPIC"
echo "Final Video: $FINAL_VIDEO"

if [ -f "$FINAL_VIDEO" ]; then
    SIZE=$(du -h "$FINAL_VIDEO" | cut -f1)
    echo "Video Size: $SIZE"
    
    # Get video metadata if ffprobe exists
    if command -v ffprobe &> /dev/null; then
        DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL_VIDEO" 2>/dev/null | cut -d. -f1)
        echo "Duration: ${DURATION}s"
    fi
fi

echo -e "\n📊 Final disk usage:"
df -h | grep overlay

echo -e "\n✅ All steps completed successfully!"
echo "=================================================="

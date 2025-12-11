#!/bin/bash
#
# OmniComni - Full Pipeline Orchestrator
# Runs the complete end-to-end workflow for a single topic
#
# Usage: ./run_pipeline_full.sh "Your Topic Here"
#
set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TOPIC="$1"

if [ -z "$TOPIC" ]; then
    echo -e "${RED}Error: No topic provided${NC}"
    echo "Usage: ./run_pipeline_full.sh \"Your Topic Here\""
    exit 1
fi

print_step() {
    echo -e "\n${BLUE}===================================================================${NC}"
    echo -e "${BLUE}STEP $1: $2${NC}"
    echo -e "${BLUE}===================================================================${NC}\n"
}

# 1. Generate Scenes & Audio
print_step "1" "Generating Scenes & Audio (LLM + TTS)"
python3 pipeline_manager.py --topic "$TOPIC"

# Identify the generated timestamp directory
# We look for the most recent directory matching the topic slug
# Sanitize topic to match what pipeline_manager does (simple approximation)
SAFE_TOPIC=$(echo "$TOPIC" | sed 's/[^a-zA-Z0-9]/\_/g' | tr -s '_' | sed 's/^_//;s/_$//' | tr '[:upper:]' '[:lower:]')
# Actually, better to just look for the folder directly since we know the structure
# output/YYYYMMDD_HHMMSS_topic_slug
LATEST_DIR=$(ls -td output/*_"$SAFE_TOPIC" 2>/dev/null | head -1)

if [ -z "$LATEST_DIR" ]; then
    echo -e "${RED}Could not find output directory for topic: $SAFE_TOPIC${NC}"
    # Try fuzzy match if exact match failed
    LATEST_DIR=$(ls -td output/* | head -1)
    echo -e "${YELLOW}Falling back to latest directory: $LATEST_DIR${NC}"
fi

if [ -z "$LATEST_DIR" ]; then
    echo -e "${RED}Critical Error: No output directory found!${NC}"
    exit 1
fi

SCENE_FILE="$LATEST_DIR/1_scripts/${SAFE_TOPIC}_scenes.json"

if [ ! -f "$SCENE_FILE" ]; then
    echo -e "${RED}Scene file not found: $SCENE_FILE${NC}"
    # Try finding any json in that folder
    SCENE_FILE=$(ls "$LATEST_DIR/1_scripts/"*_scenes.json | head -1)
    echo -e "${YELLOW}Found alternative: $SCENE_FILE${NC}"
fi

echo -e "${GREEN}Using scene file: $SCENE_FILE${NC}"

# 2. Generate Images
print_step "2" "Generating Images (Stable Diffusion)"
python3 generate_images.py --input "$SCENE_FILE"

# 3. Generate Videos
print_step "3" "Generating Videos (SVD)"
# SVD script takes the topic slug, which usually matches the folder name in output/images
# The generate_images script outputs to output/images/topic_slug
python3 generate_videos.py --topic "$SAFE_TOPIC"

# 4. Merge Audio & Video
print_step "4" "Merging Audio & Video (FFmpeg)"
python3 merge_scenes.py --topic "$SAFE_TOPIC" --no-skip

# 5. Concatenate Final Video
print_step "5" "Assembling Final Video"
python3 concat_scenes.py --topic "$SAFE_TOPIC"

echo -e "\n${GREEN}===================================================================${NC}"
echo -e "${GREEN}✅ PIPELINE COMPLETE!${NC}"
echo -e "${GREEN}===================================================================${NC}"
echo -e "Topic: $TOPIC"
echo -e "Final Video: output/video/complete/${SAFE_TOPIC}_complete.mp4"
echo -e "\nTo download (if using VS Code Remote):"
echo -e "Right-click the file in the sidebar -> Download"

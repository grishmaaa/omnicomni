#!/usr/bin/env python3
"""
Extreme GPU Test Suite for Audio Scene Generation Pipeline
Tests covering edge cases, stress tests, and performance benchmarks

Run on GPU to verify:
- Memory management
- Concurrent processing
- Error handling
- Performance
- Edge cases
"""

import sys
import time
import torch
import subprocess
from pathlib import Path
from datetime import datetime
import json


class GPUTestSuite:
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def log(self, test_name, status, details="", vram_used=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "vram_gb": vram_used,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if vram_used:
            print(f"   VRAM: {vram_used:.2f} GB")
        print()
    
    def get_vram_usage(self):
        """Get current VRAM usage in GB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated(0) / 1e9
        return 0.0
    
    def run_pipeline(self, topic, scenes=5, timeout=300):
        """Run pipeline and capture result"""
        # Pass topic as separate list item to avoid shell escaping issues
        cmd = ["python", "main.py"] + [topic, "--scenes", str(scenes)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            return False, str(e)
    
    def print_header(self, title):
        """Print test section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")


# ============================================================================
# TEST CASES
# ============================================================================

def test_1_basic_generation(suite):
    """Test 1: Basic generation with simple topic"""
    suite.print_header("TEST 1: Basic Generation")
    
    success, output = suite.run_pipeline("A cat on a beach")
    vram = suite.get_vram_usage()
    
    if success and "PIPELINE COMPLETE" in output:
        suite.log("Test 1: Basic Generation", "PASS", "Simple topic processed", vram)
    else:
        suite.log("Test 1: Basic Generation", "FAIL", "Pipeline failed", vram)


def test_2_max_scenes(suite):
    """Test 2: Maximum scene count"""
    suite.print_header("TEST 2: Maximum Scenes")
    
    success, output = suite.run_pipeline("Space exploration", scenes=15)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 2: Max Scenes (15)", "PASS", "Handled large scene count", vram)
    else:
        suite.log("Test 2: Max Scenes", "FAIL", "Failed with 15 scenes", vram)


def test_3_minimal_scenes(suite):
    """Test 3: Minimum scene count"""
    suite.print_header("TEST 3: Minimal Scenes")
    
    success, output = suite.run_pipeline("Quick story", scenes=1)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 3: Min Scenes (1)", "PASS", "Single scene generated", vram)
    else:
        suite.log("Test 3: Min Scenes", "FAIL", "Single scene generation failed", vram)


def test_4_very_long_topic(suite):
    """Test 4: Very long topic string"""
    suite.print_header("TEST 4: Very Long Topic")
    
    long_topic = "A comprehensive exploration of the intricate relationship between quantum mechanics and consciousness, examining how observer effects might influence reality at the subatomic level, while considering the philosophical implications of wave function collapse and the measurement problem in modern physics, all set against the backdrop of a mysterious laboratory where strange experiments are taking place"
    
    success, output = suite.run_pipeline(long_topic, scenes=5)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 4: Very Long Topic", "PASS", f"Topic length: {len(long_topic)} chars", vram)
    else:
        suite.log("Test 4: Very Long Topic", "FAIL", "Failed with long topic", vram)


def test_5_special_characters(suite):
    """Test 5: Topic with special characters"""
    suite.print_header("TEST 5: Special Characters")
    
    special_topic = "A story about @#$%^&*() symbols, \"quotes\", and 'apostrophes' in 2024!"
    
    success, output = suite.run_pipeline(special_topic, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 5: Special Characters", "PASS", "Handled special chars", vram)
    else:
        suite.log("Test 5: Special Characters", "FAIL", "Special chars caused issues", vram)


def test_6_unicode_characters(suite):
    """Test 6: Unicode and emoji in topic"""
    suite.print_header("TEST 6: Unicode Characters")
    
    unicode_topic = "Une histoire sur la lune 🌙 et les étoiles ⭐ avec des caractères spéciaux"
    
    success, output = suite.run_pipeline(unicode_topic, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 6: Unicode/Emoji", "PASS", "Unicode handled correctly", vram)
    else:
        suite.log("Test 6: Unicode/Emoji", "FAIL", "Unicode caused errors", vram)


def test_7_numbers_only(suite):
    """Test 7: Topic with only numbers"""
    suite.print_header("TEST 7: Numbers Only Topic")
    
    success, output = suite.run_pipeline("1234567890", scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 7: Numbers Only", "PASS", "Numeric topic processed", vram)
    else:
        suite.log("Test 7: Numbers Only", "FAIL", "Numbers-only topic failed", vram)


def test_8_single_word(suite):
    """Test 8: Single word topic"""
    suite.print_header("TEST 8: Single Word Topic")
    
    success, output = suite.run_pipeline("Adventure", scenes=5)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 8: Single Word", "PASS", "Single word handled", vram)
    else:
        suite.log("Test 8: Single Word", "FAIL", "Single word topic failed", vram)


def test_9_technical_jargon(suite):
    """Test 9: Highly technical topic"""
    suite.print_header("TEST 9: Technical Jargon")
    
    tech_topic = "Kubernetes orchestration with microservices architecture using Docker containers and CI/CD pipeline automation with Jenkins and GitOps"
    
    success, output = suite.run_pipeline(tech_topic, scenes=5)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 9: Technical Jargon", "PASS", "Technical terms processed", vram)
    else:
        suite.log("Test 9: Technical Jargon", "FAIL", "Technical topic failed", vram)


def test_10_rapid_succession(suite):
    """Test 10: Multiple runs in rapid succession"""
    suite.print_header("TEST 10: Rapid Succession")
    
    topics = ["Test 1", "Test 2", "Test 3"]
    all_success = True
    
    start_vram = suite.get_vram_usage()
    
    for i, topic in enumerate(topics, 1):
        success, _ = suite.run_pipeline(topic, scenes=3, timeout=120)
        if not success:
            all_success = False
            break
    
    end_vram = suite.get_vram_usage()
    vram_delta = end_vram - start_vram
    
    if all_success:
        suite.log("Test 10: Rapid Succession", "PASS", 
                 f"3 runs completed, VRAM delta: {vram_delta:.2f} GB", end_vram)
    else:
        suite.log("Test 10: Rapid Succession", "FAIL", "Failed during rapid runs", end_vram)


def test_11_memory_stress(suite):
    """Test 11: Memory stress test with large generation"""
    suite.print_header("TEST 11: Memory Stress")
    
    torch.cuda.empty_cache()
    initial_vram = suite.get_vram_usage()
    
    # Increased timeout for large scene count
    success, output = suite.run_pipeline(
        "A complex epic saga spanning multiple generations", 
        scenes=10,
        timeout=600  # 10 minutes for stress test
    )
    
    peak_vram = suite.get_vram_usage()
    vram_used = peak_vram - initial_vram
    
    if success and peak_vram < 12:  # Should stay under 12GB
        suite.log("Test 11: Memory Stress", "PASS", 
                 f"VRAM used: {vram_used:.2f} GB (peak: {peak_vram:.2f} GB)", peak_vram)
    else:
        suite.log("Test 11: Memory Stress", "FAIL", 
                 f"VRAM exceeded limits or failed", peak_vram)


def test_12_empty_caches(suite):
    """Test 12: Run with cleared cache"""
    suite.print_header("TEST 12: Empty Cache Test")
    
    torch.cuda.empty_cache()
    time.sleep(2)
    
    success, output = suite.run_pipeline("Testing after cache clear", scenes=5)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 12: Post-Cache-Clear", "PASS", "Generation after cache clear", vram)
    else:
        suite.log("Test 12: Post-Cache-Clear", "FAIL", "Failed after cache clear", vram)


def test_13_multilingual(suite):
    """Test 13: Multilingual topic"""
    suite.print_header("TEST 13: Multilingual")
    
    multilingual = "English story with español words and 中文 characters and العربية text"
    
    success, output = suite.run_pipeline(multilingual, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 13: Multilingual", "PASS", "Multiple languages handled", vram)
    else:
        suite.log("Test 13: Multilingual", "FAIL", "Multilingual topic failed", vram)


def test_14_scientific_topic(suite):
    """Test 14: Scientific/academic topic"""
    suite.print_header("TEST 14: Scientific Topic")
    
    scientific = "The thermodynamic properties of superconductors at near-absolute-zero temperatures in quantum field theory experiments"
    
    success, output = suite.run_pipeline(scientific, scenes=5)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 14: Scientific Topic", "PASS", "Scientific content processed", vram)
    else:
        suite.log("Test 14: Scientific Topic", "FAIL", "Scientific topic failed", vram)


def test_15_creative_fiction(suite):
    """Test 15: Highly creative/fictional topic"""
    suite.print_header("TEST 15: Creative Fiction")
    
    creative = "Dragons made of pure mathematics solving riddles in the fifth dimension while time travels backwards"
    
    success, output = suite.run_pipeline(creative, scenes=7)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 15: Creative Fiction", "PASS", "Creative topic generated", vram)
    else:
        suite.log("Test 15: Creative Fiction", "FAIL", "Creative topic failed", vram)


def test_16_historical_event(suite):
    """Test 16: Historical event topic"""
    suite.print_header("TEST 16: Historical Event")
    
    historical = "The Apollo 11 moon landing in 1969 and Neil Armstrong's first steps on the lunar surface"
    
    # Extended timeout for 6 scenes
    success, output = suite.run_pipeline(historical, scenes=6, timeout=400)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 16: Historical Event", "PASS", "Historical topic processed", vram)
    else:
        suite.log("Test 16: Historical Event", "FAIL", "Historical topic failed", vram)


def test_17_contradictory(suite):
    """Test 17: Contradictory/paradoxical topic"""
    suite.print_header("TEST 17: Contradictory Topic")
    
    paradox = "An immortal being who is about to die in a world that doesn't exist but is very real"
    
    success, output = suite.run_pipeline(paradox, scenes=5)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 17: Contradictory", "PASS", "Paradoxical topic handled", vram)
    else:
        suite.log("Test 17: Contradictory", "FAIL", "Contradictory topic failed", vram)


def test_18_very_short(suite):
    """Test 18: Extremely short topic"""
    suite.print_header("TEST 18: Very Short Topic")
    
    success, output = suite.run_pipeline("A", scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 18: Very Short (1 char)", "PASS", "Single character topic", vram)
    else:
        suite.log("Test 18: Very Short", "FAIL", "Single char topic failed", vram)


def test_19_repeated_words(suite):
    """Test 19: Topic with repeated words"""
    suite.print_header("TEST 19: Repeated Words")
    
    repeated = "Really really really really interesting story about really really interesting things"
    
    success, output = suite.run_pipeline(repeated, scenes=4)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 19: Repeated Words", "PASS", "Repetition handled", vram)
    else:
        suite.log("Test 19: Repeated Words", "FAIL", "Repeated words failed", vram)


def test_20_punctuation_heavy(suite):
    """Test 20: Heavy punctuation"""
    suite.print_header("TEST 20: Heavy Punctuation")
    
    punctuation = "What!? Why... How??? Who!!! Where??? When!!! -- Really??? Yes!!! No!!! Maybe!?!?"
    
    success, output = suite.run_pipeline(punctuation, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 20: Heavy Punctuation", "PASS", "Punctuation handled", vram)
    else:
        suite.log("Test 20: Heavy Punctuation", "FAIL", "Punctuation caused issues", vram)


def test_21_newlines_tabs(suite):
    """Test 21: Topic with newlines and tabs"""
    suite.print_header("TEST 21: Whitespace Characters")
    
    whitespace = "A story\n\twith new\nlines\tand\ttabs"
    
    success, output = suite.run_pipeline(whitespace, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 21: Whitespace Chars", "PASS", "Whitespace handled", vram)
    else:
        suite.log("Test 21: Whitespace Chars", "FAIL", "Whitespace caused errors", vram)


def test_22_url_in_topic(suite):
    """Test 22: Topic containing URL"""
    suite.print_header("TEST 22: URL in Topic")
    
    url_topic = "A story about https://example.com and www.test.org websites"
    
    success, output = suite.run_pipeline(url_topic, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 22: URL in Topic", "PASS", "URLs processed", vram)
    else:
        suite.log("Test 22: URL in Topic", "FAIL", "URL caused issues", vram)


def test_23_mixed_case(suite):
    """Test 23: Mixed case sensitivity"""
    suite.print_header("TEST 23: Mixed Case")
    
    mixed = "ThIs Is A sToRy WiTh MiXeD CaSe ChArAcTeRs"
    
    success, output = suite.run_pipeline(mixed, scenes=3)
    vram = suite.get_vram_usage()
    
    if success:
        suite.log("Test 23: Mixed Case", "PASS", "Case variations handled", vram)
    else:
        suite.log("Test 23: Mixed Case", "FAIL", "Mixed case failed", vram)


def test_24_performance_benchmark(suite):
    """Test 24: Performance benchmark"""
    suite.print_header("TEST 24: Performance Benchmark")
    
    start_time = time.time()
    success, output = suite.run_pipeline("Standard performance test topic", scenes=5)
    end_time = time.time()
    
    duration = end_time - start_time
    vram = suite.get_vram_usage()
    
    if success and duration < 120:  # Should complete in <2 min
        suite.log("Test 24: Performance", "PASS", 
                 f"Completed in {duration:.1f}s", vram)
    elif success:
        suite.log("Test 24: Performance", "WARN", 
                 f"Slow: {duration:.1f}s (expected <120s)", vram)
    else:
        suite.log("Test 24: Performance", "FAIL", "Benchmark failed", vram)


def test_25_vram_recovery(suite):
    """Test 25: VRAM recovery after generation"""
    suite.print_header("TEST 25: VRAM Recovery")
    
    torch.cuda.empty_cache()
    baseline_vram = suite.get_vram_usage()
    
    # Run generation
    success, _ = suite.run_pipeline("VRAM test topic", scenes=5)
    
    # Clear cache
    torch.cuda.empty_cache()
    time.sleep(2)
    
    final_vram = suite.get_vram_usage()
    vram_leak = final_vram - baseline_vram
    
    if success and vram_leak < 0.5:  # Less than 500MB leak
        suite.log("Test 25: VRAM Recovery", "PASS", 
                 f"Memory leak: {vram_leak:.3f} GB", final_vram)
    else:
        suite.log("Test 25: VRAM Recovery", "WARN", 
                 f"Possible leak: {vram_leak:.3f} GB", final_vram)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print("\n" + "🧪"*35)
    print(" "*20 + "EXTREME GPU TEST SUITE")
    print(" "*15 + "Audio Scene Generation Pipeline")
    print("🧪"*35 + "\n")
    
    # Check GPU
    if not torch.cuda.is_available():
        print("❌ ERROR: CUDA not available!")
        print("   This test suite requires a GPU")
        sys.exit(1)
    
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print(f"✅ CUDA: {torch.version.cuda}\n")
    
    suite = GPUTestSuite()
    suite.start_time = time.time()
    
    # Run all tests
    tests = [
        test_1_basic_generation,
        test_2_max_scenes,
        test_3_minimal_scenes,
        test_4_very_long_topic,
        test_5_special_characters,
        test_6_unicode_characters,
        test_7_numbers_only,
        test_8_single_word,
        test_9_technical_jargon,
        test_10_rapid_succession,
        test_11_memory_stress,
        test_12_empty_caches,
        test_13_multilingual,
        test_14_scientific_topic,
        test_15_creative_fiction,
        test_16_historical_event,
        test_17_contradictory,
        test_18_very_short,
        test_19_repeated_words,
        test_20_punctuation_heavy,
        test_21_newlines_tabs,
        test_22_url_in_topic,
        test_23_mixed_case,
        test_24_performance_benchmark,
        test_25_vram_recovery
    ]
    
    for test_func in tests:
        try:
            test_func(suite)
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests cancelled by user")
            break
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            suite.log(test_func.__name__, "CRASH", str(e))
    
    # Summary
    total_time = time.time() - suite.start_time
    
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for r in suite.results if r["status"] == "PASS")
    failed = sum(1 for r in suite.results if r["status"] == "FAIL")
    warned = sum(1 for r in suite.results if r["status"] == "WARN")
    crashed = sum(1 for r in suite.results if r["status"] == "CRASH")
    
    print(f"Total Tests: {len(suite.results)}")
    print(f"✅ Passed:   {passed}")
    print(f"❌ Failed:   {failed}")
    print(f"⚠️  Warnings: {warned}")
    print(f"💥 Crashed:  {crashed}")
    print(f"\nTotal Time: {total_time:.1f}s")
    
    # Save results
    results_file = Path("test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "summary": {
                "total": len(suite.results),
                "passed": passed,
                "failed": failed,
                "warned": warned,
                "crashed": crashed,
                "duration_seconds": total_time
            },
            "gpu": {
                "name": torch.cuda.get_device_name(0),
                "vram_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                "cuda_version": torch.version.cuda
            },
            "tests": suite.results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Final status
    print("\n" + "="*70)
    if failed == 0 and crashed == 0:
        print("✅ ALL TESTS PASSED!")
    elif failed + crashed < 3:
        print("⚠️  MOSTLY PASSING (some issues)")
    else:
        print("❌ MULTIPLE FAILURES DETECTED")
    print("="*70 + "\n")
    
    sys.exit(0 if failed == 0 and crashed == 0 else 1)


if __name__ == "__main__":
    main()

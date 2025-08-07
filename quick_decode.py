#!/usr/bin/env python3
"""
Quick base64 to MP4 decoder - Minimal script for testing
Usage: python quick_decode.py
"""

import base64
import sys

def quick_decode(base64_string, output_file="output.mp4"):
    """Quick decode base64 to MP4"""
    try:
        # Remove any whitespace/newlines
        base64_string = base64_string.strip().replace('\n', '').replace('\r', '')
        
        print(f"Decoding {len(base64_string)} characters...")
        
        # Decode base64
        video_bytes = base64.b64decode(base64_string)
        
        # Write to file
        with open(output_file, 'wb') as f:
            f.write(video_bytes)
        
        print(f"✅ Saved to {output_file}")
        print(f"File size: {len(video_bytes)} bytes ({len(video_bytes)/1024:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Quick Base64 to MP4 Decoder")
    print("-" * 30)
    
    if len(sys.argv) > 1:
        # Command line argument
        base64_data = sys.argv[1]
        output_name = sys.argv[2] if len(sys.argv) > 2 else "decoded_video.mp4"
    else:
        # Interactive input
        print("Paste your base64 video string (press Enter twice when done):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line.strip())
            except KeyboardInterrupt:
                print("\n❌ Cancelled")
                sys.exit(1)
        
        base64_data = "".join(lines)
        output_name = input("Output filename (default: decoded.mp4): ").strip() or "decoded.mp4"
    
    if base64_data:
        success = quick_decode(base64_data, output_name)
        if success:
            print(f"\n🎬 Video saved! You can now play: {output_name}")
            print("   - Double-click to open with default player")
            print("   - Or use: vlc/ffplay/quicktime to play")
    else:
        print("❌ No base64 data provided")
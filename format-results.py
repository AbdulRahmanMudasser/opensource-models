import json
import os
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

def format_section(title, content, reasoning_details=None):
    """Format a single response section."""
    separator = "=" * 80
    result = f"\n{separator}\n{title}\n{separator}\n\n"
    result += f"Response:\n{content}\n"
    
    if reasoning_details:
        result += f"\n{'─' * 40}\nReasoning Details:\n{'─' * 40}\n"
        for i, detail in enumerate(reasoning_details, 1):
            if isinstance(detail, dict):
                text = detail.get('text', '')
                reasoning_type = detail.get('type', 'unknown')
                result += f"\n[Reasoning Block {i}] (Type: {reasoning_type})\n"
                result += f"{text}\n"
    
    return result

def format_result_file(filepath):
    """Read and format a single result file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    model = data.get('model', 'Unknown')
    timestamp = data.get('timestamp', 'Unknown')
    
    try:
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%B %d, %Y at %I:%M:%S %p")
    except:
        formatted_time = timestamp
    
    header = "=" * 80
    result = f"\n{header}\n"
    result += f"Model: {model}\n"
    result += f"Tested: {formatted_time}\n"
    result += f"{header}\n"
    
    # First call
    first_call = data.get('first_call')
    if first_call:
        result += format_section(
            "FIRST CALL: How many r's in 'strawberry'?",
            first_call.get('content', ''),
            first_call.get('reasoning_details')
        )
    
    # Second call
    second_call = data.get('second_call')
    if second_call:
        result += format_section(
            "SECOND CALL: Are you sure? Think carefully.",
            second_call.get('content', ''),
            second_call.get('reasoning_details')
        )
    
    return result

def format_all_results():
    """Format all result files in the output directory."""
    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory not found: {OUTPUT_DIR}")
        return
    
    json_files = sorted(Path(OUTPUT_DIR).glob("*.json"))
    
    if not json_files:
        print("No result files found in output directory.")
        return
    
    print(f"\nFound {len(json_files)} result file(s)\n")
    
    for filepath in json_files:
        formatted = format_result_file(filepath)
        print(formatted)
        print("\n" + "=" * 80 + "\n")

def export_summary():
    """Export a summary of all results to a markdown file."""
    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory not found: {OUTPUT_DIR}")
        return
    
    json_files = sorted(Path(OUTPUT_DIR).glob("*.json"))
    
    if not json_files:
        print("No result files found.")
        return
    
    summary_path = os.path.join(OUTPUT_DIR, "summary.md")
    
    with open(summary_path, 'w', encoding='utf-8') as md:
        md.write("# Model Reasoning Test Results\n\n")
        md.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.write(f"**Total Tests:** {len(json_files)}\n\n")
        md.write("---\n\n")
        
        for filepath in json_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            model = data.get('model', 'Unknown')
            timestamp = data.get('timestamp', 'Unknown')
            first_call = data.get('first_call', {})
            second_call = data.get('second_call', {})
            
            md.write(f"## {model}\n\n")
            md.write(f"**Tested:** {timestamp}\n\n")
            
            md.write("### First Call Response\n\n")
            md.write(first_call.get('content', 'No response') + "\n\n")
            
            if first_call.get('reasoning_details'):
                md.write("**Reasoning:**\n\n")
                for detail in first_call['reasoning_details']:
                    if isinstance(detail, dict):
                        md.write(detail.get('text', '') + "\n\n")
            
            md.write("### Second Call Response\n\n")
            md.write(second_call.get('content', 'No response') + "\n\n")
            
            if second_call.get('reasoning_details'):
                md.write("**Reasoning:**\n\n")
                for detail in second_call['reasoning_details']:
                    if isinstance(detail, dict):
                        md.write(detail.get('text', '') + "\n\n")
            
            md.write("---\n\n")
    
    print(f"Summary exported to: {summary_path}")

if __name__ == "__main__":
    format_all_results()
    export_summary()

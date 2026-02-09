# AI Log Analyzer

Python script to analyze AI assistant logs and identify problematic responses.

## Usage

```bash
# Basic usage
python scripts/analyze_ai_logs.py path/to/logs.xlsx

# Specify output file
python scripts/analyze_ai_logs.py path/to/logs.xlsx -o results.json

# With custom client issues file
python scripts/analyze_ai_logs.py path/to/logs.xlsx --client-issues client_issues.json
```

## Example

```bash
cd /Users/rodrigoqdive/Desktop/Rodrigo_stuff/Learning/AIEngineering/interview-preparation
python scripts/analyze_ai_logs.py notebooks/ai_backend_appservice_logs_7d_29.01.26.xlsx -o analysis_results.json
```

## Output

The script generates a JSON file containing:

- **Summary statistics**: Total entries, questions, slow responses, etc.
- **Slow responses**: Questions that took >60 seconds with duration and details
- **Problematic Q&A pairs**: Questions with issues (clarifications, verbose, missing tools)
- **Client-reported issues**: Matched questions from client complaints

## JSON Structure

```json
{
  "analysis_timestamp": "2026-02-04T...",
  "source_file": "path/to/logs.xlsx",
  "summary": {
    "total_log_entries": 100,
    "total_questions": 50,
    "slow_responses_count": 5,
    "problematic_qa_count": 10,
    "matched_client_issues_count": 3
  },
  "slow_responses": [
    {
      "timestamp": "...",
      "question": "...",
      "duration_seconds": 120.5,
      "answer": "...",
      "tools_used": ["get_data"],
      "num_tools": 1
    }
  ],
  "problematic_qa_pairs": [...],
  "client_reported_issues": [...]
}
```

## Requirements

- pandas
- openpyxl

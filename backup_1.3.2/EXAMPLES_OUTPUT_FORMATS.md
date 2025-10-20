# Output Format Examples

This document demonstrates the different output formats available in Domain Checker and their use cases.

## Overview

Domain Checker supports 4 output formats:
- **Rich** (default) - Beautiful terminal output with colors and formatting
- **Plain** - Clean text output, perfect for copy/paste
- **JSON** - Structured data for programmatic use
- **CSV** - Comma-separated values for spreadsheets (bulk operations only)

## Format Comparison

### 1. Single Domain Lookup

#### Rich Format (Default)
```bash
domch lookup example.com
```
Output features:
- ✅ Colorful panels and tables
- 📧 Emojis for visual clarity
- 🎨 Styled text with bold, colors, and formatting
- 📊 Beautiful progress bars

#### Plain Format
```bash
domch lookup example.com --format plain
```
Output features:
- Clean text without any formatting
- Easy to copy/paste
- No emojis or special characters
- Simple separators (=, -)
- Perfect for scripts and text editors

#### JSON Format
```bash
domch lookup example.com --format json
```
Output features:
- Valid JSON structure
- Easy to parse programmatically
- Works with jq, Python json module, etc.
- All data fields included

## Use Cases

### Use Case 1: Copy Name Servers
**Problem:** Need to copy name servers from output to update DNS configuration.

**Solution using Plain format:**
```bash
domch lookup example.com --format plain | grep -A 10 "NAME SERVERS"
```

Output:
```
NAME SERVERS:
  a.iana-servers.net
  b.iana-servers.net
```

Now you can easily copy these without any formatting or colors!

### Use Case 2: Extract Specific Data with Scripts
**Problem:** Need to extract registrar name for multiple domains in a script.

**Solution using JSON format:**
```bash
# Using jq to extract registrar
domch lookup example.com --format json | jq -r '.data.registrar'

# Check if domain is registered
domch lookup example.com --format json | jq -r '.registration_status'

# Get expiration date
domch lookup example.com --format json | jq -r '.data.expiration_date'
```

### Use Case 3: Bulk Check and Export to Excel
**Problem:** Need to check 100 domains and create a spreadsheet report.

**Solution using CSV format:**
```bash
# Create a file with domains
echo "example.com
google.com
github.com
stackoverflow.com" > domains.txt

# Export to CSV
domch file domains.txt --format csv > results.csv
```

Now open `results.csv` in Excel!

### Use Case 4: Monitor Domain Expiration
**Problem:** Need to monitor when domains expire.

**Solution using JSON and scripting:**
```bash
#!/bin/bash
# check_expirations.sh

domains=("example.com" "google.com" "github.com")

for domain in "${domains[@]}"; do
    expiration=$(domch lookup "$domain" --format json | jq -r '.data.expiration_date')
    echo "$domain expires on: $expiration"
done
```

### Use Case 5: DNS Propagation Check - Get IPs Only
**Problem:** Need just the IP addresses from propagation check.

**Solution using Plain format:**
```bash
domch prop example.com --format plain | grep -A 100 "RESOLVED IP"
```

### Use Case 6: Integration with Other Tools
**Problem:** Need to feed domain info into another tool.

**Solution using JSON format:**
```bash
# Get all data as JSON and pipe to another tool
domch lookup example.com --format json | your-custom-tool

# Save JSON to file for later processing
domch bulk example.com google.com --format json > domains.json

# Process with Python
python3 << EOF
import json
import sys

data = json.load(sys.stdin)
for result in data['results']:
    if result['success']:
        print(f"{result['domain']}: {result['data']['registrar']}")
EOF < domains.json
```

## Command-Specific Format Support

### lookup, dig, reverse
- ✅ Rich (default)
- ✅ Plain
- ✅ JSON
- ❌ CSV (not applicable for single lookups)

```bash
domch lookup example.com --format plain
domch dig example.com --record A --format json
domch reverse 8.8.8.8 --format plain
```

### bulk, file
- ✅ Rich (default)
- ✅ Plain
- ✅ JSON
- ✅ CSV

```bash
domch bulk domain1.com domain2.com --format csv
domch file domains.txt --format json
```

### prop (propagation)
- ✅ Rich (default)
- ✅ Plain
- ✅ JSON
- ❌ CSV

```bash
domch prop example.com --format plain
domch prop example.com --format json
```

## Quick Reference

### Get registrar only
```bash
domch lookup example.com --format json | jq -r '.data.registrar'
```

### Get all name servers as list
```bash
domch lookup example.com --format plain | sed -n '/NAME SERVERS:/,/^$/p' | grep "^  "
```

### Export bulk results to CSV
```bash
domch file domains.txt --format csv > results.csv
```

### Check domain status
```bash
domch lookup example.com --format json | jq -r '.registration_status'
```

### Get JSON with pretty print
```bash
domch lookup example.com --format json | jq '.'
```

## Tips

1. **Default is Rich**: If you don't specify `--format`, you get the beautiful Rich output
2. **Pipe to file**: Use `> file.ext` to save output to a file
3. **Combine with jq**: JSON format works perfectly with jq for data extraction
4. **CSV for Excel**: CSV format is perfect for importing into Excel or Google Sheets
5. **Plain for copy/paste**: Use plain format when you need to copy data manually
6. **JSON for scripts**: Use JSON format when integrating with scripts or other tools


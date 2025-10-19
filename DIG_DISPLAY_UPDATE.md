# 🔧 DIG Display Improvement

## Overview

Updated the CLI display to show only relevant information for DIG (DNS) lookups, removing unnecessary fields that don't apply to DNS queries.

## Changes Made

### Before (Cluttered Display)
DIG lookups showed irrelevant sections with "N/A" values:
- ❌ Registrar: N/A
- ❌ Status: N/A
- ❌ Important Dates (all N/A)
- ❌ Contact Information (all N/A)

### After (Clean Display)
DIG lookups now show only relevant information:
- ✅ Domain/IP
- ✅ Method: DIG
- ✅ Lookup Time
- ✅ Name Servers (if querying NS records)
- ✅ Raw DNS data

## Examples

### A Record Lookup
```bash
$ domain-check dig www.zacroach.com

╭───────────────────────────── Domain Information ─────────────────────────────╮
│                                                                              │
│ Domain: www.zacroach.com                                                     │
│ Method: DIG                                                                  │
│ Lookup Time: 0.09s                                                           │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

Raw Data:
╭────────────────────────────────── Raw Data ──────────────────────────────────╮
│   1 q3162443.eero.online.                                                    │
│   2 50.47.26.113                                                             │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### NS Record Lookup
```bash
$ domain-check dig google.com --record NS

╭───────────────────────────── Domain Information ─────────────────────────────╮
│                                                                              │
│ Domain: google.com                                                           │
│ Method: DIG                                                                  │
│ Lookup Time: 0.02s                                                           │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
   Name Servers    
╭─────────────────╮
│ Server          │
├─────────────────┤
│ ns4.google.com. │
│ ns2.google.com. │
│ ns1.google.com. │
│ ns3.google.com. │
╰─────────────────╯

Raw Data:
[DNS records shown here]
```

### Reverse DNS Lookup
```bash
$ domain-check reverse 8.8.8.8

╭───────────────────────────── Domain Information ─────────────────────────────╮
│                                                                              │
│ Domain: dns.google                                                           │
│ Method: DIG                                                                  │
│ Lookup Time: 0.15s                                                           │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

Raw Data:
╭────────────────────────────────── Raw Data ──────────────────────────────────╮
│   1 dns.google.                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Technical Implementation

### Code Changes in `cli.py`

Added detection for DIG method:
```python
is_dig = result.method.lower() == 'dig'
```

Simplified info panel for DIG:
```python
if is_dig:
    # Show only: Domain, Method, Lookup Time
else:
    # Show full info: Domain, Method, Lookup Time, Registrar, Status
```

Conditional display sections:
```python
if not is_dig:
    # Show Important Dates table
    # Show Contact Information table
```

Name servers are still shown for DIG when available (e.g., NS record queries).

## Benefits

1. **Cleaner Output** - No more irrelevant "N/A" fields
2. **Faster Reading** - Focus on what matters for DNS queries
3. **Better UX** - Information density matches the query type
4. **Maintains Functionality** - WHOIS/RDAP still show full details

## Other Methods Unaffected

WHOIS and RDAP lookups still show complete information:
- ✅ Domain Information (Registrar, Status)
- ✅ Important Dates (Creation, Expiration, Updated)
- ✅ Name Servers
- ✅ Contact Information (when available)

## Summary

✅ **DIG lookups now have a clean, focused display**  
✅ **Removed irrelevant sections (dates, contacts, registrar)**  
✅ **Kept relevant sections (name servers for NS queries)**  
✅ **WHOIS/RDAP display unchanged and fully functional**

The DIG display is now optimized for DNS queries, showing only the information that's relevant to DNS lookups! 🎯


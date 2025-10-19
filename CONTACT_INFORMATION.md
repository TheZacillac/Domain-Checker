# 📇 Contact Information Display

## Overview

The Domain Checker now displays **full contact information** when available from WHOIS or RDAP lookups.

## What's Displayed

When contact information is available, the CLI will show:

- ✅ **Name** - Full name of the contact
- ✅ **Organization** - Company or organization name
- ✅ **Email** - 📧 Email address
- ✅ **Phone** - 📞 Phone number
- ✅ **Address** - 📍 Full postal address

## Contact Types

The tool displays three types of contacts:

1. **Registrant** - Domain owner
2. **Admin** - Administrative contact
3. **Technical** - Technical contact

## Example Display

```
                          Contact Information                           
╭────────────┬─────────────────────────────────────────────────────────╮
│ Type       │ Details                                                 │
├────────────┼─────────────────────────────────────────────────────────┤
│ Registrant │ John Doe                                                │
│            │ Acme Corporation                                        │
│            │ 📧 john.doe@example.com                                 │
│            │ 📞 +1-555-0100                                          │
│            │ 📍 123 Main St, Suite 500, San Francisco, CA 94105, USA │
├────────────┼─────────────────────────────────────────────────────────┤
│ Admin      │ Jane Smith                                              │
│            │ Acme IT Department                                      │
│            │ 📧 jane.smith@example.com                               │
│            │ 📞 +1-555-0101                                          │
├────────────┼─────────────────────────────────────────────────────────┤
│ Technical  │ Bob Johnson                                             │
│            │ 📧 bob.johnson@example.com                              │
│            │ 📞 +1-555-0102                                          │
│            │ 📍 456 Tech Lane, Building 2, Austin, TX 78701, USA     │
╰────────────┴─────────────────────────────────────────────────────────╯
```

## Privacy & GDPR Compliance

### Why Contact Information is Often Hidden

Modern domain registries and RDAP servers typically **hide detailed contact information** for several important reasons:

1. **GDPR Compliance** - European privacy regulations require protecting personal data
2. **Privacy Protection** - Prevents spam, identity theft, and harassment
3. **Security** - Reduces exposure to social engineering attacks
4. **ICANN Policy** - New policies prioritize registrant privacy

### What You'll See Instead

Most lookups will show:

```
  Contact Information   
╭────────────┬─────────╮
│ Type       │ Details │
├────────────┼─────────┤
│ Registrant │ N/A     │
├────────────┼─────────┤
│ Admin      │ N/A     │
├────────────┼─────────┤
│ Technical  │ N/A     │
╰────────────┴─────────╯
```

This is **normal and expected** behavior for modern domain lookups.

### When Contact Information IS Available

Contact details may still be visible for:

- **Organizational domains** - Some companies choose to display contact info
- **Older domains** - Registered before privacy protection was standard
- **Specific TLDs** - Some country-code TLDs have different policies
- **Explicit permission** - When the registrant opts to make information public

## Testing the Display

You can test how full contact information looks using:

```bash
cd /Users/zacroach/Projects/Domain\ Check/Domain-Checker
python3 test_contact_display.py
```

This will show a mock domain with all contact fields populated.

## Technical Implementation

### Contact Data Structure

Contact information is stored as a dictionary with these optional fields:

```python
{
    "name": "Full Name",              # or "fn" for vCard compatibility
    "organization": "Company Name",
    "email": "email@example.com",
    "phone": "+1-555-0100",
    "address": "Full postal address"
}
```

### RDAP vCard Parsing

The RDAP client parses vCard data from RDAP responses:

- `fn` → Name
- `org` → Organization
- `email` → Email
- `tel` → Phone
- `adr` → Address

### Display Format

The `format_contact()` function in `cli.py`:

- Shows each field on a separate line when available
- Uses icons (📧 📞 📍) for visual clarity
- Applies color coding for better readability
- Returns "N/A" when no information is available

## Usage Examples

### Single Domain Lookup

```bash
# Check any domain - will show contacts if available
domain-check lookup example.com

# Try both methods
domain-check lookup example.com --method whois
domain-check lookup example.com --method rdap
```

### Bulk Lookups

```bash
# Contact info in bulk results
domain-check bulk domain1.com domain2.com domain3.com
```

### Comparison Mode

```bash
# Compare WHOIS vs RDAP contact information
domain-check compare example.com
```

## Summary

✅ **Full contact display implemented**  
✅ **Shows all available fields**  
✅ **Beautiful multi-line formatting**  
✅ **Privacy-aware and GDPR-compliant**  
✅ **Works with both WHOIS and RDAP**

The contact information feature is complete and will automatically display any contact details that are publicly available through WHOIS or RDAP lookups!


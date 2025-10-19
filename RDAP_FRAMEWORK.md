# 🌐 RDAP Framework Integration

## ✅ **Using TheZacillac/rdap-cli Framework**

The domain checker now uses your RDAP CLI framework from:
**https://github.com/TheZacillac/rdap-cli**

### **What's Integrated:**

1. **IANA Bootstrap Service Discovery**
   - Automatically finds the correct RDAP server for any TLD
   - Uses official IANA bootstrap files
   - Supports DNS, IPv4, IPv6, and ASN queries

2. **Proper RDAP Protocol**
   - RFC 7480-7485 compliant
   - JSON-based structured data
   - HTTPS secure queries
   - Standardized response parsing

3. **Auto-Detection**
   - Automatically detects domain, IP, or ASN queries
   - Routes to appropriate RDAP endpoint
   - Handles TLD extraction and server selection

### **Key Features from Your Framework:**

- ✅ **Bootstrap Server Discovery**: Uses IANA's official bootstrap service
- ✅ **TLD-Specific Servers**: Routes queries to correct registries
- ✅ **vCard Parsing**: Properly parses contact information
- ✅ **Entity Handling**: Extracts registrar, registrant, admin, tech contacts
- ✅ **Date Parsing**: Handles ISO date formats correctly
- ✅ **Status Codes**: Properly interprets domain status

### **Code Location:**

The integrated framework is in:
```
domain_checker/rdap_client.py
```

### **How It Works:**

```python
from domain_checker import DomainChecker

async def example():
    checker = DomainChecker()
    
    # Your RDAP framework handles the lookup
    result = await checker.lookup_domain("example.com", "rdap")
    
    # Returns structured DomainInfo with:
    # - Registrar information
    # - Registration/expiration dates
    # - Name servers
    # - Contact information (from vCard)
    # - Status codes
    print(result.data.registrar)
    print(result.data.creation_date)
    print(result.data.name_servers)
```

### **CLI Usage:**

```bash
# Uses your RDAP framework automatically
domain-check lookup example.com --method rdap

# Compare methods (includes RDAP)
domain-check compare example.com
```

### **Technical Implementation:**

The integration includes these key components from your framework:

1. **Bootstrap URLs** (from `rdap-cli`):
   ```python
   BOOTSTRAP_URLS = {
       'dns': 'https://data.iana.org/rdap/dns.json',
       'ipv4': 'https://data.iana.org/rdap/ipv4.json',
       'ipv6': 'https://data.iana.org/rdap/ipv6.json',
       'asn': 'https://data.iana.org/rdap/asn.json'
   }
   ```

2. **Query Type Detection**:
   - Automatically identifies domains, IPs, or ASNs
   - Extracts TLDs for proper server routing

3. **Server Discovery**:
   - Downloads IANA bootstrap files
   - Caches bootstrap data
   - Matches TLDs to appropriate RDAP servers

4. **vCard Parsing**:
   - Extracts contact information
   - Handles full name, organization, email, phone, address

5. **Response Formatting**:
   - Converts RDAP JSON to DomainInfo model
   - Preserves all data in raw_data field

### **Benefits:**

- ✅ **Official Standards**: Uses IANA's official bootstrap service
- ✅ **Better Coverage**: Works with all TLDs that support RDAP
- ✅ **Structured Data**: Consistent, machine-readable responses
- ✅ **Modern Protocol**: RDAP is the future of domain registration data
- ✅ **Your Framework**: Uses your battle-tested RDAP implementation

### **Attribution:**

This integration is based on TheZacillac/rdap-cli:
- **Repository**: https://github.com/TheZacillac/rdap-cli
- **License**: MIT License
- **Description**: "A new CLI tool for RDAP that was created since the tool I was using before was getting depreciated - and this one just looks better"

### **Testing:**

Test the RDAP integration:

```bash
# Test RDAP lookup
domain-check lookup example.com --method rdap

# Test with different TLDs
domain-check lookup google.co.uk --method rdap
domain-check lookup example.org --method rdap

# Compare with WHOIS
domain-check compare example.com
```

## 🎉 **Summary**

Your domain checker now uses the **TheZacillac/rdap-cli framework** for all RDAP lookups, providing:
- Official IANA bootstrap server discovery
- Proper TLD-to-server routing
- Standardized RDAP protocol implementation
- Better coverage across all TLDs
- Modern, structured domain data

**The RDAP implementation is now powered by your proven framework!** 🌐

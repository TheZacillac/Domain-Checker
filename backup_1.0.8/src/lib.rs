use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::time::{timeout, Duration};
use reqwest::Client;
use url::Url;
use regex::Regex;
use chrono::{DateTime, Utc};
use anyhow::Result;

/// Domain information structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DomainInfo {
    pub domain: String,
    pub registrar: Option<String>,
    pub creation_date: Option<DateTime<Utc>>,
    pub expiration_date: Option<DateTime<Utc>>,
    pub updated_date: Option<DateTime<Utc>>,
    pub status: Vec<String>,
    pub name_servers: Vec<String>,
    pub registrant: Option<HashMap<String, String>>,
    pub admin_contact: Option<HashMap<String, String>>,
    pub tech_contact: Option<HashMap<String, String>>,
    pub raw_data: Option<String>,
    pub source: String,
}

/// Lookup result structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LookupResult {
    pub domain: String,
    pub success: bool,
    pub data: Option<DomainInfo>,
    pub error: Option<String>,
    pub lookup_time: f64,
    pub method: String,
}

/// High-performance RDAP client
pub struct RdapClient {
    client: Client,
    timeout: Duration,
    servers: HashMap<String, String>,
}

impl RdapClient {
    pub fn new(timeout_secs: u64) -> Self {
        let client = Client::builder()
            .user_agent("DomainChecker-Rust/1.0.0")
            .timeout(Duration::from_secs(timeout_secs))
            .build()
            .unwrap();

        let mut servers = HashMap::new();
        servers.insert("com".to_string(), "https://rdap.verisign.com/".to_string());
        servers.insert("net".to_string(), "https://rdap.verisign.com/".to_string());
        servers.insert("org".to_string(), "https://rdap.publicinterestregistry.net/".to_string());
        servers.insert("info".to_string(), "https://rdap.afilias.net/".to_string());
        servers.insert("biz".to_string(), "https://rdap.neustar.biz/".to_string());
        servers.insert("us".to_string(), "https://rdap.verisign.com/".to_string());
        servers.insert("uk".to_string(), "https://rdap.nominet.uk/".to_string());
        servers.insert("de".to_string(), "https://rdap.denic.de/".to_string());
        servers.insert("fr".to_string(), "https://rdap.afnic.fr/".to_string());
        servers.insert("it".to_string(), "https://rdap.nic.it/".to_string());
        servers.insert("es".to_string(), "https://rdap.nic.es/".to_string());
        servers.insert("nl".to_string(), "https://rdap.sidn.nl/".to_string());
        servers.insert("be".to_string(), "https://rdap.dns.be/".to_string());
        servers.insert("ch".to_string(), "https://rdap.nic.ch/".to_string());
        servers.insert("at".to_string(), "https://rdap.nic.at/".to_string());
        servers.insert("se".to_string(), "https://rdap.iis.se/".to_string());
        servers.insert("no".to_string(), "https://rdap.norid.no/".to_string());
        servers.insert("dk".to_string(), "https://rdap.dk-hostmaster.dk/".to_string());
        servers.insert("fi".to_string(), "https://rdap.traficom.fi/".to_string());
        servers.insert("pl".to_string(), "https://rdap.dns.pl/".to_string());
        servers.insert("cz".to_string(), "https://rdap.nic.cz/".to_string());
        servers.insert("sk".to_string(), "https://rdap.sk-nic.sk/".to_string());
        servers.insert("hu".to_string(), "https://rdap.nic.hu/".to_string());
        servers.insert("ro".to_string(), "https://rdap.rotld.ro/".to_string());
        servers.insert("bg".to_string(), "https://rdap.register.bg/".to_string());
        servers.insert("hr".to_string(), "https://rdap.dns.hr/".to_string());
        servers.insert("si".to_string(), "https://rdap.arnes.si/".to_string());
        servers.insert("ee".to_string(), "https://rdap.tld.ee/".to_string());
        servers.insert("lv".to_string(), "https://rdap.nic.lv/".to_string());
        servers.insert("lt".to_string(), "https://rdap.domreg.lt/".to_string());
        servers.insert("ie".to_string(), "https://rdap.weare.ie/".to_string());
        servers.insert("pt".to_string(), "https://rdap.dns.pt/".to_string());
        servers.insert("gr".to_string(), "https://rdap.forth.gr/".to_string());
        servers.insert("cy".to_string(), "https://rdap.nic.cy/".to_string());
        servers.insert("mt".to_string(), "https://rdap.nic.org.mt/".to_string());
        servers.insert("lu".to_string(), "https://rdap.dns.lu/".to_string());
        servers.insert("li".to_string(), "https://rdap.nic.li/".to_string());
        servers.insert("is".to_string(), "https://rdap.isnic.is/".to_string());
        servers.insert("fo".to_string(), "https://rdap.arnes.si/".to_string());
        servers.insert("gl".to_string(), "https://rdap.arnes.si/".to_string());
        servers.insert("ax".to_string(), "https://rdap.aland.fi/".to_string());
        servers.insert("ad".to_string(), "https://rdap.nic.ad/".to_string());
        servers.insert("mc".to_string(), "https://rdap.nic.mc/".to_string());
        servers.insert("sm".to_string(), "https://rdap.nic.sm/".to_string());
        servers.insert("va".to_string(), "https://rdap.nic.va/".to_string());
        servers.insert("gi".to_string(), "https://rdap.nic.gi/".to_string());
        servers.insert("gg".to_string(), "https://rdap.channelisles.net/".to_string());
        servers.insert("je".to_string(), "https://rdap.channelisles.net/".to_string());
        servers.insert("im".to_string(), "https://rdap.nic.im/".to_string());
        servers.insert("co".to_string(), "https://rdap.co/".to_string());
        servers.insert("ac".to_string(), "https://rdap.nic.ac/".to_string());
        servers.insert("me".to_string(), "https://rdap.nic.me/".to_string());
        servers.insert("tv".to_string(), "https://rdap.tv/".to_string());
        servers.insert("cc".to_string(), "https://rdap.verisign.com/".to_string());
        servers.insert("mobi".to_string(), "https://rdap.afilias.net/".to_string());
        servers.insert("name".to_string(), "https://rdap.verisign.com/".to_string());
        servers.insert("pro".to_string(), "https://rdap.afilias.net/".to_string());
        servers.insert("aero".to_string(), "https://rdap.information.aero/".to_string());
        servers.insert("coop".to_string(), "https://rdap.nic.coop/".to_string());
        servers.insert("museum".to_string(), "https://rdap.museum/".to_string());
        servers.insert("travel".to_string(), "https://rdap.travel/".to_string());
        servers.insert("jobs".to_string(), "https://rdap.employmedia.com/".to_string());
        servers.insert("cat".to_string(), "https://rdap.cat/".to_string());
        servers.insert("tel".to_string(), "https://rdap.tel/".to_string());
        servers.insert("asia".to_string(), "https://rdap.asia/".to_string());
        servers.insert("post".to_string(), "https://rdap.post/".to_string());
        servers.insert("xxx".to_string(), "https://rdap.icmregistry.com/".to_string());
        servers.insert("arpa".to_string(), "https://rdap.iana.org/".to_string());

        Self {
            client,
            timeout: Duration::from_secs(timeout_secs),
            servers,
        }
    }

    pub async fn lookup(&self, domain: &str) -> Result<LookupResult> {
        let start_time = std::time::Instant::now();
        
        match self.lookup_rdap(domain).await {
            Ok(domain_info) => {
                let lookup_time = start_time.elapsed().as_secs_f64();
                Ok(LookupResult {
                    domain: domain.to_string(),
                    success: true,
                    data: Some(domain_info),
                    error: None,
                    lookup_time,
                    method: "rdap".to_string(),
                })
            }
            Err(e) => {
                let lookup_time = start_time.elapsed().as_secs_f64();
                Ok(LookupResult {
                    domain: domain.to_string(),
                    success: false,
                    data: None,
                    error: Some(e.to_string()),
                    lookup_time,
                    method: "rdap".to_string(),
                })
            }
        }
    }

    async fn lookup_rdap(&self, domain: &str) -> Result<DomainInfo> {
        let tld = self.extract_tld(domain);
        let server = self.servers.get(&tld)
            .ok_or_else(|| anyhow::anyhow!("No RDAP server found for TLD: {}", tld))?;
        
        let url = format!("{}domain/{}", server, domain);
        let response = timeout(self.timeout, self.client.get(&url).send()).await??;
        
        if !response.status().is_success() {
            return Err(anyhow::anyhow!("HTTP error: {}", response.status()));
        }
        
        let rdap_data: serde_json::Value = response.json().await?;
        self.parse_rdap_data(domain, &rdap_data)
    }

    fn extract_tld(&self, domain: &str) -> String {
        domain.split('.').last().unwrap_or("").to_lowercase()
    }

    fn parse_rdap_data(&self, domain: &str, data: &serde_json::Value) -> Result<DomainInfo> {
        let mut domain_info = DomainInfo {
            domain: domain.to_string(),
            registrar: None,
            creation_date: None,
            expiration_date: None,
            updated_date: None,
            status: Vec::new(),
            name_servers: Vec::new(),
            registrant: None,
            admin_contact: None,
            tech_contact: None,
            raw_data: Some(data.to_string()),
            source: "rdap".to_string(),
        };

        // Parse events (dates)
        if let Some(events) = data.get("events").and_then(|v| v.as_array()) {
            for event in events {
                if let Some(action) = event.get("eventAction").and_then(|v| v.as_str()) {
                    if let Some(date_str) = event.get("eventDate").and_then(|v| v.as_str()) {
                        if let Ok(date) = DateTime::parse_from_rfc3339(date_str) {
                            match action.to_lowercase().as_str() {
                                "registration" => domain_info.creation_date = Some(date.with_timezone(&Utc)),
                                "expiration" => domain_info.expiration_date = Some(date.with_timezone(&Utc)),
                                "last changed" | "last update" => domain_info.updated_date = Some(date.with_timezone(&Utc)),
                                _ => {}
                            }
                        }
                    }
                }
            }
        }

        // Parse status
        if let Some(status_array) = data.get("status").and_then(|v| v.as_array()) {
            for status in status_array {
                if let Some(status_str) = status.as_str() {
                    domain_info.status.push(status_str.to_string());
                } else if let Some(status_obj) = status.as_object() {
                    if let Some(description) = status_obj.get("description").and_then(|v| v.as_str()) {
                        domain_info.status.push(description.to_string());
                    }
                }
            }
        }

        // Parse name servers
        if let Some(ns_array) = data.get("nameservers").and_then(|v| v.as_array()) {
            for ns in ns_array {
                if let Some(ldh_name) = ns.get("ldhName").and_then(|v| v.as_str()) {
                    domain_info.name_servers.push(ldh_name.to_lowercase());
                }
            }
        }

        // Parse entities (contacts)
        if let Some(entities) = data.get("entities").and_then(|v| v.as_array()) {
            for entity in entities {
                if let Some(roles) = entity.get("roles").and_then(|v| v.as_array()) {
                    for role in roles {
                        if let Some(role_str) = role.as_str() {
                            match role_str {
                                "registrant" => {
                                    domain_info.registrant = self.parse_vcard(entity);
                                }
                                "administrative" => {
                                    domain_info.admin_contact = self.parse_vcard(entity);
                                }
                                "technical" => {
                                    domain_info.tech_contact = self.parse_vcard(entity);
                                }
                                "registrar" => {
                                    if domain_info.registrar.is_none() {
                                        domain_info.registrar = self.extract_name_from_vcard(entity);
                                    }
                                }
                                _ => {}
                            }
                        }
                    }
                }
            }
        }

        Ok(domain_info)
    }

    fn parse_vcard(&self, entity: &serde_json::Value) -> Option<HashMap<String, String>> {
        let vcard = entity.get("vcardArray")?;
        let mut contact_info = HashMap::new();

        if let Some(vcard_array) = vcard.as_array() {
            if vcard_array.len() >= 3 {
                if let Some(properties) = vcard_array.get(2).and_then(|v| v.as_array()) {
                    for prop in properties {
                        if let Some(prop_array) = prop.as_array() {
                            if prop_array.len() >= 4 {
                                if let (Some(name), Some(value)) = (prop_array.get(0).and_then(|v| v.as_str()), prop_array.get(3).and_then(|v| v.as_str())) {
                                    match name {
                                        "fn" => { contact_info.insert("name".to_string(), value.to_string()); }
                                        "org" => { contact_info.insert("organization".to_string(), value.to_string()); }
                                        "email" => { contact_info.insert("email".to_string(), value.to_string()); }
                                        "tel" => { contact_info.insert("phone".to_string(), value.to_string()); }
                                        "adr" => { contact_info.insert("address".to_string(), value.to_string()); }
                                        _ => {}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        if contact_info.is_empty() { None } else { Some(contact_info) }
    }

    fn extract_name_from_vcard(&self, entity: &serde_json::Value) -> Option<String> {
        if let Some(name) = entity.get("name").and_then(|v| v.as_str()) {
            return Some(name.to_string());
        }
        
        if let Some(vcard) = entity.get("vcardArray") {
            if let Some(vcard_array) = vcard.as_array() {
                if vcard_array.len() >= 3 {
                    if let Some(properties) = vcard_array.get(2).and_then(|v| v.as_array()) {
                        for prop in properties {
                            if let Some(prop_array) = prop.as_array() {
                                if prop_array.len() >= 4 {
                                    if let (Some(name), Some(value)) = (prop_array.get(0).and_then(|v| v.as_str()), prop_array.get(3).and_then(|v| v.as_str())) {
                                        if name == "fn" {
                                            return Some(value.to_string());
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        None
    }
}

/// High-performance domain validation
pub fn validate_domain(domain: &str) -> Result<String> {
    if domain.is_empty() {
        return Err(anyhow::anyhow!("Domain cannot be empty"));
    }

    let mut domain = domain.to_string();
    
    // Remove protocol if present
    if domain.starts_with("http://") || domain.starts_with("https://") {
        if let Ok(url) = Url::parse(&domain) {
            domain = url.host_str().unwrap_or(&domain).to_string();
        }
    }
    
    // Remove www. prefix
    if domain.starts_with("www.") {
        domain = domain[4..].to_string();
    }
    
    // Remove trailing slash
    domain = domain.trim_end_matches('/').to_string();
    
    // Basic domain validation regex
    let domain_regex = Regex::new(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")?;
    
    if !domain_regex.is_match(&domain) {
        return Err(anyhow::anyhow!("Invalid domain format"));
    }
    
    // Check length
    if domain.len() > 253 {
        return Err(anyhow::anyhow!("Domain too long (max 253 characters)"));
    }
    
    // Check for valid TLD
    let parts: Vec<&str> = domain.split('.').collect();
    if parts.len() < 2 {
        return Err(anyhow::anyhow!("Domain must have at least one subdomain and TLD"));
    }
    
    let tld = parts.last().unwrap();
    if tld.len() < 2 {
        return Err(anyhow::anyhow!("TLD must be at least 2 characters"));
    }
    
    Ok(domain.to_lowercase())
}

/// Python module definition
#[pymodule]
fn domain_checker_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RdapClient>()?;
    m.add_function(wrap_pyfunction!(rust_validate_domain, m)?)?;
    m.add_function(wrap_pyfunction!(rust_lookup_domain, m)?)?;
    Ok(())
}

/// Python wrapper for domain validation
#[pyfunction]
fn rust_validate_domain(domain: &str) -> PyResult<String> {
    match validate_domain(domain) {
        Ok(validated) => Ok(validated),
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
    }
}

/// Python wrapper for domain lookup
#[pyfunction]
fn rust_lookup_domain(domain: &str, timeout_secs: u64) -> PyResult<LookupResult> {
    let rt = tokio::runtime::Runtime::new()?;
    let client = RdapClient::new(timeout_secs);
    
    rt.block_on(async {
        match client.lookup(domain).await {
            Ok(result) => Ok(result),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())),
        }
    })
}

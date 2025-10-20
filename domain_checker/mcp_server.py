"""
MCP server for domain checker
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    LoggingLevel
)

from .core import DomainChecker
from .models import LookupResult, BulkLookupResult
from .dig_client import DigClient
from .propagation_checker import DNSPropagationChecker


class DomainCheckerMCPServer:
    """MCP server for domain checker functionality"""
    
    def __init__(self):
        self.server = Server("domain-checker")
        self.checker = DomainChecker()
        self.dig_client = DigClient()
        self.propagation_checker = DNSPropagationChecker()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="lookup_domain",
                    description="Lookup domain information using WHOIS or RDAP",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain name to lookup"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["whois", "rdap", "auto"],
                                "description": "Lookup method (default: auto)",
                                "default": "auto"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["domain"]
                    }
                ),
                Tool(
                    name="lookup_domains_bulk",
                    description="Lookup multiple domains with rate limiting",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domains": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of domain names to lookup"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["whois", "rdap", "auto"],
                                "description": "Lookup method (default: auto)",
                                "default": "auto"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            },
                            "max_concurrent": {
                                "type": "integer",
                                "description": "Maximum concurrent lookups (default: 10)",
                                "default": 10
                            },
                            "rate_limit": {
                                "type": "number",
                                "description": "Rate limit in requests per second (default: 1.0)",
                                "default": 1.0
                            }
                        },
                        "required": ["domains"]
                    }
                ),
                Tool(
                    name="compare_methods",
                    description="Compare WHOIS and RDAP results for a domain",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain name to compare"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["domain"]
                    }
                ),
                Tool(
                    name="lookup_domains_from_file",
                    description="Lookup domains from a text file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file containing domains (one per line)"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["whois", "rdap", "auto"],
                                "description": "Lookup method (default: auto)",
                                "default": "auto"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            },
                            "max_concurrent": {
                                "type": "integer",
                                "description": "Maximum concurrent lookups (default: 10)",
                                "default": 10
                            },
                            "rate_limit": {
                                "type": "number",
                                "description": "Rate limit in requests per second (default: 1.0)",
                                "default": 1.0
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="dig_lookup",
                    description="Perform DNS lookup using DIG command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain name to lookup"
                            },
                            "record_type": {
                                "type": "string",
                                "enum": ["A", "AAAA", "MX", "NS", "SOA", "TXT", "ANY"],
                                "description": "DNS record type (default: A)",
                                "default": "A"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["domain"]
                    }
                ),
                Tool(
                    name="reverse_dns_lookup",
                    description="Perform reverse DNS lookup for an IP address",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ip_address": {
                                "type": "string",
                                "description": "IP address to lookup"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["ip_address"]
                    }
                ),
                Tool(
                    name="check_dns_propagation",
                    description="Check DNS propagation across regional resolvers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain name to check"
                            },
                            "record_type": {
                                "type": "string",
                                "enum": ["A", "AAAA", "MX", "NS", "SOA", "TXT"],
                                "description": "DNS record type (default: A)",
                                "default": "A"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["domain"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            
            if name == "lookup_domain":
                return await self._handle_lookup_domain(arguments)
            elif name == "lookup_domains_bulk":
                return await self._handle_lookup_domains_bulk(arguments)
            elif name == "compare_methods":
                return await self._handle_compare_methods(arguments)
            elif name == "lookup_domains_from_file":
                return await self._handle_lookup_domains_from_file(arguments)
            elif name == "dig_lookup":
                return await self._handle_dig_lookup(arguments)
            elif name == "reverse_dns_lookup":
                return await self._handle_reverse_dns_lookup(arguments)
            elif name == "check_dns_propagation":
                return await self._handle_check_dns_propagation(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def _handle_lookup_domain(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle single domain lookup"""
        domain = arguments.get("domain")
        method = arguments.get("method", "auto")
        timeout = arguments.get("timeout", 30)
        
        if not domain:
            return [TextContent(
                type="text",
                text="Error: domain parameter is required"
            )]
        
        try:
            checker = DomainChecker(timeout=timeout)
            result = await checker.lookup_domain(domain, method)
            
            # Format result as JSON
            result_data = {
                "domain": result.domain,
                "success": result.success,
                "method": result.method,
                "lookup_time": result.lookup_time,
                "error": result.error,
                "data": None
            }
            
            if result.data:
                result_data["data"] = {
                    "domain": result.data.domain,
                    "registrar": result.data.registrar,
                    "creation_date": result.data.creation_date.isoformat() if result.data.creation_date else None,
                    "expiration_date": result.data.expiration_date.isoformat() if result.data.expiration_date else None,
                    "updated_date": result.data.updated_date.isoformat() if result.data.updated_date else None,
                    "status": result.data.status,
                    "name_servers": result.data.name_servers,
                    "registrant": result.data.registrant,
                    "admin_contact": result.data.admin_contact,
                    "tech_contact": result.data.tech_contact,
                    "source": result.data.source
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def _handle_lookup_domains_bulk(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle bulk domain lookup"""
        domains = arguments.get("domains", [])
        method = arguments.get("method", "auto")
        timeout = arguments.get("timeout", 30)
        max_concurrent = arguments.get("max_concurrent", 10)
        rate_limit = arguments.get("rate_limit", 1.0)
        
        if not domains:
            return [TextContent(
                type="text",
                text="Error: domains parameter is required"
            )]
        
        try:
            checker = DomainChecker(
                timeout=timeout,
                max_concurrent=max_concurrent,
                rate_limit=rate_limit
            )
            results = await checker.lookup_domains_bulk(domains, method)
            
            # Format results as JSON
            results_data = {
                "total_domains": results.total_domains,
                "successful_lookups": results.successful_lookups,
                "failed_lookups": results.failed_lookups,
                "total_time": results.total_time,
                "average_time_per_domain": results.average_time_per_domain,
                "results": []
            }
            
            for result in results.results:
                result_data = {
                    "domain": result.domain,
                    "success": result.success,
                    "method": result.method,
                    "lookup_time": result.lookup_time,
                    "error": result.error,
                    "data": None
                }
                
                if result.data:
                    result_data["data"] = {
                        "domain": result.data.domain,
                        "registrar": result.data.registrar,
                        "creation_date": result.data.creation_date.isoformat() if result.data.creation_date else None,
                        "expiration_date": result.data.expiration_date.isoformat() if result.data.expiration_date else None,
                        "updated_date": result.data.updated_date.isoformat() if result.data.updated_date else None,
                        "status": result.data.status,
                        "name_servers": result.data.name_servers,
                        "registrant": result.data.registrant,
                        "admin_contact": result.data.admin_contact,
                        "tech_contact": result.data.tech_contact,
                        "source": result.data.source
                    }
                
                results_data["results"].append(result_data)
            
            return [TextContent(
                type="text",
                text=json.dumps(results_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def _handle_compare_methods(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle method comparison"""
        domain = arguments.get("domain")
        timeout = arguments.get("timeout", 30)
        
        if not domain:
            return [TextContent(
                type="text",
                text="Error: domain parameter is required"
            )]
        
        try:
            checker = DomainChecker(timeout=timeout)
            comparison = await checker.compare_methods(domain)
            
            # Format comparison as JSON
            comparison_data = {
                "domain": comparison["domain"],
                "whois": {
                    "success": comparison["whois"].success,
                    "method": comparison["whois"].method,
                    "lookup_time": comparison["whois"].lookup_time,
                    "error": comparison["whois"].error,
                    "data": None
                },
                "rdap": {
                    "success": comparison["rdap"].success,
                    "method": comparison["rdap"].method,
                    "lookup_time": comparison["rdap"].lookup_time,
                    "error": comparison["rdap"].error,
                    "data": None
                },
                "comparison": comparison["comparison"]
            }
            
            # Add data for both methods
            for method in ["whois", "rdap"]:
                result = comparison[method]
                if result.data:
                    comparison_data[method]["data"] = {
                        "domain": result.data.domain,
                        "registrar": result.data.registrar,
                        "creation_date": result.data.creation_date.isoformat() if result.data.creation_date else None,
                        "expiration_date": result.data.expiration_date.isoformat() if result.data.expiration_date else None,
                        "updated_date": result.data.updated_date.isoformat() if result.data.updated_date else None,
                        "status": result.data.status,
                        "name_servers": result.data.name_servers,
                        "registrant": result.data.registrant,
                        "admin_contact": result.data.admin_contact,
                        "tech_contact": result.data.tech_contact,
                        "source": result.data.source
                    }
            
            return [TextContent(
                type="text",
                text=json.dumps(comparison_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def _handle_lookup_domains_from_file(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle lookup from file"""
        file_path = arguments.get("file_path")
        method = arguments.get("method", "auto")
        timeout = arguments.get("timeout", 30)
        max_concurrent = arguments.get("max_concurrent", 10)
        rate_limit = arguments.get("rate_limit", 1.0)
        
        if not file_path:
            return [TextContent(
                type="text",
                text="Error: file_path parameter is required"
            )]
        
        try:
            checker = DomainChecker(
                timeout=timeout,
                max_concurrent=max_concurrent,
                rate_limit=rate_limit
            )
            results = await checker.lookup_domains_from_file(file_path, method)
            
            # Format results as JSON (same as bulk lookup)
            results_data = {
                "total_domains": results.total_domains,
                "successful_lookups": results.successful_lookups,
                "failed_lookups": results.failed_lookups,
                "total_time": results.total_time,
                "average_time_per_domain": results.average_time_per_domain,
                "results": []
            }
            
            for result in results.results:
                result_data = {
                    "domain": result.domain,
                    "success": result.success,
                    "method": result.method,
                    "lookup_time": result.lookup_time,
                    "error": result.error,
                    "data": None
                }
                
                if result.data:
                    result_data["data"] = {
                        "domain": result.data.domain,
                        "registrar": result.data.registrar,
                        "creation_date": result.data.creation_date.isoformat() if result.data.creation_date else None,
                        "expiration_date": result.data.expiration_date.isoformat() if result.data.expiration_date else None,
                        "updated_date": result.data.updated_date.isoformat() if result.data.updated_date else None,
                        "status": result.data.status,
                        "name_servers": result.data.name_servers,
                        "registrant": result.data.registrant,
                        "admin_contact": result.data.admin_contact,
                        "tech_contact": result.data.tech_contact,
                        "source": result.data.source
                    }
                
                results_data["results"].append(result_data)
            
            return [TextContent(
                type="text",
                text=json.dumps(results_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def _handle_dig_lookup(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle DIG lookup"""
        domain = arguments.get("domain")
        record_type = arguments.get("record_type", "A")
        timeout = arguments.get("timeout", 30)
        
        if not domain:
            return [TextContent(
                type="text",
                text="Error: domain parameter is required"
            )]
        
        try:
            dig_client = DigClient(timeout=timeout)
            result = await dig_client.lookup(domain, record_type)
            
            # Format result as JSON
            result_data = {
                "domain": result.domain,
                "source": result.source,
                "name_servers": result.name_servers,
                "raw_data": result.raw_data
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def _handle_reverse_dns_lookup(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle reverse DNS lookup"""
        ip_address = arguments.get("ip_address")
        timeout = arguments.get("timeout", 30)
        
        if not ip_address:
            return [TextContent(
                type="text",
                text="Error: ip_address parameter is required"
            )]
        
        try:
            dig_client = DigClient(timeout=timeout)
            result = await dig_client.reverse_lookup(ip_address)
            
            # Format result as JSON
            result_data = {
                "ip_address": ip_address,
                "source": result.source,
                "name_servers": result.name_servers,
                "raw_data": result.raw_data
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def _handle_check_dns_propagation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle DNS propagation check"""
        domain = arguments.get("domain")
        record_type = arguments.get("record_type", "A")
        timeout = arguments.get("timeout", 30)
        
        if not domain:
            return [TextContent(
                type="text",
                text="Error: domain parameter is required"
            )]
        
        try:
            propagation_checker = DNSPropagationChecker(timeout=timeout)
            result = await propagation_checker.check_propagation(domain, record_type)
            
            # Format result as JSON
            result_data = {
                "domain": result.domain,
                "record_type": result.record_type,
                "total_resolvers": result.total_resolvers,
                "successful_queries": result.successful,
                "failed_queries": result.failed,
                "unique_ips": list(result.unique_ips),
                "propagation_percentage": result.propagation_percentage,
                "is_fully_propagated": result.fully_propagated,
                "total_time": result.total_time,
                "results": [
                    {
                        "resolver": r.resolver_name,
                        "resolver_ip": r.resolver_ip,
                        "location": r.location,
                        "success": r.success,
                        "resolved_ips": r.resolved_ips,
                        "response_time": r.lookup_time,
                        "error": r.error
                    } for r in result.results
                ]
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result_data, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="domain-checker",
                        server_version="1.0.6",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )


async def main():
    """Main entry point for MCP server"""
    server = DomainCheckerMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

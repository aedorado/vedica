#!/usr/bin/env python
"""
Command-line interface for Vedic Astrology Chart Query Engine.
Provides interactive and batch query capabilities.
"""

import sys
import logging
from typing import Optional
from tabulate import tabulate
import json

from query_engine import create_engine
from query_parser import parse_query
from config import LOG_FORMAT, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


class CLI:
    """Command-line interface for query engine"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize CLI with database"""
        self.engine = create_engine(db_path)
        self.running = False
    
    def _parse_raw_input(self, raw_input: str) -> tuple:
        """Parse raw_input to extract name, birth_time, location"""
        if not raw_input:
            return ("N/A", "N/A", "N/A")
        
        parts = [p.strip() for p in raw_input.split("|")]
        
        name = parts[0] if len(parts) > 0 else "N/A"
        birth_time = parts[1] if len(parts) > 1 else "N/A"
        location = parts[2] if len(parts) > 2 else "N/A"
        
        return (name, birth_time, location)
    
    def print_header(self):
        """Print CLI header"""
        print("\n" + "="*70)
        print(" 🔍 Vedic Astrology Chart Query Engine")
        print("="*70)
        print(" Type 'help' for commands or 'exit' to quit\n")
    
    def print_help(self):
        """Print help message"""
        help_text = """
Available Commands:
  search <pattern>      - Search charts matching pattern
                         Examples: "(Su 11H)", "(Ca Lagna)", "(Su 11H) AND (Ca Lagna)"
  
  list [limit]          - List all charts (default limit: 50)
  
  info <chart_id>       - Show detailed info for a chart
  
  validate <pattern>    - Validate a query pattern without searching
  
  pattern-info <pattern> - Show parsed pattern structure (debug)
  
  stats                 - Show database statistics
  
  help                  - Show this help message
  
  exit / quit           - Exit the program

Examples:
  > search (Su 11H)
  > search (Ca Lagna) AND (Mo 2H)
  > search (Aq 5H) OR (Ra 8H)
  > info 1
  > list 100
  > validate (Su 11H) AND (Ca Lagna)
        """
        print(help_text)
    
    def cmd_search(self, args: list):
        """Execute search command"""
        if not args:
            print("❌ Error: Pattern required")
            print("   Usage: search <pattern>")
            print("   Example: search (Su 11H) AND (Ca Lagna)")
            return
        
        pattern = " ".join(args)
        
        try:
            print(f"\n🔍 Searching for: {pattern}")
            results, total = self.engine.search(pattern)
            
            if not results:
                print(f"✅ No charts found matching this pattern ({total} total in database)")
                return
            
            print(f"✅ Found {len(results)} matching charts (showing {len(results)} of {total})\n")
            
            # Format results table
            table_data = []
            for r in results:
                name, birth_time, location = self._parse_raw_input(r.raw_input)
                table_data.append([r.chart_id, name, birth_time, location])
            
            headers = ["ID", "Name", "Birth Time", "Location"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            print(f"\n💡 Tip: Use 'info <id>' to see full details for a chart")
        
        except Exception as e:
            print(f"❌ Search failed: {e}")
            logger.exception("Search error")
    
    def cmd_list(self, args: list):
        """Execute list command"""
        limit = 50
        if args and args[0].isdigit():
            limit = int(args[0])
        
        try:
            print(f"\n📋 Listing charts (limit: {limit})...\n")
            results, total = self.engine.list_all_charts(limit=limit)
            
            if not results:
                print("No charts in database")
                return
            
            print(f"Showing {len(results)} of {total} total charts\n")
            
            table_data = []
            for r in results:
                name, birth_time, location = self._parse_raw_input(r.raw_input)
                table_data.append([r.chart_id, name, birth_time, location])
            
            headers = ["ID", "Name", "Birth Time", "Location"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        except Exception as e:
            print(f"❌ List failed: {e}")
            logger.exception("List error")
    
    def cmd_info(self, args: list):
        """Execute info command"""
        if not args or not args[0].isdigit():
            print("❌ Error: Chart ID required")
            print("   Usage: info <chart_id>")
            return
        
        chart_id = int(args[0])
        
        try:
            details = self.engine.get_chart_details(chart_id)
            
            if not details:
                print(f"❌ Chart {chart_id} not found")
                return
            
            print(f"\n📊 Chart Details (ID: {chart_id})\n")
            print(f"Name:       {details['name'] or 'N/A'}")
            print(f"Birth Time: {details['birth_time'] or 'N/A'}")
            print(f"Location:   {details['location'] or 'N/A'}")
            print(f"Created:    {details['created_at'] or 'N/A'}")
            print(f"Raw Input:  {details['raw_input']}")
            
            if details['planet_data']:
                print(f"\n🪐 Planet Data Available: {len(details['planet_data'])} planets")
                for planet, data in list(details['planet_data'].items())[:3]:
                    print(f"   - {planet}")
            
            if details['house_data']:
                print(f"\n🏠 House Data Available: {len(details['house_data'])} houses")
        
        except Exception as e:
            print(f"❌ Info failed: {e}")
            logger.exception("Info error")
    
    def cmd_validate(self, args: list):
        """Execute validate command"""
        if not args:
            print("❌ Error: Pattern required")
            print("   Usage: validate <pattern>")
            return
        
        pattern = " ".join(args)
        
        try:
            self.engine.validate_pattern(pattern)
            print(f"✅ Pattern is valid: {pattern}")
        
        except Exception as e:
            print(f"❌ Invalid pattern: {e}")
    
    def cmd_pattern_info(self, args: list):
        """Execute pattern-info command (debug)"""
        if not args:
            print("❌ Error: Pattern required")
            print("   Usage: pattern-info <pattern>")
            return
        
        pattern = " ".join(args)
        
        try:
            info = self.engine.get_pattern_info(pattern)
            print(f"\n📐 Pattern Analysis\n")
            print(f"Pattern:     {info['pattern']}")
            print(f"Parsed AST:  {info['parsed']}")
            print(f"Is Compound: {info['is_compound']}")
            if info['operator']:
                print(f"Operator:    {info['operator']}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def cmd_stats(self, args: list):
        """Execute stats command"""
        try:
            stats = self.engine.statistics()
            print(f"\n📊 Database Statistics\n")
            print(f"Database:              {stats['database_path']}")
            print(f"Total Charts:          {stats['total_charts']}")
            print(f"Max Results per Query: {stats['max_results_per_query']}")
        
        except Exception as e:
            print(f"❌ Stats failed: {e}")
    
    def process_command(self, line: str):
        """Process a single command line"""
        line = line.strip()
        
        if not line:
            return
        
        # Split command and args
        parts = line.split(None, 1)
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        # Dispatch commands
        if command in ("exit", "quit"):
            print("\n👋 Goodbye!\n")
            self.running = False
        
        elif command == "help":
            self.print_help()
        
        elif command == "search":
            # Re-join args because pattern might have spaces
            args = [parts[1]] if len(parts) > 1 else []
            self.cmd_search(args)
        
        elif command == "list":
            self.cmd_list(args)
        
        elif command == "info":
            self.cmd_info(args)
        
        elif command == "validate":
            args = [parts[1]] if len(parts) > 1 else []
            self.cmd_validate(args)
        
        elif command == "pattern-info":
            args = [parts[1]] if len(parts) > 1 else []
            self.cmd_pattern_info(args)
        
        elif command == "stats":
            self.cmd_stats(args)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("   Type 'help' for available commands")
    
    def run_interactive(self):
        """Run interactive CLI loop"""
        self.print_header()
        self.running = True
        
        try:
            while self.running:
                try:
                    user_input = input("vedica> ").strip()
                    if user_input:
                        self.process_command(user_input)
                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted. Goodbye!\n")
                    break
                except Exception as e:
                    logger.exception(f"Unexpected error: {e}")
                    print(f"❌ Unexpected error: {e}")
        
        except EOFError:
            print("\n👋 Goodbye!\n")
    
    def run_command(self, command_line: str):
        """Run a single command and exit"""
        try:
            self.process_command(command_line)
        except Exception as e:
            logger.exception(f"Command error: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)


def main():
    """Main entry point"""
    cli = CLI()
    
    # Check if command line arguments provided
    if len(sys.argv) > 1:
        # Run command from arguments
        command = " ".join(sys.argv[1:])
        cli.run_command(command)
    else:
        # Run interactive mode
        cli.run_interactive()


if __name__ == "__main__":
    main()

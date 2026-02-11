#!/usr/bin/env python3
"""
CL Option Zone - Main Calculator
"""

import sys
import os
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.data_loader import DataLoader
from core.volume_profile import VolumeProfileAnalyzer

console = Console()

def main():
    parser = argparse.ArgumentParser(description="CL Volume Profile & Option Zone Calculator")
    parser.add_argument("--symbol", type=str, default="CL=F", help="Ticker Symbol (default: CL=F)")
    parser.add_argument("--period", type=str, default="5d", help="Lookback period (e.g. 5d, 1mo)")
    parser.add_argument("--bins", type=int, default=150, help="Number of price bins")
    args = parser.parse_args()

    console.print(Panel.fit(f"[bold gold1]📊 CL Option Zone Analyzer[/]\n[dim]Target: {args.symbol} | Period: {args.period}[/]", border_style="gold1"))

    # 1. Load Data
    loader = DataLoader(args.symbol)
    try:
        with console.status("[bold green]Fetching Data...[/]"):
            df = loader.fetch_data(period=args.period, interval="5m") # Use 5m for granularity
            current_price = loader.get_latest_price()
            
        console.print(f"✅ Data loaded: [cyan]{len(df)}[/] candles. Last Price: [bold white]{current_price:.2f}[/]")
        
    except Exception as e:
        console.print(f"[red]Error loading data: {e}[/]")
        return

    # 2. Analyze
    try:
        with console.status("[bold blue]Calculating Volume Profile...[/]"):
            analyzer = VolumeProfileAnalyzer(df, n_bins=args.bins)
            results = analyzer.calculate()
            
    except Exception as e:
        console.print(f"[red]Analysis Error: {e}[/]")
        import traceback
        console.print(traceback.format_exc())
        return

    # 3. Report
    display_report(current_price, results)

def display_report(price, res):
    # Determine Trend/Zone
    zone_status = "[bold green]INSIDE VALUE[/]"
    if price > res['VAH']:
        zone_status = "[bold red]ABOVE VALUE (Bullish/Overextended)[/]"
    elif price < res['VAL']:
        zone_status = "[bold blue]BELOW VALUE (Bearish/Discount)[/]"

    # Main Table
    table = Table(title="🛡️ Key Levels & Zones", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Price Level", style="yellow", justify="right")
    table.add_column("Relation to Spot", style="white")

    def get_diff(level):
        diff = price - level
        color = "red" if diff < 0 else "green"
        return f"[{color}]{diff:+.2f}[/]"

    table.add_row("Current Price", f"{price:.2f}", "-")
    table.add_row("VAH (Value Area High)", f"{res['VAH']}", get_diff(res['VAH']))
    table.add_row("POC (Point of Control)", f"[bold]{res['POC']}[/]", get_diff(res['POC']))
    table.add_row("VAL (Value Area Low)", f"{res['VAL']}", get_diff(res['VAL']))

    console.print(table)
    
    # Strategy Signal
    strat_panel = f"""
    [bold underline]Market Context[/]: {zone_status}
    
    [bold]🎯 Strategic Bias:[/bold]
    • [bold yellow]POC ({res['POC']})[/]: Mean Reversion Target.
    • [bold red]VAH ({res['VAH']})[/]: Resistance / Breakout Level.
    • [bold green]VAL ({res['VAL']})[/]: Support / Breakdown Level.
    
    [bold]⚠️ High Volume Nodes (Structural Levels):[/]
    {', '.join([str(x) for x in res['HVNs']])}
    
    [bold]🚀 Low Volume Nodes (Liquidity Voids):[/]
    {', '.join([str(x) for x in res['LVNs']])}
    """
    
    console.print(Panel(strat_panel, title="📊 Quantitative Analysis", border_style="cyan"))

if __name__ == "__main__":
    main()

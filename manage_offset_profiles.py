#!/usr/bin/env python3
"""
Offset Profile Management Tool

This tool provides convenient management of offset profiles for different paper sizes and printers.
Offset profiles store X/Y offset values that can be applied when creating PDFs to compensate
for printer alignment issues.

Usage examples:
    # List all profiles
    python manage_offset_profiles.py --list

    # Create a new profile
    python manage_offset_profiles.py --create letter_hp --x 5 --y -3 --paper letter --desc "HP printer with letter paper"

    # Set default profile
    python manage_offset_profiles.py --set-default letter_hp

    # Delete a profile
    python manage_offset_profiles.py --delete letter_hp

    # Show detailed info about a profile
    python manage_offset_profiles.py --info letter_hp
"""

import click
import json
from utilities import (
    load_offset_profiles,
    save_offset_profile,
    delete_offset_profile,
    set_default_offset_profile,
    list_offset_profiles
)


@click.command()
@click.option("--list", "list_all", default=False, is_flag=True, help="List all offset profiles.")
@click.option("--create", help="Create a new offset profile with the given name.")
@click.option("--delete", help="Delete an offset profile.")
@click.option("--info", help="Show detailed information about a profile.")
@click.option("--set-default", help="Set a profile as the default.")
@click.option("--x", "--x_offset", type=int, help="X-axis offset (required when creating).")
@click.option("--y", "--y_offset", type=int, help="Y-axis offset (required when creating).")
@click.option("--paper", help="Paper size for the profile (e.g., 'letter', 'a4', 'tabloid').")
@click.option("--desc", help="Description for the profile.")
@click.option("--export", help="Export all profiles to a JSON file.")
@click.option("--import", "import_file", help="Import profiles from a JSON file.")

def manage_profiles(list_all, create, delete, info, set_default, x, y, paper, desc, export, import_file):
    """Manage offset profiles for different paper sizes and printer setups."""
    
    if list_all:
        profiles = load_offset_profiles()
        if not profiles.profiles:
            print("No offset profiles found.")
            print("\nCreate your first profile with:")
            print("  python manage_offset_profiles.py --create profile_name --x X_OFFSET --y Y_OFFSET --paper PAPER_SIZE")
        else:
            print("Available offset profiles:")
            print("=" * 50)
            if profiles.default_profile:
                print(f"Default profile: {profiles.default_profile}")
            else:
                print("Default profile: None")
            print()
            
            for name, profile in profiles.profiles.items():
                default_marker = " ★" if name == profiles.default_profile else ""
                print(f"📋 {name}{default_marker}")
                print(f"   Description: {profile.description}")
                print(f"   Paper Size:  {profile.paper_size or 'Not specified'}")
                print(f"   Offsets:     x={profile.x_offset:+d}, y={profile.y_offset:+d}")
                print(f"   Created:     {profile.created_at}")
                print()
        return
    
    if create:
        if x is None or y is None:
            print("Error: Both --x and --y are required when creating a profile.")
            print("Example: python manage_offset_profiles.py --create letter_hp --x 5 --y -3 --paper letter")
            return
        
        save_offset_profile(
            name=create,
            x_offset=x,
            y_offset=y,
            paper_size=paper or "",
            description=desc or f"Offset profile for {paper or 'custom setup'}"
        )
        return
    
    if delete:
        if click.confirm(f"Are you sure you want to delete profile '{delete}'?"):
            delete_offset_profile(delete)
        return
    
    if info:
        profiles = load_offset_profiles()
        if info in profiles.profiles:
            profile = profiles.profiles[info]
            default_marker = " (default)" if info == profiles.default_profile else ""
            
            print(f"Profile: {info}{default_marker}")
            print("=" * (len(info) + 10))
            print(f"Description:  {profile.description}")
            print(f"Paper Size:   {profile.paper_size or 'Not specified'}")
            print(f"X Offset:     {profile.x_offset:+d} pixels")
            print(f"Y Offset:     {profile.y_offset:+d} pixels")
            print(f"Created:      {profile.created_at}")
            print()
            print("Usage in create_pdf.py:")
            print(f"  python create_pdf.py --offset_profile {info} [other options...]")
        else:
            print(f"Profile '{info}' not found.")
        return
    
    if set_default:
        set_default_offset_profile(set_default)
        return
    
    if export:
        profiles = load_offset_profiles()
        with open(export, 'w') as f:
            f.write(profiles.model_dump_json(indent=2))
        print(f"Exported {len(profiles.profiles)} profiles to {export}")
        return
    
    if import_file:
        try:
            with open(import_file, 'r') as f:
                data = json.load(f)
            
            # Import profiles (this would need additional implementation)
            print(f"Import functionality would load profiles from {import_file}")
            print("Note: Import functionality not yet implemented")
        except Exception as e:
            print(f"Error importing profiles: {e}")
        return
    
    # If no specific action, show help
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    print("\nCommon examples:")
    print("  # List all profiles")
    print("  python manage_offset_profiles.py --list")
    print()
    print("  # Create a new profile for letter paper")
    print("  python manage_offset_profiles.py --create letter_office --x 5 --y -2 --paper letter --desc 'Office printer'")
    print()
    print("  # Use a profile in create_pdf")
    print("  python create_pdf.py --offset_profile letter_office [other options...]")


if __name__ == '__main__':
    manage_profiles()
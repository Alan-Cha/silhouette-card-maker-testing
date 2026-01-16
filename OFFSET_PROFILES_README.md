# Offset Profile System Documentation

The offset profile system allows you to save and manage multiple offset configurations for different paper sizes and printer setups. This is useful when you print on different printers or paper sizes that require different alignment adjustments.

## Overview

**What are offsets?**
Offsets are X/Y adjustments applied to every other page of your PDF to compensate for printer alignment issues. When printing double-sided cards, some printers may have slight misalignment between the front and back sides.

**How offsets work:**
- Page 1 (front): No offset applied
- Page 2 (back): Offset applied
- Page 3 (front): No offset applied  
- Page 4 (back): Offset applied
- And so on...

## Profile System Features

### 🆕 **New Profile-Based System**
- Save multiple named offset profiles
- Organize by paper size, printer, or any custom naming scheme
- Set a default profile for quick access
- Include descriptions and metadata

### 🔄 **Backwards Compatibility**
- Legacy single-offset system still works
- Existing `--load_offset` flag unchanged
- Old `data/offset_data.json` files still supported

## Usage Examples

### 1. Finding Your Offset Values

First, create a test PDF and use `offset_pdf.py` to find the right values:

```bash
# Create a test PDF
python create_pdf.py game/front game/back --paper_size letter --card_size standard

# Test different offset values
python offset_pdf.py --x_offset 5 --y_offset -3
# Check the output, adjust values as needed
python offset_pdf.py --x_offset 3 --y_offset -2
```

### 2. Saving Offset Profiles

Once you find good values, save them as a named profile:

```bash
# Save a profile for your office printer with letter paper
python offset_pdf.py --x_offset 5 --y_offset -3 --save_profile "letter_office" --paper_size letter --description "Office HP printer with letter paper"

# Save a profile for A4 paper
python offset_pdf.py --x_offset 2 --y_offset -1 --save_profile "a4_home" --paper_size a4 --description "Home printer with A4 paper"

# Save a profile for tabloid/A3 paper
python offset_pdf.py --x_offset 8 --y_offset -5 --save_profile "tabloid_print_shop" --paper_size tabloid --description "Print shop large format printer"
```

### 3. Managing Profiles

Use the management tool for easier profile administration:

```bash
# List all profiles
python manage_offset_profiles.py --list

# Create a new profile directly
python manage_offset_profiles.py --create "letter_hp" --x 4 --y -2 --paper letter --desc "HP LaserJet with letter paper"

# Set a default profile
python manage_offset_profiles.py --set-default letter_office

# Get detailed info about a profile
python manage_offset_profiles.py --info letter_office

# Delete a profile
python manage_offset_profiles.py --delete old_profile
```

### 4. Using Profiles in PDF Creation

Apply offset profiles when creating PDFs:

```bash
# Use a specific profile
python create_pdf.py game/front game/back --offset_profile letter_office --paper_size letter --card_size standard

# Use the default profile
python create_pdf.py game/front game/back --offset_profile default --paper_size letter --card_size standard

# Still works: legacy offset loading
python create_pdf.py game/front game/back --load_offset --paper_size letter --card_size standard
```

## Profile Management Commands

### offset_pdf.py (Enhanced)
```bash
# New profile options
--save_profile NAME          # Save as named profile
--paper_size SIZE           # Associate with paper size  
--description TEXT          # Add description
--list_profiles            # List all profiles
--delete_profile NAME      # Delete a profile
--set_default NAME         # Set default profile

# Legacy options (still work)
--save                     # Save to legacy single-offset file
```

### manage_offset_profiles.py (New Tool)
```bash
--list                     # List all profiles
--create NAME              # Create new profile
--delete NAME              # Delete profile  
--info NAME                # Show profile details
--set-default NAME         # Set as default
--x X_OFFSET               # X offset (for --create)
--y Y_OFFSET               # Y offset (for --create)
--paper SIZE               # Paper size
--desc TEXT                # Description
```

### create_pdf.py (Enhanced)
```bash
# New profile option
--offset_profile NAME      # Use named profile ("default" for default profile)

# Legacy option (still works)
--load_offset             # Use legacy single-offset file
```

## File Structure

The new system creates these files:

```
data/
├── offset_profiles.json   # New: Named profiles
└── offset_data.json      # Legacy: Single offset (backwards compatibility)
```

### Profile Data Structure
```json
{
  "profiles": {
    "letter_office": {
      "name": "letter_office",
      "description": "Office HP printer with letter paper",
      "x_offset": 5,
      "y_offset": -3,
      "paper_size": "letter",
      "created_at": "2024-01-15T10:30:00"
    }
  },
  "default_profile": "letter_office"
}
```

## Recommended Workflow

### For Different Paper Sizes:
1. **Letter paper**: Create `letter_[printer_name]` profiles
2. **A4 paper**: Create `a4_[printer_name]` profiles  
3. **Tabloid/A3**: Create `tabloid_[printer_name]` or `a3_[printer_name]` profiles

### Naming Conventions:
- `{paper_size}_{location}`: `letter_office`, `a4_home`
- `{paper_size}_{printer_model}`: `letter_hp_laserjet`, `a4_canon_pixma`
- `{purpose}_{paper_size}`: `prototyping_letter`, `final_print_tabloid`

### Example Setup:
```bash
# Home setup
python offset_pdf.py --x_offset 3 --y_offset -1 --save_profile "letter_home" --paper_size letter --description "Home inkjet printer"
python offset_pdf.py --x_offset 2 --y_offset -1 --save_profile "a4_home" --paper_size a4 --description "Home inkjet printer A4"

# Office setup  
python offset_pdf.py --x_offset 5 --y_offset -3 --save_profile "letter_office" --paper_size letter --description "Office laser printer"

# Print shop
python offset_pdf.py --x_offset 8 --y_offset -5 --save_profile "tabloid_print_shop" --paper_size tabloid --description "Professional print shop"

# Set most common as default
python manage_offset_profiles.py --set-default letter_home
```

## Migration from Legacy System

If you have existing offset data in `data/offset_data.json`:

1. **Your existing workflows continue to work** - no changes needed
2. **To migrate to profiles**: Note your current offset values and create a profile:
   ```bash
   # Check current legacy values
   python offset_pdf.py --list_profiles  # (this shows legacy values too)
   
   # Create a profile with those values
   python manage_offset_profiles.py --create "my_main_setup" --x [current_x] --y [current_y] --paper [your_paper_size]
   ```

## Troubleshooting

### Profile not found
```bash
# List available profiles
python manage_offset_profiles.py --list

# Check exact name spelling
python manage_offset_profiles.py --info profile_name
```

### No default profile set
```bash
# Set a default
python manage_offset_profiles.py --set-default profile_name

# Or use specific profile name instead of "default"
python create_pdf.py --offset_profile profile_name [other options...]
```

### Legacy vs Profile conflicts
- `--load_offset` and `--offset_profile` can both be used, but `--offset_profile` takes priority
- If both are specified, the profile system will be used and legacy loading will be skipped

This system provides much more flexibility while maintaining full backwards compatibility with existing workflows.
import json
import os


def parse_dimension(dim_str):
    if dim_str.endswith("in"):
        return float(dim_str[:-2]), "in"
    elif dim_str.endswith("mm"):
        return float(dim_str[:-2]), "mm"
    raise ValueError(f"Unknown unit in '{dim_str}'")


def to_inches(value, unit):
    if unit == "in":
        return value
    return value / 25.4


def to_mm(value, unit):
    if unit == "mm":
        return value
    return value * 25.4


def format_number(n):
    rounded = round(n, 3)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def generate_tables():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    layouts_path = os.path.join(script_dir, "assets", "layouts.json")

    with open(layouts_path) as f:
        data = json.load(f)

    card_sizes = data["card_sizes"]
    paper_sizes = data["paper_sizes"]
    layouts = data["layouts"]

    paper_order = ["letter", "tabloid", "a4", "a3", "arch_b"]

    # Card size order for table 2: largest dimension first, then second dimension
    def card_size_sort_key(name):
        info = card_sizes[name]
        w_val, w_unit = parse_dimension(info["width"])
        h_val, h_unit = parse_dimension(info["height"])
        w_mm = to_mm(w_val, w_unit)
        h_mm = to_mm(h_val, h_unit)
        long_side = max(w_mm, h_mm)
        short_side = min(w_mm, h_mm)
        return (-long_side, -short_side, name)

    card_order_alpha = sorted(card_sizes.keys(), key=lambda n: (n[0].isdigit(), n))
    card_order_by_size = sorted(card_sizes.keys(), key=card_size_sort_key)

    # Table 1: Layouts (alphabetical)
    print("| Format |", " | ".join(f"`{p}`" for p in paper_order), "|")
    print("|---|" + "---|" * len(paper_order))

    for card in card_order_alpha:
        cells = []
        for paper in paper_order:
            if paper in layouts and card in layouts[paper]:
                layout = layouts[paper][card]
                r = layout["num_rows"]
                c = layout["num_cols"]
                cells.append(f"{c}x{r} ({c * r})")
            else:
                cells.append("❌")
        print(f"| `{card}` | {' | '.join(cells)} |")

    print()

    # Table 2: Card sizes
    print("| Card size | Inches | Millimeters | Aspect Ratio | Notes |")
    print("| --- | --- | --- | --- | --- |")

    for card in card_order_by_size:
        info = card_sizes[card]
        w_val, w_unit = parse_dimension(info["width"])
        h_val, h_unit = parse_dimension(info["height"])

        native_unit = w_unit

        w_in = to_inches(w_val, w_unit)
        h_in = to_inches(h_val, h_unit)
        w_mm = to_mm(w_val, w_unit)
        h_mm = to_mm(h_val, h_unit)

        in_short, in_long = min(w_in, h_in), max(w_in, h_in)
        mm_short, mm_long = min(w_mm, h_mm), max(w_mm, h_mm)

        in_str = f"{format_number(in_short)} x {format_number(in_long)}"
        mm_str = f"{format_number(mm_short)} x {format_number(mm_long)}"

        if native_unit == "in":
            in_str = f"**{in_str}**"
        else:
            mm_str = f"**{mm_str}**"

        aspect = min(w_val, h_val) / max(w_val, h_val)

        aliases = info.get("aliases", [])
        notes = ""
        if aliases:
            notes = "<br>".join(f"AKA `{a}`" for a in aliases)

        print(f"| `{card}` | {in_str} | {mm_str} | {aspect:.4f} | {notes} |")

    print()

    # Table 3: Paper sizes
    print("| Paper size | Inches | Millimeters | Notes |")
    print("| --- | --- | --- | --- |")

    for paper in paper_order:
        info = paper_sizes[paper]
        w_val, w_unit = parse_dimension(info["width"])
        h_val, h_unit = parse_dimension(info["height"])

        native_unit = w_unit

        w_in = to_inches(w_val, w_unit)
        h_in = to_inches(h_val, h_unit)
        w_mm = to_mm(w_val, w_unit)
        h_mm = to_mm(h_val, h_unit)

        in_short, in_long = min(w_in, h_in), max(w_in, h_in)
        mm_short, mm_long = min(w_mm, h_mm), max(w_mm, h_mm)

        in_str = f"{format_number(in_short)} x {format_number(in_long)}"
        mm_str = f"{format_number(mm_short)} x {format_number(mm_long)}"

        if native_unit == "in":
            in_str = f"**{in_str}**"
        else:
            mm_str = f"**{mm_str}**"

        aliases = info.get("aliases", [])
        notes = ""
        if aliases:
            notes = "<br>".join(f"AKA `{a}`" for a in aliases)

        print(f"| `{paper}` | {in_str} | {mm_str} | {notes} |")


if __name__ == "__main__":
    generate_tables()

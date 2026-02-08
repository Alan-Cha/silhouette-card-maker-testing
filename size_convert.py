import re

    
def size_to_pixel(size_string, ppi):    
    float_pattern = r"(?:\d+\.\d*|\.\d+|\d+)"  # matches 1.0, .5, or 2
    
    # Match mm
    mm_match = re.fullmatch(rf"({float_pattern})mm", size_string)
    if mm_match:
        size_mm = float(mm_match.group(1))
        return round(size_mm / 25.4 * ppi)

    # Match inches
    in_match = re.fullmatch(rf"({float_pattern})in", size_string)
    if in_match:
        size_in = float(in_match.group(1))
        return round(size_in*ppi)
    
    #If no match
    return round(float(size_string))


def size_to_pt(size_string):
    float_pattern = r"(?:\d+\.\d*|\.\d+|\d+)"  # matches 1.0, .5, or 2
    
    # Match mm
    mm_match = re.fullmatch(rf"({float_pattern})mm", size_string)
    if mm_match:
        size_mm = float(mm_match.group(1))
        return size_mm / 25.4 * 72

    # Match inches
    in_match = re.fullmatch(rf"({float_pattern})in", size_string)
    if in_match:
        size_in = float(in_match.group(1))
        return size_in * 72
    
    #If no match
    return float(size_string)

def size_to_mm(size_string):
    float_pattern = r"(?:\d+\.\d*|\.\d+|\d+)"  # matches 1.0, .5, or 2
    
    # Match mm
    mm_match = re.fullmatch(rf"({float_pattern})mm", size_string)
    if mm_match:
        size_mm = float(mm_match.group(1))
        return size_mm

    # Match inches
    in_match = re.fullmatch(rf"({float_pattern})in", size_string)
    if in_match:
        size_in = float(in_match.group(1))
        return size_in * 25.4
    
    #If no match
    return float(size_string)

def size_to_in(size_string):
    float_pattern = r"(?:\d+\.\d*|\.\d+|\d+)"  # matches 1.0, .5, or 2
    
    # Match mm
    mm_match = re.fullmatch(rf"({float_pattern})mm", size_string)
    if mm_match:
        size_mm = float(mm_match.group(1))
        return size_mm / 25.4

    # Match inches
    in_match = re.fullmatch(rf"({float_pattern})in", size_string)
    if in_match:
        return float(in_match.group(1))
    
    #If no match
    return float(size_string)
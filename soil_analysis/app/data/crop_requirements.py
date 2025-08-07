"""
Crop requirements database
Contains optimal soil conditions for different crops
"""

from typing import Dict, List, Any

# Crop requirements database
CROP_REQUIREMENTS = {
    "wheat": {
        "ph_range": (6.0, 7.5),
        "salinity_tolerance": 4.0,  # dS/m
        "preferred_textures": ["loam", "clay_loam", "silt_loam"],
        "bulk_density_range": (1.1, 1.4),
        "nutrients": {
            "nitrogen": {"min": 120, "max": 180, "optimal": 150},  # kg/ha
            "phosphorus": {"min": 25, "max": 40, "optimal": 30},
            "potassium": {"min": 40, "max": 60, "optimal": 50},
            "calcium": {"min": 1000, "max": 3000, "optimal": 2000},  # mg/kg
            "magnesium": {"min": 150, "max": 400, "optimal": 250},
            "sulfur": {"min": 10, "max": 25, "optimal": 15},
            "iron": {"min": 4.5, "max": 15, "optimal": 8},  # mg/kg
            "manganese": {"min": 2, "max": 10, "optimal": 5},
            "zinc": {"min": 0.8, "max": 3, "optimal": 1.5}
        }
    },
    "rice": {
        "ph_range": (5.5, 7.0),
        "salinity_tolerance": 3.0,
        "preferred_textures": ["clay", "clay_loam", "silty_clay"],
        "bulk_density_range": (1.0, 1.3),
        "nutrients": {
            "nitrogen": {"min": 100, "max": 150, "optimal": 120},
            "phosphorus": {"min": 20, "max": 35, "optimal": 25},
            "potassium": {"min": 50, "max": 80, "optimal": 60},
            "calcium": {"min": 800, "max": 2500, "optimal": 1500},
            "magnesium": {"min": 120, "max": 350, "optimal": 200},
            "sulfur": {"min": 8, "max": 20, "optimal": 12},
            "iron": {"min": 5, "max": 20, "optimal": 10},
            "manganese": {"min": 3, "max": 15, "optimal": 8},
            "zinc": {"min": 1, "max": 4, "optimal": 2}
        }
    },
    "corn": {
        "ph_range": (6.0, 6.8),
        "salinity_tolerance": 1.7,
        "preferred_textures": ["loam", "silt_loam", "clay_loam"],
        "bulk_density_range": (1.1, 1.4),
        "nutrients": {
            "nitrogen": {"min": 150, "max": 220, "optimal": 180},
            "phosphorus": {"min": 30, "max": 50, "optimal": 40},
            "potassium": {"min": 60, "max": 100, "optimal": 80},
            "calcium": {"min": 1200, "max": 3500, "optimal": 2200},
            "magnesium": {"min": 180, "max": 450, "optimal": 300},
            "sulfur": {"min": 12, "max": 30, "optimal": 20},
            "iron": {"min": 4, "max": 12, "optimal": 7},
            "manganese": {"min": 2, "max": 8, "optimal": 4},
            "zinc": {"min": 1, "max": 3.5, "optimal": 2}
        }
    },
    "tomato": {
        "ph_range": (6.0, 6.8),
        "salinity_tolerance": 2.5,
        "preferred_textures": ["loam", "sandy_loam", "silt_loam"],
        "bulk_density_range": (1.0, 1.3),
        "nutrients": {
            "nitrogen": {"min": 100, "max": 160, "optimal": 130},
            "phosphorus": {"min": 40, "max": 70, "optimal": 55},
            "potassium": {"min": 120, "max": 200, "optimal": 160},
            "calcium": {"min": 1500, "max": 4000, "optimal": 2500},
            "magnesium": {"min": 200, "max": 500, "optimal": 350},
            "sulfur": {"min": 15, "max": 35, "optimal": 25},
            "iron": {"min": 5, "max": 15, "optimal": 9},
            "manganese": {"min": 3, "max": 12, "optimal": 6},
            "zinc": {"min": 1.2, "max": 4, "optimal": 2.5}
        }
    },
    "potato": {
        "ph_range": (5.0, 6.5),
        "salinity_tolerance": 1.7,
        "preferred_textures": ["sandy_loam", "loam", "silt_loam"],
        "bulk_density_range": (1.0, 1.3),
        "nutrients": {
            "nitrogen": {"min": 120, "max": 180, "optimal": 150},
            "phosphorus": {"min": 35, "max": 60, "optimal": 45},
            "potassium": {"min": 150, "max": 250, "optimal": 200},
            "calcium": {"min": 1000, "max": 3000, "optimal": 1800},
            "magnesium": {"min": 150, "max": 400, "optimal": 250},
            "sulfur": {"min": 12, "max": 28, "optimal": 18},
            "iron": {"min": 4, "max": 12, "optimal": 7},
            "manganese": {"min": 2, "max": 10, "optimal": 5},
            "zinc": {"min": 0.8, "max": 3, "optimal": 1.8}
        }
    },
    "soybean": {
        "ph_range": (6.0, 7.0),
        "salinity_tolerance": 5.0,
        "preferred_textures": ["loam", "clay_loam", "silt_loam"],
        "bulk_density_range": (1.1, 1.4),
        "nutrients": {
            "nitrogen": {"min": 40, "max": 80, "optimal": 60},  # Lower due to N fixation
            "phosphorus": {"min": 25, "max": 45, "optimal": 35},
            "potassium": {"min": 80, "max": 120, "optimal": 100},
            "calcium": {"min": 1200, "max": 3500, "optimal": 2200},
            "magnesium": {"min": 180, "max": 450, "optimal": 300},
            "sulfur": {"min": 10, "max": 25, "optimal": 15},
            "iron": {"min": 4, "max": 12, "optimal": 7},
            "manganese": {"min": 2, "max": 8, "optimal": 4},
            "zinc": {"min": 0.8, "max": 3, "optimal": 1.5}
        }
    }
}

# Alternative crops for different soil conditions
ALTERNATIVE_CROPS = {
    "high_salinity": ["barley", "sugar_beet", "spinach", "asparagus"],
    "acidic_soil": ["blueberry", "cranberry", "potato", "sweet_potato"],
    "alkaline_soil": ["alfalfa", "sugar_beet", "barley", "asparagus"],
    "clay_soil": ["rice", "wheat", "cabbage", "broccoli"],
    "sandy_soil": ["carrot", "radish", "potato", "peanut"],
    "low_fertility": ["legumes", "clover", "alfalfa", "peas"]
}

def get_crop_requirements(crop_name: str) -> Dict[str, Any]:
    """Get requirements for a specific crop"""
    return CROP_REQUIREMENTS.get(crop_name.lower(), None)

def get_alternative_crops(soil_condition: str) -> List[str]:
    """Get alternative crops for specific soil conditions"""
    return ALTERNATIVE_CROPS.get(soil_condition, [])

def get_all_crops() -> List[str]:
    """Get list of all available crops"""
    return list(CROP_REQUIREMENTS.keys())

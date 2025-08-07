"""
Fertilizer recommendations database
Contains fertilizer suggestions for different nutrient deficiencies
"""

from typing import Dict, List
from app.models.soil import FertilizerRecommendation

# Fertilizer recommendations for nutrient deficiencies
FERTILIZER_DATABASE = {
    "nitrogen": [
        {
            "name": "Urea (46-0-0)",
            "amount_per_kg_deficit": 2.17,  # kg fertilizer per kg N deficit
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate into soil",
            "timing": "Split application: 50% at planting, 50% at tillering"
        },
        {
            "name": "Ammonium Sulfate (21-0-0)",
            "amount_per_kg_deficit": 4.76,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply 2-3 weeks before planting"
        }
    ],
    "phosphorus": [
        {
            "name": "Triple Superphosphate (0-46-0)",
            "amount_per_kg_deficit": 2.17,
            "unit": "kg/ha",
            "application_method": "Band application near seed/root zone",
            "timing": "Apply at planting time"
        },
        {
            "name": "Diammonium Phosphate (18-46-0)",
            "amount_per_kg_deficit": 2.17,
            "unit": "kg/ha",
            "application_method": "Band application or broadcast",
            "timing": "Apply at planting"
        }
    ],
    "potassium": [
        {
            "name": "Muriate of Potash (0-0-60)",
            "amount_per_kg_deficit": 1.67,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply before planting or at planting"
        },
        {
            "name": "Sulfate of Potash (0-0-50)",
            "amount_per_kg_deficit": 2.0,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply before planting"
        }
    ],
    "calcium": [
        {
            "name": "Gypsum (CaSO4)",
            "amount_per_mg_deficit": 0.01,  # kg fertilizer per mg/kg Ca deficit
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply 2-4 weeks before planting"
        },
        {
            "name": "Lime (CaCO3)",
            "amount_per_mg_deficit": 0.008,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate deeply",
            "timing": "Apply 3-6 months before planting"
        }
    ],
    "magnesium": [
        {
            "name": "Epsom Salt (MgSO4)",
            "amount_per_mg_deficit": 0.02,
            "unit": "kg/ha",
            "application_method": "Broadcast or foliar spray",
            "timing": "Apply at planting or as foliar spray during growth"
        },
        {
            "name": "Dolomitic Lime",
            "amount_per_mg_deficit": 0.015,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply 3-6 months before planting"
        }
    ],
    "sulfur": [
        {
            "name": "Elemental Sulfur",
            "amount_per_mg_deficit": 0.05,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply 2-4 weeks before planting"
        },
        {
            "name": "Gypsum (CaSO4)",
            "amount_per_mg_deficit": 0.08,
            "unit": "kg/ha",
            "application_method": "Broadcast and incorporate",
            "timing": "Apply before planting"
        }
    ],
    "iron": [
        {
            "name": "Iron Sulfate (FeSO4)",
            "amount_per_mg_deficit": 0.1,
            "unit": "kg/ha",
            "application_method": "Soil application or foliar spray",
            "timing": "Apply when deficiency symptoms appear"
        },
        {
            "name": "Chelated Iron (Fe-EDTA)",
            "amount_per_mg_deficit": 0.05,
            "unit": "kg/ha",
            "application_method": "Foliar spray or soil drench",
            "timing": "Apply during active growth"
        }
    ],
    "manganese": [
        {
            "name": "Manganese Sulfate (MnSO4)",
            "amount_per_mg_deficit": 0.15,
            "unit": "kg/ha",
            "application_method": "Foliar spray or soil application",
            "timing": "Apply when deficiency symptoms appear"
        }
    ],
    "zinc": [
        {
            "name": "Zinc Sulfate (ZnSO4)",
            "amount_per_mg_deficit": 0.2,
            "unit": "kg/ha",
            "application_method": "Soil application or foliar spray",
            "timing": "Apply before planting or during early growth"
        }
    ],

}

# pH adjustment recommendations
PH_ADJUSTMENT = {
    "acidic": {
        "name": "Agricultural Lime (CaCO3)",
        "amount_per_ph_unit": 2000,  # kg/ha per pH unit to raise
        "unit": "kg/ha",
        "application_method": "Broadcast and incorporate to 15-20cm depth",
        "timing": "Apply 3-6 months before planting"
    },
    "alkaline": {
        "name": "Elemental Sulfur",
        "amount_per_ph_unit": 500,  # kg/ha per pH unit to lower
        "unit": "kg/ha",
        "application_method": "Broadcast and incorporate",
        "timing": "Apply 2-4 months before planting"
    }
}

def get_fertilizer_recommendations(nutrient: str, deficit_amount: float) -> List[FertilizerRecommendation]:
    """Get fertilizer recommendations for a specific nutrient deficit"""
    recommendations = []
    
    if nutrient.lower() in FERTILIZER_DATABASE:
        fertilizers = FERTILIZER_DATABASE[nutrient.lower()]
        
        for fert in fertilizers:
            if nutrient in ["nitrogen", "phosphorus", "potassium"]:
                amount = deficit_amount * fert["amount_per_kg_deficit"]
            else:
                amount = deficit_amount * fert["amount_per_mg_deficit"]
            
            recommendations.append(FertilizerRecommendation(
                name=fert["name"],
                amount=round(amount, 2),
                unit=fert["unit"],
                application_method=fert["application_method"],
                timing=fert["timing"]
            ))
    
    return recommendations

def get_ph_adjustment_recommendation(current_ph: float, target_ph: float) -> FertilizerRecommendation:
    """Get pH adjustment recommendation"""
    ph_diff = abs(current_ph - target_ph)
    
    if current_ph < target_ph:  # Need to raise pH
        adjustment = PH_ADJUSTMENT["acidic"]
        amount = ph_diff * adjustment["amount_per_ph_unit"]
        
        return FertilizerRecommendation(
            name=adjustment["name"],
            amount=round(amount, 2),
            unit=adjustment["unit"],
            application_method=adjustment["application_method"],
            timing=adjustment["timing"]
        )
    elif current_ph > target_ph:  # Need to lower pH
        adjustment = PH_ADJUSTMENT["alkaline"]
        amount = ph_diff * adjustment["amount_per_ph_unit"]
        
        return FertilizerRecommendation(
            name=adjustment["name"],
            amount=round(amount, 2),
            unit=adjustment["unit"],
            application_method=adjustment["application_method"],
            timing=adjustment["timing"]
        )
    
    return None

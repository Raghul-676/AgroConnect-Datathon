"""
Soil analysis engine
Core logic for analyzing soil parameters and generating recommendations
"""

from typing import List, Dict, Any
from loguru import logger

from app.models.soil import SoilParameters, AnalysisResult, FertilizerRecommendation
from app.data.crop_requirements import get_crop_requirements, get_alternative_crops, get_all_crops
from app.data.fertilizer_recommendations import get_fertilizer_recommendations, get_ph_adjustment_recommendation
from app.ml.soil_classifier import SoilSuitabilityClassifier

class SoilAnalysisEngine:
    """Main engine for soil analysis and recommendations"""
    
    def __init__(self):
        self.classifier = SoilSuitabilityClassifier()
        
    def analyze_soil(self, soil_params: SoilParameters, crop_name: str) -> AnalysisResult:
        """
        Analyze soil parameters for a specific crop and generate recommendations
        """
        crop_name = crop_name.lower().strip()
        
        # Validate crop
        if crop_name not in get_all_crops():
            raise ValueError(f"Crop '{crop_name}' not supported. Available crops: {', '.join(get_all_crops())}")
        
        # Get crop requirements
        requirements = get_crop_requirements(crop_name)
        if not requirements:
            raise ValueError(f"Requirements not found for crop: {crop_name}")
        
        # Get ML prediction
        ml_category, confidence = self.classifier.predict(soil_params, crop_name)
        
        # Calculate detailed suitability score
        suitability_score = self._calculate_suitability_score(soil_params, requirements)
        
        # Determine final category (combine ML and rule-based)
        final_category = self._determine_final_category(ml_category, suitability_score, confidence)
        
        # Generate recommendations based on category
        if final_category == "excellent":
            return self._generate_excellent_analysis(soil_params, crop_name, suitability_score)
        elif final_category == "average":
            return self._generate_average_analysis(soil_params, crop_name, requirements, suitability_score)
        else:  # bad
            return self._generate_bad_analysis(soil_params, crop_name, requirements, suitability_score)
    
    def _calculate_suitability_score(self, soil_params: SoilParameters, requirements: Dict) -> float:
        """Calculate detailed suitability score based on soil parameters"""
        scores = []
        
        # pH score
        ph_min, ph_max = requirements["ph_range"]
        if ph_min <= soil_params.ph <= ph_max:
            ph_score = 100
        else:
            ph_deviation = min(abs(soil_params.ph - ph_min), abs(soil_params.ph - ph_max))
            ph_score = max(0, 100 - (ph_deviation * 20))
        scores.append(ph_score)
        
        # Salinity score
        salinity_tolerance = requirements["salinity_tolerance"]
        if soil_params.salinity <= salinity_tolerance:
            salinity_score = 100 - (soil_params.salinity / salinity_tolerance * 30)
        else:
            excess = soil_params.salinity - salinity_tolerance
            salinity_score = max(0, 70 - (excess * 15))
        scores.append(salinity_score)
        
        # Texture score
        if soil_params.texture.value in requirements["preferred_textures"]:
            texture_score = 100
        else:
            texture_score = 60  # Moderate score for non-preferred textures
        scores.append(texture_score)
        
        # Bulk density score
        bd_min, bd_max = requirements["bulk_density_range"]
        if bd_min <= soil_params.bulk_density <= bd_max:
            bd_score = 100
        else:
            bd_deviation = min(abs(soil_params.bulk_density - bd_min), abs(soil_params.bulk_density - bd_max))
            bd_score = max(0, 100 - (bd_deviation * 50))
        scores.append(bd_score)
        
        # Nutrient scores
        nutrient_scores = []
        for nutrient, values in requirements["nutrients"].items():
            current_value = getattr(soil_params.nutrients, nutrient)
            optimal = values["optimal"]
            min_val, max_val = values["min"], values["max"]
            
            if min_val <= current_value <= max_val:
                # Within acceptable range
                deviation_from_optimal = abs(current_value - optimal) / optimal
                nutrient_score = max(70, 100 - (deviation_from_optimal * 30))
            elif current_value < min_val:
                # Deficient
                deficit_ratio = (min_val - current_value) / min_val
                nutrient_score = max(0, 70 - (deficit_ratio * 70))
            else:
                # Excess
                excess_ratio = (current_value - max_val) / max_val
                nutrient_score = max(0, 70 - (excess_ratio * 35))
            
            nutrient_scores.append(nutrient_score)
        
        scores.extend(nutrient_scores)
        
        # Calculate weighted average
        weights = [0.2, 0.15, 0.1, 0.1] + [0.45 / len(nutrient_scores)] * len(nutrient_scores)
        weighted_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return min(100, max(0, weighted_score))
    
    def _determine_final_category(self, ml_category: str, rule_score: float, confidence: float) -> str:
        """Determine final category combining ML and rule-based approaches"""
        
        # Rule-based category
        if rule_score >= 80:
            rule_category = "excellent"
        elif rule_score >= 60:
            rule_category = "average"
        else:
            rule_category = "bad"
        
        # If ML confidence is high, trust ML more
        if confidence > 0.8:
            return ml_category
        
        # Otherwise, use rule-based with ML as secondary
        if rule_category == ml_category:
            return rule_category
        
        # Handle conflicts
        if rule_score >= 75:
            return "excellent"
        elif rule_score >= 55:
            return "average"
        else:
            return "bad"
    
    def _generate_excellent_analysis(self, soil_params: SoilParameters, crop_name: str, score: float) -> AnalysisResult:
        """Generate analysis for excellent soil conditions"""
        
        cultivation_tips = [
            f"Your soil is excellent for {crop_name} cultivation!",
            "Maintain current soil conditions through regular monitoring",
            "Apply organic matter annually to sustain soil health",
            "Follow crop rotation practices to prevent nutrient depletion",
            "Monitor soil moisture levels regularly",
            "Consider precision agriculture techniques for optimal yields"
        ]
        
        recommendations = [
            "Continue current soil management practices",
            "Regular soil testing every 6 months",
            "Maintain organic matter content above 3%",
            "Use cover crops during off-season"
        ]
        
        return AnalysisResult(
            suitability_score=score,
            category="excellent",
            message=f"Excellent! Your soil conditions are ideal for {crop_name} cultivation. "
                   f"The soil parameters are well within the optimal range for this crop.",
            recommendations=recommendations,
            fertilizer_recommendations=[],
            alternative_crops=[],
            cultivation_tips=cultivation_tips
        )
    
    def _generate_average_analysis(self, soil_params: SoilParameters, crop_name: str, 
                                 requirements: Dict, score: float) -> AnalysisResult:
        """Generate analysis for average soil conditions"""
        
        fertilizer_recs = []
        recommendations = []
        
        # Check pH adjustment needs
        ph_min, ph_max = requirements["ph_range"]
        target_ph = (ph_min + ph_max) / 2
        
        if abs(soil_params.ph - target_ph) > 0.3:
            ph_rec = get_ph_adjustment_recommendation(soil_params.ph, target_ph)
            if ph_rec:
                fertilizer_recs.append(ph_rec)
                recommendations.append(f"Adjust soil pH from {soil_params.ph:.1f} to {target_ph:.1f}")
        
        # Check nutrient deficiencies
        for nutrient, values in requirements["nutrients"].items():
            current_value = getattr(soil_params.nutrients, nutrient)
            min_required = values["min"]
            optimal = values["optimal"]
            
            if current_value < min_required:
                deficit = optimal - current_value
                nutrient_recs = get_fertilizer_recommendations(nutrient, deficit)
                fertilizer_recs.extend(nutrient_recs)
                recommendations.append(f"Increase {nutrient} levels (current: {current_value:.1f}, target: {optimal:.1f})")
        
        # Check salinity
        if soil_params.salinity > requirements["salinity_tolerance"]:
            recommendations.append("Improve drainage to reduce soil salinity")
            recommendations.append("Consider leaching with good quality water")
        
        message = (f"Your soil is suitable for {crop_name} with some improvements. "
                  f"Adding the recommended fertilizers will optimize growing conditions.")
        
        return AnalysisResult(
            suitability_score=score,
            category="average",
            message=message,
            recommendations=recommendations,
            fertilizer_recommendations=fertilizer_recs,
            alternative_crops=[],
            cultivation_tips=[]
        )

    def _generate_bad_analysis(self, soil_params: SoilParameters, crop_name: str,
                             requirements: Dict, score: float) -> AnalysisResult:
        """Generate analysis for poor soil conditions"""

        fertilizer_recs = []
        recommendations = []
        alternative_crops = []

        # Major pH adjustment
        ph_min, ph_max = requirements["ph_range"]
        target_ph = (ph_min + ph_max) / 2

        if abs(soil_params.ph - target_ph) > 0.5:
            ph_rec = get_ph_adjustment_recommendation(soil_params.ph, target_ph)
            if ph_rec:
                fertilizer_recs.append(ph_rec)
                recommendations.append(f"Major pH adjustment needed: {soil_params.ph:.1f} → {target_ph:.1f}")

        # Address all nutrient deficiencies
        for nutrient, values in requirements["nutrients"].items():
            current_value = getattr(soil_params.nutrients, nutrient)
            optimal = values["optimal"]

            if current_value < values["min"]:
                deficit = optimal - current_value
                nutrient_recs = get_fertilizer_recommendations(nutrient, deficit)
                fertilizer_recs.extend(nutrient_recs)
                recommendations.append(f"Severe {nutrient} deficiency - increase from {current_value:.1f} to {optimal:.1f}")

        # Suggest alternative crops based on soil conditions
        if soil_params.salinity > requirements["salinity_tolerance"] * 1.5:
            alternative_crops.extend(get_alternative_crops("high_salinity"))
            recommendations.append("Consider salt-tolerant crops due to high salinity")

        if soil_params.ph < 5.5:
            alternative_crops.extend(get_alternative_crops("acidic_soil"))
            recommendations.append("Consider acid-tolerant crops")
        elif soil_params.ph > 8.0:
            alternative_crops.extend(get_alternative_crops("alkaline_soil"))
            recommendations.append("Consider alkaline-tolerant crops")

        if soil_params.texture.value in ["clay", "silty_clay"]:
            alternative_crops.extend(get_alternative_crops("clay_soil"))
        elif soil_params.texture.value in ["sandy", "sandy_loam"]:
            alternative_crops.extend(get_alternative_crops("sandy_soil"))

        # Remove duplicates and current crop
        alternative_crops = list(set(alternative_crops))
        if crop_name in alternative_crops:
            alternative_crops.remove(crop_name)

        recommendations.extend([
            "Soil improvement will take 6-12 months",
            "Consider soil testing every 3 months during improvement",
            "Add organic matter to improve soil structure",
            "Ensure proper drainage system"
        ])

        message = (f"Your soil is not suitable for {crop_name} in its current condition. "
                  f"Significant soil improvement is required, and alternative crops should be considered.")

        return AnalysisResult(
            suitability_score=score,
            category="bad",
            message=message,
            recommendations=recommendations,
            fertilizer_recommendations=fertilizer_recs,
            alternative_crops=alternative_crops[:5],  # Limit to top 5 alternatives
            cultivation_tips=[]
        )

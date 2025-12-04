"""Expanded search keywords based on Visual Techniques Taxonomy"""

# === ART MOVEMENTS / STYLES ===
ART_MOVEMENTS = {
    "surrealism": {
        "search_terms": [
            "surrealist advertising photography", "dreamscape product photography",
            "impossible scale advertising", "melting objects commercial", "Dali inspired ads",
            "floating objects photography", "surreal luxury campaign"
        ],
        "type": "art_movement"
    },
    "magical_realism": {
        "search_terms": [
            "magical realism photography", "everyday wonder advertising",
            "subtle magic commercial", "quiet impossible photography"
        ],
        "type": "art_movement"
    },
    "hyperrealism": {
        "search_terms": [
            "hyperrealistic product photography", "extreme detail commercial",
            "larger than life advertising", "macro product shot luxury"
        ],
        "type": "art_movement"
    },
    "minimalism": {
        "search_terms": [
            "minimalist advertising", "negative space product photography",
            "clean aesthetic commercial", "essential forms advertising",
            "minimal luxury brand photography"
        ],
        "type": "art_movement"
    },
    "pop_art": {
        "search_terms": [
            "pop art advertising", "bold colors commercial photography",
            "Warhol inspired ads", "repetition pattern advertising"
        ],
        "type": "art_movement"
    },
    "romanticism": {
        "search_terms": [
            "romantic advertising photography", "dramatic light commercial",
            "sublime nature product", "emotional landscape advertising"
        ],
        "type": "art_movement"
    },
    "art_nouveau": {
        "search_terms": [
            "art nouveau advertising", "organic curves commercial",
            "botanical luxury photography", "ornamental product photography"
        ],
        "type": "art_movement"
    },
    "bauhaus": {
        "search_terms": [
            "bauhaus advertising", "geometric commercial photography",
            "primary colors product", "functional beauty advertising"
        ],
        "type": "art_movement"
    },
    "japanese_aesthetics": {
        "search_terms": [
            "wabi sabi photography", "japanese minimalist advertising",
            "ma negative space commercial", "imperfection beauty product"
        ],
        "type": "art_movement"
    },
    "futurism": {
        "search_terms": [
            "futurist advertising", "motion blur commercial",
            "dynamic lines product", "speed photography advertising"
        ],
        "type": "art_movement"
    }
}

# === VISUAL TECHNIQUES ===
VISUAL_TECHNIQUES = {
    "visual_integration": {
        "search_terms": [
            "product integration photography", "seamless environment advertising",
            "product becoming part of scene"
        ],
        "type": "technique"
    },
    "partial_immersion": {
        "search_terms": [
            "partial submersion photography", "dissolving product advertising",
            "half submerged commercial"
        ],
        "type": "technique"
    },
    "reality_canvas_fusion": {
        "search_terms": [
            "painting becoming reality advertising", "frame as portal commercial",
            "art meets reality photography"
        ],
        "type": "technique"
    },
    "material_transformation": {
        "search_terms": [
            "material morphing photography", "texture transformation advertising",
            "elemental dissolution commercial", "paint spilling reality"
        ],
        "type": "technique"
    },
    "dimensional_breaking": {
        "search_terms": [
            "3D emerging from 2D advertising", "dimensional break photography",
            "fragment drift commercial", "floating pieces advertising"
        ],
        "type": "technique"
    },
    "impossible_lighting": {
        "search_terms": [
            "impossible light source photography", "otherworldly illumination advertising",
            "dramatic chiaroscuro commercial", "light leak photography"
        ],
        "type": "technique"
    },
    "shadow_play": {
        "search_terms": [
            "creative shadow photography", "shadow storytelling advertising",
            "mismatched shadow commercial"
        ],
        "type": "technique"
    },
    "scale_distortion": {
        "search_terms": [
            "miniature world advertising", "giant everyday object photography",
            "scale juxtaposition commercial", "tilt shift advertising"
        ],
        "type": "technique"
    },
    "frozen_motion": {
        "search_terms": [
            "frozen motion photography", "suspended moment advertising",
            "high speed commercial photography"
        ],
        "type": "technique"
    },
    "time_manipulation": {
        "search_terms": [
            "time lapse composite advertising", "multiple moments photography",
            "decay and bloom commercial"
        ],
        "type": "technique"
    }
}

# === AD TYPES (for Ads of the World) ===
AD_TYPES = {
    "ooh_concept": {
        "search_terms": ["OOH advertising concept", "outdoor advertising creative", "billboard design"],
        "type": "ad_format"
    },
    "minimalist_print": {
        "search_terms": ["minimalist print ad", "clean print advertising", "simple print campaign"],
        "type": "ad_format"
    },
    "optical_illusion": {
        "search_terms": ["optical illusion advertising", "visual trick commercial", "perspective play ads"],
        "type": "ad_format"
    },
    "surreal_ads": {
        "search_terms": ["surreal advertising campaign", "dreamlike commercial", "impossible ads"],
        "type": "ad_format"
    },
    "kv_composition": {
        "search_terms": ["key visual composition", "hero image advertising", "campaign key visual"],
        "type": "ad_format"
    }
}

# === BRAND AESTHETICS ===
BRAND_AESTHETICS = {
    "hermes_style": {
        "search_terms": ["Hermes advertising style", "luxury brand surrealism", "high fashion dreamscape"],
        "type": "brand_aesthetic"
    },
    "apple_style": {
        "search_terms": ["Apple advertising aesthetic", "tech minimalism photography", "clean product hero"],
        "type": "brand_aesthetic"
    },
    "chanel_style": {
        "search_terms": ["Chanel advertising", "luxury fashion editorial", "elegant brand photography"],
        "type": "brand_aesthetic"
    },
    "nike_style": {
        "search_terms": ["Nike advertising style", "athletic brand photography", "dynamic sports commercial"],
        "type": "brand_aesthetic"
    }
}

# === INDUSTRY SPECIFIC ===
INDUSTRY_VISUALS = {
    "perfume_advertising": {
        "search_terms": [
            "perfume advertising photography", "fragrance campaign visual",
            "luxury perfume commercial", "scent visualization advertising"
        ],
        "type": "industry"
    },
    "watch_advertising": {
        "search_terms": [
            "luxury watch photography", "timepiece advertising",
            "watch commercial campaign", "horology brand visual"
        ],
        "type": "industry"
    },
    "automotive_advertising": {
        "search_terms": [
            "automotive advertising photography", "car commercial campaign",
            "luxury vehicle visual", "automotive brand photography"
        ],
        "type": "industry"
    },
    "skincare_advertising": {
        "search_terms": [
            "skincare advertising photography", "beauty product commercial",
            "cosmetics campaign visual", "luxury skincare photography"
        ],
        "type": "industry"
    }
}

def get_all_pinterest_keywords() -> list[dict]:
    """Get all keywords formatted for Pinterest scraping"""
    all_keywords = []
    
    for category, data in {**ART_MOVEMENTS, **VISUAL_TECHNIQUES, **AD_TYPES, **BRAND_AESTHETICS, **INDUSTRY_VISUALS}.items():
        for term in data["search_terms"]:
            all_keywords.append({
                "category": category,
                "category_type": data["type"],
                "search_term": term
            })
    
    return all_keywords

def get_keyword_count():
    """Get total count of new keywords"""
    keywords = get_all_pinterest_keywords()
    print(f"📊 Total new Pinterest keywords: {len(keywords)}")
    print(f"\n   By type:")
    from collections import Counter
    types = Counter(k["category_type"] for k in keywords)
    for t, count in types.items():
        print(f"   - {t}: {count}")
    return len(keywords)

if __name__ == "__main__":
    get_keyword_count()




from pathlib import Path # Centralized config for Pinterest scraper

# === OUTPUT ===
OUTPUT_DIR = Path("output")
MASTER_CSV = OUTPUT_DIR / "master_dataset.csv"
LOG_FILE = OUTPUT_DIR / "scraper.log"

# === BROWSER ===
CHROME_DEBUG_PORT = 9222 # Connect to your Chrome: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# === RATE LIMITING (EXPLORATION MODE) ===
DELAY_BETWEEN_PAGES = (2, 3) # Random 2-3 sec between page loads
DELAY_BETWEEN_SCROLLS = (0.2, 0.4) # Fast scrolling
COOLDOWN_EVERY_N_PINS = 25 # Take break every N pins
COOLDOWN_DURATION = (15, 30) # 15-30 sec cooldown
PINS_PER_SEARCH = 30 # Get 30 initial pins from search
SCROLLS_PER_PIN = 50 # Scroll 50 times per pin page
MAX_URLS_PER_PIN = 100 # Images per pin (more pins > more images per pin)

# === DUPLICATE THRESHOLD ===
DUPLICATE_STOP_THRESHOLD = 0.76 # Stop when 76% new URLs are duplicates

# === CATEGORIES (48 total, starting with Products) ===
CATEGORIES = {
    # === 1. PRODUCT CATEGORIES (12) ===
    "luxury_bags": {"search": "luxury handbag aesthetic", "type": "product"},
    "shoes": {"search": "designer shoes photography", "type": "product"},
    "sportswear": {"search": "athletic wear photoshoot", "type": "product"},
    "fashion": {"search": "fashion lookbook", "type": "product"},
    "chinese_fashion": {"search": "chinese fashion editorial", "type": "product"},
    "jewelry": {"search": "jewelry product photography", "type": "product"},
    "furniture": {"search": "furniture interior design", "type": "product"},
    "drinks": {"search": "beverage photography aesthetic", "type": "product"},
    "food": {"search": "food photography styling", "type": "product"},
    "beauty": {"search": "skincare product flat lay", "type": "product"},
    "tech": {"search": "tech product photography", "type": "product"},
    "home_decor": {"search": "home styling aesthetic", "type": "product"},
    
    # === 2. VISUAL STYLES (8) ===
    "style_minimalist": {"search": "minimalist product photography", "type": "style"},
    "style_luxury": {"search": "luxury brand aesthetic", "type": "style"},
    "style_warm": {"search": "warm cozy aesthetic photography", "type": "style"},
    "style_bold": {"search": "bold colorful product", "type": "style"},
    "style_vintage": {"search": "vintage aesthetic photography", "type": "style"},
    "style_dark": {"search": "dark moody product photography", "type": "style"},
    "style_pastel": {"search": "pastel aesthetic flat lay", "type": "style"},
    "style_natural": {"search": "organic natural product styling", "type": "style"},
    
    # === 3. E-COMMERCE VISUAL TYPES (10) ===
    "visual_ugc": {"search": "user generated content aesthetic", "type": "visual"},
    "visual_hero": {"search": "hero product photography", "type": "visual"},
    "visual_flatlay": {"search": "flat lay photography", "type": "visual"},
    "visual_lifestyle": {"search": "lifestyle product photography", "type": "visual"},
    "visual_model": {"search": "model product photoshoot", "type": "visual"},
    "visual_detail": {"search": "product detail macro", "type": "visual"},
    "visual_unboxing": {"search": "unboxing aesthetic", "type": "visual"},
    "visual_beforeafter": {"search": "before after transformation", "type": "visual"},
    "visual_social": {"search": "customer review aesthetic", "type": "visual"},
    "visual_bts": {"search": "behind the scenes brand", "type": "visual"},
    
    # === 4. MARKETING OCCASIONS (10) ===
    "occasion_blackfriday": {"search": "black friday sale aesthetic", "type": "occasion"},
    "occasion_christmas": {"search": "christmas gift aesthetic", "type": "occasion"},
    "occasion_newyear": {"search": "new year celebration aesthetic", "type": "occasion"},
    "occasion_valentines": {"search": "valentines day aesthetic", "type": "occasion"},
    "occasion_cny": {"search": "chinese new year aesthetic", "type": "occasion"},
    "occasion_mothers": {"search": "mothers day gift aesthetic", "type": "occasion"},
    "occasion_singles": {"search": "singles day shopping", "type": "occasion"},
    "occasion_summer": {"search": "summer sale aesthetic", "type": "occasion"},
    "occasion_school": {"search": "back to school aesthetic", "type": "occasion"},
    "occasion_halloween": {"search": "halloween aesthetic", "type": "occasion"},
    
    # === 5. INDUSTRY VERTICALS (8) ===
    "vertical_cafe": {"search": "cafe aesthetic photography", "type": "vertical"},
    "vertical_fitness": {"search": "fitness lifestyle aesthetic", "type": "vertical"},
    "vertical_travel": {"search": "travel photography aesthetic", "type": "vertical"},
    "vertical_wedding": {"search": "wedding aesthetic photography", "type": "vertical"},
    "vertical_kids": {"search": "baby product photography", "type": "vertical"},
    "vertical_pet": {"search": "pet product photography", "type": "vertical"},
    "vertical_outdoor": {"search": "outdoor gear photography", "type": "vertical"},
    "vertical_art": {"search": "art supplies aesthetic", "type": "vertical"},
}

# === CATEGORY ORDER (Original 48) ===
ORIGINAL_ORDER = [
    # Products first (your customers' needs)
    "luxury_bags", "shoes", "sportswear", "fashion", "chinese_fashion",
    "jewelry", "furniture", "drinks", "food", "beauty", "tech", "home_decor",
    # Then visual styles
    "style_minimalist", "style_luxury", "style_warm", "style_bold",
    "style_vintage", "style_dark", "style_pastel", "style_natural",
    # Then visual types
    "visual_ugc", "visual_hero", "visual_flatlay", "visual_lifestyle",
    "visual_model", "visual_detail", "visual_unboxing", "visual_beforeafter",
    "visual_social", "visual_bts",
    # Then occasions
    "occasion_blackfriday", "occasion_christmas", "occasion_newyear",
    "occasion_valentines", "occasion_cny", "occasion_mothers",
    "occasion_singles", "occasion_summer", "occasion_school", "occasion_halloween",
    # Then verticals
    "vertical_cafe", "vertical_fitness", "vertical_travel", "vertical_wedding",
    "vertical_kids", "vertical_pet", "vertical_outdoor", "vertical_art",
]

# === 6. ART MOVEMENTS (30) - Visual Techniques Taxonomy ===
EXPANDED_CATEGORIES = {
    # Surrealism
    "art_surrealism_1": {"search": "surrealist advertising photography", "type": "art_movement"},
    "art_surrealism_2": {"search": "dreamscape product photography", "type": "art_movement"},
    "art_surrealism_3": {"search": "impossible scale advertising", "type": "art_movement"},
    # Magical Realism
    "art_magical_realism_1": {"search": "magical realism photography", "type": "art_movement"},
    "art_magical_realism_2": {"search": "everyday wonder advertising", "type": "art_movement"},
    "art_magical_realism_3": {"search": "subtle magic commercial", "type": "art_movement"},
    # Hyperrealism
    "art_hyperrealism_1": {"search": "hyperrealistic product photography", "type": "art_movement"},
    "art_hyperrealism_2": {"search": "extreme detail commercial", "type": "art_movement"},
    "art_hyperrealism_3": {"search": "macro product shot luxury", "type": "art_movement"},
    # Minimalism
    "art_minimalism_1": {"search": "minimalist advertising campaign", "type": "art_movement"},
    "art_minimalism_2": {"search": "negative space product photography", "type": "art_movement"},
    "art_minimalism_3": {"search": "essential forms advertising", "type": "art_movement"},
    # Pop Art
    "art_pop_art_1": {"search": "pop art advertising", "type": "art_movement"},
    "art_pop_art_2": {"search": "bold colors commercial photography", "type": "art_movement"},
    "art_pop_art_3": {"search": "Warhol inspired ads", "type": "art_movement"},
    # Romanticism
    "art_romanticism_1": {"search": "romantic advertising photography", "type": "art_movement"},
    "art_romanticism_2": {"search": "dramatic light commercial", "type": "art_movement"},
    "art_romanticism_3": {"search": "sublime nature product", "type": "art_movement"},
    # Art Nouveau
    "art_nouveau_1": {"search": "art nouveau advertising", "type": "art_movement"},
    "art_nouveau_2": {"search": "organic curves commercial", "type": "art_movement"},
    "art_nouveau_3": {"search": "botanical luxury photography", "type": "art_movement"},
    # Bauhaus
    "art_bauhaus_1": {"search": "bauhaus advertising design", "type": "art_movement"},
    "art_bauhaus_2": {"search": "geometric commercial photography", "type": "art_movement"},
    "art_bauhaus_3": {"search": "primary colors product", "type": "art_movement"},
    # Japanese Aesthetics
    "art_japanese_1": {"search": "wabi sabi photography", "type": "art_movement"},
    "art_japanese_2": {"search": "japanese minimalist advertising", "type": "art_movement"},
    "art_japanese_3": {"search": "ma negative space commercial", "type": "art_movement"},
    # Futurism
    "art_futurism_1": {"search": "futurist advertising", "type": "art_movement"},
    "art_futurism_2": {"search": "motion blur commercial", "type": "art_movement"},
    "art_futurism_3": {"search": "dynamic lines product", "type": "art_movement"},
    
    # === 7. VISUAL TECHNIQUES (20) ===
    "tech_visual_integration_1": {"search": "product integration photography", "type": "technique"},
    "tech_visual_integration_2": {"search": "seamless environment advertising", "type": "technique"},
    "tech_partial_immersion_1": {"search": "partial submersion photography", "type": "technique"},
    "tech_partial_immersion_2": {"search": "dissolving product advertising", "type": "technique"},
    "tech_reality_canvas_1": {"search": "painting becoming reality advertising", "type": "technique"},
    "tech_reality_canvas_2": {"search": "art meets reality photography", "type": "technique"},
    "tech_material_transform_1": {"search": "material morphing photography", "type": "technique"},
    "tech_material_transform_2": {"search": "texture transformation advertising", "type": "technique"},
    "tech_dimensional_break_1": {"search": "3D emerging from 2D advertising", "type": "technique"},
    "tech_dimensional_break_2": {"search": "floating pieces advertising", "type": "technique"},
    "tech_impossible_light_1": {"search": "impossible light source photography", "type": "technique"},
    "tech_impossible_light_2": {"search": "dramatic chiaroscuro commercial", "type": "technique"},
    "tech_shadow_play_1": {"search": "creative shadow photography", "type": "technique"},
    "tech_shadow_play_2": {"search": "shadow storytelling advertising", "type": "technique"},
    "tech_scale_distort_1": {"search": "miniature world advertising", "type": "technique"},
    "tech_scale_distort_2": {"search": "giant everyday object photography", "type": "technique"},
    "tech_frozen_motion_1": {"search": "frozen motion photography", "type": "technique"},
    "tech_frozen_motion_2": {"search": "high speed commercial photography", "type": "technique"},
    "tech_time_manip_1": {"search": "time lapse composite advertising", "type": "technique"},
    "tech_time_manip_2": {"search": "decay and bloom commercial", "type": "technique"},
    
    # === 8. AD FORMATS (10) ===
    "ad_ooh_1": {"search": "OOH advertising concept", "type": "ad_format"},
    "ad_ooh_2": {"search": "billboard design creative", "type": "ad_format"},
    "ad_minimalist_print_1": {"search": "minimalist print ad", "type": "ad_format"},
    "ad_minimalist_print_2": {"search": "clean print advertising", "type": "ad_format"},
    "ad_optical_illusion_1": {"search": "optical illusion advertising", "type": "ad_format"},
    "ad_optical_illusion_2": {"search": "perspective play ads", "type": "ad_format"},
    "ad_surreal_1": {"search": "surreal advertising campaign", "type": "ad_format"},
    "ad_surreal_2": {"search": "dreamlike commercial", "type": "ad_format"},
    "ad_kv_1": {"search": "key visual composition", "type": "ad_format"},
    "ad_kv_2": {"search": "hero image advertising", "type": "ad_format"},
    
    # === 9. BRAND AESTHETICS (8) ===
    "brand_hermes_1": {"search": "Hermes advertising style", "type": "brand_aesthetic"},
    "brand_hermes_2": {"search": "luxury brand surrealism", "type": "brand_aesthetic"},
    "brand_apple_1": {"search": "Apple advertising aesthetic", "type": "brand_aesthetic"},
    "brand_apple_2": {"search": "tech minimalism photography", "type": "brand_aesthetic"},
    "brand_chanel_1": {"search": "Chanel advertising campaign", "type": "brand_aesthetic"},
    "brand_chanel_2": {"search": "luxury fashion editorial", "type": "brand_aesthetic"},
    "brand_nike_1": {"search": "Nike advertising style", "type": "brand_aesthetic"},
    "brand_nike_2": {"search": "dynamic sports commercial", "type": "brand_aesthetic"},
    
    # === 10. INDUSTRY VISUALS (8) ===
    "ind_perfume_1": {"search": "perfume advertising photography", "type": "industry"},
    "ind_perfume_2": {"search": "fragrance campaign visual", "type": "industry"},
    "ind_watch_1": {"search": "luxury watch photography", "type": "industry"},
    "ind_watch_2": {"search": "timepiece advertising", "type": "industry"},
    "ind_auto_1": {"search": "automotive advertising photography", "type": "industry"},
    "ind_auto_2": {"search": "car commercial campaign", "type": "industry"},
    "ind_skincare_1": {"search": "skincare advertising photography", "type": "industry"},
    "ind_skincare_2": {"search": "beauty product commercial", "type": "industry"},
}

# Merge expanded into main CATEGORIES
CATEGORIES.update(EXPANDED_CATEGORIES)

# === EXPANDED CATEGORY ORDER (New Taxonomy keywords) ===
EXPANDED_ORDER = [
    # Art Movements
    "art_surrealism_1", "art_surrealism_2", "art_surrealism_3",
    "art_magical_realism_1", "art_magical_realism_2", "art_magical_realism_3",
    "art_hyperrealism_1", "art_hyperrealism_2", "art_hyperrealism_3",
    "art_minimalism_1", "art_minimalism_2", "art_minimalism_3",
    "art_pop_art_1", "art_pop_art_2", "art_pop_art_3",
    "art_romanticism_1", "art_romanticism_2", "art_romanticism_3",
    "art_nouveau_1", "art_nouveau_2", "art_nouveau_3",
    "art_bauhaus_1", "art_bauhaus_2", "art_bauhaus_3",
    "art_japanese_1", "art_japanese_2", "art_japanese_3",
    "art_futurism_1", "art_futurism_2", "art_futurism_3",
    # Techniques
    "tech_visual_integration_1", "tech_visual_integration_2",
    "tech_partial_immersion_1", "tech_partial_immersion_2",
    "tech_reality_canvas_1", "tech_reality_canvas_2",
    "tech_material_transform_1", "tech_material_transform_2",
    "tech_dimensional_break_1", "tech_dimensional_break_2",
    "tech_impossible_light_1", "tech_impossible_light_2",
    "tech_shadow_play_1", "tech_shadow_play_2",
    "tech_scale_distort_1", "tech_scale_distort_2",
    "tech_frozen_motion_1", "tech_frozen_motion_2",
    "tech_time_manip_1", "tech_time_manip_2",
    # Ad Formats
    "ad_ooh_1", "ad_ooh_2", "ad_minimalist_print_1", "ad_minimalist_print_2",
    "ad_optical_illusion_1", "ad_optical_illusion_2",
    "ad_surreal_1", "ad_surreal_2", "ad_kv_1", "ad_kv_2",
    # Brand Aesthetics
    "brand_hermes_1", "brand_hermes_2", "brand_apple_1", "brand_apple_2",
    "brand_chanel_1", "brand_chanel_2", "brand_nike_1", "brand_nike_2",
    # Industry
    "ind_perfume_1", "ind_perfume_2", "ind_watch_1", "ind_watch_2",
    "ind_auto_1", "ind_auto_2", "ind_skincare_1", "ind_skincare_2",
]

# === DEFAULT CATEGORY ORDER ===
# Default: Run EXPANDED (new taxonomy) 76 keywords
# Options: python master_scraper.py --original | --expanded | --all
CATEGORY_ORDER = EXPANDED_ORDER

# === CSV COLUMNS ===
CSV_COLUMNS = [
    "url", "pin_url", "category", "category_type", "search_term",
    "title", "alt_text", "saves", "comments", "engagement_score",
    "content_hash", "collected_at"
]

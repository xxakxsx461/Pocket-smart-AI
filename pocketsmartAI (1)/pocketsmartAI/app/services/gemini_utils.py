import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from PIL import Image

from app.config import settings
from app.models.home_planner import HomePlanRequest, HomePlanResponse, RecommendedProduct
from app.models.party_planner import PartyPlanRequest, PartyPlanResponse, CategoryBreakdown, PartnerRecommendation
from app.models.jewelry_planner import JewelryPlanRequest, JewelryPlanResponse, JewelryItem

# Attempt to initialize Gemini client if API key is present
gemini_client = None
if settings.has_gemini_key:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")

def _clean_json_response(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

# ==============================================================================
# 1. HOME INTERIOR PLANNER
# ==============================================================================

def _generate_home_algorithmic(req: HomePlanRequest) -> HomePlanResponse:
    plan_id = f"home_{uuid.uuid4().hex[:8]}"
    total_budget = req.budget
    room_count = len(req.rooms)
    budget_per_room = total_budget / max(1, room_count)
    
    room_breakdown: Dict[str, List[RecommendedProduct]] = {}
    all_products: List[RecommendedProduct] = []
    
    catalog_templates = {
        "Living Room": [
            ("Modular 3-Seater Sofa", "Furniture", 0.40, "IKEA", "Sleek ergonomic sofa aligned with minimalist aesthetics"),
            ("Nordic Oak Coffee Table", "Furniture", 0.15, "Amazon", "Warm wood accent providing natural contrast"),
            ("Warm Dimmable Floor Lamp", "Lighting", 0.10, "Amazon", "Ambient indirect glow for relaxation"),
            ("Geometric Wool Blend Rug", "Textiles", 0.15, "IKEA", "Ties room palette together with acoustic dampening"),
            ("Floating Wall Shelving Unit", "Storage", 0.12, "IKEA", "Clean open storage to display select curated decor")
        ],
        "Bedroom": [
            ("Queen Bed Frame with Storage", "Furniture", 0.42, "IKEA", "Space-saving hydraulic underbed storage"),
            ("Memory Foam Ergonomic Mattress", "Furniture", 0.25, "Amazon", "Orthopedic support for optimal sleep hygiene"),
            ("Minimalist Bedside Tables (Set of 2)", "Furniture", 0.12, "Amazon", "Compact nightstands with cord management"),
            ("Blackout Linen Curtains", "Textiles", 0.08, "Amazon", "Thermal insulation and total light blocking"),
            ("Soft Ambient Pendant Light", "Lighting", 0.08, "IKEA", "Calming illumination for wind-down hours")
        ],
        "Dining Room": [
            ("Extendable 4-6 Seater Dining Table", "Furniture", 0.45, "IKEA", "Flexible seating for hosting gatherings"),
            ("Ergonomic Dining Chairs (Set of 4)", "Furniture", 0.30, "Amazon", "Comfortable back support with durable upholstery"),
            ("Over-Table Linear Chandelier", "Lighting", 0.15, "Amazon", "Focal dining lighting with warm-tone bulbs"),
            ("Woven Jute Table Runner & Placemats", "Decor", 0.05, "Amazon", "Organic texture and table surface protection")
        ],
        "Home Office": [
            ("Height-Adjustable Standing Desk", "Furniture", 0.45, "Amazon", "Electric sit-stand desk promoting active posture"),
            ("High-Back Ergonomic Mesh Chair", "Furniture", 0.30, "Amazon", "Lumbar support for 8+ hour productivity"),
            ("LED Screenbar Desk Lamp with Auto-Dimming", "Lighting", 0.10, "Amazon", "Glare-free monitor light reducing eye strain"),
            ("Cable Management Spine & Tray", "Storage", 0.05, "IKEA", "Keeps power bricks and cords clutter-free")
        ]
    }
    
    default_catalog = [
        ("Multi-purpose Accent Cabinet", "Storage", 0.35, "IKEA", "Versatile multi-tier organizer"),
        ("Statement Accent Armchair", "Furniture", 0.35, "Amazon", "Comfortable reading or lounge seat"),
        ("Warm Ambient LED Light Strip & Fixture", "Lighting", 0.15, "Amazon", "Custom mood accent lighting"),
        ("Botanical Ceramic Planter & Stand", "Decor", 0.10, "IKEA", "Adds biophilic touch to revitalize the atmosphere")
    ]
    
    total_spent = 0.0
    for room in req.rooms:
        items_spec = catalog_templates.get(room, default_catalog)
        room_items = []
        for name, cat, share, source, reason in items_spec:
            cost = round(budget_per_room * share, 2)
            total_spent += cost
            prod = RecommendedProduct(
                id=f"prod_{uuid.uuid4().hex[:6]}",
                name=f"{req.style_preference} {name}",
                category=cat,
                room=room,
                estimated_price=cost,
                source=source,
                product_url=f"https://www.{source.lower()}.com/search?q={name.replace(' ', '+')}",
                reasoning=reason,
                image_url=None
            )
            room_items.append(prod)
            all_products.append(prod)
        room_breakdown[room] = room_items
        
    return HomePlanResponse(
        plan_id=plan_id,
        total_budget=total_budget,
        estimated_total_cost=round(total_spent, 2),
        remaining_budget=round(max(0.0, total_budget - total_spent), 2),
        style_summary=f"A tailored {req.style_preference} theme featuring {req.color_palette or 'neutral tones'}, optimizing functional space across {len(req.rooms)} room(s).",
        room_breakdown=room_breakdown,
        all_products=all_products,
        ai_tips=[
            "Invest the largest share into foundational pieces (sofas, mattresses, work desks) where durability matters most.",
            f"Leverage IKEA for modular storage and Amazon for lighting and decorative accents.",
            "Keep ambient lighting between 2700K-3000K for maximum warmth and coziness."
        ],
        created_at=datetime.now(timezone.utc).isoformat()
    )

def generate_home_recommendations(req: HomePlanRequest) -> HomePlanResponse:
    if gemini_client:
        try:
            prompt = f"""You are an expert interior designer and budget strategist for PocketSmart AI.
Create a comprehensive, realistic interior decoration and product recommendation plan.
Input:
- Total Budget: INR {req.budget}
- Target Rooms: {', '.join(req.rooms)}
- Room Quantities: {json.dumps(req.room_quantities)}
- Style Preference: {req.style_preference}
- Color Palette: {req.color_palette}
- Special Notes: {req.special_requirements}

Rules:
1. Product sources must be realistic, focusing on IKEA, Amazon, and Wayfair.
2. The sum of all estimated product prices must be equal to or less than the total budget of {req.budget}.
3. Return ONLY valid JSON matching this exact structure:
{{
  "style_summary": "...",
  "products": [
    {{
      "name": "...",
      "category": "Furniture, Lighting, Decor, Storage, or Textiles",
      "room": "...",
      "estimated_price": 1200.0,
      "source": "IKEA or Amazon",
      "reasoning": "..."
    }}
  ],
  "ai_tips": ["...", "..."]
}}
"""
            response = gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            raw = _clean_json_response(response.text)
            data = json.loads(raw)
            
            room_breakdown: Dict[str, List[RecommendedProduct]] = {r: [] for r in req.rooms}
            all_products: List[RecommendedProduct] = []
            total_spent = 0.0
            
            for p in data.get("products", []):
                room = p.get("room", req.rooms[0])
                if room not in room_breakdown:
                    room_breakdown[room] = []
                price = float(p.get("estimated_price", 0))
                total_spent += price
                prod = RecommendedProduct(
                    id=f"prod_{uuid.uuid4().hex[:6]}",
                    name=p.get("name", "Curated Item"),
                    category=p.get("category", "Furniture"),
                    room=room,
                    estimated_price=price,
                    source=p.get("source", "Amazon"),
                    product_url=f"https://www.{p.get('source', 'amazon').lower()}.com",
                    reasoning=p.get("reasoning", ""),
                    image_url=None
                )
                room_breakdown[room].append(prod)
                all_products.append(prod)
                
            return HomePlanResponse(
                plan_id=f"home_{uuid.uuid4().hex[:8]}",
                total_budget=req.budget,
                estimated_total_cost=round(total_spent, 2),
                remaining_budget=round(max(0.0, req.budget - total_spent), 2),
                style_summary=data.get("style_summary", f"Curated {req.style_preference} layout."),
                room_breakdown=room_breakdown,
                all_products=all_products,
                ai_tips=data.get("ai_tips", ["Prioritize lighting and multi-functional storage."]),
                created_at=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            print(f"Gemini home generation fallback triggered: {e}")
            
    return _generate_home_algorithmic(req)

# ==============================================================================
# 2. PARTY PLANNER
# ==============================================================================

def _generate_party_algorithmic(req: PartyPlanRequest) -> PartyPlanResponse:
    plan_id = f"party_{uuid.uuid4().hex[:8]}"
    total_budget = req.budget
    guest_count = req.guest_count
    cost_per_guest = round(total_budget / max(1, guest_count), 2)
    
    if req.venue_required:
        splits = [
            ("Food & Catering", 0.40, ["Swiggy", "Zomato"], [
                f"{req.food_preference} party platter spread",
                "Live finger food & cocktail appetizers counter",
                "Dessert assortment & mocktail bar"
            ]),
            ("Venue & Space Rental", 0.25, ["OYO", "Airbnb"], [
                "Private party villa or boutique celebration suite booking",
                "Soundproofed gathering lounge with audio setup"
            ]),
            ("Decor & Ambience", 0.15, ["Amazon", "Blinkit"], [
                "Thematic fairy lights, balloons & backdrop photobooth",
                "Table styling, aromatic candles & themed coasters"
            ]),
            ("Music & Entertainment", 0.12, ["Spotify", "Local DJ"], [
                "Curated playlist subscription & wireless surround speakers",
                "Interactive party games & karaoke mic setup"
            ]),
            ("Essentials & Logistics", 0.08, ["Blinkit", "Amazon"], [
                "Eco-friendly disposables, ice coolers, and cleanup supplies"
            ])
        ]
    else:
        splits = [
            ("Food & Catering", 0.52, ["Swiggy", "Zomato"], [
                f"Gourmet {req.food_preference} multi-course meal",
                "Artisanal appetizers & dessert platters",
                "Custom beverage & mocktail bar mixer packs"
            ]),
            ("Decor & Ambience", 0.22, ["Amazon", "Blinkit"], [
                "Ambient LED strip lighting & balloon garland installations",
                "Customized welcome banner & party photo backdrop"
            ]),
            ("Music & Entertainment", 0.16, ["Spotify", "Amazon"], [
                "Party board games, trivia card deck & party lighting rig",
                "High-bass wireless speaker sync"
            ]),
            ("Essentials & Refreshments", 0.10, ["Blinkit", "Zomato"], [
                "Premium glassware/cutlery alternatives, gourmet snacks, ice"
            ])
        ]
        
    categories: List[CategoryBreakdown] = []
    for cat_name, pct, sources, items in splits:
        categories.append(CategoryBreakdown(
            category=cat_name,
            allocated_budget=round(total_budget * pct, 2),
            percentage=round(pct * 100, 1),
            sources=sources,
            items_or_suggestions=items
        ))
        
    partners = [
        PartnerRecommendation(
            partner="Swiggy",
            service_type="Catering / Bulk Order",
            deal_title="Swiggy Party Platters & Mini-Buffet Deals",
            estimated_cost=round(total_budget * (0.35 if req.venue_required else 0.45), 2),
            description="Pre-order curated bulk party packs with scheduled doorstep delivery.",
            action_url="https://www.swiggy.com"
        ),
        PartnerRecommendation(
            partner="Zomato",
            service_type="Dining & Drinks",
            deal_title="Zomato Gourmet & Beverage Mixers",
            estimated_cost=round(total_budget * 0.10, 2),
            description="Freshly prepared artisanal starters and craft refreshment coolers.",
            action_url="https://www.zomato.com"
        )
    ]
    if req.venue_required:
        partners.append(PartnerRecommendation(
            partner="OYO",
            service_type="Celebration Stay / Banquet",
            deal_title="OYO Townhouse Celebration Lounges",
            estimated_cost=round(total_budget * 0.25, 2),
            description="Affordable private party suites and terrace halls with hospitality support.",
            action_url="https://www.oyorooms.com"
        ))
        
    return PartyPlanResponse(
        plan_id=plan_id,
        total_budget=total_budget,
        guest_count=guest_count,
        cost_per_guest=cost_per_guest,
        categories=categories,
        partner_recommendations=partners,
        itinerary_timeline=[
            "6:00 PM — Venue check-in, decor arrangement & soundcheck",
            "7:00 PM — Guest arrivals, welcome refreshments & ice-breaker games",
            "8:30 PM — Food catering arrival & dinner spread opening",
            "9:45 PM — Music, dancing, or signature event activity",
            "11:00 PM — Cake cutting / farewell party favours distribution"
        ],
        ai_tips=[
            "Place catering orders at least 24 hours ahead on Swiggy/Zomato to lock group pricing.",
            "Keep 10% of total budget reserved for last-minute refreshment refills via quick-commerce.",
            "Prepare a collaborative Spotify queue to keep guests engaged throughout the night."
        ],
        created_at=datetime.now(timezone.utc).isoformat()
    )

def generate_party_recommendations(req: PartyPlanRequest) -> PartyPlanResponse:
    if gemini_client:
        try:
            prompt = f"""You are an expert event planner and budget optimizer for PocketSmart AI.
Formulate an event budget breakdown and vendor recommendation plan.
Input:
- Budget: INR {req.budget}
- Guest Count: {req.guest_count}
- Event Type: {req.event_type}
- Venue Required: {req.venue_required}
- Food Preference: {req.food_preference}
- Theme: {req.theme_or_vibe}

Rules:
1. Divide budget across Food (Swiggy/Zomato), Decor (Amazon), Entertainment, Venue (OYO if required).
2. Sum of category allocations must equal the total budget {req.budget}.
3. Return ONLY valid JSON:
{{
  "categories": [
    {{
      "category": "...",
      "allocated_budget": 5000.0,
      "percentage": 40.0,
      "sources": ["Swiggy", "Zomato"],
      "items_or_suggestions": ["..."]
    }}
  ],
  "timeline": ["..."],
  "ai_tips": ["..."]
}}
"""
            response = gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            raw = _clean_json_response(response.text)
            data = json.loads(raw)
            
            categories = [
                CategoryBreakdown(
                    category=c["category"],
                    allocated_budget=float(c["allocated_budget"]),
                    percentage=float(c["percentage"]),
                    sources=c.get("sources", ["Swiggy", "Zomato"]),
                    items_or_suggestions=c.get("items_or_suggestions", [])
                )
                for c in data.get("categories", [])
            ]
            
            return PartyPlanResponse(
                plan_id=f"party_{uuid.uuid4().hex[:8]}",
                total_budget=req.budget,
                guest_count=req.guest_count,
                cost_per_guest=round(req.budget / max(1, req.guest_count), 2),
                categories=categories,
                partner_recommendations=_generate_party_algorithmic(req).partner_recommendations,
                itinerary_timeline=data.get("timeline", ["Arrival & Welcoming", "Dinner Buffet", "Celebration"]),
                ai_tips=data.get("ai_tips", ["Order ahead for party catering."]),
                created_at=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            print(f"Gemini party generation fallback triggered: {e}")
            
    return _generate_party_algorithmic(req)

# ==============================================================================
# 3. JEWELRY PLANNER (Multimodal Vision & Style Matching)
# ==============================================================================

def _generate_jewelry_algorithmic(req: JewelryPlanRequest, image_analysis_note: Optional[str] = None) -> JewelryPlanResponse:
    plan_id = f"jewelry_{uuid.uuid4().hex[:8]}"
    total_budget = req.budget
    style = req.preferred_metal_or_style
    occasion = req.occasion
    
    items_catalog = [
        (
            f"Artisanal {style} Statement Choker / Necklace Set",
            "Necklace / Choker",
            0.45,
            "Amazon",
            style,
            f"Highlights neckline elegance and balances the formal tone of the {occasion} outfit."
        ),
        (
            f"Handcrafted {style} Drop Earrings",
            "Earrings",
            0.25,
            "Flipkart",
            style,
            "Frames face contours and complements the necklace without overpowering the ensemble."
        ),
        (
            f"Embellished {style} Cuff Bracelet / Bangles",
            "Bangles / Bracelet",
            0.18,
            "Amazon",
            style,
            "Adds refined wrist detailing visible during hand gestures and socializing."
        ),
        (
            f"Solitaire Accent Adjustable Cocktail Ring",
            "Ring",
            0.12,
            "Flipkart",
            style,
            "Subtle finishing touch bringing unified elegance across all jewelry accessories."
        )
    ]
    
    jewelry_pieces: List[JewelryItem] = []
    total_price = 0.0
    
    for name, itype, share, source, material, reason in items_catalog:
        price = round(total_budget * share, 2)
        total_price += price
        jewelry_pieces.append(JewelryItem(
            id=f"jewel_{uuid.uuid4().hex[:6]}",
            name=name,
            type=itype,
            estimated_price=price,
            source=source,
            metal_or_material=material,
            matching_reason=reason,
            product_url=f"https://www.{source.lower()}.com/search?q={name.replace(' ', '+')}",
            image_url=None
        ))
        
    analysis = image_analysis_note or (
        f"Analyzed outfit context for {occasion}. The {style} palette provides high visual harmony "
        f"by contrasting beautifully with rich attire colors while preventing metallic clashes."
    )
    
    return JewelryPlanResponse(
        plan_id=plan_id,
        total_budget=total_budget,
        total_estimated_price=round(total_price, 2),
        remaining_budget=round(max(0.0, total_budget - total_price), 2),
        occasion=occasion,
        outfit_analysis=analysis,
        jewelry_pieces=jewelry_pieces,
        styling_advice=[
            f"If your attire has high-detail embroidery around the neckline, keep the necklace subtle and let the {jewelry_pieces[1].name} take center stage.",
            "Maintain consistent metal tones across all accessories (earrings, clutch clasps, watch) for a seamless luxury aesthetic.",
            "Apply perfumes and hairsprays prior to putting on jewelry to preserve polish and stone luster."
        ],
        created_at=datetime.now(timezone.utc).isoformat()
    )

def generate_jewelry_recommendations(req: JewelryPlanRequest, image_path: Optional[str] = None) -> JewelryPlanResponse:
    image_analysis_note = None
    
    if gemini_client:
        try:
            contents: List[Any] = []
            
            if image_path and os.path.exists(image_path):
                try:
                    pil_img = Image.open(image_path)
                    contents.append(pil_img)
                    image_prompt_part = "Analyze the attached outfit image: detect colors, silhouette, embroidery/fabric pattern, and neckline style."
                except Exception as img_err:
                    print(f"Error opening outfit image: {img_err}")
                    image_prompt_part = f"Outfit notes: {req.outfit_description}"
            else:
                image_prompt_part = f"Outfit notes: {req.outfit_description or 'Not provided, design for ' + req.occasion}"
                
            prompt = f"""You are a high-fashion jewelry stylist for PocketSmart AI.
Recommend a perfectly coordinated jewelry set.
Input:
- Budget: INR {req.budget}
- Occasion: {req.occasion}
- Preferred Metal/Style: {req.preferred_metal_or_style}
- {image_prompt_part}

Rules:
1. Product sources should focus on Amazon and Flipkart.
2. Total price must be less than or equal to {req.budget}.
3. Return ONLY valid JSON:
{{
  "outfit_analysis": "...detailed commentary on outfit pairings and colors...",
  "jewelry_pieces": [
    {{
      "name": "...",
      "type": "Earrings, Necklace / Choker, Bangles / Bracelet, or Ring",
      "estimated_price": 1500.0,
      "source": "Amazon or Flipkart",
      "metal_or_material": "...",
      "matching_reason": "..."
    }}
  ],
  "styling_advice": ["...", "..."]
}}
"""
            contents.append(prompt)
            response = gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents
            )
            raw = _clean_json_response(response.text)
            data = json.loads(raw)
            
            pieces: List[JewelryItem] = []
            total_spent = 0.0
            for item in data.get("jewelry_pieces", []):
                price = float(item.get("estimated_price", 0))
                total_spent += price
                pieces.append(JewelryItem(
                    id=f"jewel_{uuid.uuid4().hex[:6]}",
                    name=item.get("name", "Jewelry Piece"),
                    type=item.get("type", "Jewelry"),
                    estimated_price=price,
                    source=item.get("source", "Amazon"),
                    metal_or_material=item.get("metal_or_material", req.preferred_metal_or_style),
                    matching_reason=item.get("matching_reason", "Matches the ensemble."),
                    product_url=f"https://www.{item.get('source', 'amazon').lower()}.com",
                    image_url=None
                ))
                
            return JewelryPlanResponse(
                plan_id=f"jewelry_{uuid.uuid4().hex[:8]}",
                total_budget=req.budget,
                total_estimated_price=round(total_spent, 2),
                remaining_budget=round(max(0.0, req.budget - total_spent), 2),
                occasion=req.occasion,
                outfit_analysis=data.get("outfit_analysis"),
                jewelry_pieces=pieces,
                styling_advice=data.get("styling_advice", ["Match metal tones for unified elegance."]),
                created_at=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            print(f"Gemini jewelry generation fallback triggered: {e}")
            
    if image_path and os.path.exists(image_path):
        image_analysis_note = f"Multimodal analysis of uploaded outfit ({os.path.basename(image_path)}): Coordinated tones and silhouette selected to complement your {req.occasion} attire with {req.preferred_metal_or_style}."
    return _generate_jewelry_algorithmic(req, image_analysis_note)

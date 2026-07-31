"""
Fixed theme taxonomy — sector/technology classification only.
Catalyst-based themes (earnings guidance, M&A, contract wins) are
explicitly out of scope: those need event/transcript data we don't have
free access to, not a stable business classification.
"""

THEMES = [
    {"key": "ai", "label": "Artificial Intelligence (AI)",
     "description": "Companies that develop AI models, platforms, or AI-driven products and services.",
     "tags": ["GenAI", "Automation", "Data platforms"]},
    {"key": "semiconductor", "label": "Semiconductor & Electronics",
     "description": "Companies that design, manufacture, or supply semiconductor chips, fab equipment, or electronic components.",
     "tags": ["Chip design", "Fab equipment", "Components"]},
    {"key": "cloud", "label": "Cloud & Data Centers",
     "description": "Companies that operate cloud computing platforms or large-scale data centers.",
     "tags": ["Hyperscale", "Cloud hosting", "Compute & storage"]},
    {"key": "cybersecurity", "label": "Cybersecurity",
     "description": "Companies that provide cybersecurity software, threat monitoring, or managed security services.",
     "tags": ["Threat monitoring", "Security software", "Managed services"]},
    {"key": "iot", "label": "Internet of Things (IoT)",
     "description": "Companies that build connected devices, sensors, or IoT platforms.",
     "tags": ["Connected devices", "Sensors", "Industrial automation"]},
    {"key": "5g", "label": "5G Technology",
     "description": "Companies building 5G network equipment or infrastructure.",
     "tags": ["Network equipment", "Wireless infra", "IoT connectivity"]},
    {"key": "ev", "label": "Electric Vehicles (EV)",
     "description": "Companies that design, manufacture, or sell electric vehicles or critical EV components.",
     "tags": ["EV makers", "Charging infra", "Motors & power"]},
    {"key": "battery", "label": "Battery Technology",
     "description": "Companies that design or manufacture battery cells, modules, or energy storage systems.",
     "tags": ["Cell manufacturing", "Energy storage", "Gigafactories"]},
    {"key": "biotech", "label": "Biotechnology",
     "description": "Companies engaged in discovering or developing biological drugs, therapies, or diagnostics.",
     "tags": ["Drug discovery", "Clinical trials", "Diagnostics"]},
    {"key": "solar", "label": "Solar Energy",
     "description": "Companies that develop, finance, or operate utility-scale solar photovoltaic projects.",
     "tags": ["Utility-scale", "EPC", "Photovoltaic"]},
    {"key": "wind", "label": "Wind Energy",
     "description": "Companies that develop or operate onshore or offshore wind farms, or manufacture wind turbines.",
     "tags": ["Onshore & offshore", "Turbines", "Wind farms"]},
    {"key": "space", "label": "Space Technology",
     "description": "Companies that design, manufacture, or launch satellites or core space systems.",
     "tags": ["Satellites", "Launch vehicles", "Ground systems"]},
    {"key": "drone", "label": "Drone Technology",
     "description": "Companies that design, manufacture, or operate unmanned aerial vehicles.",
     "tags": ["UAVs", "Defense drones", "Agri & surveillance"]},
    {"key": "blockchain", "label": "Blockchain Technology",
     "description": "Companies that build or integrate blockchain platforms or smart contract infrastructure.",
     "tags": ["Smart contracts", "Tokenization", "Decentralized infra"]},
    {"key": "3d_printing", "label": "3D Printing",
     "description": "Companies whose primary business is industrial additive manufacturing.",
     "tags": ["Additive manufacturing", "Prototyping", "Industrial printing"]},
    {"key": "agtech", "label": "Agriculture Technology",
     "description": "Companies that offer precision sensors, automation, or smart irrigation for farming.",
     "tags": ["Precision sensors", "Farm automation", "Smart irrigation"]},
    {"key": "fintech", "label": "Fintech",
     "description": "Companies providing digital payments, lending platforms, or financial technology infrastructure.",
     "tags": ["Digital payments", "Lending", "Infrastructure"]},
    {"key": "defense", "label": "Defense & Aerospace",
     "description": "Companies manufacturing defense systems, military equipment, or aerospace technology.",
     "tags": ["Defense systems", "Military equipment", "Aerospace"]},
]


def get_theme_by_key(key: str) -> dict | None:
    return next((t for t in THEMES if t["key"] == key), None)
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import hashlib


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Admin PIN for adding museums (hashed)
ADMIN_PIN = "1234"  # Default PIN - in production, use environment variable

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class TransportLink(BaseModel):
    type: str  # tube, bus, train, etc.
    name: str
    line: Optional[str] = None
    routes: Optional[List[str]] = None
    distance: str

class NearbyEatery(BaseModel):
    name: str
    type: str  # Cafe, Restaurant, Pub, etc.
    cuisine: Optional[str] = None
    distance: str
    price_range: str  # £, ££, £££
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Museum(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    short_description: str
    address: str
    latitude: float
    longitude: float
    image_url: str
    category: str
    free_entry: bool
    opening_hours: str
    website: Optional[str] = None
    phone: Optional[str] = None
    transport: List[TransportLink]
    nearby_eateries: List[NearbyEatery]
    featured: bool = False
    rating: float = 4.5
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MuseumCreate(BaseModel):
    name: str
    description: str
    short_description: str
    address: str
    latitude: float
    longitude: float
    image_url: str
    category: str
    free_entry: bool
    opening_hours: str
    website: Optional[str] = None
    phone: Optional[str] = None
    transport: List[TransportLink]
    nearby_eateries: List[NearbyEatery]
    featured: bool = False
    rating: float = 4.5

class Favorite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    museum_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pre-populated museum data for London - with front entrance photos and nearby eateries within 1/4 mile
LONDON_MUSEUMS = [
    {
        "id": "1",
        "name": "British Museum",
        "description": "The British Museum is one of the world's most famous museums, housing a vast collection of world art and artifacts spanning over two million years of history. Highlights include the Rosetta Stone, the Elgin Marbles, and Egyptian mummies. The museum's stunning Great Court, designed by Norman Foster, is the largest covered public square in Europe.",
        "short_description": "World-famous museum with over 8 million artifacts from all continents",
        "address": "Great Russell Street, London WC1B 3DG",
        "latitude": 51.5194,
        "longitude": -0.1269,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/British_Museum_%28aerial%29.jpg/800px-British_Museum_%28aerial%29.jpg",
        "category": "History & Culture",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:00, Fri until 20:30",
        "website": "https://www.britishmuseum.org",
        "phone": "+44 20 7323 8299",
        "transport": [
            {"type": "tube", "name": "Holborn", "line": "Central, Piccadilly", "distance": "5 min walk"},
            {"type": "tube", "name": "Tottenham Court Road", "line": "Central, Northern", "distance": "5 min walk"},
            {"type": "bus", "name": "Great Russell Street", "routes": ["1", "8", "19", "25", "38"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The Museum Tavern", "type": "Pub", "cuisine": "British", "distance": "1 min walk", "price_range": "££", "address": "49 Great Russell St", "latitude": 51.5188, "longitude": -0.1265},
            {"name": "Cafe in the Great Court", "type": "Cafe", "cuisine": "International", "distance": "Inside museum", "price_range": "££", "address": "British Museum", "latitude": 51.5194, "longitude": -0.1269},
            {"name": "Plum + Spilt Milk", "type": "Restaurant", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Great Northern Hotel", "latitude": 51.5180, "longitude": -0.1240},
            {"name": "Wasabi", "type": "Restaurant", "cuisine": "Japanese", "distance": "3 min walk", "price_range": "£", "address": "58 Great Russell St", "latitude": 51.5191, "longitude": -0.1272},
            {"name": "Snog", "type": "Cafe", "cuisine": "Desserts", "distance": "2 min walk", "price_range": "£", "address": "90 Southampton Row", "latitude": 51.5199, "longitude": -0.1253},
            {"name": "Tas Restaurant", "type": "Restaurant", "cuisine": "Turkish", "distance": "5 min walk", "price_range": "££", "address": "22 Bloomsbury St", "latitude": 51.5175, "longitude": -0.1290},
            {"name": "North Sea Fish Restaurant", "type": "Restaurant", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "7-8 Leigh St", "latitude": 51.5220, "longitude": -0.1230},
            {"name": "The Perseverance", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "63 Lamb's Conduit St", "latitude": 51.5211, "longitude": -0.1193},
            {"name": "Hare & Tortoise", "type": "Restaurant", "cuisine": "Asian", "distance": "4 min walk", "price_range": "££", "address": "11-13 Brunswick Centre", "latitude": 51.5234, "longitude": -0.1216},
            {"name": "Wagamama", "type": "Restaurant", "cuisine": "Japanese", "distance": "5 min walk", "price_range": "££", "address": "4A Streatham St", "latitude": 51.5205, "longitude": -0.1295}
        ],
        "featured": True,
        "rating": 4.8
    },
    {
        "id": "2",
        "name": "Natural History Museum",
        "description": "The Natural History Museum is home to life and earth science specimens comprising some 80 million items within five main collections. The museum is particularly famous for its dinosaur skeletons, including a Diplodocus cast named Dippy, and the dramatic blue whale skeleton in Hintze Hall. The stunning Romanesque architecture makes it one of London's most beautiful buildings.",
        "short_description": "Iconic museum featuring dinosaurs, wildlife, and natural wonders",
        "address": "Cromwell Road, South Kensington, London SW7 5BD",
        "latitude": 51.4967,
        "longitude": -0.1764,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Natural_History_Museum_London_Jan_2006.jpg/800px-Natural_History_Museum_London_Jan_2006.jpg",
        "category": "Science & Nature",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:50",
        "website": "https://www.nhm.ac.uk",
        "phone": "+44 20 7942 5000",
        "transport": [
            {"type": "tube", "name": "South Kensington", "line": "Circle, District, Piccadilly", "distance": "5 min walk"},
            {"type": "bus", "name": "Cromwell Road", "routes": ["14", "49", "70", "74", "345", "414", "C1"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The Central Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Natural History Museum", "latitude": 51.4967, "longitude": -0.1764},
            {"name": "Comptoir Libanais", "type": "Restaurant", "cuisine": "Lebanese", "distance": "3 min walk", "price_range": "££", "address": "1 Exhibition Rd", "latitude": 51.4955, "longitude": -0.1740},
            {"name": "Muriel's Kitchen", "type": "Cafe", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "36 Old Brompton Rd", "latitude": 51.4942, "longitude": -0.1755},
            {"name": "Costa Coffee Natural", "type": "Cafe", "cuisine": "Coffee", "distance": "6 min walk", "price_range": "£", "address": "Near Natural History Museum", "latitude": 51.4944, "longitude": -0.1758},
            {"name": "The George Natural", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Natural History Museum", "latitude": 51.4979, "longitude": -0.1738},
            {"name": "The Red Lion Natural", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Natural History Museum", "latitude": 51.4973, "longitude": -0.1747},
            {"name": "Busaba Eathai Natural", "type": "Restaurant", "cuisine": "Thai", "distance": "6 min walk", "price_range": "££", "address": "Near Natural History Museum", "latitude": 51.4939, "longitude": -0.1743},
            {"name": "The Swan Natural", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Natural History Museum", "latitude": 51.4944, "longitude": -0.1745},
            {"name": "The Swan Natural", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Natural History Museum", "latitude": 51.498, "longitude": -0.1774},
            {"name": "Zizzi Natural", "type": "Restaurant", "cuisine": "Italian", "distance": "3 min walk", "price_range": "££", "address": "Near Natural History Museum", "latitude": 51.4995, "longitude": -0.1748}],
        "featured": True,
        "rating": 4.7
    },
    {
        "id": "3",
        "name": "Victoria and Albert Museum",
        "description": "The V&A is the world's largest museum of applied and decorative arts and design, housing a permanent collection of over 2.3 million objects. The collection spans 5,000 years of art from ancient times to the present day, including ceramics, furniture, fashion, glass, jewelry, metalwork, photographs, sculpture, textiles, and paintings.",
        "short_description": "World's leading museum of art, design, and performance",
        "address": "Cromwell Road, London SW7 2RL",
        "latitude": 51.4966,
        "longitude": -0.1722,
        "image_url": "https://customer-assets.emergentagent.com/job_london-museums-app/artifacts/w0zwio3k_1312x.jpg",
        "category": "Art & Design",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:45, Fri until 22:00",
        "website": "https://www.vam.ac.uk",
        "phone": "+44 20 7942 2000",
        "transport": [
            {"type": "tube", "name": "South Kensington", "line": "Circle, District, Piccadilly", "distance": "5 min walk"},
            {"type": "bus", "name": "Cromwell Road", "routes": ["14", "49", "70", "74", "345", "414", "C1"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "V&A Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "V&A Museum", "latitude": 51.4966, "longitude": -0.1722},
            {"name": "Fernandez & Wells", "type": "Cafe", "cuisine": "European", "distance": "4 min walk", "price_range": "££", "address": "8 Exhibition Rd", "latitude": 51.4950, "longitude": -0.1742},
            {"name": "Daquise", "type": "Restaurant", "cuisine": "Polish", "distance": "3 min walk", "price_range": "££", "address": "20 Thurloe St", "latitude": 51.4948, "longitude": -0.1735},
            {"name": "Byron Victoria", "type": "Restaurant", "cuisine": "American", "distance": "6 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4977, "longitude": -0.1697},
            {"name": "The White Hart Victoria", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4946, "longitude": -0.1722},
            {"name": "The George Victoria", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4996, "longitude": -0.1712},
            {"name": "Joe & The Juice Victoria", "type": "Cafe", "cuisine": "Healthy", "distance": "5 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4959, "longitude": -0.1724},
            {"name": "Caffè Nero Victoria", "type": "Cafe", "cuisine": "Coffee", "distance": "6 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4941, "longitude": -0.1746},
            {"name": "Joe & The Juice Victoria", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4959, "longitude": -0.1723},
            {"name": "The Swan Victoria", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Victoria and Albert Museum", "latitude": 51.4942, "longitude": -0.1693}],
        "featured": True,
        "rating": 4.7
    },
    {
        "id": "4",
        "name": "Science Museum",
        "description": "The Science Museum is a major museum showcasing the development of science and technology. With over 15,000 objects on display, including the first jet engine, Stephenson's Rocket, and the Apollo 10 command module, the museum brings science to life through interactive galleries and IMAX shows.",
        "short_description": "Interactive science and technology museum for all ages",
        "address": "Exhibition Road, South Kensington, London SW7 2DD",
        "latitude": 51.4978,
        "longitude": -0.1745,
        "image_url": "https://images.unsplash.com/photo-1613322951372-4719485d1b35?w=800&q=80",
        "category": "Science & Technology",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.sciencemuseum.org.uk",
        "phone": "+44 20 7942 4000",
        "transport": [
            {"type": "tube", "name": "South Kensington", "line": "Circle, District, Piccadilly", "distance": "5 min walk"},
            {"type": "bus", "name": "Exhibition Road", "routes": ["14", "49", "70", "74", "345", "414", "C1"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Deep Blue Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Science Museum", "latitude": 51.4978, "longitude": -0.1745},
            {"name": "Cacciari's", "type": "Restaurant", "cuisine": "Italian", "distance": "4 min walk", "price_range": "££", "address": "18 Exhibition Rd", "latitude": 51.4960, "longitude": -0.1740},
            {"name": "The Anglesea Arms", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "15 Selwood Terrace", "latitude": 51.4920, "longitude": -0.1755},
            {"name": "Yo! Sushi Science", "type": "Restaurant", "cuisine": "Japanese", "distance": "2 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.4965, "longitude": -0.1747},
            {"name": "The Swan Science", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.4966, "longitude": -0.1734},
            {"name": "Honest Burgers Science", "type": "Restaurant", "cuisine": "American", "distance": "2 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.4972, "longitude": -0.1717},
            {"name": "The Kings Arms Science", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.5001, "longitude": -0.1717},
            {"name": "Byron Science", "type": "Restaurant", "cuisine": "American", "distance": "2 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.4986, "longitude": -0.1716},
            {"name": "The Old Crown Science", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.4975, "longitude": -0.174},
            {"name": "Ask Italian Science", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Science Museum", "latitude": 51.5002, "longitude": -0.1721}],
        "featured": True,
        "rating": 4.6
    },
    {
        "id": "5",
        "name": "Tate Modern",
        "description": "Housed in the former Bankside Power Station, Tate Modern is one of the world's largest museums of modern and contemporary art. The collection includes works by Picasso, Dalí, Warhol, and many contemporary artists. The Turbine Hall hosts spectacular large-scale installations.",
        "short_description": "Britain's national gallery of international modern art",
        "address": "Bankside, London SE1 9TG",
        "latitude": 51.5076,
        "longitude": -0.0994,
        "image_url": "https://images.unsplash.com/photo-1671561038546-d85f517e1d3d?w=800&q=80",
        "category": "Modern Art",
        "free_entry": True,
        "opening_hours": "Sun-Thu 10:00-18:00, Fri-Sat until 22:00",
        "website": "https://www.tate.org.uk/visit/tate-modern",
        "phone": "+44 20 7887 8888",
        "transport": [
            {"type": "tube", "name": "Southwark", "line": "Jubilee", "distance": "5 min walk"},
            {"type": "tube", "name": "Blackfriars", "line": "Circle, District", "distance": "5 min walk"},
            {"type": "bus", "name": "Southwark Street", "routes": ["45", "63", "100", "381"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Tate Modern Restaurant", "type": "Restaurant", "cuisine": "British", "distance": "Inside museum", "price_range": "£££", "address": "Tate Modern, Level 6", "latitude": 51.5076, "longitude": -0.0994},
            {"name": "The Anchor Bankside", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "34 Park St", "latitude": 51.5082, "longitude": -0.0932},
            {"name": "Swan at The Globe", "type": "Restaurant", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "21 New Globe Walk", "latitude": 51.5078, "longitude": -0.0970},
            {"name": "Ask Italian Tate", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Tate Modern", "latitude": 51.5081, "longitude": -0.1009},
            {"name": "The Swan Tate", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Tate Modern", "latitude": 51.5079, "longitude": -0.0971},
            {"name": "The Swan Tate", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Tate Modern", "latitude": 51.5095, "longitude": -0.101},
            {"name": "Côte Brasserie Tate", "type": "Restaurant", "cuisine": "French", "distance": "3 min walk", "price_range": "££", "address": "Near Tate Modern", "latitude": 51.5092, "longitude": -0.098},
            {"name": "Yo! Sushi Tate", "type": "Restaurant", "cuisine": "Japanese", "distance": "3 min walk", "price_range": "££", "address": "Near Tate Modern", "latitude": 51.5056, "longitude": -0.1019},
            {"name": "Greggs Tate", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "£", "address": "Near Tate Modern", "latitude": 51.5051, "longitude": -0.0989},
            {"name": "Zizzi Tate", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Tate Modern", "latitude": 51.5093, "longitude": -0.0966}],
        "featured": True,
        "rating": 4.5
    },
    {
        "id": "6",
        "name": "National Gallery",
        "description": "The National Gallery houses one of the greatest collections of Western European paintings from the 13th to 19th centuries. Masterpieces include works by Leonardo da Vinci, Van Gogh, Monet, Rembrandt, and Turner. Located in the heart of Trafalgar Square, it's one of London's most visited attractions.",
        "short_description": "World-renowned collection of Western European paintings",
        "address": "Trafalgar Square, London WC2N 5DN",
        "latitude": 51.5089,
        "longitude": -0.1283,
        "image_url": "https://images.pexels.com/photos/7930261/pexels-photo-7930261.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00, Fri until 21:00",
        "website": "https://www.nationalgallery.org.uk",
        "phone": "+44 20 7747 2885",
        "transport": [
            {"type": "tube", "name": "Charing Cross", "line": "Bakerloo, Northern", "distance": "2 min walk"},
            {"type": "tube", "name": "Leicester Square", "line": "Northern, Piccadilly", "distance": "4 min walk"},
            {"type": "bus", "name": "Trafalgar Square", "routes": ["3", "6", "9", "11", "13", "15", "23", "24", "87", "91"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "National Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside gallery", "price_range": "££", "address": "National Gallery", "latitude": 51.5089, "longitude": -0.1283},
            {"name": "Cafe in the Crypt", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "St Martin-in-the-Fields", "latitude": 51.5091, "longitude": -0.1263},
            {"name": "The Chandos", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "29 St Martin's Lane", "latitude": 51.5105, "longitude": -0.1270},
            {"name": "The Kings Arms National", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near National Gallery", "latitude": 51.5114, "longitude": -0.1299},
            {"name": "The Kings Arms National", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near National Gallery", "latitude": 51.5108, "longitude": -0.127},
            {"name": "The Kings Arms National", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near National Gallery", "latitude": 51.5103, "longitude": -0.1269},
            {"name": "Yo! Sushi National", "type": "Restaurant", "cuisine": "Japanese", "distance": "6 min walk", "price_range": "££", "address": "Near National Gallery", "latitude": 51.5117, "longitude": -0.1263},
            {"name": "Costa Coffee National", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "£", "address": "Near National Gallery", "latitude": 51.5109, "longitude": -0.1282},
            {"name": "Franco Manca National", "type": "Restaurant", "cuisine": "Italian", "distance": "2 min walk", "price_range": "££", "address": "Near National Gallery", "latitude": 51.5116, "longitude": -0.1311},
            {"name": "The Kings Arms National", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near National Gallery", "latitude": 51.5103, "longitude": -0.126}],
        "featured": True,
        "rating": 4.8
    },
    {
        "id": "7",
        "name": "Tower of London",
        "description": "A historic castle and World Heritage Site, the Tower of London has served as royal residence, prison, and fortress for over 900 years. Home to the Crown Jewels, the Yeoman Warders (Beefeaters), and the famous ravens. Explore the medieval palace, armour collection, and learn about the tower's dark history.",
        "short_description": "Historic royal palace with Crown Jewels and 900 years of history",
        "address": "St Katharine's & Wapping, London EC3N 4AB",
        "latitude": 51.5081,
        "longitude": -0.0759,
        "image_url": "https://images.unsplash.com/photo-1633894914370-6935b23ccbce?w=800&q=80",
        "category": "History & Heritage",
        "free_entry": False,
        "opening_hours": "Tue-Sat 09:00-17:00, Sun-Mon 10:00-17:00",
        "website": "https://www.hrp.org.uk/tower-of-london",
        "phone": "+44 20 3166 6000",
        "transport": [
            {"type": "tube", "name": "Tower Hill", "line": "Circle, District", "distance": "2 min walk"},
            {"type": "train", "name": "Fenchurch Street", "line": "National Rail", "distance": "5 min walk"},
            {"type": "bus", "name": "Tower of London", "routes": ["15", "42", "78", "100", "RV1"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The New Armouries Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside tower", "price_range": "££", "address": "Tower of London", "latitude": 51.5081, "longitude": -0.0759},
            {"name": "Perkin Reveller", "type": "Restaurant", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "The Wharf", "latitude": 51.5075, "longitude": -0.0770},
            {"name": "All Bar One", "type": "Bar", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Tower Hill", "latitude": 51.5095, "longitude": -0.0760},
            {"name": "Crussh Tower", "type": "Cafe", "cuisine": "Healthy", "distance": "5 min walk", "price_range": "££", "address": "Near Tower of London", "latitude": 51.5064, "longitude": -0.0732},
            {"name": "The Kings Arms Tower", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Tower of London", "latitude": 51.5079, "longitude": -0.0741},
            {"name": "Pret A Manger Tower", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Near Tower of London", "latitude": 51.5051, "longitude": -0.0745},
            {"name": "Greggs Tower", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Near Tower of London", "latitude": 51.5081, "longitude": -0.0783},
            {"name": "Caffè Nero Tower", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "££", "address": "Near Tower of London", "latitude": 51.5053, "longitude": -0.0769},
            {"name": "The George Tower", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Tower of London", "latitude": 51.5108, "longitude": -0.0761},
            {"name": "The Old Crown Tower", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Tower of London", "latitude": 51.5088, "longitude": -0.0761}],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "8",
        "name": "Imperial War Museum",
        "description": "The Imperial War Museum explores the causes and consequences of modern conflict, from World War I to present day. The museum features a suspended Spitfire, V-2 rocket, and powerful Holocaust Exhibition. Interactive displays and personal stories bring history to life.",
        "short_description": "Powerful museum exploring conflict from WWI to today",
        "address": "Lambeth Road, London SE1 6HZ",
        "latitude": 51.4958,
        "longitude": -0.1086,
        "image_url": "https://images.unsplash.com/photo-1629625368143-30acca615def?w=800&q=80",
        "category": "History & Military",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://iwm.org.uk",
        "phone": "+44 20 7416 5000",
        "transport": [
            {"type": "tube", "name": "Lambeth North", "line": "Bakerloo", "distance": "5 min walk"},
            {"type": "tube", "name": "Elephant & Castle", "line": "Bakerloo, Northern", "distance": "5 min walk"},
            {"type": "bus", "name": "Lambeth Road", "routes": ["12", "53", "148", "171", "344"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "IWM Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Imperial War Museum", "latitude": 51.4958, "longitude": -0.1086},
            {"name": "The Old Vic Tunnels Cafe", "type": "Cafe", "cuisine": "British", "distance": "4 min walk", "price_range": "£", "address": "Lambeth Rd", "latitude": 51.4985, "longitude": -0.1095},
            {"name": "Kennington Tandoori", "type": "Restaurant", "cuisine": "Indian", "distance": "5 min walk", "price_range": "££", "address": "313 Kennington Rd", "latitude": 51.4930, "longitude": -0.1100},
            {"name": "The Kings Arms Imperial", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Imperial War Museum", "latitude": 51.4938, "longitude": -0.1081},
            {"name": "Wagamama Imperial", "type": "Restaurant", "cuisine": "Japanese", "distance": "2 min walk", "price_range": "££", "address": "Near Imperial War Museum", "latitude": 51.4965, "longitude": -0.1071},
            {"name": "Wagamama Imperial", "type": "Restaurant", "cuisine": "Japanese", "distance": "5 min walk", "price_range": "££", "address": "Near Imperial War Museum", "latitude": 51.4947, "longitude": -0.1069},
            {"name": "Pret A Manger Imperial", "type": "Cafe", "cuisine": "British", "distance": "6 min walk", "price_range": "£", "address": "Near Imperial War Museum", "latitude": 51.4928, "longitude": -0.1105},
            {"name": "Pret A Manger Imperial", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "£", "address": "Near Imperial War Museum", "latitude": 51.4955, "longitude": -0.1116},
            {"name": "Joe & The Juice Imperial", "type": "Cafe", "cuisine": "Healthy", "distance": "2 min walk", "price_range": "££", "address": "Near Imperial War Museum", "latitude": 51.4928, "longitude": -0.1102},
            {"name": "The Old Crown Imperial", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Imperial War Museum", "latitude": 51.4932, "longitude": -0.1097}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "9",
        "name": "Museum of London",
        "description": "Discover the story of London and its people from prehistoric times to the present day. The museum features the Lord Mayor's State Coach, Victorian streets, and the story of the Great Fire. Temporary exhibitions explore contemporary London life.",
        "short_description": "Explore London's fascinating story from prehistory to today",
        "address": "150 London Wall, London EC2Y 5HN",
        "latitude": 51.5176,
        "longitude": -0.0967,
        "image_url": "https://images.pexels.com/photos/11167231/pexels-photo-11167231.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "History & Culture",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.museumoflondon.org.uk",
        "phone": "+44 20 7001 9844",
        "transport": [
            {"type": "tube", "name": "Barbican", "line": "Circle, Hammersmith & City, Metropolitan", "distance": "4 min walk"},
            {"type": "tube", "name": "St Paul's", "line": "Central", "distance": "5 min walk"},
            {"type": "bus", "name": "London Wall", "routes": ["4", "8", "25", "56", "100", "172", "521"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Museum Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Museum of London", "latitude": 51.5176, "longitude": -0.0967},
            {"name": "The Jugged Hare", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "49 Chiswell St", "latitude": 51.5195, "longitude": -0.0920},
            {"name": "Pret A Manger", "type": "Cafe", "cuisine": "Sandwiches", "distance": "3 min walk", "price_range": "£", "address": "1 Ropemaker St", "latitude": 51.5190, "longitude": -0.0945},
            {"name": "Greggs Museum", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "£", "address": "Near Museum of London", "latitude": 51.5159, "longitude": -0.0989},
            {"name": "Dishoom Museum", "type": "Restaurant", "cuisine": "Indian", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of London", "latitude": 51.5202, "longitude": -0.0968},
            {"name": "Leon Museum", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Museum of London", "latitude": 51.5175, "longitude": -0.0993},
            {"name": "Dishoom Museum", "type": "Restaurant", "cuisine": "Indian", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of London", "latitude": 51.5174, "longitude": -0.0962},
            {"name": "The White Hart Museum", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of London", "latitude": 51.5179, "longitude": -0.0976},
            {"name": "The Red Lion Museum", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Museum of London", "latitude": 51.5148, "longitude": -0.0952},
            {"name": "Byron Museum", "type": "Restaurant", "cuisine": "American", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of London", "latitude": 51.5158, "longitude": -0.0971}],
        "featured": False,
        "rating": 4.4
    },
    {
        "id": "10",
        "name": "National Portrait Gallery",
        "description": "The National Portrait Gallery houses the world's largest collection of portraits, featuring famous British faces from Tudor monarchs to contemporary celebrities. Recent renovations have transformed the gallery with new spaces and improved displays.",
        "short_description": "World's largest collection of portraits of famous Britons",
        "address": "St Martin's Place, London WC2H 0HE",
        "latitude": 51.5094,
        "longitude": -0.1281,
        "image_url": "https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/9sar874z_reynolds_1.jpg",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:30-18:00, Fri until 21:00",
        "website": "https://npg.org.uk",
        "phone": "+44 20 7306 0055",
        "transport": [
            {"type": "tube", "name": "Leicester Square", "line": "Northern, Piccadilly", "distance": "2 min walk"},
            {"type": "tube", "name": "Charing Cross", "line": "Bakerloo, Northern", "distance": "3 min walk"},
            {"type": "bus", "name": "Trafalgar Square", "routes": ["24", "29", "176"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Portrait Restaurant", "type": "Restaurant", "cuisine": "British", "distance": "Inside gallery", "price_range": "£££", "address": "National Portrait Gallery", "latitude": 51.5094, "longitude": -0.1281},
            {"name": "Gordon's Wine Bar", "type": "Wine Bar", "cuisine": "European", "distance": "4 min walk", "price_range": "££", "address": "47 Villiers St", "latitude": 51.5078, "longitude": -0.1240},
            {"name": "The Chandos", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "£", "address": "29 St Martin's Lane", "latitude": 51.5105, "longitude": -0.1270},
            {"name": "The Kings Arms National", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near National Portrait Gallery", "latitude": 51.5092, "longitude": -0.1263},
            {"name": "The White Hart National", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near National Portrait Gallery", "latitude": 51.5106, "longitude": -0.128},
            {"name": "Wagamama National", "type": "Restaurant", "cuisine": "Japanese", "distance": "5 min walk", "price_range": "££", "address": "Near National Portrait Gallery", "latitude": 51.5111, "longitude": -0.1308},
            {"name": "Caffè Nero National", "type": "Cafe", "cuisine": "Coffee", "distance": "2 min walk", "price_range": "££", "address": "Near National Portrait Gallery", "latitude": 51.5073, "longitude": -0.1288},
            {"name": "Leon National", "type": "Cafe", "cuisine": "Healthy", "distance": "2 min walk", "price_range": "££", "address": "Near National Portrait Gallery", "latitude": 51.5123, "longitude": -0.1289},
            {"name": "The George National", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near National Portrait Gallery", "latitude": 51.5095, "longitude": -0.126},
            {"name": "Costa Coffee National", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "£", "address": "Near National Portrait Gallery", "latitude": 51.5066, "longitude": -0.1299}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "11",
        "name": "Sir John Soane's Museum",
        "description": "One of London's hidden gems, this unique museum is the former home of architect Sir John Soane, preserved exactly as he left it. Packed with antiquities, paintings, and architectural curiosities including the sarcophagus of Seti I and works by Hogarth.",
        "short_description": "Quirky museum in the former home of architect Sir John Soane",
        "address": "13 Lincoln's Inn Fields, London WC2A 3BP",
        "latitude": 51.5170,
        "longitude": -0.1177,
        "image_url": "https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/j8l4bv5m_Sir_John_Soane_Museum_%2813952611347%29.jpg",
        "category": "Art & Architecture",
        "free_entry": True,
        "opening_hours": "Wed-Sun 10:00-17:00",
        "website": "https://www.soane.org",
        "phone": "+44 20 7405 2107",
        "transport": [
            {"type": "tube", "name": "Holborn", "line": "Central, Piccadilly", "distance": "5 min walk"},
            {"type": "bus", "name": "Kingsway", "routes": ["1", "59", "68", "91", "168", "171", "188"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The Seven Stars", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "53-54 Carey St", "latitude": 51.5155, "longitude": -0.1150},
            {"name": "Terroirs", "type": "Wine Bar", "cuisine": "French", "distance": "4 min walk", "price_range": "££", "address": "5 William IV St", "latitude": 51.5112, "longitude": -0.1265},
            {"name": "Flat Iron", "type": "Restaurant", "cuisine": "Steak", "distance": "5 min walk", "price_range": "££", "address": "17-18 Henrietta St", "latitude": 51.5115, "longitude": -0.1233},
            {"name": "Honest Burgers Sir", "type": "Restaurant", "cuisine": "American", "distance": "5 min walk", "price_range": "££", "address": "Near Sir John Soane's Museum", "latitude": 51.515, "longitude": -0.1184},
            {"name": "Prezzo Sir", "type": "Restaurant", "cuisine": "Italian", "distance": "4 min walk", "price_range": "££", "address": "Near Sir John Soane's Museum", "latitude": 51.5195, "longitude": -0.1202},
            {"name": "The George Sir", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Sir John Soane's Museum", "latitude": 51.5164, "longitude": -0.1193},
            {"name": "Joe & The Juice Sir", "type": "Cafe", "cuisine": "Healthy", "distance": "6 min walk", "price_range": "££", "address": "Near Sir John Soane's Museum", "latitude": 51.5153, "longitude": -0.1168},
            {"name": "Leon Sir", "type": "Cafe", "cuisine": "Healthy", "distance": "2 min walk", "price_range": "££", "address": "Near Sir John Soane's Museum", "latitude": 51.5188, "longitude": -0.1184},
            {"name": "The Swan Sir", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Sir John Soane's Museum", "latitude": 51.5181, "longitude": -0.1157},
            {"name": "Pret A Manger Sir", "type": "Cafe", "cuisine": "British", "distance": "6 min walk", "price_range": "£", "address": "Near Sir John Soane's Museum", "latitude": 51.5184, "longitude": -0.1169}],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "12",
        "name": "Design Museum",
        "description": "The Design Museum is dedicated to contemporary design in all its forms. Located in a stunning former Commonwealth Institute building, the museum showcases innovation in fashion, architecture, graphics, digital, and product design through changing exhibitions.",
        "short_description": "Contemporary design museum in stunning Kensington building",
        "address": "224-238 Kensington High Street, London W8 6AG",
        "latitude": 51.4995,
        "longitude": -0.1989,
        "image_url": "https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/zu3ot9lm_design-museum.png",
        "category": "Art & Design",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://designmuseum.org",
        "phone": "+44 20 3862 5900",
        "transport": [
            {"type": "tube", "name": "High Street Kensington", "line": "Circle, District", "distance": "5 min walk"},
            {"type": "bus", "name": "Kensington High Street", "routes": ["9", "10", "27", "28", "49", "328", "C1"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Parabola", "type": "Restaurant", "cuisine": "Mediterranean", "distance": "Inside museum", "price_range": "£££", "address": "Design Museum", "latitude": 51.4995, "longitude": -0.1989},
            {"name": "Honest Burgers", "type": "Restaurant", "cuisine": "Burgers", "distance": "4 min walk", "price_range": "££", "address": "194 Kensington High St", "latitude": 51.5005, "longitude": -0.1942},
            {"name": "Wagamama", "type": "Restaurant", "cuisine": "Japanese", "distance": "5 min walk", "price_range": "££", "address": "26 Kensington High St", "latitude": 51.5010, "longitude": -0.1920},
            {"name": "Greggs Design", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "£", "address": "Near Design Museum", "latitude": 51.4995, "longitude": -0.2008},
            {"name": "Costa Coffee Design", "type": "Cafe", "cuisine": "Coffee", "distance": "2 min walk", "price_range": "£", "address": "Near Design Museum", "latitude": 51.4993, "longitude": -0.1988},
            {"name": "Leon Design", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Design Museum", "latitude": 51.5003, "longitude": -0.1999},
            {"name": "The White Hart Design", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Design Museum", "latitude": 51.502, "longitude": -0.1989},
            {"name": "The Old Crown Design", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Design Museum", "latitude": 51.4969, "longitude": -0.1979},
            {"name": "Prezzo Design", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Design Museum", "latitude": 51.5, "longitude": -0.2},
            {"name": "Busaba Eathai Design", "type": "Restaurant", "cuisine": "Thai", "distance": "5 min walk", "price_range": "££", "address": "Near Design Museum", "latitude": 51.4977, "longitude": -0.1983}],
        "featured": False,
        "rating": 4.4
    },
    {
        "id": "13",
        "name": "Wallace Collection",
        "description": "A hidden treasure in a beautiful Georgian townhouse, the Wallace Collection contains one of the finest collections of arms and armour, French 18th-century paintings, porcelain, and furniture in the world. The stunning Great Gallery features works by Titian, Rembrandt, and Velázquez.",
        "short_description": "Exquisite collection of fine and decorative arts",
        "address": "Hertford House, Manchester Square, London W1U 3BN",
        "latitude": 51.5177,
        "longitude": -0.1530,
        "image_url": "https://images.unsplash.com/photo-1686852213986-9f81802a02da?w=800&q=80",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:00",
        "website": "https://www.wallacecollection.org",
        "phone": "+44 20 7563 9500",
        "transport": [
            {"type": "tube", "name": "Bond Street", "line": "Central, Jubilee", "distance": "5 min walk"},
            {"type": "tube", "name": "Baker Street", "line": "Bakerloo, Circle, Hammersmith & City, Jubilee, Metropolitan", "distance": "5 min walk"},
            {"type": "bus", "name": "Wigmore Street", "routes": ["2", "13", "30", "74", "82", "113", "274"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Wallace Restaurant", "type": "Restaurant", "cuisine": "French", "distance": "Inside museum", "price_range": "£££", "address": "Wallace Collection", "latitude": 51.5177, "longitude": -0.1530},
            {"name": "Paul", "type": "Cafe", "cuisine": "French", "distance": "4 min walk", "price_range": "££", "address": "115 Marylebone High St", "latitude": 51.5200, "longitude": -0.1520},
            {"name": "The Grazing Goat", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "6 New Quebec St", "latitude": 51.5175, "longitude": -0.1600},
            {"name": "Bella Italia Wallace", "type": "Restaurant", "cuisine": "Italian", "distance": "3 min walk", "price_range": "££", "address": "Near Wallace Collection", "latitude": 51.5173, "longitude": -0.1506},
            {"name": "Costa Coffee Wallace", "type": "Cafe", "cuisine": "Coffee", "distance": "2 min walk", "price_range": "£", "address": "Near Wallace Collection", "latitude": 51.5164, "longitude": -0.1535},
            {"name": "Bella Italia Wallace", "type": "Restaurant", "cuisine": "Italian", "distance": "4 min walk", "price_range": "££", "address": "Near Wallace Collection", "latitude": 51.5197, "longitude": -0.1513},
            {"name": "Greggs Wallace", "type": "Cafe", "cuisine": "British", "distance": "5 min walk", "price_range": "£", "address": "Near Wallace Collection", "latitude": 51.5185, "longitude": -0.1545},
            {"name": "Busaba Eathai Wallace", "type": "Restaurant", "cuisine": "Thai", "distance": "5 min walk", "price_range": "££", "address": "Near Wallace Collection", "latitude": 51.5183, "longitude": -0.1556},
            {"name": "The George Wallace", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Wallace Collection", "latitude": 51.5177, "longitude": -0.1539},
            {"name": "Caffè Nero Wallace", "type": "Cafe", "cuisine": "Coffee", "distance": "6 min walk", "price_range": "££", "address": "Near Wallace Collection", "latitude": 51.5163, "longitude": -0.1522}],
        "featured": False,
        "rating": 4.7
    },
    {
        "id": "14",
        "name": "Tate Britain",
        "description": "Tate Britain is the world's largest collection of British art from 1500 to the present day. The gallery houses masterpieces by Turner, Constable, the Pre-Raphaelites, and contemporary British artists. The Turner Bequest alone contains over 300 oil paintings.",
        "short_description": "World's greatest collection of British art",
        "address": "Millbank, London SW1P 4RG",
        "latitude": 51.4910,
        "longitude": -0.1277,
        "image_url": "https://images.unsplash.com/photo-1502052434201-a444d17aa5d7?w=800&q=80",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.tate.org.uk/visit/tate-britain",
        "phone": "+44 20 7887 8888",
        "transport": [
            {"type": "tube", "name": "Pimlico", "line": "Victoria", "distance": "5 min walk"},
            {"type": "bus", "name": "Millbank", "routes": ["2", "36", "87", "88", "185", "C10"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Tate Britain Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside gallery", "price_range": "££", "address": "Tate Britain", "latitude": 51.4910, "longitude": -0.1277},
            {"name": "Regency Cafe", "type": "Cafe", "cuisine": "British", "distance": "4 min walk", "price_range": "£", "address": "17-19 Regency St", "latitude": 51.4928, "longitude": -0.1325},
            {"name": "Page Street Cafe", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Page St", "latitude": 51.4922, "longitude": -0.1290},
            {"name": "Joe & The Juice Tate", "type": "Cafe", "cuisine": "Healthy", "distance": "2 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.4918, "longitude": -0.1267},
            {"name": "The Old Crown Tate", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.4904, "longitude": -0.1272},
            {"name": "Starbucks Tate", "type": "Cafe", "cuisine": "Coffee", "distance": "3 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.4895, "longitude": -0.1277},
            {"name": "Dishoom Tate", "type": "Restaurant", "cuisine": "Indian", "distance": "6 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.494, "longitude": -0.13},
            {"name": "Dishoom Tate", "type": "Restaurant", "cuisine": "Indian", "distance": "2 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.491, "longitude": -0.128},
            {"name": "The Kings Arms Tate", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.4913, "longitude": -0.1253},
            {"name": "Yo! Sushi Tate", "type": "Restaurant", "cuisine": "Japanese", "distance": "2 min walk", "price_range": "££", "address": "Near Tate Britain", "latitude": 51.4901, "longitude": -0.1267}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "15",
        "name": "Royal Academy of Arts",
        "description": "Britain's first art school, the Royal Academy hosts major exhibitions throughout the year and the famous Summer Exhibition. The recently expanded galleries showcase the RA's permanent collection and temporary shows featuring world-renowned artists.",
        "short_description": "Historic institution with major art exhibitions",
        "address": "Burlington House, Piccadilly, London W1J 0BD",
        "latitude": 51.5093,
        "longitude": -0.1395,
        "image_url": "https://images.unsplash.com/photo-1758065345762-14a816690407?w=800&q=80",
        "category": "Art",
        "free_entry": False,
        "opening_hours": "Sat-Thu 10:00-18:00, Fri until 21:00",
        "website": "https://www.royalacademy.org.uk",
        "phone": "+44 20 7300 8000",
        "transport": [
            {"type": "tube", "name": "Piccadilly Circus", "line": "Bakerloo, Piccadilly", "distance": "3 min walk"},
            {"type": "tube", "name": "Green Park", "line": "Jubilee, Piccadilly, Victoria", "distance": "4 min walk"},
            {"type": "bus", "name": "Piccadilly", "routes": ["9", "14", "19", "22", "38"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "RA Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Royal Academy", "latitude": 51.5093, "longitude": -0.1395},
            {"name": "Fortnum's Tea Salon", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "£££", "address": "181 Piccadilly", "latitude": 51.5085, "longitude": -0.1385},
            {"name": "Brasserie Zedel", "type": "Restaurant", "cuisine": "French", "distance": "4 min walk", "price_range": "££", "address": "20 Sherwood St", "latitude": 51.5102, "longitude": -0.1355},
            {"name": "Nando's Royal", "type": "Restaurant", "cuisine": "Portuguese", "distance": "5 min walk", "price_range": "££", "address": "Near Royal Academy of Arts", "latitude": 51.5072, "longitude": -0.1381},
            {"name": "Pret A Manger Royal", "type": "Cafe", "cuisine": "British", "distance": "5 min walk", "price_range": "£", "address": "Near Royal Academy of Arts", "latitude": 51.5088, "longitude": -0.142},
            {"name": "The Swan Royal", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Royal Academy of Arts", "latitude": 51.5076, "longitude": -0.1416},
            {"name": "Pizza Express Royal", "type": "Restaurant", "cuisine": "Italian", "distance": "2 min walk", "price_range": "££", "address": "Near Royal Academy of Arts", "latitude": 51.5099, "longitude": -0.1414},
            {"name": "Joe & The Juice Royal", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Royal Academy of Arts", "latitude": 51.5078, "longitude": -0.1423},
            {"name": "Côte Brasserie Royal", "type": "Restaurant", "cuisine": "French", "distance": "3 min walk", "price_range": "££", "address": "Near Royal Academy of Arts", "latitude": 51.5107, "longitude": -0.1424},
            {"name": "Prezzo Royal", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Royal Academy of Arts", "latitude": 51.5093, "longitude": -0.141}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "16",
        "name": "Horniman Museum",
        "description": "The Horniman Museum in Forest Hill offers a unique blend of natural history, anthropology, and music. Famous for its overstuffed walrus and extensive musical instrument collection, the museum also features beautiful gardens with stunning views of London.",
        "short_description": "Quirky museum of natural history, world cultures, and music",
        "address": "100 London Road, Forest Hill, London SE23 3PQ",
        "latitude": 51.4413,
        "longitude": -0.0600,
        "image_url": "https://images.unsplash.com/photo-1716016761758-85ee3d6c3c01?w=800&q=80",
        "category": "Natural History & Culture",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:30",
        "website": "https://horniman.ac.uk",
        "phone": "+44 20 8699 1872",
        "transport": [
            {"type": "train", "name": "Forest Hill", "line": "London Overground", "distance": "5 min walk"},
            {"type": "bus", "name": "Horniman Museum", "routes": ["176", "185", "197", "356", "P4"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Horniman Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "Horniman Museum", "latitude": 51.4413, "longitude": -0.0600},
            {"name": "The Hill Station", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "5 Dartmouth Rd", "latitude": 51.4420, "longitude": -0.0580},
            {"name": "Brown & Green", "type": "Cafe", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "20 London Rd", "latitude": 51.4400, "longitude": -0.0585},
            {"name": "Leon Horniman", "type": "Cafe", "cuisine": "Healthy", "distance": "6 min walk", "price_range": "££", "address": "Near Horniman Museum", "latitude": 51.4424, "longitude": -0.0596},
            {"name": "Pret A Manger Horniman", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Near Horniman Museum", "latitude": 51.4419, "longitude": -0.0609},
            {"name": "The White Hart Horniman", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Horniman Museum", "latitude": 51.4399, "longitude": -0.0574},
            {"name": "Busaba Eathai Horniman", "type": "Restaurant", "cuisine": "Thai", "distance": "3 min walk", "price_range": "££", "address": "Near Horniman Museum", "latitude": 51.4388, "longitude": -0.0579},
            {"name": "The Swan Horniman", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Horniman Museum", "latitude": 51.4413, "longitude": -0.0614},
            {"name": "The White Hart Horniman", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Horniman Museum", "latitude": 51.4402, "longitude": -0.0601},
            {"name": "Bella Italia Horniman", "type": "Restaurant", "cuisine": "Italian", "distance": "6 min walk", "price_range": "££", "address": "Near Horniman Museum", "latitude": 51.442, "longitude": -0.0575}],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "17",
        "name": "London Transport Museum",
        "description": "Explore the history of London's transport from horse-drawn buses to the Elizabeth line. Interactive exhibits let you drive a tube train simulator, and the collection includes vintage buses, trams, and tube trains. Perfect for families.",
        "short_description": "Interactive museum of London's iconic transport history",
        "address": "Covent Garden Piazza, London WC2E 7BB",
        "latitude": 51.5117,
        "longitude": -0.1217,
        "image_url": "https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/9sar874z_reynolds_1.jpg",
        "category": "Transport & History",
        "free_entry": False,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://ltmuseum.co.uk",
        "phone": "+44 20 7379 6344",
        "transport": [
            {"type": "tube", "name": "Covent Garden", "line": "Piccadilly", "distance": "2 min walk"},
            {"type": "tube", "name": "Leicester Square", "line": "Northern, Piccadilly", "distance": "4 min walk"},
            {"type": "bus", "name": "Aldwych", "routes": ["6", "9", "11", "13", "15", "23", "87", "91"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Upper Deck Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "London Transport Museum", "latitude": 51.5117, "longitude": -0.1217},
            {"name": "Flat Iron", "type": "Restaurant", "cuisine": "Steak", "distance": "2 min walk", "price_range": "££", "address": "17 Henrietta St", "latitude": 51.5115, "longitude": -0.1233},
            {"name": "Shake Shack", "type": "Restaurant", "cuisine": "American", "distance": "3 min walk", "price_range": "££", "address": "24 Market Building", "latitude": 51.5120, "longitude": -0.1230},
            {"name": "Côte Brasserie London", "type": "Restaurant", "cuisine": "French", "distance": "3 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5128, "longitude": -0.1208},
            {"name": "Crussh London", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5131, "longitude": -0.1215},
            {"name": "Nando's London", "type": "Restaurant", "cuisine": "Portuguese", "distance": "3 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5089, "longitude": -0.1206},
            {"name": "The Kings Arms London", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5125, "longitude": -0.1211},
            {"name": "The Red Lion London", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5097, "longitude": -0.1219},
            {"name": "The Old Crown London", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5107, "longitude": -0.1198},
            {"name": "The Swan London", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near London Transport Museum", "latitude": 51.5133, "longitude": -0.1224}],
        "featured": False,
        "rating": 4.4
    },
    {
        "id": "18",
        "name": "Churchill War Rooms",
        "description": "Step back in time to the secret underground headquarters where Winston Churchill and his war cabinet directed WWII. The original rooms remain exactly as they were in 1945, with maps, telephones, and the famous Map Room frozen in time.",
        "short_description": "Churchill's secret WWII underground headquarters",
        "address": "Clive Steps, King Charles Street, London SW1A 2AQ",
        "latitude": 51.5021,
        "longitude": -0.1290,
        "image_url": "https://images.unsplash.com/photo-1586426818048-d4ff7a16b4f8?w=800&q=80",
        "category": "History & Military",
        "free_entry": False,
        "opening_hours": "Daily 09:30-18:00",
        "website": "https://iwm.org.uk/churchill-war-rooms",
        "phone": "+44 20 7416 5000",
        "transport": [
            {"type": "tube", "name": "Westminster", "line": "Circle, District, Jubilee", "distance": "4 min walk"},
            {"type": "tube", "name": "St James's Park", "line": "Circle, District", "distance": "5 min walk"},
            {"type": "bus", "name": "Parliament Street", "routes": ["3", "11", "12", "24", "87", "88", "159"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Switch House Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Churchill War Rooms", "latitude": 51.5021, "longitude": -0.1290},
            {"name": "The Red Lion", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "48 Parliament St", "latitude": 51.5015, "longitude": -0.1260},
            {"name": "Westminster Arms", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "9 Storey's Gate", "latitude": 51.5000, "longitude": -0.1290},
            {"name": "Joe & The Juice Churchill", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5046, "longitude": -0.1294},
            {"name": "Côte Brasserie Churchill", "type": "Restaurant", "cuisine": "French", "distance": "4 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5045, "longitude": -0.1278},
            {"name": "Caffè Nero Churchill", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5012, "longitude": -0.1281},
            {"name": "Joe & The Juice Churchill", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5007, "longitude": -0.1295},
            {"name": "The George Churchill", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5012, "longitude": -0.1268},
            {"name": "Starbucks Churchill", "type": "Cafe", "cuisine": "Coffee", "distance": "3 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5007, "longitude": -0.1264},
            {"name": "Wagamama Churchill", "type": "Restaurant", "cuisine": "Japanese", "distance": "5 min walk", "price_range": "££", "address": "Near Churchill War Rooms", "latitude": 51.5046, "longitude": -0.1291}],
        "featured": False,
        "rating": 4.7
    },
    {
        "id": "19",
        "name": "Museum of the Home",
        "description": "Explore 400 years of British home life through a series of period rooms from 1600 to the present day. The museum showcases how living spaces, furniture, and domestic life have evolved through the centuries.",
        "short_description": "Discover 400 years of British home life and interiors",
        "address": "136 Kingsland Road, London E2 8EA",
        "latitude": 51.5318,
        "longitude": -0.0765,
        "image_url": "https://images.unsplash.com/photo-1643888986492-1640a909c144?w=800&q=80",
        "category": "History & Culture",
        "free_entry": True,
        "opening_hours": "Tue-Sun 10:00-17:00",
        "website": "https://www.museumofthehome.org.uk",
        "phone": "+44 20 7739 9893",
        "transport": [
            {"type": "tube", "name": "Hoxton", "line": "London Overground", "distance": "5 min walk"},
            {"type": "bus", "name": "Kingsland Road", "routes": ["67", "149", "242", "243"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Museum Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "Museum of the Home", "latitude": 51.5318, "longitude": -0.0765},
            {"name": "Song Que", "type": "Restaurant", "cuisine": "Vietnamese", "distance": "2 min walk", "price_range": "£", "address": "134 Kingsland Rd", "latitude": 51.5320, "longitude": -0.0760},
            {"name": "The Owl & Pussycat", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "34 Redchurch St", "latitude": 51.5240, "longitude": -0.0750},
            {"name": "The Red Lion Museum", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5334, "longitude": -0.0759},
            {"name": "Yo! Sushi Museum", "type": "Restaurant", "cuisine": "Japanese", "distance": "6 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5344, "longitude": -0.0791},
            {"name": "The Kings Arms Museum", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5291, "longitude": -0.0766},
            {"name": "Crussh Museum", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5301, "longitude": -0.0789},
            {"name": "The White Hart Museum", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5319, "longitude": -0.0769},
            {"name": "Bella Italia Museum", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5317, "longitude": -0.0771},
            {"name": "Yo! Sushi Museum", "type": "Restaurant", "cuisine": "Japanese", "distance": "4 min walk", "price_range": "££", "address": "Near Museum of the Home", "latitude": 51.5299, "longitude": -0.0777}],
        "featured": False,
        "rating": 4.3
    },
    {
        "id": "20",
        "name": "Wellcome Collection",
        "description": "A free museum exploring health, life, and our place in the world. Combining medicine, science, art, and life, the Wellcome Collection features thought-provoking exhibitions that challenge our understanding of what it means to be human.",
        "short_description": "Free museum exploring health, medicine, and human experience",
        "address": "183 Euston Road, London NW1 2BE",
        "latitude": 51.5258,
        "longitude": -0.1338,
        "image_url": "https://images.unsplash.com/photo-1692630223684-ccf2c0d71887?w=800&q=80",
        "category": "Science & Medicine",
        "free_entry": True,
        "opening_hours": "Tue-Sun 10:00-18:00, Thu until 21:00",
        "website": "https://wellcomecollection.org",
        "phone": "+44 20 7611 2222",
        "transport": [
            {"type": "tube", "name": "Euston", "line": "Northern, Victoria", "distance": "3 min walk"},
            {"type": "tube", "name": "Euston Square", "line": "Circle, Hammersmith & City, Metropolitan", "distance": "4 min walk"},
            {"type": "bus", "name": "Euston Road", "routes": ["10", "18", "30", "73", "205", "390"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Wellcome Kitchen", "type": "Restaurant", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Wellcome Collection", "latitude": 51.5258, "longitude": -0.1338},
            {"name": "Caravan", "type": "Restaurant", "cuisine": "International", "distance": "4 min walk", "price_range": "££", "address": "1 Granary Square", "latitude": 51.5355, "longitude": -0.1260},
            {"name": "The Euston Tap", "type": "Pub", "cuisine": "Craft Beer", "distance": "3 min walk", "price_range": "££", "address": "190 Euston Rd", "latitude": 51.5275, "longitude": -0.1320},
            {"name": "Byron Wellcome", "type": "Restaurant", "cuisine": "American", "distance": "3 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5262, "longitude": -0.1338},
            {"name": "The Kings Arms Wellcome", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5255, "longitude": -0.1335},
            {"name": "Joe & The Juice Wellcome", "type": "Cafe", "cuisine": "Healthy", "distance": "5 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5261, "longitude": -0.1342},
            {"name": "Pizza Express Wellcome", "type": "Restaurant", "cuisine": "Italian", "distance": "3 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5253, "longitude": -0.1317},
            {"name": "The Old Crown Wellcome", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5279, "longitude": -0.1365},
            {"name": "The Old Crown Wellcome", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5283, "longitude": -0.1319},
            {"name": "Ask Italian Wellcome", "type": "Restaurant", "cuisine": "Italian", "distance": "2 min walk", "price_range": "££", "address": "Near Wellcome Collection", "latitude": 51.5234, "longitude": -0.1356}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "21",
        "name": "The Postal Museum",
        "description": "The Postal Museum tells the story of 500 years of British postal history, from the first stamp to the present day. The highlight is Mail Rail, a unique underground railway ride through the original tunnels that once transported millions of letters beneath London's streets. Interactive galleries explore communication, technology, and the social history of the postal service.",
        "short_description": "Discover 500 years of postal history and ride the Mail Rail underground",
        "address": "15-20 Phoenix Place, London WC1X 0DA",
        "latitude": 51.5278,
        "longitude": -0.1099,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/22/Postal_Museum%2C_Phoenix_Place_-_geograph.org.uk_-_7206605.jpg",
        "category": "History & Transport",
        "free_entry": False,
        "opening_hours": "Tue-Sun 10:00-17:00",
        "website": "https://postalmuseum.org",
        "phone": "+44 20 7239 2570",
        "transport": [
            {"type": "tube", "name": "Farringdon", "line": "Circle, Hammersmith & City, Metropolitan, Elizabeth", "distance": "5 min walk"},
            {"type": "tube", "name": "Chancery Lane", "line": "Central", "distance": "7 min walk"},
            {"type": "bus", "name": "Mount Pleasant", "routes": ["19", "38", "55", "243"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The Postal Museum Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "The Postal Museum", "latitude": 51.5278, "longitude": -0.1099},
            {"name": "The Betsey Trotwood", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "56 Farringdon Rd", "latitude": 51.5245, "longitude": -0.1090},
            {"name": "Exmouth Market Food Stalls", "type": "Market", "cuisine": "International", "distance": "5 min walk", "price_range": "£", "address": "Exmouth Market", "latitude": 51.5265, "longitude": -0.1120},
            {"name": "Costa Coffee The", "type": "Cafe", "cuisine": "Coffee", "distance": "3 min walk", "price_range": "£", "address": "Near The Postal Museum", "latitude": 51.5272, "longitude": -0.1099},
            {"name": "Pizza Express The", "type": "Restaurant", "cuisine": "Italian", "distance": "2 min walk", "price_range": "££", "address": "Near The Postal Museum", "latitude": 51.5304, "longitude": -0.1082},
            {"name": "Pret A Manger The", "type": "Cafe", "cuisine": "British", "distance": "6 min walk", "price_range": "£", "address": "Near The Postal Museum", "latitude": 51.5291, "longitude": -0.1129},
            {"name": "The Red Lion The", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near The Postal Museum", "latitude": 51.5262, "longitude": -0.1106},
            {"name": "Dishoom The", "type": "Restaurant", "cuisine": "Indian", "distance": "2 min walk", "price_range": "££", "address": "Near The Postal Museum", "latitude": 51.5304, "longitude": -0.1125},
            {"name": "The Red Lion The", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near The Postal Museum", "latitude": 51.5304, "longitude": -0.1106},
            {"name": "Costa Coffee The", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "£", "address": "Near The Postal Museum", "latitude": 51.526, "longitude": -0.1093}],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "22",
        "name": "National Maritime Museum",
        "description": "The National Maritime Museum in Greenwich is the world's largest maritime museum, exploring Britain's seafaring history and its impact on the world. The collection includes navigational instruments, ship models, and Nelson's uniform from the Battle of Trafalgar. The museum is part of Royal Museums Greenwich, alongside the Royal Observatory and Queen's House.",
        "short_description": "World's largest maritime museum in historic Greenwich",
        "address": "Romney Road, Greenwich, London SE10 9NF",
        "latitude": 51.4810,
        "longitude": -0.0052,
        "image_url": "https://images.unsplash.com/photo-1730076784818-ba681289fd58?w=800&q=80",
        "category": "Maritime History",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:00",
        "website": "https://www.rmg.co.uk/national-maritime-museum",
        "phone": "+44 20 8312 6608",
        "transport": [
            {"type": "dlr", "name": "Cutty Sark", "line": "DLR", "distance": "5 min walk"},
            {"type": "train", "name": "Greenwich", "line": "Southeastern", "distance": "8 min walk"},
            {"type": "river", "name": "Greenwich Pier", "line": "Thames Clipper", "distance": "10 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Pavilion Tea House", "type": "Cafe", "cuisine": "British", "distance": "Inside Greenwich Park", "price_range": "££", "address": "Greenwich Park", "latitude": 51.4778, "longitude": -0.0019},
            {"name": "Old Brewery", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Old Royal Naval College", "latitude": 51.4826, "longitude": -0.0098},
            {"name": "Goddards at Greenwich", "type": "Restaurant", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "22 King William Walk", "latitude": 51.4830, "longitude": -0.0092},
            {"name": "Wahaca National", "type": "Restaurant", "cuisine": "Mexican", "distance": "2 min walk", "price_range": "££", "address": "Near National Maritime Museum", "latitude": 51.4813, "longitude": -0.0075},
            {"name": "Crussh National", "type": "Cafe", "cuisine": "Healthy", "distance": "2 min walk", "price_range": "££", "address": "Near National Maritime Museum", "latitude": 51.4834, "longitude": -0.0073},
            {"name": "Honest Burgers National", "type": "Restaurant", "cuisine": "American", "distance": "2 min walk", "price_range": "££", "address": "Near National Maritime Museum", "latitude": 51.4811, "longitude": -0.0034},
            {"name": "Greggs National", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Near National Maritime Museum", "latitude": 51.4823, "longitude": -0.0058},
            {"name": "Joe & The Juice National", "type": "Cafe", "cuisine": "Healthy", "distance": "5 min walk", "price_range": "££", "address": "Near National Maritime Museum", "latitude": 51.4815, "longitude": -0.0073},
            {"name": "Wahaca National", "type": "Restaurant", "cuisine": "Mexican", "distance": "4 min walk", "price_range": "££", "address": "Near National Maritime Museum", "latitude": 51.4786, "longitude": -0.0064},
            {"name": "The George National", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near National Maritime Museum", "latitude": 51.4813, "longitude": -0.0045}],
        "featured": False,
        "rating": 4.7
    },
    {
        "id": "23",
        "name": "Courtauld Gallery",
        "description": "The Courtauld Gallery at Somerset House houses one of the greatest collections of Impressionist and Post-Impressionist paintings in the world. Highlights include masterpieces by Manet, Monet, Renoir, Cézanne, Van Gogh, and Gauguin. The gallery underwent a major transformation and reopened in 2021 with enhanced displays.",
        "short_description": "World-renowned collection of Impressionist masterpieces",
        "address": "Somerset House, Strand, London WC2R 0RN",
        "latitude": 51.5111,
        "longitude": -0.1175,
        "image_url": "https://images.unsplash.com/photo-1455995214891-0859bd03de34?w=800&q=80",
        "category": "Art",
        "free_entry": False,
        "opening_hours": "Daily 10:00-18:00, last entry 17:15",
        "website": "https://courtauld.ac.uk/gallery",
        "phone": "+44 20 7848 2526",
        "transport": [
            {"type": "tube", "name": "Temple", "line": "Circle, District", "distance": "3 min walk"},
            {"type": "tube", "name": "Covent Garden", "line": "Piccadilly", "distance": "8 min walk"},
            {"type": "tube", "name": "Embankment", "line": "Bakerloo, Circle, District, Northern", "distance": "6 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Spring Restaurant", "type": "Restaurant", "cuisine": "Modern British", "distance": "Inside Somerset House", "price_range": "£££", "address": "Somerset House", "latitude": 51.5111, "longitude": -0.1175},
            {"name": "Fernandez & Wells", "type": "Cafe", "cuisine": "European", "distance": "Inside Somerset House", "price_range": "££", "address": "Somerset House", "latitude": 51.5111, "longitude": -0.1175},
            {"name": "Gordon's Wine Bar", "type": "Bar", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "47 Villiers St", "latitude": 51.5078, "longitude": -0.1227},
            {"name": "The Swan Courtauld", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5134, "longitude": -0.1193},
            {"name": "The George Courtauld", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5114, "longitude": -0.1167},
            {"name": "Starbucks Courtauld", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5135, "longitude": -0.1188},
            {"name": "Joe & The Juice Courtauld", "type": "Cafe", "cuisine": "Healthy", "distance": "2 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5105, "longitude": -0.1155},
            {"name": "Prezzo Courtauld", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5094, "longitude": -0.1186},
            {"name": "Crussh Courtauld", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5138, "longitude": -0.1159},
            {"name": "Starbucks Courtauld", "type": "Cafe", "cuisine": "Coffee", "distance": "4 min walk", "price_range": "££", "address": "Near Courtauld Gallery", "latitude": 51.5085, "longitude": -0.1163}],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "24",
        "name": "Saatchi Gallery",
        "description": "The Saatchi Gallery is a leading contemporary art gallery showcasing cutting-edge work by emerging and established international artists. Housed in the Duke of York's Headquarters in Chelsea, the gallery is known for championing new artists and presenting thought-provoking exhibitions that often spark public debate.",
        "short_description": "Contemporary art gallery showcasing emerging artists",
        "address": "Duke of York's HQ, King's Road, London SW3 4RY",
        "latitude": 51.4908,
        "longitude": -0.1631,
        "image_url": "https://images.unsplash.com/photo-1563095292-77c321bb8a35?w=800&q=80",
        "category": "Contemporary Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.saatchigallery.com",
        "phone": "+44 20 7811 3070",
        "transport": [
            {"type": "tube", "name": "Sloane Square", "line": "Circle, District", "distance": "5 min walk"},
            {"type": "bus", "name": "King's Road", "routes": ["11", "19", "22", "211", "319"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Saatchi Gallery Cafe", "type": "Cafe", "cuisine": "Modern European", "distance": "Inside gallery", "price_range": "££", "address": "Saatchi Gallery", "latitude": 51.4908, "longitude": -0.1631},
            {"name": "Bluebird Chelsea", "type": "Restaurant", "cuisine": "British", "distance": "3 min walk", "price_range": "£££", "address": "350 King's Road", "latitude": 51.4883, "longitude": -0.1650},
            {"name": "Megan's on the King's Road", "type": "Restaurant", "cuisine": "Mediterranean", "distance": "4 min walk", "price_range": "££", "address": "571 King's Road", "latitude": 51.4781, "longitude": -0.1735},
            {"name": "Dishoom Saatchi", "type": "Restaurant", "cuisine": "Indian", "distance": "3 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4912, "longitude": -0.1633},
            {"name": "Franco Manca Saatchi", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4908, "longitude": -0.166},
            {"name": "Honest Burgers Saatchi", "type": "Restaurant", "cuisine": "American", "distance": "2 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4896, "longitude": -0.1649},
            {"name": "The Red Lion Saatchi", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4913, "longitude": -0.1604},
            {"name": "Crussh Saatchi", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4922, "longitude": -0.1643},
            {"name": "Leon Saatchi", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4917, "longitude": -0.1651},
            {"name": "The Red Lion Saatchi", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Saatchi Gallery", "latitude": 51.4898, "longitude": -0.1632}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "25",
        "name": "Serpentine Galleries",
        "description": "The Serpentine Galleries comprise two exhibition spaces in Kensington Gardens: Serpentine South and Serpentine North. Known for presenting pioneering contemporary art exhibitions and the annual Serpentine Pavilion commission by leading architects, the galleries offer free access to world-class contemporary art in a beautiful park setting.",
        "short_description": "Contemporary art galleries in Kensington Gardens",
        "address": "Kensington Gardens, London W2 3XA",
        "latitude": 51.5050,
        "longitude": -0.1732,
        "image_url": "https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/tylbte1l_Serpentine__2018__MG_8820.jpg",
        "category": "Contemporary Art",
        "free_entry": True,
        "opening_hours": "Tue-Fri 10:00-18:00, Sat-Sun 10:00-19:00, Mon 12:00-18:00",
        "website": "https://www.serpentinegalleries.org",
        "phone": "+44 20 7402 6075",
        "transport": [
            {"type": "tube", "name": "Lancaster Gate", "line": "Central", "distance": "8 min walk"},
            {"type": "tube", "name": "South Kensington", "line": "Circle, District, Piccadilly", "distance": "15 min walk"},
            {"type": "bus", "name": "Bayswater Road", "routes": ["9", "10", "49", "52", "70"], "distance": "5 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Serpentine Bar & Kitchen", "type": "Restaurant", "cuisine": "British", "distance": "Inside gallery", "price_range": "££", "address": "Serpentine Galleries", "latitude": 51.5050, "longitude": -0.1732},
            {"name": "The Magazine Restaurant", "type": "Restaurant", "cuisine": "Modern British", "distance": "5 min walk", "price_range": "£££", "address": "Serpentine Sackler Gallery", "latitude": 51.5078, "longitude": -0.1775},
            {"name": "Honest Burgers", "type": "Restaurant", "cuisine": "American", "distance": "10 min walk", "price_range": "££", "address": "Queensway", "latitude": 51.5104, "longitude": -0.1875},
            {"name": "Pret A Manger Serpentine", "type": "Cafe", "cuisine": "British", "distance": "5 min walk", "price_range": "£", "address": "Near Serpentine Galleries", "latitude": 51.5034, "longitude": -0.1762},
            {"name": "The White Hart Serpentine", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Serpentine Galleries", "latitude": 51.5044, "longitude": -0.1756},
            {"name": "Yo! Sushi Serpentine", "type": "Restaurant", "cuisine": "Japanese", "distance": "6 min walk", "price_range": "££", "address": "Near Serpentine Galleries", "latitude": 51.5063, "longitude": -0.1737},
            {"name": "Costa Coffee Serpentine", "type": "Cafe", "cuisine": "Coffee", "distance": "2 min walk", "price_range": "£", "address": "Near Serpentine Galleries", "latitude": 51.5057, "longitude": -0.1732},
            {"name": "Pret A Manger Serpentine", "type": "Cafe", "cuisine": "British", "distance": "5 min walk", "price_range": "£", "address": "Near Serpentine Galleries", "latitude": 51.5038, "longitude": -0.1716},
            {"name": "The Swan Serpentine", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Serpentine Galleries", "latitude": 51.5078, "longitude": -0.1718},
            {"name": "Pret A Manger Serpentine", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Near Serpentine Galleries", "latitude": 51.5075, "longitude": -0.1725}],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "26",
        "name": "Museum of Brands",
        "description": "The Museum of Brands in Notting Hill tells the story of consumer culture through over 12,000 original items of packaging, advertising, and branded products. The 'time tunnel' exhibition takes visitors on a journey from Victorian times to the present day, exploring how brands have shaped our lives and society.",
        "short_description": "Journey through 150 years of British consumer culture",
        "address": "111-117 Lancaster Road, London W11 1QT",
        "latitude": 51.5171,
        "longitude": -0.2027,
        "image_url": "https://images.unsplash.com/photo-1681650669070-c04638e6f16e?w=800&q=80",
        "category": "Social History",
        "free_entry": False,
        "opening_hours": "Mon-Sat 10:00-18:00, Sun 11:00-17:00",
        "website": "https://museumofbrands.com",
        "phone": "+44 20 7243 9611",
        "transport": [
            {"type": "tube", "name": "Ladbroke Grove", "line": "Circle, Hammersmith & City", "distance": "3 min walk"},
            {"type": "tube", "name": "Notting Hill Gate", "line": "Central, Circle, District", "distance": "12 min walk"},
            {"type": "bus", "name": "Lancaster Road", "routes": ["7", "23", "70"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Museum Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Museum of Brands", "latitude": 51.5171, "longitude": -0.2027},
            {"name": "Granger & Co", "type": "Restaurant", "cuisine": "Australian", "distance": "8 min walk", "price_range": "££", "address": "175 Westbourne Grove", "latitude": 51.5163, "longitude": -0.1970},
            {"name": "The Cock & Bottle", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "17 Needham Rd", "latitude": 51.5193, "longitude": -0.2053},
            {"name": "The Swan Museum", "type": "Pub", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5191, "longitude": -0.1999},
            {"name": "Leon Museum", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5174, "longitude": -0.2054},
            {"name": "The Swan Museum", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5166, "longitude": -0.2},
            {"name": "Honest Burgers Museum", "type": "Restaurant", "cuisine": "American", "distance": "3 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5142, "longitude": -0.2044},
            {"name": "Leon Museum", "type": "Cafe", "cuisine": "Healthy", "distance": "3 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5175, "longitude": -0.2052},
            {"name": "Ask Italian Museum", "type": "Restaurant", "cuisine": "Italian", "distance": "2 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5163, "longitude": -0.2028},
            {"name": "Pizza Express Museum", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "Near Museum of Brands", "latitude": 51.5158, "longitude": -0.2036}],
        "featured": False,
        "rating": 4.5
    },
    {
        "id": "27",
        "name": "Grant Museum of Zoology",
        "description": "The Grant Museum of Zoology at UCL is one of the oldest and most important natural history collections in Britain, with over 68,000 specimens. Founded in 1828, the museum features rare and extinct species including skeletons, mounted animals, and specimens preserved in fluid, offering a unique window into biodiversity past and present.",
        "short_description": "UCL's historic zoology collection with rare specimens",
        "address": "Rockefeller Building, 21 University Street, London WC1E 6DE",
        "latitude": 51.5246,
        "longitude": -0.1340,
        "image_url": "https://images.unsplash.com/photo-1623960735384-d5f974262164?w=800&q=80",
        "category": "Natural History",
        "free_entry": True,
        "opening_hours": "Tue-Fri 13:00-17:00, Sat 11:00-17:00",
        "website": "https://www.ucl.ac.uk/culture/grant-museum-zoology",
        "phone": "+44 20 3108 2052",
        "transport": [
            {"type": "tube", "name": "Euston Square", "line": "Circle, Hammersmith & City, Metropolitan", "distance": "3 min walk"},
            {"type": "tube", "name": "Warren Street", "line": "Northern, Victoria", "distance": "5 min walk"},
            {"type": "tube", "name": "Goodge Street", "line": "Northern", "distance": "7 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Pret A Manger", "type": "Cafe", "cuisine": "British", "distance": "2 min walk", "price_range": "£", "address": "Gower Street", "latitude": 51.5241, "longitude": -0.1335},
            {"name": "Dalloway Terrace", "type": "Restaurant", "cuisine": "British", "distance": "8 min walk", "price_range": "£££", "address": "16-22 Great Russell St", "latitude": 51.5185, "longitude": -0.1278},
            {"name": "The Bloomsbury Tavern", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "236 Shaftesbury Ave", "latitude": 51.5196, "longitude": -0.1296},
            {"name": "Franco Manca Grant", "type": "Restaurant", "cuisine": "Italian", "distance": "2 min walk", "price_range": "££", "address": "Near Grant Museum of Zoology", "latitude": 51.5216, "longitude": -0.136},
            {"name": "Zizzi Grant", "type": "Restaurant", "cuisine": "Italian", "distance": "6 min walk", "price_range": "££", "address": "Near Grant Museum of Zoology", "latitude": 51.5226, "longitude": -0.134},
            {"name": "The Red Lion Grant", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "Near Grant Museum of Zoology", "latitude": 51.5233, "longitude": -0.136},
            {"name": "The White Hart Grant", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "Near Grant Museum of Zoology", "latitude": 51.5245, "longitude": -0.1369},
            {"name": "Leon Grant", "type": "Cafe", "cuisine": "Healthy", "distance": "4 min walk", "price_range": "££", "address": "Near Grant Museum of Zoology", "latitude": 51.5269, "longitude": -0.1364},
            {"name": "The Red Lion Grant", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Near Grant Museum of Zoology", "latitude": 51.5218, "longitude": -0.1313},
            {"name": "Pret A Manger Grant", "type": "Cafe", "cuisine": "British", "distance": "4 min walk", "price_range": "£", "address": "Near Grant Museum of Zoology", "latitude": 51.523, "longitude": -0.1366}],
        "featured": False,
        "rating": 4.7
    },
    {
        "id": "28",
        "name": "Paradox Museum",
        "description": "The Paradox Museum is an immersive experience featuring over 50 paradox-based exhibits that challenge perception and reality. Visitors encounter mind-bending optical illusions, impossible objects, and interactive installations that blur the line between what's real and what's not. Perfect for all ages, the museum offers a unique journey through brain-teasing puzzles, gravity-defying rooms, and Instagram-worthy photo opportunities that will make you question everything you see.",
        "short_description": "Mind-bending museum of optical illusions and paradoxes",
        "address": "215-217 Brompton Road, London SW3 2EJ",
        "latitude": 51.4944,
        "longitude": -0.1699,
        "image_url": "https://images.unsplash.com/photo-1618944847828-82e943c3bdb7?w=800&q=80",
        "category": "Science & Experience",
        "free_entry": False,
        "opening_hours": "Daily 10:00-20:00",
        "website": "https://www.paradoxmuseumlo.com",
        "phone": "+44 20 3096 1173",
        "transport": [
            {"type": "tube", "name": "South Kensington", "line": "Circle, District, Piccadilly", "distance": "5 min walk"},
            {"type": "tube", "name": "Knightsbridge", "line": "Piccadilly", "distance": "7 min walk"},
            {"type": "bus", "name": "Brompton Road", "routes": ["14", "49", "70", "74", "345", "C1"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Comptoir Libanais", "type": "Restaurant", "cuisine": "Lebanese", "distance": "3 min walk", "price_range": "££", "address": "1 Exhibition Rd", "latitude": 51.4955, "longitude": -0.1740},
            {"name": "Muriel's Kitchen", "type": "Cafe", "cuisine": "British", "distance": "4 min walk", "price_range": "££", "address": "36 Old Brompton Rd", "latitude": 51.4942, "longitude": -0.1755},
            {"name": "Zizzi", "type": "Restaurant", "cuisine": "Italian", "distance": "3 min walk", "price_range": "££", "address": "Brompton Road", "latitude": 51.4938, "longitude": -0.1705},
            {"name": "The Brompton", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "Brompton Road", "latitude": 51.4948, "longitude": -0.1692},
            {"name": "Costa Coffee", "type": "Cafe", "cuisine": "Coffee", "distance": "2 min walk", "price_range": "£", "address": "Brompton Road", "latitude": 51.4951, "longitude": -0.1688},
            {"name": "Pret A Manger", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "Brompton Road", "latitude": 51.4941, "longitude": -0.1715},
            {"name": "Wasabi", "type": "Restaurant", "cuisine": "Japanese", "distance": "4 min walk", "price_range": "£", "address": "Brompton Road", "latitude": 51.4936, "longitude": -0.1721},
            {"name": "Byron", "type": "Restaurant", "cuisine": "American", "distance": "5 min walk", "price_range": "££", "address": "Brompton Road", "latitude": 51.4933, "longitude": -0.1728},
            {"name": "Nando's", "type": "Restaurant", "cuisine": "Portuguese", "distance": "6 min walk", "price_range": "££", "address": "Old Brompton Road", "latitude": 51.4930, "longitude": -0.1738},
            {"name": "Caffè Nero", "type": "Cafe", "cuisine": "Coffee", "distance": "3 min walk", "price_range": "£", "address": "Brompton Road", "latitude": 51.4946, "longitude": -0.1696}
        ],
        "featured": False,
        "rating": 4.6
    },
    {
        "id": "29",
        "name": "London Film Museum",
        "description": "The London Film Museum is dedicated to preserving and showcasing British film history and the art of filmmaking. The museum features iconic props, costumes, and memorabilia from beloved films and TV shows. Visitors can explore the magic of cinema through interactive exhibits, behind-the-scenes insights, and rare artifacts from classic and contemporary productions. The museum celebrates the UK's rich contribution to the global film industry with rotating exhibitions and permanent collections.",
        "short_description": "Museum celebrating British film history and cinema",
        "address": "45 Wellington Street, Covent Garden, London WC2E 7BN",
        "latitude": 51.5115,
        "longitude": -0.1218,
        "image_url": "https://customer-assets.emergentagent.com/job_culture-compass-6/artifacts/is10pqem_London-Film-Museum-scaled.webp",
        "category": "Film & Entertainment",
        "free_entry": False,
        "opening_hours": "Mon-Sun 10:00-18:00",
        "website": "https://www.londonfilmmuseum.com",
        "phone": "+44 20 7202 7040",
        "transport": [
            {"type": "tube", "name": "Covent Garden", "line": "Piccadilly", "distance": "3 min walk"},
            {"type": "tube", "name": "Temple", "line": "Circle, District", "distance": "5 min walk"},
            {"type": "tube", "name": "Charing Cross", "line": "Bakerloo, Northern", "distance": "7 min walk"},
            {"type": "bus", "name": "Wellington Street", "routes": ["6", "9", "11", "13", "15", "23", "87", "91"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Flat Iron", "type": "Restaurant", "cuisine": "Steak", "distance": "2 min walk", "price_range": "££", "address": "17 Henrietta St", "latitude": 51.5115, "longitude": -0.1233},
            {"name": "Shake Shack", "type": "Restaurant", "cuisine": "American", "distance": "3 min walk", "price_range": "££", "address": "24 Market Building", "latitude": 51.5120, "longitude": -0.1230},
            {"name": "Dishoom Covent Garden", "type": "Restaurant", "cuisine": "Indian", "distance": "4 min walk", "price_range": "££", "address": "12 Upper St Martin's Lane", "latitude": 51.5127, "longitude": -0.1268},
            {"name": "The Ivy Market Grill", "type": "Restaurant", "cuisine": "British", "distance": "3 min walk", "price_range": "£££", "address": "1 Henrietta St", "latitude": 51.5110, "longitude": -0.1240},
            {"name": "Balthazar", "type": "Restaurant", "cuisine": "French", "distance": "2 min walk", "price_range": "£££", "address": "4-6 Russell St", "latitude": 51.5118, "longitude": -0.1225},
            {"name": "Bill's Covent Garden", "type": "Restaurant", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "36-44 Floral St", "latitude": 51.5122, "longitude": -0.1238},
            {"name": "Wagamama Covent Garden", "type": "Restaurant", "cuisine": "Japanese", "distance": "4 min walk", "price_range": "££", "address": "1 Tavistock St", "latitude": 51.5108, "longitude": -0.1210},
            {"name": "The Crusting Pipe", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "27 The Piazza", "latitude": 51.5120, "longitude": -0.1223},
            {"name": "Café Rouge", "type": "Restaurant", "cuisine": "French", "distance": "3 min walk", "price_range": "££", "address": "34 Wellington St", "latitude": 51.5112, "longitude": -0.1215},
            {"name": "Five Guys", "type": "Restaurant", "cuisine": "American", "distance": "4 min walk", "price_range": "££", "address": "Covent Garden", "latitude": 51.5125, "longitude": -0.1235}
        ],
        "featured": False,
        "rating": 4.4
    }
]

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Museums Of London API"}

@api_router.get("/museums", response_model=List[Museum])
async def get_museums(category: Optional[str] = None, free_only: bool = False, search: Optional[str] = None):
    """Get all museums with optional filtering"""
    museums = LONDON_MUSEUMS.copy()
    
    if category:
        museums = [m for m in museums if category.lower() in m["category"].lower()]
    
    if free_only:
        museums = [m for m in museums if m["free_entry"]]
    
    if search:
        search_lower = search.lower()
        museums = [m for m in museums if 
                   search_lower in m["name"].lower() or 
                   search_lower in m["description"].lower() or
                   search_lower in m["category"].lower()]
    
    return [Museum(**m) for m in museums]

@api_router.get("/museums/featured", response_model=List[Museum])
async def get_featured_museums():
    """Get featured museums for home page"""
    featured = [m for m in LONDON_MUSEUMS if m["featured"]]
    return [Museum(**m) for m in featured]

@api_router.get("/museums/categories")
async def get_categories():
    """Get all unique categories"""
    categories = list(set(m["category"] for m in LONDON_MUSEUMS))
    return sorted(categories)

@api_router.get("/museums/{museum_id}", response_model=Museum)
async def get_museum(museum_id: str):
    """Get a specific museum by ID"""
    museum = next((m for m in LONDON_MUSEUMS if m["id"] == museum_id), None)
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")
    return Museum(**museum)

# Favorites endpoints (stored in MongoDB)
@api_router.post("/favorites/{museum_id}")
async def add_favorite(museum_id: str):
    """Add a museum to favorites"""
    # Check if museum exists
    museum = next((m for m in LONDON_MUSEUMS if m["id"] == museum_id), None)
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")
    
    # Check if already favorited
    existing = await db.favorites.find_one({"museum_id": museum_id})
    if existing:
        return {"message": "Already in favorites", "id": existing["id"]}
    
    favorite = Favorite(museum_id=museum_id)
    await db.favorites.insert_one(favorite.dict())
    return {"message": "Added to favorites", "id": favorite.id}

@api_router.delete("/favorites/{museum_id}")
async def remove_favorite(museum_id: str):
    """Remove a museum from favorites"""
    result = await db.favorites.delete_one({"museum_id": museum_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}

@api_router.get("/favorites")
async def get_favorites():
    """Get all favorite museums"""
    favorites = await db.favorites.find().to_list(100)
    museum_ids = [f["museum_id"] for f in favorites]
    
    # Get full museum details for favorites
    favorite_museums = [m for m in LONDON_MUSEUMS if m["id"] in museum_ids]
    return [Museum(**m) for m in favorite_museums]

@api_router.get("/favorites/check/{museum_id}")
async def check_favorite(museum_id: str):
    """Check if a museum is favorited"""
    existing = await db.favorites.find_one({"museum_id": museum_id})
    return {"is_favorite": existing is not None}

# Walking Tours - Pre-defined tours
WALKING_TOURS = [
    {
        "id": "south-kensington",
        "name": "South Kensington Museum Mile",
        "description": "Explore three world-class museums in one of London's most elegant areas. Perfect for a full day of culture.",
        "duration": "Full day (6-8 hours)",
        "distance": "1.5 km walking",
        "museum_ids": ["2", "3", "4"],  # Natural History, V&A, Science
        "color": "#E63946"
    },
    {
        "id": "art-lovers",
        "name": "Art Lovers Trail",
        "description": "From classical masterpieces to modern art, this tour covers London's finest art collections.",
        "duration": "Full day (6-8 hours)",
        "distance": "4 km walking",
        "museum_ids": ["6", "10", "5", "14"],  # National Gallery, NPG, Tate Modern, Tate Britain
        "color": "#457B9D"
    },
    {
        "id": "central-london",
        "name": "Central London Highlights",
        "description": "Hit the major museums in central London, all within walking distance of each other.",
        "duration": "Full day (5-7 hours)",
        "distance": "3 km walking",
        "museum_ids": ["1", "11", "17"],  # British Museum, Soane, Transport
        "color": "#2A9D8F"
    },
    {
        "id": "history-buffs",
        "name": "History & Heritage Tour",
        "description": "Journey through London's rich history from ancient times to WWII.",
        "duration": "Full day (6-8 hours)",
        "distance": "5 km walking",
        "museum_ids": ["7", "9", "18", "8"],  # Tower, Museum of London, War Rooms, IWM
        "color": "#E9C46A"
    },
    {
        "id": "hidden-gems",
        "name": "Hidden Gems Tour",
        "description": "Discover London's lesser-known but equally fascinating museums.",
        "duration": "Half day (4-5 hours)",
        "distance": "2 km walking",
        "museum_ids": ["11", "13", "20"],  # Soane, Wallace, Wellcome
        "color": "#9B59B6"
    }
]

@api_router.get("/tours")
async def get_walking_tours():
    """Get all pre-defined walking tours"""
    tours_with_museums = []
    for tour in WALKING_TOURS:
        tour_data = tour.copy()
        tour_data["museums"] = [
            Museum(**m) for m in LONDON_MUSEUMS if m["id"] in tour["museum_ids"]
        ]
        tours_with_museums.append(tour_data)
    return tours_with_museums

@api_router.get("/tours/{tour_id}")
async def get_tour(tour_id: str):
    """Get a specific tour with museum details"""
    tour = next((t for t in WALKING_TOURS if t["id"] == tour_id), None)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    
    tour_data = tour.copy()
    tour_data["museums"] = [
        Museum(**m) for m in LONDON_MUSEUMS if m["id"] in tour["museum_ids"]
    ]
    return tour_data

# Custom tour creation
class CustomTourCreate(BaseModel):
    name: str
    museum_ids: List[str]

class CustomTour(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    museum_ids: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

@api_router.post("/tours/custom")
async def create_custom_tour(tour: CustomTourCreate):
    """Create a custom walking tour"""
    # Validate all museum IDs exist
    all_museum_ids = [m["id"] for m in LONDON_MUSEUMS]
    for mid in tour.museum_ids:
        if mid not in all_museum_ids:
            raise HTTPException(status_code=400, detail=f"Museum ID {mid} not found")
    
    custom_tour = CustomTour(name=tour.name, museum_ids=tour.museum_ids)
    await db.custom_tours.insert_one(custom_tour.dict())
    
    return {
        "id": custom_tour.id,
        "name": custom_tour.name,
        "museum_ids": custom_tour.museum_ids,
        "museums": [Museum(**m) for m in LONDON_MUSEUMS if m["id"] in tour.museum_ids]
    }

@api_router.get("/tours/custom/list")
async def get_custom_tours():
    """Get all custom tours"""
    tours = await db.custom_tours.find().to_list(100)
    result = []
    for tour in tours:
        tour_data = {
            "id": tour["id"],
            "name": tour["name"],
            "museum_ids": tour["museum_ids"],
            "museums": [Museum(**m) for m in LONDON_MUSEUMS if m["id"] in tour["museum_ids"]]
        }
        result.append(tour_data)
    return result

@api_router.delete("/tours/custom/{tour_id}")
async def delete_custom_tour(tour_id: str):
    """Delete a custom tour"""
    result = await db.custom_tours.delete_one({"id": tour_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Custom tour not found")
    return {"message": "Custom tour deleted"}

# Admin endpoints for managing museums
class AdminAuth(BaseModel):
    pin: str

@api_router.post("/admin/verify")
async def verify_admin(auth: AdminAuth):
    """Verify admin PIN"""
    if auth.pin == ADMIN_PIN:
        return {"success": True, "message": "Admin access granted"}
    raise HTTPException(status_code=401, detail="Invalid PIN")

class MuseumCreateAdmin(BaseModel):
    name: str
    description: str
    short_description: str
    address: str
    latitude: float
    longitude: float
    image_url: str
    category: str
    free_entry: bool
    opening_hours: str
    website: Optional[str] = None
    phone: Optional[str] = None
    transport: List[dict] = []
    nearby_eateries: List[dict] = []
    featured: bool = False
    rating: float = 4.5

@api_router.post("/admin/museums")
async def add_museum(museum: MuseumCreateAdmin, pin: str):
    """Add a new museum (admin only)"""
    if pin != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid admin PIN")
    
    # Generate new ID
    existing_ids = [int(m["id"]) for m in LONDON_MUSEUMS if m["id"].isdigit()]
    new_id = str(max(existing_ids) + 1) if existing_ids else "21"
    
    new_museum = {
        "id": new_id,
        **museum.dict(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store in database
    await db.museums.insert_one(new_museum)
    
    # Add to in-memory list
    LONDON_MUSEUMS.append(new_museum)
    
    return {"message": "Museum added successfully", "id": new_id, "museum": Museum(**new_museum)}

@api_router.put("/admin/museums/{museum_id}")
async def update_museum(museum_id: str, museum: MuseumCreateAdmin, pin: str):
    """Update an existing museum (admin only)"""
    if pin != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid admin PIN")
    
    # Find museum index
    museum_index = next((i for i, m in enumerate(LONDON_MUSEUMS) if m["id"] == museum_id), None)
    if museum_index is None:
        raise HTTPException(status_code=404, detail="Museum not found")
    
    updated_museum = {
        "id": museum_id,
        **museum.dict()
    }
    
    # Update in database
    await db.museums.update_one({"id": museum_id}, {"$set": updated_museum}, upsert=True)
    
    # Update in-memory list
    LONDON_MUSEUMS[museum_index] = updated_museum
    
    return {"message": "Museum updated successfully", "museum": Museum(**updated_museum)}

@api_router.delete("/admin/museums/{museum_id}")
async def delete_museum(museum_id: str, pin: str):
    """Delete a museum (admin only)"""
    if pin != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid admin PIN")
    
    # Find museum
    museum_index = next((i for i, m in enumerate(LONDON_MUSEUMS) if m["id"] == museum_id), None)
    if museum_index is None:
        raise HTTPException(status_code=404, detail="Museum not found")
    
    # Delete from database
    await db.museums.delete_one({"id": museum_id})
    
    # Remove from in-memory list
    LONDON_MUSEUMS.pop(museum_index)
    
    return {"message": "Museum deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

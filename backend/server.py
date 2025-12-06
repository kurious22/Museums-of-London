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

# Pre-populated museum data for London
LONDON_MUSEUMS = [
    {
        "id": "1",
        "name": "British Museum",
        "description": "The British Museum is one of the world's most famous museums, housing a vast collection of world art and artifacts spanning over two million years of history. Highlights include the Rosetta Stone, the Elgin Marbles, and Egyptian mummies. The museum's stunning Great Court, designed by Norman Foster, is the largest covered public square in Europe.",
        "short_description": "World-famous museum with over 8 million artifacts from all continents",
        "address": "Great Russell Street, London WC1B 3DG",
        "latitude": 51.5194,
        "longitude": -0.1269,
        "image_url": "https://images.unsplash.com/photo-1590792024908-f579e0e81c4e?w=800",
        "category": "History & Culture",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:00, Fri until 20:30",
        "website": "https://www.britishmuseum.org",
        "phone": "+44 20 7323 8299",
        "transport": [
            {"type": "tube", "name": "Holborn", "line": "Central, Piccadilly", "distance": "5 min walk"},
            {"type": "tube", "name": "Tottenham Court Road", "line": "Central, Northern", "distance": "7 min walk"},
            {"type": "bus", "name": "Great Russell Street", "routes": ["1", "8", "19", "25", "38"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The Museum Tavern", "type": "Pub", "cuisine": "British", "distance": "1 min walk", "price_range": "££", "address": "49 Great Russell St"},
            {"name": "Cafe in the Great Court", "type": "Cafe", "cuisine": "International", "distance": "Inside museum", "price_range": "££", "address": "British Museum"},
            {"name": "Honey & Co", "type": "Restaurant", "cuisine": "Middle Eastern", "distance": "5 min walk", "price_range": "£££", "address": "25a Warren St"}
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
        "image_url": "https://images.unsplash.com/photo-1574176104669-c3db2e09be50?w=800",
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
            {"name": "The Central Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Natural History Museum"},
            {"name": "Comptoir Libanais", "type": "Restaurant", "cuisine": "Lebanese", "distance": "3 min walk", "price_range": "££", "address": "1 Exhibition Rd"},
            {"name": "Byron", "type": "Restaurant", "cuisine": "Burgers", "distance": "5 min walk", "price_range": "££", "address": "27 Old Brompton Rd"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1567593810070-7a3d471af022?w=800",
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
            {"name": "V&A Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "V&A Museum"},
            {"name": "Fernandez & Wells", "type": "Cafe", "cuisine": "European", "distance": "4 min walk", "price_range": "££", "address": "8 Exhibition Rd"},
            {"name": "Daquise", "type": "Restaurant", "cuisine": "Polish", "distance": "5 min walk", "price_range": "££", "address": "20 Thurloe St"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800",
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
            {"name": "Deep Blue Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Science Museum"},
            {"name": "Pizza Express", "type": "Restaurant", "cuisine": "Italian", "distance": "5 min walk", "price_range": "££", "address": "6 Old Brompton Rd"},
            {"name": "Cafe Concerto", "type": "Cafe", "cuisine": "Italian", "distance": "6 min walk", "price_range": "££", "address": "8 Exhibition Rd"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1544621028-b9a3fb9e3d5c?w=800",
        "category": "Modern Art",
        "free_entry": True,
        "opening_hours": "Sun-Thu 10:00-18:00, Fri-Sat until 22:00",
        "website": "https://www.tate.org.uk/visit/tate-modern",
        "phone": "+44 20 7887 8888",
        "transport": [
            {"type": "tube", "name": "Southwark", "line": "Jubilee", "distance": "8 min walk"},
            {"type": "tube", "name": "Blackfriars", "line": "Circle, District", "distance": "10 min walk"},
            {"type": "bus", "name": "Southwark Street", "routes": ["45", "63", "100", "381"], "distance": "5 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Tate Modern Restaurant", "type": "Restaurant", "cuisine": "British", "distance": "Inside museum", "price_range": "£££", "address": "Tate Modern, Level 6"},
            {"name": "The Anchor Bankside", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "34 Park St"},
            {"name": "Swan at The Globe", "type": "Restaurant", "cuisine": "British", "distance": "3 min walk", "price_range": "£££", "address": "21 New Globe Walk"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=800",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00, Fri until 21:00",
        "website": "https://www.nationalgallery.org.uk",
        "phone": "+44 20 7747 2885",
        "transport": [
            {"type": "tube", "name": "Charing Cross", "line": "Bakerloo, Northern", "distance": "2 min walk"},
            {"type": "tube", "name": "Leicester Square", "line": "Northern, Piccadilly", "distance": "5 min walk"},
            {"type": "bus", "name": "Trafalgar Square", "routes": ["3", "6", "9", "11", "13", "15", "23", "24", "87", "91"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "National Dining Rooms", "type": "Restaurant", "cuisine": "British", "distance": "Inside gallery", "price_range": "£££", "address": "National Gallery"},
            {"name": "Cafe in the Crypt", "type": "Cafe", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "St Martin-in-the-Fields"},
            {"name": "The Admiralty", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "66 Trafalgar Square"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1564666230378-0e60c4c81df8?w=800",
        "category": "History & Heritage",
        "free_entry": False,
        "opening_hours": "Tue-Sat 09:00-17:00, Sun-Mon 10:00-17:00",
        "website": "https://www.hrp.org.uk/tower-of-london",
        "phone": "+44 20 3166 6000",
        "transport": [
            {"type": "tube", "name": "Tower Hill", "line": "Circle, District", "distance": "2 min walk"},
            {"type": "train", "name": "Fenchurch Street", "line": "National Rail", "distance": "10 min walk"},
            {"type": "bus", "name": "Tower of London", "routes": ["15", "42", "78", "100", "RV1"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "The New Armouries Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside tower", "price_range": "££", "address": "Tower of London"},
            {"name": "Coppa Club", "type": "Restaurant", "cuisine": "Mediterranean", "distance": "5 min walk", "price_range": "£££", "address": "3 Three Quays Walk"},
            {"name": "Dickens Inn", "type": "Pub", "cuisine": "British", "distance": "7 min walk", "price_range": "££", "address": "St Katharine Docks"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1559135197-8a45ea74d367?w=800",
        "category": "History & Military",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.iwm.org.uk/visits/iwm-london",
        "phone": "+44 20 7416 5000",
        "transport": [
            {"type": "tube", "name": "Lambeth North", "line": "Bakerloo", "distance": "5 min walk"},
            {"type": "tube", "name": "Elephant & Castle", "line": "Bakerloo, Northern", "distance": "10 min walk"},
            {"type": "bus", "name": "Lambeth Road", "routes": ["12", "53", "148", "171", "344"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "IWM Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Imperial War Museum"},
            {"name": "Masters Super Fish", "type": "Restaurant", "cuisine": "Fish & Chips", "distance": "8 min walk", "price_range": "£", "address": "191 Waterloo Rd"},
            {"name": "The Camel", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "277 Globe Rd"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1526129318478-62ed807ebdf9?w=800",
        "category": "History & Culture",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.museumoflondon.org.uk",
        "phone": "+44 20 7001 9844",
        "transport": [
            {"type": "tube", "name": "Barbican", "line": "Circle, Hammersmith & City, Metropolitan", "distance": "5 min walk"},
            {"type": "tube", "name": "St Paul's", "line": "Central", "distance": "7 min walk"},
            {"type": "bus", "name": "London Wall", "routes": ["4", "8", "25", "56", "100", "172", "521"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Museum Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Museum of London"},
            {"name": "The Jugged Hare", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "49 Chiswell St"},
            {"name": "Itsu", "type": "Restaurant", "cuisine": "Japanese", "distance": "4 min walk", "price_range": "££", "address": "1 Ropemaker St"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:30-18:00, Fri until 21:00",
        "website": "https://www.npg.org.uk",
        "phone": "+44 20 7306 0055",
        "transport": [
            {"type": "tube", "name": "Leicester Square", "line": "Northern, Piccadilly", "distance": "2 min walk"},
            {"type": "tube", "name": "Charing Cross", "line": "Bakerloo, Northern", "distance": "3 min walk"},
            {"type": "bus", "name": "Trafalgar Square", "routes": ["24", "29", "176"], "distance": "2 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Portrait Restaurant", "type": "Restaurant", "cuisine": "British", "distance": "Inside gallery", "price_range": "£££", "address": "National Portrait Gallery"},
            {"name": "Gordon's Wine Bar", "type": "Wine Bar", "cuisine": "European", "distance": "5 min walk", "price_range": "££", "address": "47 Villiers St"},
            {"name": "The Chandos", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "£", "address": "29 St Martin's Lane"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800",
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
            {"name": "The Seven Stars", "type": "Pub", "cuisine": "British", "distance": "2 min walk", "price_range": "££", "address": "53-54 Carey St"},
            {"name": "Fleet Street Press", "type": "Cafe", "cuisine": "Coffee", "distance": "5 min walk", "price_range": "£", "address": "3 Fleet St"},
            {"name": "Dishoom", "type": "Restaurant", "cuisine": "Indian", "distance": "7 min walk", "price_range": "££", "address": "12 Upper St Martin's Lane"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1554907984-15263bfd63bd?w=800",
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
            {"name": "Parabola", "type": "Restaurant", "cuisine": "Mediterranean", "distance": "Inside museum", "price_range": "£££", "address": "Design Museum"},
            {"name": "The Scarsdale Tavern", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "23A Edwardes Square"},
            {"name": "Honest Burgers", "type": "Restaurant", "cuisine": "Burgers", "distance": "6 min walk", "price_range": "££", "address": "194 Kensington High St"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1572953109213-3be62398eb95?w=800",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:00",
        "website": "https://www.wallacecollection.org",
        "phone": "+44 20 7563 9500",
        "transport": [
            {"type": "tube", "name": "Bond Street", "line": "Central, Jubilee", "distance": "5 min walk"},
            {"type": "tube", "name": "Baker Street", "line": "Bakerloo, Circle, Hammersmith & City, Jubilee, Metropolitan", "distance": "8 min walk"},
            {"type": "bus", "name": "Wigmore Street", "routes": ["2", "13", "30", "74", "82", "113", "274"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Wallace Restaurant", "type": "Restaurant", "cuisine": "French", "distance": "Inside museum", "price_range": "£££", "address": "Wallace Collection"},
            {"name": "Paul", "type": "Cafe", "cuisine": "French", "distance": "5 min walk", "price_range": "££", "address": "115 Marylebone High St"},
            {"name": "The Grazing Goat", "type": "Pub", "cuisine": "British", "distance": "6 min walk", "price_range": "££", "address": "6 New Quebec St"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1568454537842-d933259bb258?w=800",
        "category": "Art",
        "free_entry": True,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.tate.org.uk/visit/tate-britain",
        "phone": "+44 20 7887 8888",
        "transport": [
            {"type": "tube", "name": "Pimlico", "line": "Victoria", "distance": "8 min walk"},
            {"type": "bus", "name": "Millbank", "routes": ["2", "36", "87", "88", "185", "C10"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Rex Whistler Restaurant", "type": "Restaurant", "cuisine": "British", "distance": "Inside gallery", "price_range": "£££", "address": "Tate Britain"},
            {"name": "Regency Cafe", "type": "Cafe", "cuisine": "British", "distance": "5 min walk", "price_range": "£", "address": "17-19 Regency St"},
            {"name": "Kazan", "type": "Restaurant", "cuisine": "Turkish", "distance": "7 min walk", "price_range": "££", "address": "93-94 Wilton Rd"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
        "category": "Art",
        "free_entry": False,
        "opening_hours": "Sat-Thu 10:00-18:00, Fri until 21:00",
        "website": "https://www.royalacademy.org.uk",
        "phone": "+44 20 7300 8000",
        "transport": [
            {"type": "tube", "name": "Piccadilly Circus", "line": "Bakerloo, Piccadilly", "distance": "3 min walk"},
            {"type": "tube", "name": "Green Park", "line": "Jubilee, Piccadilly, Victoria", "distance": "5 min walk"},
            {"type": "bus", "name": "Piccadilly", "routes": ["9", "14", "19", "22", "38"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "RA Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Royal Academy"},
            {"name": "The Wolseley", "type": "Restaurant", "cuisine": "European", "distance": "3 min walk", "price_range": "£££", "address": "160 Piccadilly"},
            {"name": "Fortnum & Mason", "type": "Restaurant", "cuisine": "British", "distance": "2 min walk", "price_range": "£££", "address": "181 Piccadilly"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1600723889622-e6bbeac4b62b?w=800",
        "category": "Natural History & Culture",
        "free_entry": True,
        "opening_hours": "Daily 10:00-17:30",
        "website": "https://www.horniman.ac.uk",
        "phone": "+44 20 8699 1872",
        "transport": [
            {"type": "train", "name": "Forest Hill", "line": "London Overground", "distance": "10 min walk"},
            {"type": "bus", "name": "Horniman Museum", "routes": ["176", "185", "197", "356", "P4"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Horniman Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "Horniman Museum"},
            {"name": "Babur", "type": "Restaurant", "cuisine": "Indian", "distance": "10 min walk", "price_range": "££", "address": "119 Brockley Rise"},
            {"name": "The Hill", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "94 Kirkdale"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "category": "Transport & History",
        "free_entry": False,
        "opening_hours": "Daily 10:00-18:00",
        "website": "https://www.ltmuseum.co.uk",
        "phone": "+44 20 7379 6344",
        "transport": [
            {"type": "tube", "name": "Covent Garden", "line": "Piccadilly", "distance": "2 min walk"},
            {"type": "tube", "name": "Leicester Square", "line": "Northern, Piccadilly", "distance": "5 min walk"},
            {"type": "bus", "name": "Aldwych", "routes": ["6", "9", "11", "13", "15", "23", "87", "91"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Upper Deck Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "London Transport Museum"},
            {"name": "Flat Iron", "type": "Restaurant", "cuisine": "Steak", "distance": "3 min walk", "price_range": "££", "address": "17 Henrietta St"},
            {"name": "The Ivy Market Grill", "type": "Restaurant", "cuisine": "British", "distance": "2 min walk", "price_range": "£££", "address": "1 Henrietta St"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1590478615277-d37c9dd51c40?w=800",
        "category": "History & Military",
        "free_entry": False,
        "opening_hours": "Daily 09:30-18:00",
        "website": "https://www.iwm.org.uk/visits/churchill-war-rooms",
        "phone": "+44 20 7416 5000",
        "transport": [
            {"type": "tube", "name": "Westminster", "line": "Circle, District, Jubilee", "distance": "5 min walk"},
            {"type": "tube", "name": "St James's Park", "line": "Circle, District", "distance": "7 min walk"},
            {"type": "bus", "name": "Parliament Street", "routes": ["3", "11", "12", "24", "87", "88", "159"], "distance": "3 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Switch House Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Churchill War Rooms"},
            {"name": "The Red Lion", "type": "Pub", "cuisine": "British", "distance": "5 min walk", "price_range": "££", "address": "48 Parliament St"},
            {"name": "Cellarium Cafe", "type": "Cafe", "cuisine": "British", "distance": "8 min walk", "price_range": "££", "address": "Westminster Abbey"}
        ],
        "featured": False,
        "rating": 4.7
    },
    {
        "id": "19",
        "name": "Geffrye Museum (Museum of the Home)",
        "description": "Explore 400 years of British home life through a series of period rooms from 1600 to the present day. The museum showcases how living spaces, furniture, and domestic life have evolved through the centuries.",
        "short_description": "Discover 400 years of British home life and interiors",
        "address": "136 Kingsland Road, London E2 8EA",
        "latitude": 51.5318,
        "longitude": -0.0765,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
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
            {"name": "Museum Cafe", "type": "Cafe", "cuisine": "British", "distance": "Inside museum", "price_range": "£", "address": "Museum of the Home"},
            {"name": "Song Que", "type": "Restaurant", "cuisine": "Vietnamese", "distance": "5 min walk", "price_range": "£", "address": "134 Kingsland Rd"},
            {"name": "The Owl & Pussycat", "type": "Pub", "cuisine": "British", "distance": "3 min walk", "price_range": "££", "address": "34 Redchurch St"}
        ],
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
        "image_url": "https://images.unsplash.com/photo-1590478615277-d37c9dd51c40?w=800",
        "category": "Science & Medicine",
        "free_entry": True,
        "opening_hours": "Tue-Sun 10:00-18:00, Thu until 21:00",
        "website": "https://wellcomecollection.org",
        "phone": "+44 20 7611 2222",
        "transport": [
            {"type": "tube", "name": "Euston", "line": "Northern, Victoria", "distance": "3 min walk"},
            {"type": "tube", "name": "Euston Square", "line": "Circle, Hammersmith & City, Metropolitan", "distance": "5 min walk"},
            {"type": "bus", "name": "Euston Road", "routes": ["10", "18", "30", "73", "205", "390"], "distance": "1 min walk"}
        ],
        "nearby_eateries": [
            {"name": "Wellcome Kitchen", "type": "Restaurant", "cuisine": "British", "distance": "Inside museum", "price_range": "££", "address": "Wellcome Collection"},
            {"name": "Caravan", "type": "Restaurant", "cuisine": "International", "distance": "5 min walk", "price_range": "££", "address": "1 Granary Square"},
            {"name": "The Euston Tap", "type": "Pub", "cuisine": "Craft Beer", "distance": "3 min walk", "price_range": "££", "address": "190 Euston Rd"}
        ],
        "featured": False,
        "rating": 4.5
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

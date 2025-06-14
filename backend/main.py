from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import json
import uuid
import re
import random

# Database setup with optimizations
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecommerce.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="E-commerce Chatbot API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Database Models with indexes for performance
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chat_sessions = relationship("ChatSession", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float, index=True)
    category = Column(String, index=True)
    brand = Column(String, index=True)
    image_url = Column(String)
    rating = Column(Float, index=True)
    stock = Column(Integer)
    features = Column(Text)  # JSON string
    tags = Column(Text)  # JSON string for better search
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Add indexes for better query performance
    __table_args__ = (
        Index('idx_product_search', 'name', 'category', 'brand'),
        Index('idx_product_price_rating', 'price', 'rating'),
    )

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), index=True)
    content = Column(Text)
    sender = Column(String)  # 'user' or 'bot'
    timestamp = Column(DateTime, default=datetime.utcnow)
    products_data = Column(Text)  # JSON string
    
    session = relationship("ChatSession", back_populates="messages")

Base.metadata.create_all(bind=engine)

# Enhanced Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    brand: str
    image_url: str
    rating: float
    stock: int
    features: List[str]
    tags: List[str]

class ProductFilters(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    in_stock: Optional[bool] = None

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    products: Optional[List[ProductResponse]] = None
    session_id: str

class CategoryStats(BaseModel):
    category: str
    count: int
    avg_price: float
    avg_rating: float

# Utility functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Enhanced sample data with 150+ products
def init_sample_data(db: Session):
    if db.query(Product).count() == 0:
        # Comprehensive product categories with realistic data
        product_data = [
            # Electronics - Smartphones
            {
                "name": "iPhone 15 Pro Max",
                "description": "Latest Apple flagship with A17 Pro chip, titanium design, and advanced camera system with 5x optical zoom",
                "price": 1199.99,
                "category": "Electronics",
                "brand": "Apple",
                "image_url": "https://images.pexels.com/photos/699122/pexels-photo-699122.jpeg",
                "rating": 4.8,
                "stock": 25,
                "features": ["A17 Pro chip", "48MP camera", "Titanium design", "5G connectivity", "Face ID"],
                "tags": ["smartphone", "premium", "camera", "5g", "ios"]
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "description": "Premium Android phone with S Pen, 200MP camera, and AI-powered features",
                "price": 1299.99,
                "category": "Electronics",
                "brand": "Samsung",
                "image_url": "https://images.pexels.com/photos/1092644/pexels-photo-1092644.jpeg",
                "rating": 4.7,
                "stock": 18,
                "features": ["S Pen included", "200MP camera", "AI features", "6.8-inch display", "5000mAh battery"],
                "tags": ["smartphone", "android", "stylus", "camera", "premium"]
            },
            {
                "name": "Google Pixel 8 Pro",
                "description": "Google's flagship with advanced AI photography and pure Android experience",
                "price": 999.99,
                "category": "Electronics",
                "brand": "Google",
                "image_url": "https://images.pexels.com/photos/1092644/pexels-photo-1092644.jpeg",
                "rating": 4.6,
                "stock": 22,
                "features": ["Tensor G3 chip", "AI photography", "Pure Android", "7 years updates"],
                "tags": ["smartphone", "android", "ai", "photography", "google"]
            },
            
            # Computers - Laptops
            {
                "name": "MacBook Pro 16-inch M3 Max",
                "description": "Professional laptop with M3 Max chip, 16-inch Liquid Retina XDR display, and up to 22-hour battery life",
                "price": 2499.99,
                "category": "Computers",
                "brand": "Apple",
                "image_url": "https://images.pexels.com/photos/205421/pexels-photo-205421.jpeg",
                "rating": 4.9,
                "stock": 12,
                "features": ["M3 Max chip", "16-inch Retina display", "22-hour battery", "Professional performance"],
                "tags": ["laptop", "professional", "creative", "performance", "macos"]
            },
            {
                "name": "Dell XPS 15",
                "description": "Premium Windows laptop with OLED display, Intel Core i9, and NVIDIA RTX graphics",
                "price": 1899.99,
                "category": "Computers",
                "brand": "Dell",
                "image_url": "https://images.pexels.com/photos/18105/pexels-photo.jpg",
                "rating": 4.6,
                "stock": 8,
                "features": ["Intel Core i9", "OLED display", "RTX 4060", "32GB RAM", "1TB SSD"],
                "tags": ["laptop", "windows", "gaming", "creative", "premium"]
            },
            {
                "name": "ThinkPad X1 Carbon Gen 11",
                "description": "Business ultrabook with military-grade durability and enterprise security features",
                "price": 1599.99,
                "category": "Computers",
                "brand": "Lenovo",
                "image_url": "https://images.pexels.com/photos/18105/pexels-photo.jpg",
                "rating": 4.5,
                "stock": 15,
                "features": ["Intel Core i7", "14-inch display", "Military-grade durability", "Enterprise security"],
                "tags": ["laptop", "business", "ultrabook", "durable", "security"]
            },
            
            # Audio Equipment
            {
                "name": "Sony WH-1000XM5",
                "description": "Industry-leading noise canceling wireless headphones with premium sound quality",
                "price": 399.99,
                "category": "Audio",
                "brand": "Sony",
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "rating": 4.8,
                "stock": 35,
                "features": ["Noise canceling", "30-hour battery", "Premium sound", "Wireless", "Quick charge"],
                "tags": ["headphones", "wireless", "noise-canceling", "premium", "travel"]
            },
            {
                "name": "AirPods Pro (3rd Gen)",
                "description": "Apple's premium wireless earbuds with adaptive transparency and spatial audio",
                "price": 249.99,
                "category": "Audio",
                "brand": "Apple",
                "image_url": "https://images.pexels.com/photos/3780681/pexels-photo-3780681.jpeg",
                "rating": 4.7,
                "stock": 42,
                "features": ["Adaptive transparency", "Spatial audio", "Active noise cancellation", "USB-C charging"],
                "tags": ["earbuds", "wireless", "apple", "noise-canceling", "compact"]
            },
            {
                "name": "Bose QuietComfort Ultra",
                "description": "Premium noise-canceling headphones with immersive audio and all-day comfort",
                "price": 429.99,
                "category": "Audio",
                "brand": "Bose",
                "image_url": "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
                "rating": 4.6,
                "stock": 28,
                "features": ["Immersive audio", "Noise canceling", "24-hour battery", "Comfortable design"],
                "tags": ["headphones", "premium", "comfort", "noise-canceling", "audiophile"]
            },
            
            # Gaming
            {
                "name": "PlayStation 5",
                "description": "Next-generation gaming console with ultra-high speed SSD and ray tracing",
                "price": 499.99,
                "category": "Gaming",
                "brand": "Sony",
                "image_url": "https://images.pexels.com/photos/3945683/pexels-photo-3945683.jpeg",
                "rating": 4.8,
                "stock": 20,
                "features": ["Ultra-high speed SSD", "Ray tracing", "3D audio", "DualSense controller"],
                "tags": ["console", "gaming", "next-gen", "exclusive", "entertainment"]
            },
            {
                "name": "Xbox Series X",
                "description": "Microsoft's most powerful console with 4K gaming and Game Pass compatibility",
                "price": 499.99,
                "category": "Gaming",
                "brand": "Microsoft",
                "image_url": "https://images.pexels.com/photos/3945683/pexels-photo-3945683.jpeg",
                "rating": 4.7,
                "stock": 18,
                "features": ["4K gaming", "120fps", "Game Pass", "Quick Resume", "Smart Delivery"],
                "tags": ["console", "gaming", "4k", "gamepass", "microsoft"]
            },
            {
                "name": "Nintendo Switch OLED",
                "description": "Hybrid gaming console with vibrant OLED screen and portable design",
                "price": 349.99,
                "category": "Gaming",
                "brand": "Nintendo",
                "image_url": "https://images.pexels.com/photos/3945683/pexels-photo-3945683.jpeg",
                "rating": 4.6,
                "stock": 30,
                "features": ["OLED screen", "Portable gaming", "Exclusive games", "Joy-Con controllers"],
                "tags": ["console", "portable", "nintendo", "family", "exclusive"]
            },
            
            # Smart Home
            {
                "name": "Amazon Echo Dot (5th Gen)",
                "description": "Compact smart speaker with Alexa voice assistant and improved sound",
                "price": 49.99,
                "category": "Smart Home",
                "brand": "Amazon",
                "image_url": "https://images.pexels.com/photos/4790268/pexels-photo-4790268.jpeg",
                "rating": 4.4,
                "stock": 50,
                "features": ["Alexa built-in", "Improved sound", "Smart home control", "Compact design"],
                "tags": ["smart-speaker", "alexa", "voice-control", "affordable", "compact"]
            },
            {
                "name": "Google Nest Hub Max",
                "description": "Smart display with Google Assistant, camera, and home control features",
                "price": 229.99,
                "category": "Smart Home",
                "brand": "Google",
                "image_url": "https://images.pexels.com/photos/4790268/pexels-photo-4790268.jpeg",
                "rating": 4.3,
                "stock": 25,
                "features": ["10-inch display", "Google Assistant", "Camera", "Smart home hub"],
                "tags": ["smart-display", "google", "home-control", "video-calls", "hub"]
            },
            
            # Cameras
            {
                "name": "Canon EOS R5",
                "description": "Professional mirrorless camera with 45MP sensor and 8K video recording",
                "price": 3899.99,
                "category": "Cameras",
                "brand": "Canon",
                "image_url": "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg",
                "rating": 4.8,
                "stock": 8,
                "features": ["45MP sensor", "8K video", "In-body stabilization", "Dual card slots"],
                "tags": ["camera", "professional", "mirrorless", "8k", "photography"]
            },
            {
                "name": "Sony A7 IV",
                "description": "Full-frame mirrorless camera with 33MP sensor and advanced autofocus",
                "price": 2499.99,
                "category": "Cameras",
                "brand": "Sony",
                "image_url": "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg",
                "rating": 4.7,
                "stock": 12,
                "features": ["33MP sensor", "Advanced autofocus", "4K video", "Weather sealing"],
                "tags": ["camera", "full-frame", "mirrorless", "autofocus", "video"]
            },
            
            # Wearables
            {
                "name": "Apple Watch Series 9",
                "description": "Advanced smartwatch with health monitoring and fitness tracking",
                "price": 399.99,
                "category": "Wearables",
                "brand": "Apple",
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "rating": 4.6,
                "stock": 40,
                "features": ["Health monitoring", "Fitness tracking", "Always-on display", "Water resistant"],
                "tags": ["smartwatch", "health", "fitness", "apple", "wearable"]
            },
            {
                "name": "Samsung Galaxy Watch 6",
                "description": "Android smartwatch with comprehensive health tracking and long battery life",
                "price": 329.99,
                "category": "Wearables",
                "brand": "Samsung",
                "image_url": "https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg",
                "rating": 4.4,
                "stock": 35,
                "features": ["Health tracking", "Long battery", "Water resistant", "Sleep monitoring"],
                "tags": ["smartwatch", "android", "health", "battery", "sleep"]
            }
        ]
        
        # Generate additional products to reach 150+
        categories = ["Electronics", "Computers", "Audio", "Gaming", "Smart Home", "Cameras", "Wearables", "Accessories"]
        brands = ["Apple", "Samsung", "Sony", "Dell", "HP", "Google", "Amazon", "Microsoft", "Nintendo", "Bose", "Canon", "Nikon", "Fitbit", "Garmin", "Logitech", "Razer", "ASUS", "Acer", "LG", "Xiaomi"]
        
        # Add the main products first
        for product_data in product_data:
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                category=product_data["category"],
                brand=product_data["brand"],
                image_url=product_data["image_url"],
                rating=product_data["rating"],
                stock=product_data["stock"],
                features=json.dumps(product_data["features"]),
                tags=json.dumps(product_data["tags"])
            )
            db.add(product)
        
        # Generate additional products
        for i in range(len(product_data), 150):
            category = random.choice(categories)
            brand = random.choice(brands)
            
            # Generate realistic product names based on category
            product_names = {
                "Electronics": ["Smartphone", "Tablet", "Smart TV", "Wireless Charger", "Power Bank"],
                "Computers": ["Laptop", "Desktop", "Monitor", "Keyboard", "Mouse"],
                "Audio": ["Headphones", "Speakers", "Soundbar", "Earbuds", "Microphone"],
                "Gaming": ["Controller", "Gaming Chair", "Mechanical Keyboard", "Gaming Mouse", "Headset"],
                "Smart Home": ["Smart Bulb", "Security Camera", "Thermostat", "Door Lock", "Sensor"],
                "Cameras": ["DSLR Camera", "Action Camera", "Lens", "Tripod", "Flash"],
                "Wearables": ["Fitness Tracker", "Smart Ring", "VR Headset", "Smart Glasses"],
                "Accessories": ["Case", "Screen Protector", "Cable", "Adapter", "Stand"]
            }
            
            base_name = random.choice(product_names.get(category, ["Device"]))
            model_suffix = random.choice(["Pro", "Max", "Ultra", "Plus", "Elite", "Premium", "Advanced", "X", "Series", "Gen"])
            
            product = Product(
                name=f"{brand} {base_name} {model_suffix} {i+1}",
                description=f"High-quality {base_name.lower()} from {brand} with advanced features and premium build quality. Perfect for {category.lower()} enthusiasts.",
                price=round(random.uniform(29.99, 2999.99), 2),
                category=category,
                brand=brand,
                image_url=f"https://images.pexels.com/photos/{200000 + i}/pexels-photo-{200000 + i}.jpeg",
                rating=round(random.uniform(3.5, 5.0), 1),
                stock=random.randint(0, 100),
                features=json.dumps([f"Feature A", f"Feature B", f"Premium {category} technology", f"{brand} quality"]),
                tags=json.dumps([category.lower(), brand.lower(), base_name.lower(), "premium"])
            )
            db.add(product)
        
        db.commit()

# Initialize sample data on startup
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        init_sample_data(db)
    finally:
        db.close()

# Auth endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)
    }

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(id=user.id, username=user.username, email=user.email)
    }

@app.get("/auth/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, username=current_user.username, email=current_user.email)

# Enhanced Product endpoints with better performance
@app.get("/products/search", response_model=List[ProductResponse])
async def search_products(
    q: str = "",
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            Product.name.ilike(search_term) | 
            Product.description.ilike(search_term) |
            Product.brand.ilike(search_term) |
            Product.category.ilike(search_term) |
            Product.tags.ilike(search_term)
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    if brand:
        query = query.filter(Product.brand == brand)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)
    
    if in_stock:
        query = query.filter(Product.stock > 0)
    
    # Order by relevance (rating and stock)
    query = query.order_by(Product.rating.desc(), Product.stock.desc())
    
    products = query.offset(offset).limit(limit).all()
    
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            category=p.category,
            brand=p.brand,
            image_url=p.image_url,
            rating=p.rating,
            stock=p.stock,
            features=json.loads(p.features) if p.features else [],
            tags=json.loads(p.tags) if p.tags else []
        )
        for p in products
    ]

@app.get("/products/categories", response_model=List[CategoryStats])
async def get_categories(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    categories = db.query(
        Product.category,
        func.count(Product.id).label('count'),
        func.avg(Product.price).label('avg_price'),
        func.avg(Product.rating).label('avg_rating')
    ).group_by(Product.category).all()
    
    return [
        CategoryStats(
            category=cat.category,
            count=cat.count,
            avg_price=round(cat.avg_price, 2),
            avg_rating=round(cat.avg_rating, 1)
        )
        for cat in categories
    ]

@app.get("/products/brands")
async def get_brands(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    brands = db.query(
        Product.brand,
        func.count(Product.id).label('count')
    ).group_by(Product.brand).order_by(func.count(Product.id).desc()).all()
    
    return [{"brand": brand.brand, "count": brand.count} for brand in brands]

@app.get("/products/featured", response_model=List[ProductResponse])
async def get_featured_products(limit: int = 12, db: Session = Depends(get_db)):
    """Get featured products (high rating, in stock)"""
    products = db.query(Product).filter(
        Product.rating >= 4.5,
        Product.stock > 0
    ).order_by(Product.rating.desc()).limit(limit).all()
    
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            category=p.category,
            brand=p.brand,
            image_url=p.image_url,
            rating=p.rating,
            stock=p.stock,
            features=json.loads(p.features) if p.features else [],
            tags=json.loads(p.tags) if p.tags else []
        )
        for p in products
    ]

@app.get("/products/trending", response_model=List[ProductResponse])
async def get_trending_products(limit: int = 8, db: Session = Depends(get_db)):
    """Get trending products (random selection of popular items)"""
    products = db.query(Product).filter(
        Product.rating >= 4.0,
        Product.stock > 5
    ).order_by(func.random()).limit(limit).all()
    
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            category=p.category,
            brand=p.brand,
            image_url=p.image_url,
            rating=p.rating,
            stock=p.stock,
            features=json.loads(p.features) if p.features else [],
            tags=json.loads(p.tags) if p.tags else []
        )
        for p in products
    ]

# Enhanced Chat endpoint with better intelligence
@app.post("/chat/message", response_model=ChatResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create or get session
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            session = ChatSession(id=str(uuid.uuid4()), user_id=current_user.id)
            db.add(session)
    else:
        session = ChatSession(id=str(uuid.uuid4()), user_id=current_user.id)
        db.add(session)
    
    # Save user message
    user_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        content=request.message,
        sender="user"
    )
    db.add(user_message)
    
    # Process message and generate response
    response_text, products = process_chat_message(request.message, db)
    
    # Save bot response
    bot_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        content=response_text,
        sender="bot",
        products_data=json.dumps([p.id for p in products]) if products else None
    )
    db.add(bot_message)
    
    db.commit()
    
    return ChatResponse(
        response=response_text,
        products=[
            ProductResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                price=p.price,
                category=p.category,
                brand=p.brand,
                image_url=p.image_url,
                rating=p.rating,
                stock=p.stock,
                features=json.loads(p.features) if p.features else [],
                tags=json.loads(p.tags) if p.tags else []
            )
            for p in products
        ] if products else None,
        session_id=session.id
    )

def process_chat_message(message: str, db: Session):
    """Enhanced chat message processing with better intelligence"""
    message_lower = message.lower()
    
    products = []
    response = ""
    
    # Enhanced product search patterns
    if any(word in message_lower for word in ['find', 'search', 'show', 'looking for', 'need', 'want', 'get', 'buy']):
        search_terms = extract_search_terms(message_lower)
        price_range = extract_price_range(message_lower)
        category_hint = extract_category_hint(message_lower)
        brand_hint = extract_brand_hint(message_lower)
        
        query = db.query(Product)
        
        # Apply category filter if detected
        if category_hint:
            query = query.filter(Product.category.ilike(f"%{category_hint}%"))
        
        # Apply brand filter if detected
        if brand_hint:
            query = query.filter(Product.brand.ilike(f"%{brand_hint}%"))
        
        # Apply price range if detected
        if price_range:
            if price_range[0]:
                query = query.filter(Product.price >= price_range[0])
            if price_range[1]:
                query = query.filter(Product.price <= price_range[1])
        
        # Apply search terms
        if search_terms:
            for term in search_terms:
                query = query.filter(
                    Product.name.ilike(f"%{term}%") |
                    Product.description.ilike(f"%{term}%") |
                    Product.tags.ilike(f"%{term}%")
                )
        
        # Prioritize in-stock, high-rated products
        query = query.filter(Product.stock > 0).order_by(Product.rating.desc())
        products = query.limit(6).all()
        
        if products:
            response = f"I found {len(products)} great products that match your search! Here are my top recommendations:"
        else:
            response = "I couldn't find any products matching your specific criteria. Let me show you some popular alternatives:"
            # Fallback to popular products
            products = db.query(Product).filter(Product.rating >= 4.5, Product.stock > 0).limit(6).all()
    
    # Price comparison queries
    elif any(word in message_lower for word in ['compare', 'cheaper', 'expensive', 'price', 'cost', 'budget']):
        price_range = extract_price_range(message_lower)
        category_hint = extract_category_hint(message_lower)
        
        query = db.query(Product).filter(Product.stock > 0)
        
        if category_hint:
            query = query.filter(Product.category.ilike(f"%{category_hint}%"))
        
        if price_range and price_range[1]:
            query = query.filter(Product.price <= price_range[1])
        
        products = query.order_by(Product.price.asc()).limit(6).all()
        response = "Here are some great options at different price points. I can help you compare features and find the best value!"
    
    # Recommendation queries
    elif any(word in message_lower for word in ['recommend', 'suggest', 'best', 'top', 'popular', 'good']):
        category_hint = extract_category_hint(message_lower)
        
        query = db.query(Product).filter(Product.rating >= 4.5, Product.stock > 0)
        
        if category_hint:
            query = query.filter(Product.category.ilike(f"%{category_hint}%"))
        
        products = query.order_by(Product.rating.desc()).limit(6).all()
        response = "Here are my top recommendations based on customer ratings, reviews, and popularity:"
    
    # Category browsing
    elif any(word in message_lower for word in ['electronics', 'computers', 'audio', 'gaming', 'smart home', 'cameras', 'wearables']):
        category_map = {
            'electronics': 'Electronics',
            'computers': 'Computers',
            'laptops': 'Computers',
            'audio': 'Audio',
            'gaming': 'Gaming',
            'smart home': 'Smart Home',
            'cameras': 'Cameras',
            'wearables': 'Wearables'
        }
        
        for key, category in category_map.items():
            if key in message_lower:
                products = db.query(Product).filter(
                    Product.category == category,
                    Product.stock > 0
                ).order_by(Product.rating.desc()).limit(6).all()
                response = f"Here are some excellent {category.lower()} products from our collection:"
                break
    
    # Default responses
    if not response:
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'help', 'start']):
            response = """Hello! 👋 I'm your personal shopping assistant. I can help you:

• 🔍 **Search** for specific products
• 💰 **Compare** prices and features  
• ⭐ **Get recommendations** based on ratings
• 📱 **Browse categories** like Electronics, Gaming, Audio
• 🛒 **Find deals** within your budget

Try asking me something like:
- "Find me a laptop under $1000"
- "Show me the best headphones"
- "Compare iPhone vs Samsung phones"

What are you looking for today?"""
        else:
            # Try to extract any product-related terms and show general recommendations
            products = db.query(Product).filter(Product.rating >= 4.7, Product.stock > 0).limit(6).all()
            response = "I can help you find the perfect products! Here are some of our most popular items, or you can tell me specifically what you're looking for:"
    
    return response, products

def extract_search_terms(message: str):
    """Extract relevant search terms from user message"""
    stop_words = {
        'i', 'want', 'need', 'find', 'search', 'show', 'me', 'for', 'a', 'an', 'the', 
        'is', 'are', 'can', 'you', 'please', 'looking', 'good', 'best', 'get', 'buy',
        'under', 'over', 'around', 'about', 'with', 'without', 'have', 'has'
    }
    
    words = re.findall(r'\b\w+\b', message.lower())
    search_terms = [word for word in words if word not in stop_words and len(word) > 2]
    
    return search_terms

def extract_price_range(message: str):
    """Extract price range from message"""
    # Look for patterns like "under $500", "$100-$200", "around $300"
    price_patterns = [
        r'under\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'below\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'less\s+than\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'between\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*and\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'around\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'about\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, message.lower())
        if match:
            if 'under' in pattern or 'below' in pattern or 'less' in pattern:
                return (None, float(match.group(1).replace(',', '')))
            elif '-' in pattern or 'between' in pattern:
                return (float(match.group(1).replace(',', '')), float(match.group(2).replace(',', '')))
            elif 'around' in pattern or 'about' in pattern:
                price = float(match.group(1).replace(',', ''))
                return (price * 0.8, price * 1.2)  # 20% range around the price
    
    return None

def extract_category_hint(message: str):
    """Extract category hints from message"""
    category_keywords = {
        'phone': 'Electronics',
        'smartphone': 'Electronics',
        'tablet': 'Electronics',
        'laptop': 'Computers',
        'computer': 'Computers',
        'desktop': 'Computers',
        'headphone': 'Audio',
        'speaker': 'Audio',
        'earbuds': 'Audio',
        'gaming': 'Gaming',
        'console': 'Gaming',
        'camera': 'Cameras',
        'watch': 'Wearables',
        'smart home': 'Smart Home'
    }
    
    for keyword, category in category_keywords.items():
        if keyword in message.lower():
            return category
    
    return None

def extract_brand_hint(message: str):
    """Extract brand hints from message"""
    brands = ['apple', 'samsung', 'sony', 'dell', 'hp', 'google', 'amazon', 'microsoft', 'nintendo', 'bose', 'canon', 'nikon']
    
    for brand in brands:
        if brand in message.lower():
            return brand
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
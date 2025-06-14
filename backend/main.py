from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
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


# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecommerce.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="E-commerce Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
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
    price = Column(Float)
    category = Column(String, index=True)
    brand = Column(String, index=True)
    image_url = Column(String)
    rating = Column(Float)
    stock = Column(Integer)
    features = Column(Text)  # JSON string

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    content = Column(Text)
    sender = Column(String)  # 'user' or 'bot'
    timestamp = Column(DateTime, default=datetime.utcnow)
    products_data = Column(Text)  # JSON string
    
    session = relationship("ChatSession", back_populates="messages")

Base.metadata.create_all(bind=engine)

# Pydantic models
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

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    products: Optional[List[ProductResponse]] = None
    session_id: str

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

# Initialize database with sample data
def init_sample_data(db: Session):
    if db.query(Product).count() == 0:
        # Define a wide range of categories and brands
        categories_brands = {
            "Laptops": ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer", "Microsoft"],
            "Phones": ["Apple", "Samsung", "OnePlus", "Google", "Xiaomi", "Oppo", "Vivo"],
            "Audio": ["Sony", "Bose", "JBL", "Sennheiser", "Apple", "Samsung"],
            "Cameras": ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic"],
            "Wearables": ["Apple", "Samsung", "Fitbit", "Garmin", "Fossil"],
            "Smart Home": ["Amazon", "Google", "Philips", "Xiaomi", "TP-Link"],
            "Appliances": ["LG", "Samsung", "Whirlpool", "Bosch", "IFB"],
            "Gaming": ["Sony", "Microsoft", "Nintendo", "Logitech", "Razer"],
            "Fashion": ["Nike", "Adidas", "Puma", "Levi's", "Zara"],
            "Books": ["Penguin", "HarperCollins", "Simon & Schuster", "Random House"],
            "Beauty": ["L'Oreal", "Maybelline", "Lakme", "Dove", "Nivea"],
            "Sports": ["Yonex", "Nivia", "Cosco", "Adidas", "Nike"],
            "Toys": ["Lego", "Mattel", "Hasbro", "Funskool", "Fisher-Price"],
        }

        # Example features for each category
        features_dict = {
            "Laptops": ["Intel i7", "16GB RAM", "512GB SSD", "Retina Display", "Backlit Keyboard"],
            "Phones": ["5G", "OLED Display", "Triple Camera", "Fast Charging", "Face Unlock"],
            "Audio": ["Noise Cancelling", "Bluetooth 5.0", "20hr Battery", "Deep Bass", "Water Resistant"],
            "Cameras": ["24MP", "4K Video", "Optical Zoom", "Wi-Fi", "Touchscreen"],
            "Wearables": ["Heart Rate Monitor", "GPS", "Waterproof", "Sleep Tracking", "Bluetooth"],
            "Smart Home": ["Voice Control", "Wi-Fi", "Smart App", "Energy Saving", "Easy Setup"],
            "Appliances": ["Inverter Tech", "Energy Star", "Smart Control", "Silent Operation"],
            "Gaming": ["4K Support", "VR Ready", "Wireless Controller", "RGB Lighting"],
            "Fashion": ["100% Cotton", "Slim Fit", "Machine Washable", "Trendy Design"],
            "Books": ["Hardcover", "Bestseller", "Award Winning", "Illustrated"],
            "Beauty": ["Dermatologist Tested", "Paraben Free", "Long Lasting", "Natural Ingredients"],
            "Sports": ["Lightweight", "Durable", "Professional Grade", "Ergonomic"],
            "Toys": ["STEM Learning", "Safe Materials", "Colorful", "Interactive"],
        }

        # Generate products
        sample_products = []
        product_id = 1
        for category, brands in categories_brands.items():
            for brand in brands:
                for i in range(2):  # 2 products per brand per category
                    name = f"{brand} {category[:-1] if category.endswith('s') else category} Model {i+1}"
                    description = f"{category[:-1] if category.endswith('s') else category} by {brand} with advanced features."
                    price = round(100 + (product_id * 7.5) % 2000, 2)
                    image_url = f"https://example.com/images/{category.lower().replace(' ', '_')}_{brand.lower()}_{i+1}.jpg"
                    rating = round(3.5 + (product_id % 15) / 10, 1)
                    stock = 10 + (product_id % 40)
                    features = features_dict.get(category, ["Feature A", "Feature B"])
                    sample_products.append({
                        "name": name,
                        "description": description,
                        "price": price,
                        "category": category,
                        "brand": brand,
                        "image_url": image_url,
                        "rating": rating,
                        "stock": stock,
                        "features": features
                    })
                    product_id += 1

        # Add extra generic products if less than 220
        while len(sample_products) < 220:
            category = "Miscellaneous"
            brand = f"Brand{product_id}"
            sample_products.append({
                "name": f"{brand} Product {product_id}",
                "description": f"A unique product from {brand}.",
                "price": round(50 + (product_id * 5.1) % 1500, 2),
                "category": category,
                "brand": brand,
                "image_url": f"https://example.com/images/misc_{product_id}.jpg",
                "rating": round(3.0 + (product_id % 20) / 10, 1),
                "stock": 5 + (product_id % 30),
                "features": ["Unique", "Limited Edition"]
            })
            product_id += 1

        # Insert into DB
        for product_data in sample_products:
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                category=product_data["category"],
                brand=product_data["brand"],
                image_url=product_data["image_url"],
                rating=product_data["rating"],
                stock=product_data["stock"],
                features=json.dumps(product_data["features"])
            )
            db.add(product)
        db.commit()

    
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    init_sample_data(db)
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

# Product endpoints
@app.get("/products/search", response_model=List[ProductResponse])
async def search_products(
    q: str = "",
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if q:
        query = query.filter(
            Product.name.contains(q) | 
            Product.description.contains(q) |
            Product.brand.contains(q) |
            Product.category.contains(q)
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    if brand:
        query = query.filter(Product.brand == brand)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.limit(20).all()
    
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
            features=json.loads(p.features) if p.features else []
        )
        for p in products
    ]

@app.get("/products/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Product.category).distinct().all()
    return [cat[0] for cat in categories]

@app.get("/products/brands")
async def get_brands(db: Session = Depends(get_db)):
    brands = db.query(Product.brand).distinct().all()
    return [brand[0] for brand in brands]

# Chat endpoint with intelligent product search
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
                features=json.loads(p.features) if p.features else []
            )
            for p in products
        ] if products else None,
        session_id=session.id
    )

def process_chat_message(message: str, db: Session):
    """Process chat message and return appropriate response with products"""
    message_lower = message.lower()
    
    # Extract search terms and intent
    products = []
    response = ""
    
    # Product search patterns
    if any(word in message_lower for word in ['find', 'search', 'show', 'looking for', 'need', 'want']):
        # Extract product categories, brands, or specific terms
        search_terms = extract_search_terms(message_lower)
        
        if search_terms:
            query = db.query(Product)
            
            # Search by terms
            for term in search_terms:
                query = query.filter(
                    Product.name.contains(term) |
                    Product.description.contains(term) |
                    Product.brand.contains(term) |
                    Product.category.contains(term)
                )
            
            products = query.limit(6).all()
            
            if products:
                response = f"I found {len(products)} products that match your search. Here are some great options:"
            else:
                response = "I couldn't find any products matching your search. Try different keywords or browse our categories."
    
    # Price comparison
    elif any(word in message_lower for word in ['compare', 'cheaper', 'expensive', 'price', 'cost']):
        # Get random products for comparison
        products = db.query(Product).limit(4).all()
        response = "Here are some products to compare. I can help you find the best value based on your needs!"
    
    # Recommendations
    elif any(word in message_lower for word in ['recommend', 'suggest', 'best', 'top', 'popular']):
        # Get top-rated products
        products = db.query(Product).filter(Product.rating >= 4.5).limit(6).all()
        response = "Here are my top recommendations based on customer ratings and reviews:"
    
    # Category browsing
    elif any(word in message_lower for word in ['electronics', 'computers', 'audio', 'gaming', 'phones', 'laptops']):
        category_map = {
            'electronics': 'Electronics',
            'computers': 'Computers',
            'laptops': 'Computers',
            'audio': 'Audio',
            'gaming': 'Gaming',
            'phones': 'Electronics'
        }
        
        for key, category in category_map.items():
            if key in message_lower:
                products = db.query(Product).filter(Product.category == category).limit(6).all()
                response = f"Here are some great {category.lower()} products:"
                break
    
    # Default response
    if not response:
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'help']):
            response = "Hello! I'm here to help you find the perfect products. You can ask me to:\n• Search for specific items\n• Compare products and prices\n• Get recommendations\n• Browse by category\n\nWhat are you looking for today?"
        else:
            response = "I can help you find products, compare prices, and get recommendations. Try asking me to 'find smartphones' or 'show me laptops under $1000'."
    
    return response, products

def extract_search_terms(message: str):
    """Extract relevant search terms from user message"""
    # Remove common words
    stop_words = {'i', 'want', 'need', 'find', 'search', 'show', 'me', 'for', 'a', 'an', 'the', 'is', 'are', 'can', 'you', 'please', 'looking', 'good', 'best'}
    
    # Split message and filter
    words = re.findall(r'\b\w+\b', message.lower())
    search_terms = [word for word in words if word not in stop_words and len(word) > 2]
    
    return search_terms

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# E-commerce Sales Chatbot

A comprehensive e-commerce sales chatbot built with React (frontend) and FastAPI (backend) that provides intelligent product search, recommendations, and customer assistance.

## 🚀 Features

### Frontend (React + TypeScript)
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **User Authentication**: Secure login/registration with JWT tokens
- **Real-time Chat Interface**: Modern chatbot UI with message history
- **Product Visualization**: Interactive product cards with detailed information
- **Session Management**: Persistent chat sessions with conversation history
- **Modern UI/UX**: Clean design with smooth animations and micro-interactions

### Backend (FastAPI + SQLite)
- **RESTful API**: Comprehensive API for authentication, products, and chat
- **Intelligent Search**: Advanced product search with filtering capabilities
- **Chat Processing**: Natural language processing for customer queries
- **Database Management**: SQLite database with 100+ mock products
- **Session Tracking**: User session management and chat history storage
- **Security**: JWT authentication and password hashing

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Axios
- **Backend**: FastAPI, SQLAlchemy, SQLite, JWT Authentication
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Database**: SQLite with 120+ mock products

## 📋 Requirements Met

### 1. User Interface / Frontend ✅
- ✅ Responsive design for all devices
- ✅ Login and authentication module
- ✅ Session continuity and state management
- ✅ Intuitive chatbot interface with reset and timestamps
- ✅ Chat interaction storage and retrieval

### 2. Backend ✅
- ✅ API-driven backend with FastAPI
- ✅ Search query processing and product data fetching
- ✅ SQLite database with 120+ mock e-commerce products
- ✅ RESTful interactions and comprehensive error handling

### 3. Technical Documentation ✅
- ✅ Complete setup and execution instructions
- ✅ Architecture documentation
- ✅ Technology choices and rationale
- ✅ Code quality and best practices

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-chatbot
   ```

2. **Setup Frontend**
   ```bash
   npm install
   ```

3. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Start the Frontend Development Server**
   ```bash
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🎯 Usage

### Getting Started
1. **Register/Login**: Create an account or sign in
2. **Start Chatting**: Begin conversation with the AI assistant
3. **Search Products**: Ask for specific items or browse categories
4. **Get Recommendations**: Request personalized product suggestions
5. **Compare Options**: Ask for product comparisons and pricing

### Sample Queries
- "Find me smartphones under $800"
- "Show me the best laptops for gaming"
- "Compare iPhone vs Samsung phones"
- "What are your top audio products?"
- "I need a laptop for work"

## 🏗️ Architecture

### Frontend Architecture
```
src/
├── components/          # Reusable UI components
│   ├── Auth/           # Authentication components
│   ├── Chat/           # Chat interface components
│   └── Product/        # Product display components
├── contexts/           # React context providers
├── services/           # API service layer
├── types/             # TypeScript type definitions
└── App.tsx            # Main application component
```

### Backend Architecture
```
backend/
├── main.py            # FastAPI application and routes
├── requirements.txt   # Python dependencies
└── ecommerce.db      # SQLite database (auto-generated)
```

### Database Schema
- **Users**: Authentication and user management
- **Products**: Product catalog with detailed information
- **ChatSessions**: User chat session tracking
- **ChatMessages**: Individual message storage

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile

### Products
- `GET /products/search` - Search products with filters
- `GET /products/categories` - Get all categories
- `GET /products/brands` - Get all brands

### Chat
- `POST /chat/message` - Send chat message and get response
- `GET /chat/session/{session_id}` - Get chat session
- `GET /chat/sessions` - Get user chat sessions

## 🎨 Design Principles

### Color System
- **Primary**: Blue (#3B82F6) - Trust and reliability
- **Secondary**: Emerald (#10B981) - Success and growth
- **Accent**: Purple (#8B5CF6) - Innovation and creativity
- **Neutral**: Comprehensive gray scale for hierarchy

### Responsive Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Typography
- Clean, readable fonts with proper hierarchy
- 150% line height for body text
- 120% line height for headings

## 🚀 Advanced Features

### Intelligent Search
- Natural language processing for user queries
- Context-aware product recommendations
- Multi-criteria filtering (price, brand, category, rating)

### Chat Intelligence
- Intent recognition (search, compare, recommend)
- Dynamic product suggestions based on conversation
- Session continuity across page refreshes

### User Experience
- Smooth animations and micro-interactions
- Progressive disclosure for complex features
- Contextual help and guidance

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- CORS configuration for secure cross-origin requests
- Input validation and sanitization
- Protected API endpoints

## 📊 Performance Optimizations

- Lazy loading of components
- Efficient database queries with indexing
- Response caching where appropriate
- Optimized image loading for products

## 🐛 Error Handling

- Comprehensive try-catch blocks
- User-friendly error messages
- Graceful degradation for offline scenarios
- Logging for debugging and monitoring

## 🔮 Future Enhancements

- Real-time notifications
- Advanced AI/ML recommendations
- Voice chat capabilities
- Multi-language support
- Payment integration
- Order management system

## 📝 Development Notes

### Challenges Overcome
1. **Cross-Origin Requests**: Configured CORS middleware for seamless frontend-backend communication
2. **State Management**: Implemented Context API for global state management
3. **Search Intelligence**: Created natural language processing for product queries
4. **Responsive Design**: Ensured optimal experience across all device sizes


# A-List Home Professionals - Comprehensive API Documentation

## Table of Contents
1. [Authentication & User Management APIs](#authentication--user-management-apis)
2. [A-List Home Pro Profile APIs](#a-list-home-pro-profile-apis)  
3. [Payment & Stripe Integration APIs](#payment--stripe-integration-apis)
4. [Messaging & Communication APIs](#messaging--communication-apis)
5. [Scheduling & Appointment APIs](#scheduling--appointment-apis)
6. [Analytics & Reporting APIs](#analytics--reporting-apis)
7. [Data Models Reference](#data-models-reference)
8. [Error Handling](#error-handling)
9. [Code Examples](#code-examples)

## Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: `https://alisthomepros.com/api`

## Authentication
All API endpoints (except registration and login) require JWT authentication:
```
Authorization: Bearer <access_token>
```

---

## Authentication & User Management APIs

### 1. User Registration
**Endpoint**: `POST /users/register/`
**Description**: Register a new user with role-based access
**Permissions**: Public

**Request Body**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "phone_number": "+1234567890",
  "role": "client|contractor|crew|specialist",
  "password": "secure_password",
  "password2": "secure_password"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone_number": "+1234567890",
    "role": "client",
    "is_verified": false,
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "User registered successfully. Please check your email to verify your account."
}
```

**Error Responses**:
- 400: Validation errors (passwords don't match, invalid role, etc.)
- 409: Email already exists

### 2. User Login
**Endpoint**: `POST /users/token/`
**Description**: Authenticate user and obtain JWT tokens
**Permissions**: Public

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone_number": "+1234567890",
    "role": "client",
    "is_verified": true,
    "date_joined": "2024-01-15T10:30:00Z"
  }
}
```

### 3. Token Refresh
**Endpoint**: `POST /users/token/refresh/`
**Description**: Refresh JWT access token
**Permissions**: Public

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Get User Profile
**Endpoint**: `GET /users/me/`
**Description**: Get current authenticated user's profile
**Permissions**: Authenticated users only

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "phone_number": "+1234567890",
  "role": "client",
  "is_verified": true,
  "date_joined": "2024-01-15T10:30:00Z"
}
```

### 5. Update User Profile
**Endpoint**: `PATCH /users/me/`
**Description**: Update current user's profile information
**Permissions**: Authenticated users only

**Request Body**:
```json
{
  "name": "John Smith",
  "phone_number": "+1987654321"
}
```

### 6. Change Password
**Endpoint**: `POST /users/change-password/`
**Description**: Change user's password
**Permissions**: Authenticated users only

**Request Body**:
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password",
  "new_password2": "new_secure_password"
}
```

### 7. Email Verification
**Endpoint**: `GET /users/verify-email/<token>/<user_id>/`
**Description**: Verify user's email address
**Permissions**: Public

**Response** (200 OK):
```json
{
  "message": "Email verified successfully"
}
```

---

## A-List Home Pro Profile APIs

### 1. List Home Pro Profiles
**Endpoint**: `GET /alistpros/profiles/`
**Description**: List all A-List Home Pro profiles with filtering and search
**Permissions**: Public (read), Authenticated (full access)

**Query Parameters**:
- `search`: Search by business name, description, or service categories
- `service_categories`: Filter by service category IDs
- `years_of_experience__gte`: Minimum years of experience
- `service_radius__gte`: Minimum service radius
- `ordering`: Order by fields (business_name, years_of_experience, created_at)

**Example Request**:
```
GET /alistpros/profiles/?search=plumbing&years_of_experience__gte=5&ordering=business_name
```

**Response** (200 OK):
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/alistpros/profiles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "email": "contractor@example.com",
        "name": "John Pro",
        "phone_number": "+1234567890",
        "role": "contractor"
      },
      "business_name": "Elite Plumbing Services",
      "business_description": "Professional plumbing services...",
      "years_of_experience": 10,
      "license_number": "PL12345",
      "insurance_info": "Fully insured - Policy #ABC123",
      "service_radius": 50,
      "profile_image": "http://localhost:8000/media/alistpro_profiles/profile.jpg",
      "is_onboarded": true,
      "service_categories": [
        {
          "id": 1,
          "name": "Plumbing",
          "description": "Plumbing services"
        }
      ],
      "portfolio_items": [
        {
          "id": 1,
          "title": "Bathroom Renovation",
          "description": "Complete bathroom renovation...",
          "image": "http://localhost:8000/media/alistpro_portfolio/bathroom.jpg",
          "completion_date": "2024-01-10"
        }
      ],
      "reviews": [
        {
          "id": 1,
          "client": {
            "id": 3,
            "name": "Client Name"
          },
          "rating": 5,
          "comment": "Excellent service!",
          "is_verified": true,
          "created_at": "2024-01-15T10:30:00Z"
        }
      ],
      "average_rating": 4.8,
      "total_reviews": 15,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 2. Create Home Pro Profile
**Endpoint**: `POST /alistpros/profiles/create/`
**Description**: Create a new A-List Home Pro profile
**Permissions**: A-List Home Pros only

**Request Body**:
```json
{
  "business_name": "Elite Plumbing Services",
  "business_description": "Professional plumbing services with 10+ years experience",
  "years_of_experience": 10,
  "license_number": "PL12345",
  "insurance_info": "Fully insured - Policy #ABC123",
  "service_radius": 50,
  "service_categories": [1, 2, 3]
}
```

### 3. Update Home Pro Profile
**Endpoint**: `PUT /alistpros/profiles/update/`
**Description**: Update existing A-List Home Pro profile
**Permissions**: Profile owner only

**Request Body**: Same as create, but all fields optional

### 4. Get Service Categories
**Endpoint**: `GET /alistpros/services/`
**Description**: List all available service categories
**Permissions**: Public

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Plumbing",
    "description": "Professional plumbing services including repair, installation, and maintenance"
  },
  {
    "id": 2,
    "name": "Electrical",
    "description": "Licensed electrical services for residential and commercial properties"
  }
]
```

### 5. Portfolio Management
**Endpoint**: `GET /alistpros/portfolio/`
**Description**: List portfolio items for authenticated Home Pro
**Permissions**: Authenticated Home Pros

**Endpoint**: `POST /alistpros/portfolio/`
**Description**: Add new portfolio item
**Permissions**: Home Pro (owner)

**Request Body**:
```json
{
  "title": "Kitchen Renovation",
  "description": "Complete kitchen remodel with custom cabinets",
  "completion_date": "2024-01-15"
}
```
*Note: Include image file in multipart/form-data request*

### 6. Create Review
**Endpoint**: `POST /alistpros/profiles/<alistpro_id>/reviews/`
**Description**: Create a review for an A-List Home Pro
**Permissions**: Clients only

**Request Body**:
```json
{
  "rating": 5,
  "comment": "Excellent service! Very professional and completed work on time."
}
```

---

## Payment & Stripe Integration APIs

### 1. Stripe Onboarding
**Endpoint**: `POST /payments/onboard/`
**Description**: Initiate Stripe Connect onboarding for Home Pros
**Permissions**: A-List Home Pros only

**Response** (200 OK):
```json
{
  "account_link": "https://connect.stripe.com/setup/s/account_link_...",
  "stripe_account_id": "acct_1234567890",
  "onboarding_started": true
}
```

### 2. Check Stripe Account Status
**Endpoint**: `GET /payments/status/`
**Description**: Check Stripe Connect account status
**Permissions**: Authenticated users

**Response** (200 OK):
```json
{
  "has_account": true,
  "stripe_account_id": "acct_1234567890",
  "is_details_submitted": true,
  "is_charges_enabled": true,
  "is_payouts_enabled": true,
  "onboarding_complete": true,
  "onboarding_completed_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Payment
**Endpoint**: `POST /payments/create/`
**Description**: Create payment intent for service
**Permissions**: Clients only

**Request Body**:
```json
{
  "alistpro_id": 1,
  "amount": "150.00",
  "description": "Plumbing repair service"
}
```

**Response** (200 OK):
```json
{
  "payment_id": 1,
  "client_secret": "pi_1234567890_secret_..."
}
```

### 4. List Payments
**Endpoint**: `GET /payments/`
**Description**: List payments for authenticated user
**Permissions**: Authenticated users

**Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "client": {
        "id": 3,
        "name": "Client Name"
      },
      "alistpro": {
        "id": 1,
        "business_name": "Elite Plumbing Services"
      },
      "amount": "150.00",
      "description": "Plumbing repair service",
      "status": "completed",
      "stripe_payment_intent_id": "pi_1234567890",
      "completed_at": "2024-01-15T14:30:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 5. Stripe Dashboard Link
**Endpoint**: `GET /payments/dashboard-link/`
**Description**: Get link to Stripe Express dashboard
**Permissions**: A-List Home Pros only

**Response** (200 OK):
```json
{
  "url": "https://connect.stripe.com/express/dashboard/acct_1234567890"
}
```

---

## Messaging & Communication APIs

### 1. List Conversations
**Endpoint**: `GET /messaging/conversations/`
**Description**: List conversations for authenticated user
**Permissions**: Authenticated users

**Response** (200 OK):
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "participants": [
        {
          "id": 1,
          "name": "John Client",
          "role": "client"
        },
        {
          "id": 2,
          "name": "Jane Pro",
          "role": "contractor"
        }
      ],
      "title": "Plumbing Project Discussion",
      "last_message": {
        "id": 15,
        "sender": {
          "id": 2,
          "name": "Jane Pro"
        },
        "content": "I can start the project next Monday.",
        "created_at": "2024-01-15T14:30:00Z"
      },
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### 2. Create Conversation
**Endpoint**: `POST /messaging/conversations/`
**Description**: Start a new conversation
**Permissions**: Authenticated users

**Request Body**:
```json
{
  "participants": [2],
  "title": "Kitchen Renovation Project"
}
```

### 3. List Messages in Conversation
**Endpoint**: `GET /messaging/conversations/<conversation_id>/messages/`
**Description**: Get all messages in a conversation
**Permissions**: Conversation participants only

**Response** (200 OK):
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "sender": {
        "id": 1,
        "name": "John Client"
      },
      "content": "Hi, I'm interested in your plumbing services.",
      "read_by": [1, 2],
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "sender": {
        "id": 2,
        "name": "Jane Pro"
      },
      "content": "Hello! I'd be happy to help. What kind of plumbing work do you need?",
      "read_by": [1, 2],
      "created_at": "2024-01-15T10:15:00Z"
    }
  ]
}
```

### 4. Send Message
**Endpoint**: `POST /messaging/conversations/<conversation_id>/messages/`
**Description**: Send a message in a conversation
**Permissions**: Conversation participants only

**Request Body**:
```json
{
  "content": "I need help with a leaky faucet in my kitchen."
}
```

---

## Scheduling & Appointment APIs

### 1. List Appointments
**Endpoint**: `GET /scheduling/appointments/`
**Description**: List appointments for authenticated user
**Permissions**: Authenticated users

**Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "client": {
        "id": 3,
        "name": "John Client"
      },
      "contractor": {
        "id": 1,
        "business_name": "Elite Plumbing Services"
      },
      "service_category": {
        "id": 1,
        "name": "Plumbing"
      },
      "appointment_date": "2024-01-20",
      "start_time": "09:00:00",
      "end_time": "11:00:00",
      "status": "CONFIRMED",
      "notes": "Kitchen faucet repair",
      "location": "123 Main St, City, State",
      "estimated_cost": "150.00",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 2. Create Appointment
**Endpoint**: `POST /scheduling/appointments/`
**Description**: Book a new appointment
**Permissions**: Clients only

**Request Body**:
```json
{
  "contractor": 1,
  "service_category": 1,
  "appointment_date": "2024-01-20",
  "start_time": "09:00:00",
  "end_time": "11:00:00",
  "notes": "Kitchen faucet repair - urgent",
  "location": "123 Main St, City, State",
  "estimated_cost": "150.00"
}
```

### 3. Update Appointment
**Endpoint**: `PATCH /scheduling/appointments/<id>/`
**Description**: Update appointment details or status
**Permissions**: Appointment participants or admin

**Request Body**:
```json
{
  "status": "CONFIRMED",
  "notes": "Updated: Will need additional parts"
}
```

### 4. Availability Management
**Endpoint**: `GET /scheduling/availability-slots/`
**Description**: List contractor availability slots
**Permissions**: Authenticated users

**Endpoint**: `POST /scheduling/availability-slots/`
**Description**: Create availability slot
**Permissions**: Contractors only

**Request Body**:
```json
{
  "day_of_week": 1,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "is_recurring": true
}
```

---

## Data Models Reference

### User Model
- **Fields**: id, email, name, phone_number, role, stripe_account_id, is_verified, is_staff, is_active, email_verified, date_joined
- **Roles**: client, contractor, crew, specialist, admin
- **Relationships**: One-to-One with AListHomeProProfile (if contractor)

### AListHomeProProfile Model
- **Fields**: id, user, business_name, business_description, years_of_experience, license_number, insurance_info, service_radius, profile_image, is_onboarded
- **Relationships**: ManyToMany with ServiceCategory, OneToMany with Portfolio, Reviews

### Payment Model
- **Fields**: id, client, alistpro, amount, description, status, stripe_payment_intent_id, stripe_transfer_id, completed_at
- **Status Options**: pending, processing, completed, failed, refunded

### Appointment Model
- **Fields**: id, client, contractor, service_category, appointment_date, start_time, end_time, status, notes, location, estimated_cost
- **Status Options**: REQUESTED, CONFIRMED, COMPLETED, CANCELLED, RESCHEDULED

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error description",
  "details": {
    "field_name": ["Specific field error message"]
  },
  "status_code": 400
}
```

### Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **409**: Conflict (duplicate resource)
- **500**: Internal Server Error

---

## Code Examples

### Frontend Authentication Example (JavaScript)
```javascript
// Register a new user
const registerUser = async (userData) => {
  const response = await fetch('/api/users/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData)
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    return data;
  }
  throw new Error('Registration failed');
};

// Make authenticated API calls
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  };
  
  const response = await fetch(url, config);
  
  if (response.status === 401) {
    // Token expired, try to refresh
    await refreshToken();
    config.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`;
    return fetch(url, config);
  }
  
  return response;
};

// Search for contractors
const searchContractors = async (searchParams) => {
  const queryString = new URLSearchParams(searchParams).toString();
  const response = await fetch(`/api/alistpros/profiles/?${queryString}`);
  return response.json();
};
```

### Payment Integration Example
```javascript
// Initialize Stripe payment
const handlePayment = async (paymentData) => {
  // Create payment intent
  const response = await makeAuthenticatedRequest('/api/payments/create/', {
    method: 'POST',
    body: JSON.stringify(paymentData)
  });
  
  const { client_secret } = await response.json();
  
  // Confirm payment with Stripe
  const { error } = await stripe.confirmCardPayment(client_secret, {
    payment_method: {
      card: cardElement,
      billing_details: {
        name: 'Customer Name',
      },
    }
  });
  
  if (error) {
    console.error('Payment failed:', error);
  } else {
    console.log('Payment succeeded!');
  }
};
```

### Real-time Messaging Example
```javascript
// Send message in conversation
const sendMessage = async (conversationId, content) => {
  const response = await makeAuthenticatedRequest(
    `/api/messaging/conversations/${conversationId}/messages/`, 
    {
      method: 'POST',
      body: JSON.stringify({ content })
    }
  );
  return response.json();
};

// Poll for new messages (or use WebSocket in production)
const pollMessages = async (conversationId) => {
  const response = await makeAuthenticatedRequest(
    `/api/messaging/conversations/${conversationId}/messages/`
  );
  return response.json();
};
```

---

## Utility Functions & Helper Classes

### Payment Utilities (`payments/utils.py`)

#### `create_stripe_account(user)`
Creates a Stripe Connect Express account for an A-List Home Pro.

**Parameters**:
- `user`: User instance (must be A-List Home Pro role)

**Returns**: `AListHomeProStripeAccount` instance

**Example**:
```python
from payments.utils import create_stripe_account

# Create Stripe account for Home Pro
stripe_account = create_stripe_account(user)
print(f"Created account: {stripe_account.stripe_account_id}")
```

#### `generate_account_link(stripe_account, refresh_url, return_url)`
Generates onboarding link for Stripe Connect Express account.

**Parameters**:
- `stripe_account`: AListHomeProStripeAccount instance
- `refresh_url`: URL for link expiration redirect
- `return_url`: URL for onboarding completion redirect

**Returns**: Account link URL string

#### `create_payment_intent(client, alistpro, amount, description)`
Creates a payment intent for client-to-pro payments.

**Parameters**:
- `client`: Client user instance
- `alistpro`: AListHomeProProfile instance
- `amount`: Payment amount (Decimal)
- `description`: Payment description string

**Returns**: Stripe PaymentIntent object

**Example**:
```python
from payments.utils import create_payment_intent

payment_intent = create_payment_intent(
    client=client_user,
    alistpro=pro_profile,
    amount=150.00,
    description="Plumbing repair service"
)
```

#### `handle_account_updated_webhook(event_data)`
Processes Stripe account.updated webhook events.

**Parameters**:
- `event_data`: Stripe webhook event data

**Returns**: Updated AListHomeProStripeAccount instance or None

#### `get_stripe_dashboard_link(stripe_account_id)`
Generates Stripe Express dashboard link for Home Pros.

**Parameters**:
- `stripe_account_id`: Stripe account ID string

**Returns**: Dashboard URL string

### Custom Permission Classes (`users/permissions.py`)

#### `IsAdmin`
Restricts access to admin users only.

**Usage**:
```python
from users.permissions import IsAdmin

class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]
```

#### `IsAListHomePro`
Restricts access to A-List Home Pro users only.

#### `IsClient`
Restricts access to client users only.

#### `IsCrew`
Restricts access to crew member users only.

#### `IsSpecialist`
Restricts access to specialist users only.

#### `IsOwnerOrAdmin`
Object-level permission for resource owners or admins.

**Usage**:
```python
from users.permissions import IsOwnerOrAdmin

class ProfileUpdateView(UpdateAPIView):
    permission_classes = [IsOwnerOrAdmin]
    
    def get_object(self):
        return self.request.user.alistpro_profile
```

### Core Models (`core/models.py`)

#### `TimeStampedModel`
Abstract base model providing automatic timestamp fields.

**Fields**:
- `created_at`: Auto-set on creation
- `updated_at`: Auto-updated on save

**Usage**:
```python
from core.models import TimeStampedModel

class MyModel(TimeStampedModel):
    name = models.CharField(max_length=100)
    # Automatically gets created_at and updated_at fields
```

#### `Address`
Model for storing user address information.

**Fields**:
- `street_address`, `city`, `state`, `zip_code`, `country`
- `is_primary`: Boolean for primary address
- `user`: Foreign key to user

### Email Verification (`users/email_verification.py`)

#### `send_verification_email(user)`
Sends email verification to newly registered users.

**Parameters**:
- `user`: User instance to send verification to

#### `verify_email_token(token, user_id)`
Verifies email verification token.

**Parameters**:
- `token`: Verification token string
- `user_id`: User ID string

**Returns**: Boolean indicating verification success

### Filtering Classes

#### `AListHomeProFilter` (`alistpros_profiles/filters.py`)
Django Filter class for filtering Home Pro profiles.

**Filterable Fields**:
- `service_categories`: Filter by service category IDs
- `years_of_experience__gte`: Minimum experience filter
- `service_radius__gte`: Minimum service radius filter
- `is_onboarded`: Filter by onboarding status

**Usage**:
```python
# In view
filter_backends = [DjangoFilterBackend]
filterset_class = AListHomeProFilter

# In API call
GET /alistpros/profiles/?service_categories=1,2&years_of_experience__gte=5
```

---

## Testing Utilities

### Test Data Creation (`create_fake_data.py`)
Comprehensive script for generating test data across all models.

**Creates**:
- Users with different roles
- Service categories
- Home Pro profiles with portfolios
- Appointments and availability
- Messages and conversations
- Payment records

**Usage**:
```bash
python create_fake_data.py
```

### API Endpoint Testing (`test_api_endpoints.py`)
Script for testing all API endpoints with different user roles.

**Features**:
- Tests authentication endpoints
- Validates role-based permissions
- Tests CRUD operations
- Checks error handling

**Usage**:
```bash
python test_api_endpoints.py
```

---

## Environment Configuration

### Required Environment Variables
```bash
# Django Configuration
SECRET_KEY=your_secret_key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database_name

# Stripe Integration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# URLs
SITE_URL=https://your-backend-domain.com
FRONTEND_URL=https://your-frontend-domain.com

# Platform Configuration
PLATFORM_FEE_PERCENTAGE=0.10  # 10% platform fee
```

### Settings Configuration
Key Django settings for the platform:

```python
# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 10,
}
```

---

## WebSocket Support (Future Enhancement)

The platform is designed to support real-time features via WebSocket integration:

### Planned WebSocket Events
- `message.new`: Real-time message notifications
- `appointment.updated`: Appointment status changes
- `payment.completed`: Payment completion notifications
- `notification.new`: System notifications

### Implementation Guide
```python
# consumers.py (future implementation)
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            f"user_{self.scope['user'].id}",
            self.channel_name
        )
        await self.accept()
    
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'data': event['data']
        }))
```

---

## Performance Considerations

### Database Optimization
- Use `select_related()` for foreign key relationships
- Use `prefetch_related()` for many-to-many relationships
- Implement database indexing for frequently queried fields

### Caching Strategy
```python
# Example caching for Home Pro profiles
from django.core.cache import cache

def get_featured_alistpros():
    cache_key = 'featured_alistpros'
    featured = cache.get(cache_key)
    
    if not featured:
        featured = AListHomeProProfile.objects.filter(
            is_onboarded=True
        ).select_related('user').prefetch_related(
            'service_categories', 'reviews'
        )[:10]
        cache.set(cache_key, featured, 300)  # 5 minutes
    
    return featured
```

### API Rate Limiting
Implement rate limiting for API endpoints:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def register_view(request):
    # Registration logic
    pass
```

---

## Security Best Practices

### Input Validation
- All user inputs validated through DRF serializers
- Custom validation methods for business logic
- File upload restrictions and validation

### Authentication Security
- JWT tokens with expiration
- Secure password hashing with Django's built-in functions
- Email verification for new accounts

### API Security
- CORS configuration for frontend domains
- CSRF protection enabled
- Sensitive data excluded from API responses

### Payment Security
- Stripe-managed payment processing
- No storage of sensitive payment data
- Webhook signature verification

---

## Postman Collection

The project includes a comprehensive Postman collection (`postman_collection.json`) with pre-configured API requests for testing all endpoints.

### Collection Features
- **Authentication flows**: Register, login, token refresh, logout
- **User management**: Profile creation and updates
- **A-List Home Pro operations**: Profile management, service categories
- **Payment processing**: Stripe onboarding, payment creation
- **Messaging**: Conversation and message management
- **Scheduling**: Appointment booking and management
- **Admin operations**: User management and analytics

### Environment Variables
Configure these variables in Postman:
```json
{
  "base_url": "http://localhost:8000",
  "access_token": "your_jwt_access_token",
  "refresh_token": "your_jwt_refresh_token"
}
```

### Import Instructions
1. Open Postman
2. Click "Import" button
3. Select `postman_collection.json` from project root
4. Configure environment variables
5. Start testing API endpoints

---

## Interactive API Documentation

The platform provides multiple ways to explore and test the APIs:

### Swagger UI
- **URL**: `http://localhost:8000/api/swagger/`
- **Features**: Interactive API explorer, request/response examples, authentication testing
- **Best for**: API exploration and one-off testing

### ReDoc
- **URL**: `http://localhost:8000/api/redoc/`
- **Features**: Clean documentation format, detailed schema information
- **Best for**: API reference and documentation reading

### Django Admin
- **URL**: `http://localhost:8000/admin/`
- **Features**: Direct database manipulation, user management, data inspection
- **Best for**: Administrative tasks and data management

---

## Quick Start Guide

### For Developers
1. **Set up environment**: Follow README.md setup instructions
2. **Create test data**: Run `python create_fake_data.py`
3. **Test APIs**: Import Postman collection or use Swagger UI
4. **Explore code**: Review this documentation and source code

### For Frontend Developers
1. **Authentication**: Implement JWT token management
2. **API Integration**: Use provided endpoints for data operations
3. **Real-time features**: Plan for WebSocket integration
4. **Error handling**: Implement proper error response handling

### For A-List Home Pros
1. **Registration**: Sign up with contractor role
2. **Profile setup**: Complete business profile information
3. **Stripe onboarding**: Connect payment account
4. **Service management**: Add portfolio items and set availability

### For Clients
1. **Registration**: Sign up with client role
2. **Search professionals**: Browse and filter A-List Home Pros
3. **Book services**: Schedule appointments and communicate
4. **Payment**: Secure payment processing through Stripe

---

## Support and Maintenance

### Logging and Monitoring
- Comprehensive logging for payment operations
- Error tracking for Stripe webhooks
- User activity monitoring for security

### Database Maintenance
```python
# Regular maintenance tasks
python manage.py clearsessions  # Clear expired sessions
python manage.py collectstatic  # Update static files
python manage.py check --deploy  # Security checks
```

### Backup Procedures
- Regular database backups for user data and transactions
- Media file backups for uploaded content
- Environment configuration backups

---

This comprehensive documentation covers all public APIs, utility functions, helper classes, and implementation details for the A-List Home Professionals platform. For additional examples or clarification on specific components, refer to:

- **Interactive API Documentation**: `/api/swagger/` (development server)
- **Postman Collection**: `postman_collection.json` (comprehensive testing)
- **Source Code**: Individual app directories for implementation details
- **Admin Interface**: `/admin/` (data management and inspection)
# A-List Home Pros

A secure contractor-client matching platform that connects homeowners with qualified contractors, specialists, and service providers. The system features role-based authentication, messaging, scheduling, payments via Stripe Connect, and comprehensive contractor profiles.

## 🏗️ Project Structure

```
List Home Professionals LLC/
├── server/                   # Django backend
│   ├── venv/                 # Python virtual environment
│   ├── alistpros/            # Django project configuration
│   ├── core/                 # Shared utils, constants, base models
│   ├── users/                # Custom user model, auth logic, role permissions
│   ├── contractors/          # Contractor profiles, portfolios, and reviews
│   ├── payments/             # Stripe Connect, payment APIs, webhooks
│   ├── messaging/            # Conversations and messages between users
│   ├── scheduling/           # Availability, appointments, and booking
│   ├── notifications/        # User notifications and email/SMS verification
│   ├── analytics/            # Reporting and analytics (future)
│   ├── leads/                # Lead generation and matching (future)
│   ├── manage.py             # Django management script
│   ├── .env                  # Environment variables
│   ├── requirements.txt      # Python dependencies
│   ├── create_fake_data.py   # Script to generate test data
│   ├── fix_email_verification.py # Script to fix email verification
│   ├── show_verification_codes.py # Script to display verification codes
│   ├── reset_passwords.py    # Script to reset user passwords
│   └── test_api_endpoints.py # Script to test API endpoints
└── client/                   # Next.js frontend (to be implemented)
```

## 🔑 Key Features

### 👤 User Authentication & Role Management
- Custom user model with JWT authentication
- Role-based access control (Client, Contractor, Crew, Specialist, Admin)
- Secure password handling and validation
- Token-based authentication with refresh capabilities
- Email and SMS verification for users

### 👷 Contractor Management
- Detailed contractor profiles with business information
- Service categories for classification
- Portfolio management for showcasing work
- Review and rating system
- Geographic service radius
- Verification and approval workflow

### 📅 Scheduling System
- Contractor availability management (recurring slots)
- Unavailable date blocking
- Appointment booking and management
- Appointment status workflow (requested, confirmed, completed, cancelled)
- Notes and private comments on appointments

### 💬 Messaging System
- Real-time conversations between clients and contractors
- Message tracking with read status
- Conversation history and organization
- File and image sharing (future)

### 🔔 Notification System
- In-app notifications for important events
- Email notifications with templates
- SMS notifications and verification
- Notification preferences and settings

### 💳 Payment Processing
- Stripe Connect Express integration for contractor onboarding
- Secure payment processing between clients and contractors
- Platform fee handling (escrow-style payments)
- Webhook handling for payment events
- Payment status tracking

### 🔒 Security Features
- Environment variable management with python-decouple
- CORS protection for API endpoints
- Role-based permissions for all operations
- JWT token authentication with refresh capabilities
- Input validation with serializers

### 📚 API Documentation
- Swagger/OpenAPI documentation
- RESTful API design
- Comprehensive endpoint documentation

### 🎨 User Interface
- Customizable color scheme with centralized theme management
- Responsive design for all screen sizes (mobile, tablet, desktop)
- Reusable UI components (buttons, cards, inputs, tables, modals)
- Role-based navigation with dynamic sidebar and navbar
- Accessible UI components following WCAG guidelines
- Modern and professional design language
- Interactive tables with sorting, filtering, and pagination
- Form components with validation and error handling

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: High-level Python web framework
- **Django REST Framework 3.14.0**: Toolkit for building Web APIs
- **PostgreSQL**: Production-ready relational database system
- **SimpleJWT**: JWT authentication for Django REST Framework
- **Stripe API**: Payment processing and Connect Express
- **drf-yasg**: Swagger/OpenAPI documentation generator
- **drf-nested-routers**: Nested routing for related resources
- **python-decouple**: Environment variable management
- **Faker**: Library for generating fake data for testing

### Frontend
- **Next.js**: React framework for production with App Router
- **React**: JavaScript library for building user interfaces
- **TypeScript**: Typed JavaScript for better developer experience
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Stripe.js**: Client-side payment processing
- **Axios**: Promise-based HTTP client for API requests
- **Class Variance Authority**: Creating variant components with TypeScript support
- **Headless UI**: Unstyled, accessible UI components
- **React Hook Form**: Form validation and handling
- **Zod**: TypeScript-first schema validation
- **React Query**: Data fetching and state management
- **JWT Authentication**: Custom JWT authentication implementation

## 🚀 Setup and Installation Guide

### Frontend (Next.js)

#### Initial Setup

1. Navigate to the client directory:
   ```
   cd client
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Install additional required packages:
   ```
   npm install axios class-variance-authority clsx tailwind-merge @headlessui/react react-hook-form zod @hookform/resolvers
   ```

#### Development Server

4. Start the development server:
   ```
   npm run dev
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

#### Building for Production

6. Build the production version:
   ```
   npm run build
   ```

7. Start the production server:
   ```
   npm run start
   ```

#### Environment Variables

8. Create a `.env.local` file in the client directory with the following variables:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   ```

### Backend (Django)

#### Initial Setup

1. Clone the repository (if not already done):
   ```
   git clone <repository-url>
   cd "List Home Professionals LLC"
   ```

2. Navigate to the server directory:
   ```
   cd server
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. Create or update the `.env` file with the following variables:
   ```
   SECRET_KEY=django-insecure-z0yk!o2h=81=di$agvixrz4x*3_=4c7b3s8%1cl-5we_m$i*=n
   DEBUG=True
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/a_list_home_pros?schema=public
   ALLOWED_HOSTS=localhost,127.0.0.1
   #STRIPE_SECRET_KEY=your_stripe_secret_key
   #STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   #STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   ```
   
   Note: Replace `your_password` with your actual PostgreSQL password.

#### Installation and Configuration

6. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   If you encounter issues, install core packages individually:
   ```
   pip install Django==4.2.7
   pip install djangorestframework==3.14.0
   pip install djangorestframework-simplejwt==5.3.0
   pip install django-cors-headers==4.3.0
   pip install drf-yasg==1.21.7
   pip install stripe==6.0.0
   pip install python-decouple==3.8
   pip install drf-nested-routers
   pip install faker
   ```

7. Create a static directory for static files:
   ```
   mkdir static
   ```

8. Generate migrations for all apps:
   ```
   python manage.py makemigrations users core contractors payments messaging scheduling notifications analytics
   ```

9. Apply migrations to set up the database:
   ```
   python manage.py migrate
   ```

#### Creating Test Data

10. Create a superuser (admin account):
    ```
    python manage.py createsuperuser
    ```
    - Email: `admin@alistpros.com`
    - Name: `Admin User`
    - Phone: `1234567890`
    - Password: `admin123`

11. Generate comprehensive test data:
    ```
    python create_fake_data.py
    ```
    This script will create:
    - Users with different roles (clients, contractors, crew, specialists)
    - Contractor profiles with service categories
    - Portfolio items for contractors
    - Reviews for contractors
    - Availability schedules
    - Appointments between clients and contractors
    - Conversations and messages
    - Notifications
    - Email verification tokens

12. Fix email verification and generate verification codes:
    ```
    python fix_email_verification.py
    ```

13. Reset passwords for all users (if needed):
    ```
    python reset_passwords.py
    ```
    This sets passwords based on user roles:
    - Admin: `admin123`
    - Client: `client123`
    - Contractor: `contractor123`
    - Crew: `crew123`
    - Specialist: `specialist123`

#### Running the Server

14. Start the development server:
    ```
    python manage.py runserver
    ```

15. Access the application:
    - Admin panel: http://localhost:8000/admin/
    - API documentation: http://localhost:8000/api/swagger/
    - API endpoints: http://localhost:8000/api/

16. Test API endpoints:
    ```
    python test_api_endpoints.py
    ```
    This script tests various API endpoints to ensure they are working correctly.

### Frontend (Next.js) - To be implemented

1. Navigate to the client directory:
   ```
   cd ../client
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Access the frontend application:
   - http://localhost:3000/

## 📡 API Endpoints

### Authentication
- `POST /api/users/register/` - Register a new user with role
- `POST /api/users/token/` - Get JWT access and refresh tokens
- `POST /api/users/token/refresh/` - Refresh JWT token
- `GET /api/users/me/` - Get current user profile
- `POST /api/users/change-password/` - Change user password
- `GET /api/users/verify-email/<token>/<user_id>/` - Verify user email

### Contractor Management
- `GET /api/contractors/profiles/` - List all contractor profiles
- `GET /api/contractors/profiles/{id}/` - Get contractor profile details
- `POST /api/contractors/create/` - Create contractor profile
- `PUT /api/contractors/update/` - Update contractor profile
- `GET /api/contractors/categories/` - List service categories

### Portfolio Management
- `GET /api/contractors/{contractor_id}/portfolio/` - List contractor portfolio items
- `POST /api/contractors/{contractor_id}/portfolio/` - Add portfolio item
- `GET /api/contractors/portfolio/{id}/` - Get portfolio item details
- `PUT /api/contractors/portfolio/{id}/` - Update portfolio item
- `DELETE /api/contractors/portfolio/{id}/` - Delete portfolio item

### Reviews
- `POST /api/contractors/{contractor_id}/reviews/` - Create review for contractor

### Scheduling
- `GET /api/scheduling/availability-slots/` - List availability slots
- `POST /api/scheduling/availability-slots/` - Create availability slot
- `GET /api/scheduling/availability-slots/{id}/` - Get availability slot details
- `PUT /api/scheduling/availability-slots/{id}/` - Update availability slot
- `DELETE /api/scheduling/availability-slots/{id}/` - Delete availability slot
- `GET /api/scheduling/unavailable-dates/` - List unavailable dates
- `POST /api/scheduling/unavailable-dates/` - Create unavailable date
- `GET /api/scheduling/appointments/` - List appointments
- `POST /api/scheduling/appointments/` - Create appointment
- `GET /api/scheduling/appointments/{id}/` - Get appointment details
- `PUT /api/scheduling/appointments/{id}/` - Update appointment
- `POST /api/scheduling/appointments/{id}/notes/` - Add note to appointment

### Messaging
- `GET /api/messaging/conversations/` - List conversations
- `POST /api/messaging/conversations/` - Create conversation
- `GET /api/messaging/conversations/{id}/` - Get conversation details
- `GET /api/messaging/conversations/{conversation_id}/messages/` - List messages in conversation
- `POST /api/messaging/conversations/{conversation_id}/messages/` - Send message in conversation

### Notifications
- `GET /api/notifications/notifications/` - List notifications
- `PUT /api/notifications/notifications/{id}/` - Mark notification as read
- `GET /api/notifications/settings/` - Get notification settings
- `PUT /api/notifications/settings/` - Update notification settings
- `POST /api/notifications/sms/` - Send SMS verification code

### Payments
- `POST /api/payments/onboard/` - Start Stripe Connect onboarding
- `GET /api/payments/status/` - Check onboarding status
- `POST /api/payments/create/` - Create payment intent
- `GET /api/payments/` - List user payments
- `GET /api/payments/{id}/` - Get payment details

### Admin
- `GET /api/users/admin/users/` - List all users
- `GET /api/users/admin/users/{id}/` - Get user details
- `PUT /api/users/admin/users/{id}/` - Update user details
- `GET /api/contractors/admin/pending/` - List pending contractors

## 🔄 Data Flow

### User Registration and Authentication Flow
1. User registers with email, name, phone, password, and role
2. System creates user account and sends verification email
3. User verifies email by clicking link in email
4. User logs in with email and password
5. System returns JWT tokens for authentication
6. User includes token in Authorization header for subsequent requests

### Contractor Onboarding Flow
1. Contractor registers with contractor role
2. Contractor creates profile with business information
3. Contractor adds portfolio items to showcase work
4. Contractor sets availability schedule
5. Admin reviews and approves contractor profile
6. Contractor connects Stripe account for payments
7. Contractor profile becomes visible to clients

### Appointment Booking Flow
1. Client searches for contractors by service category
2. Client views contractor profiles, portfolios, and reviews
3. Client selects contractor and views availability
4. Client requests appointment for specific date/time
5. Contractor receives notification of appointment request
6. Contractor confirms or rejects appointment
7. Client receives notification of appointment status
8. If confirmed, appointment is added to both users' schedules

### Messaging Flow
1. User initiates conversation with another user
2. System creates conversation and adds both users as participants
3. User sends message in conversation
4. Recipient receives notification of new message
5. Recipient views and responds to message
6. System tracks read status of messages

### Payment Flow
1. Client initiates payment for service
2. System creates payment intent with Stripe
3. Client completes payment on frontend
4. Stripe webhooks notify system of payment status
5. System updates payment status and notifies users
6. Funds are held in escrow until service is completed
7. After service completion, funds are transferred to contractor minus platform fee

## 🧪 Testing

### API Testing
Test API endpoints with the included script:

```
python test_api_endpoints.py
```

This script tests all major API endpoints with different user roles to ensure proper functionality and permissions.

### Manual Testing
Use the Swagger UI at `/api/swagger/` to manually test API endpoints.

## 🚨 Common Issues and Solutions

### Issue: Database Migration Errors
**Solution:**
```
python manage.py makemigrations
python manage.py migrate --fake-initial
python manage.py migrate
```

### Issue: Email Verification Table Missing Columns
**Solution:**
```
python fix_email_verification.py
```

### Issue: Authentication Failures
**Solution:**
```
python reset_passwords.py
```
Then use the role-based passwords (admin123, client123, contractor123, etc.)

### Issue: Missing Static Files
**Solution:**
```
mkdir static
python manage.py collectstatic
```

### Issue: API Endpoint Not Found
**Solution:**
Check URL patterns in the respective app's `urls.py` file and ensure the endpoint is properly registered.

### Issue: Permission Denied for API Endpoint
**Solution:**
Verify that the user has the correct role and permissions for the requested action. Check the permission classes in the view.

## 📝 Development Guidelines

1. **Code Style**: Follow PEP 8 guidelines for Python code.
2. **API Design**: Follow RESTful principles for API endpoints.
3. **Security**: Never hardcode sensitive information; use environment variables.
4. **Documentation**: Document all API endpoints with docstrings and Swagger.
5. **Testing**: Write tests for all new features and bug fixes.

## 🔐 Login Credentials

### Admin User
- Email: `admin@alistpros.com`
- Password: `admin123`

### Test Users (after running create_fake_data.py)
- Client: `client1@example.com` / `client123`
- Contractor: `contractor1@example.com` / `contractor123`
- Crew: `crew1@example.com` / `crew123`
- Specialist: `specialist1@example.com` / `specialist123`

## 📚 Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Stripe API: https://stripe.com/docs/api
- JWT Authentication: https://django-rest-framework-simplejwt.readthedocs.io/

## 📅 Future Enhancements

1. Real-time notifications using WebSockets
2. Mobile app using React Native
3. Advanced search and filtering for contractors
4. Contractor ranking and recommendation system
5. Integration with home service marketplaces
6. Client loyalty and referral program

pip install -r requirements.txt
pip install djangorestframework djangorestframework-simplejwt django-cors-headers drf-yasg stripe
mkdir static
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
pip install drf-nested-routers

python manage.py makemigrations 
pip install faker
python -m pip install faker
python manage.py create_test_data --clients 10 --contractors 20
python get_verification_codes.py
python create_fake_data.py
python manage.py check
python create_fake_data.py --help
python create_initial_data.py
```

admin@alistpros.com
Password: admin123

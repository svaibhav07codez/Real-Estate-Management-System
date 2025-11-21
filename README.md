# Real Estate Database Management System

## Project Overview

A comprehensive web-based Real Estate Database Management System built with Django and MySQL. This application facilitates property listings, client management, agent operations, appointment scheduling, and transaction tracking for the real estate industry.

### Developed By
- **Group Members:** Vaibhav Sankaran, Gangatharan Idayachandiran
- **Course:** CS 5200 - Database Management Systems
- **Institution:** Northeastern University
- **Semester:** Fall 2025

---

## Project Purpose

This system serves as a central platform for managing all aspects of real estate operations, from property listing to final sale or rental. It demonstrates the practical application of database design principles, normalization techniques, and full-stack web development.

### Key Features
- Multi-user role management (Admin, Agent, Client)
- Complete CRUD operations for properties, appointments, transactions, and reviews
- Advanced property search with multiple filters
- Automated commission calculations
- Real-time appointment scheduling
- Property image management
- Review and rating system
- Comprehensive analytics dashboard

---

## System Architecture

### Technology Stack

**Backend:**
- **Framework:** Django 4.2
- **Language:** Python 3.8+
- **Database:** MySQL 8.0+
- **ORM:** Django ORM

**Frontend:**
- **Templates:** Django Template Engine
- **Styling:** Bootstrap 5
- **Icons:** Bootstrap Icons
- **Forms:** django-crispy-forms with Bootstrap 5

**Database Connector:**
- PyMySQL (MySQL database adapter)

---

## Database Design

### Database Schema

The system uses a **normalized relational database** with 10 main tables:

1. **Users** - Base user authentication and information
2. **Agents** - Real estate agent profiles
3. **Clients** - Property buyer/renter profiles
4. **Properties** - Property listings with detailed information
5. **Locations** - Physical addresses and geographic data
6. **PropertyTypes** - Property categorization
7. **PropertyImages** - Multiple images per property
8. **Appointments** - Property viewing schedules
9. **Transactions** - Sales and rental records
10. **Reviews** - Property and agent feedback

### Normalization
All tables are normalized to **Third Normal Form (3NF)**:
- No partial dependencies
- No transitive dependencies
- Minimal data redundancy

### Database Programming Objects

**Stored Procedures (3):**
- `sp_create_property` - Create new property listings with transaction handling
- `sp_schedule_appointment` - Schedule appointments with conflict checking
- `sp_complete_transaction` - Process sales/rentals with automatic commission calculation

**User-Defined Functions (3):**
- `fn_price_per_sqft()` - Calculate price per square foot for properties
- `fn_agent_total_commission()` - Calculate total commission earned by an agent
- `fn_avg_price_by_city()` - Get average property price for a city

**Triggers (3):**
- `tr_update_agent_rating` - Automatically update agent ratings when reviews are added
- `tr_check_property_delete` - Prevent deletion of properties with active appointments
- `tr_cancel_appointments_on_status_change` - Auto-cancel appointments when property status changes

**Views (2):**
- `vw_available_properties` - Comprehensive view of available properties
- `vw_agent_performance` - Agent performance metrics

---

## Installation & Setup

### Prerequisites

Before starting, ensure you have the following installed:
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Virtual environment support

### Step 1: Clone or Download Project

```bash
# Navigate to your desired directory
cd Desktop

# Create project folder
mkdir real_estate_project
cd real_estate_project
```

### Step 2: Set Up Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your command prompt.

### Step 3: Install Required Packages

```bash
pip install django==4.2
pip install pymysql
pip install python-dotenv
pip install pillow
pip install django-crispy-forms
pip install crispy-bootstrap5
```

### Step 4: Database Setup

#### 4.1 Import Database Schema

**Option A - Using MySQL Workbench:**
1. Open MySQL Workbench
2. Connect to your MySQL server
3. File → Run SQL Script
4. Select `real_estate_schema.sql`
5. Click "Run"

**Option B - Using Command Line:**
```bash
mysql -u root -p < real_estate_schema.sql
# Enter your MySQL root password when prompted
```

#### 4.2 Add Required Columns

The Django User model requires additional columns. Run this in MySQL:

```sql
USE real_estate_db;

-- Add Django-required fields
ALTER TABLE Users 
ADD COLUMN last_login DATETIME NULL,
ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE,
ADD COLUMN is_staff BOOLEAN DEFAULT FALSE,
ADD COLUMN date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN username VARCHAR(150) NULL UNIQUE;

-- Set username to email for existing users
UPDATE Users SET username = email WHERE username IS NULL;
```

### Step 5: Configure Django Project

#### 5.1 Create .env File

Create a file named `.env` in the project root:

```env
DB_NAME=real_estate_db
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=django-insecure-change-this-key
DEBUG=True
```

**Important:** Replace `your_mysql_password_here` with your actual MySQL password.

#### 5.2 Configure PyMySQL

Open `manage.py` and add these lines at the very top:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Step 6: Run Migrations

```bash
python manage.py migrate
```

This creates Django's system tables (sessions, admin, etc.).

## Step 7 is optional since we have a dummy user created for admin/superuser, client, and agent roles. Credentials are below:

Superuser/admin - superuser@realestate.com, admin123
Client - client@realestate.com, client123
Agent - agent@realestate.com, agent123

### Step 7: Create Superuser 

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

After creating the superuser, update the database:

```sql
USE real_estate_db;

UPDATE Users 
SET is_superuser = TRUE, 
    is_staff = TRUE,
    user_type = 'admin'
WHERE email = 'your_superuser_email@example.com';
```

Set the password properly:

```bash
python manage.py shell
```

```python
from properties.models import User
from django.contrib.auth.hashers import make_password

user = User.objects.get(email='your_superuser_email@example.com')
user.password = make_password('your_password')
user.save()
exit()
```

### Step 8: Add Static Files

Place property images in the `static/images/` folder. The project expects these image files:
- `prop1_exterior.jpg`
- `prop2_exterior.jpg`
- `prop3_exterior.jpg`
- etc.

### Step 9: Run the Server

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

---

## Running the Application

### Starting the Application

Every time you want to run the application:

1. **Navigate to project directory:**
   ```bash
   cd path/to/real_estate_project
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

4. **Access the application:**
   - Homepage: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`
   - Analytics Dashboard: `http://127.0.0.1:8000/analytics/`

### Stopping the Application

Press **Ctrl+C** in the terminal to stop the server.

---

## User Roles & Functionality

### Admin Users
- Access Django admin panel
- View system-wide statistics and analytics
- Access comprehensive analytics dashboard
- Manage all users, properties, and transactions
- Monitor system performance
- Generate analytics reports
- View market insights and trends

### Agent Users
- Create and manage property listings
- Update property information and status
- Schedule and manage appointments
- Create transactions (sales/rentals)
- View performance metrics and analytics
- Track commission earnings
- Access analytics dashboard for market insights

### Client Users
- Browse and search properties
- Schedule property viewings
- Manage appointments
- Write reviews for properties and agents
- Track viewing history
- Update preferences and budget

---

## Application Features

### 1. Property Management (CRUD)

**Create:**
- Agents can list new properties
- Input comprehensive property details
- Add multiple images
- Set pricing and availability

**Read:**
- Browse all available properties
- Advanced search with filters:
  - Price range
  - Location (city, zip code)
  - Property type
  - Number of bedrooms/bathrooms
  - Listing type (sale/rent)
- View detailed property information
- See property images in carousel

**Update:**
- Agents can modify their listings
- Update prices and descriptions
- Change property status
- Add/remove images

**Delete:**
- Agents can remove their properties
- System prevents deletion if active appointments exist

### 2. Appointment Management (CRUD)

**Create:**
- Clients schedule property viewings
- Select date and time
- Add special requests/notes
- System checks for scheduling conflicts

**Read:**
- View all scheduled appointments
- Filter by status (scheduled, completed, cancelled)
- See appointment details and notes

**Update:**
- Change appointment status
- Add notes after viewing
- Reschedule appointments

**Delete:**
- Cancel appointments
- Automatic cancellation when property status changes

### 3. Transaction Management (CRUD)

**Create:**
- Agents complete sales/rentals
- System automatically calculates commission
- Update property status to sold/rented
- Record payment information

**Read:**
- View transaction history
- Filter by type (sale/rental)
- See commission details
- Track payment status

### 4. Review System (CRUD)

**Create:**
- Clients write reviews
- Rate properties (1-5 stars)
- Rate agents
- Provide detailed feedback

**Read:**
- View all reviews
- See average ratings
- Filter reviews by property or agent

**Delete:**
- Users can delete their own reviews
- Admins can moderate reviews

### 5. User Profile Management

**Clients:**
- Set budget preferences
- Specify desired locations
- Indicate purchase/rental intent
- Update contact preferences

**Agents:**
- Update license information
- Manage agency details
- Set commission rates
- Track performance metrics

### 6. Search & Filtering

**Property Search:**
- Keyword search (title, city, description)
- Multi-filter search with:
  - Price range (min/max)
  - Location (city)
  - Property type
  - Number of bedrooms
  - Listing type (sale/rent)
  - Status (available, pending, sold, rented)
- Sort by price, date, location
- Real-time search results

### 7. Analytics Dashboard

**System-wide Analytics** (Admin/Agent access):
- **Key Metrics:**
  - Total properties in system
  - Available properties count
  - Sold properties count
  - Average property price
- **Properties by Type:**
  - Distribution across property types
  - Count and percentage breakdown
- **Geographic Analysis:**
  - Top cities by property count
  - City-wise distribution
- **Price Distribution:**
  - Average prices by location
  - Market pricing insights
- **Property Status Overview:**
  - Visual breakdown of all statuses
  - Available, pending, sold, rented counts
- **Market Insights:**
  - Most popular property type
  - Most active city
  - Market availability percentage

---

## Project Structure

```
real_estate_project/
├── venv/                          # Virtual environment
├── real_estate_system/            # Main project settings
│   ├── __init__.py
│   ├── settings.py               # Django configuration
│   ├── urls.py                   # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
├── properties/                    # Main application
│   ├── migrations/               # Database migrations
│   ├── __init__.py
│   ├── admin.py                  # Admin interface config
│   ├── apps.py
│   ├── backends.py               # Custom authentication
│   ├── models.py                 # Database models (ORM)
│   ├── views.py                  # Business logic (26 views)
│   ├── urls.py                   # App URL routing
│   ├── forms.py                  # Form definitions
│   └── tests.py
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── home.html                 # Homepage
│   ├── registration/             # Auth templates
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/                # Dashboard templates
│   │   ├── client_dashboard.html
│   │   ├── agent_dashboard.html
│   │   └── admin_dashboard.html
│   ├── properties/               # Property templates
│   │   ├── property_list.html
│   │   ├── property_detail.html
│   │   ├── property_form.html
│   │   └── property_confirm_delete.html
│   ├── profile/                  # Profile templates
│   │   ├── client_profile_form.html
│   │   └── agent_profile_form.html
│   ├── appointments/             # Appointment templates
│   │   ├── appointment_list.html
│   │   ├── appointment_form.html
│   │   ├── appointment_update.html
│   │   └── appointment_confirm_delete.html
│   ├── transactions/             # Transaction templates
│   │   ├── transaction_list.html
│   │   ├── transaction_detail.html
│   │   └── transaction_form.html
│   ├── reviews/                  # Review templates
│   │   ├── review_form.html
│   │   └── review_confirm_delete.html
│   └── analytics/                # Analytics templates
│       └── analytics.html
├── static/                        # Static files
│   ├── css/                      # Custom stylesheets
│   ├── js/                       # JavaScript files
│   └── images/                   # Property images
├── media/                         # User-uploaded files
│   └── property_images/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
└── real_estate_schema.sql        # Database schema
```

---

## Security Features

- **Password Hashing:** All passwords encrypted using PBKDF2-SHA256
- **CSRF Protection:** Cross-site request forgery protection on all forms
- **SQL Injection Prevention:** Django ORM prevents SQL injection
- **Role-Based Access Control:** Users can only access authorized features
- **Session Management:** Secure session handling
- **Input Validation:** All user inputs validated before processing

---

## Testing the Application

### Testing CRUD Operations

#### 1. Test Property CRUD (as Agent)
1. Login as agent
2. Create a new property
3. View property details
4. Update property information
5. Attempt to delete property

#### 2. Test Appointment CRUD (as Client)
1. Login as client
2. Browse properties
3. Schedule an appointment
4. View appointments list
5. Update appointment status
6. Cancel an appointment

#### 3. Test Transaction (as Agent)
1. Login as agent
2. Navigate to a property
3. Create a transaction
4. Verify commission calculation
5. Check property status update

#### 4. Test Review (as Client)
1. Login as client
2. View a property
3. Write a review with rating
4. View review on property page
5. Delete review

#### 5. Test Analytics Dashboard (as Admin/Agent)
1. Login as admin or agent
2. Navigate to Analytics page
3. View system-wide statistics
4. Check properties by type breakdown
5. Review top cities data
6. Examine price distribution
7. Verify all metrics display correctly

### Database Verification

After each operation, verify in MySQL Workbench:

```sql
USE real_estate_db;

-- Check properties
SELECT * FROM Properties ORDER BY created_at DESC LIMIT 5;

-- Check appointments
SELECT * FROM Appointments ORDER BY created_at DESC LIMIT 5;

-- Check transactions
SELECT * FROM Transactions ORDER BY transaction_date DESC LIMIT 5;

-- Check reviews
SELECT * FROM Reviews ORDER BY review_date DESC LIMIT 5;
```

---

## Sample Data

The database includes sample data:
- 10 pre-loaded properties
- Multiple property images
- Sample users (agents and clients)
- Property types (Single Family, Condo, Townhouse, etc.)
- Various locations in Massachusetts

---

## Troubleshooting

### Common Issues

**Issue: "Table doesn't exist" errors**
- Solution: Run migrations - `python manage.py migrate`

**Issue: Images not showing**
- Solution: Check if images are in `static/images/` folder
- Run: `python manage.py collectstatic`
- Verify image URLs in database

**Issue: Login not working**
- Solution: Reset password using Django shell (see Setup Step 7)

**Issue: "Module not found" errors**
- Solution: Activate virtual environment and reinstall packages
  ```bash
  pip install -r requirements.txt
  ```

**Issue: Database connection fails**
- Solution: Check MySQL is running
- Verify credentials in `.env` file
- Test connection: `python manage.py dbshell`

**Issue: Port 8000 already in use**
- Solution: Use different port
  ```bash
  python manage.py runserver 8080
  ```

---

## Dependencies

### Python Packages

```
Django==4.2
pymysql
python-dotenv
Pillow
django-crispy-forms
crispy-bootstrap5
```

### External Resources

- **Bootstrap 5:** CSS framework (CDN)
- **Bootstrap Icons:** Icon library (CDN)
- **MySQL 8.0+:** Database server

---

## Learning Outcomes

This project demonstrates:

1. **Database Design:**
   - Entity-Relationship modeling
   - Normalization (3NF)
   - Referential integrity
   - Constraint implementation

2. **SQL Programming:**
   - Stored procedures
   - User-defined functions
   - Triggers
   - Complex queries with joins

3. **Full-Stack Development:**
   - Backend API design
   - Frontend templating
   - Form handling and validation
   - User authentication and authorization

4. **Software Engineering:**
   - MVC architecture (Django MVT)
   - Code organization
   - Error handling
   - Security best practices

---

## Future Enhancements

Potential improvements for the system:

1. **Advanced Features:**
   - Real-time notifications
   - Email integration
   - SMS alerts for appointments
   - Payment gateway integration
   - Property comparison tool
   - Mortgage calculator

2. **Analytics:**
   - Market trend analysis with visual representations
   - Price prediction models
   - Interactive agent performance dashboards
   - Advanced charts and graphs using Chart.js or D3.js
   - Historical data comparison
   - Predictive analytics for property values
   - Seasonal trend analysis

3. **User Experience:**
   - Mobile responsive design
   - Progressive Web App (PWA)
   - Advanced filtering options
   - Saved searches
   - Favorite properties
   - Virtual property tours

4. **Integration:**
   - Google Maps API for location
   - Third-party property listings
   - CRM integration
   - Document management
   - E-signature capabilities

---

## License

This project is developed for educational purposes as part of the CS 5200 Database Management Systems course at Northeastern University.

---

## Contributors

- Vaibhav Sankaran
- Gangatharan Idayachandiran

---

## Support

For issues or questions:
- **Email:** vaibhavsankaran24@gmail.com
- **Course:** CS 5200 - Database Management Systems
- **Institution:** Northeastern University

---

## Acknowledgments

- Course Instructor and Teaching Assistants
- Northeastern University CS Department
- Django Documentation
- Bootstrap Framework
- MySQL Community

---

**Last Updated:** November 2025

**Version:** 1.0

---

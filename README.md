# 🏢 Azmira Real Estate ERP — Backend API

A production-ready, modular **Real Estate ERP system** built with Django REST Framework. Designed to manage the full lifecycle of a real estate business — from land acquisition and project management to customer bookings, installment tracking, commission distribution, investor dividends, and HR payroll.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | Django 5.x + Django REST Framework |
| Authentication | JWT (SimpleJWT) |
| Database | PostgreSQL |
| File Storage | Django Media / S3-compatible |
| Image Processing | Pillow (auto WebP conversion) |
| PDF Generation | WeasyPrint |
| Filtering | django-filter |
| Task Scheduling | Celery (planned) |

---

## 📦 Core Modules

### 1. User & Authentication
- Custom `ERPUser` model with JSON-based multi-role system
- Roles: `super_admin`, `admin`, `accounts`, `employee`, `marketing_officer`, `marketing_manager`, `customer_care`, `hr`, `customer`, `investor`
- JWT login with role-based access
- Auto WebP image conversion on upload

### 2. Project Management
- Full project CRUD with type classification (Lot, Flat, Commercial, Mixed)
- Dynamic **Project Tab system** — admin creates custom tabs and assigns projects
- Each tab returns project list + total count
- Filter by status, city, district, upazila, price range, land area

### 3. Plot / Flat Management
- Plot inventory per project with status tracking (available, booked, sold, hold)
- Rich filtering: price range, area range, facing direction, floor, bedrooms, bathrooms
- Cross-project search via related project fields (city, district)
- Featured plot listing

### 4. Land Acquisition
- Track land owners, suppliers, dag/khatiyan numbers
- Monitor payment status: Power of Attorney → Saf-Kabala
- Mutation and survey tracking
- Outstanding amount auto-calculation

### 5. Customer Management
- Individual, Joint, and Corporate customer profiles
- Source tracking (walk-in, referral, marketing, online)
- NID image upload with WebP auto-conversion
- Loyalty points system

### 6. Lead Management
- Full lead pipeline: New → Contacted → Interested → Follow-up → Visit → Negotiating → Converted
- Assign leads to marketing officers
- Conversation log (JSON), follow-up scheduling
- Lead-to-customer conversion tracking

### 7. Booking System
- Booking with token, down payment, and installment tracking
- Token expiry logic: ≤500 tk = 30 days, ≤1000 tk = 60 days, >1000 tk = 90 days
- Auto `final_price`, `total_paid`, `total_due` calculation
- Booking transfer with service charge
- Cancellation with refund tracking

### 8. Installment Plan
- Auto-generate monthly installment schedule from booking
- Per-installment paid/due tracking
- Booking totals auto-update on installment save
- SMS reminder flags (48h before, on due date)

### 9. Money Receipt (3-stage Approval)
- `Pending → Complete → Authorized` workflow
- Payment modes: Cash, Bank Transfer, Cheque, Mobile Banking (bKash/Nagad)
- Cheque clearance tracking (30-day expiry alert)
- PDF receipt download via WeasyPrint
- E-signature support

### 10. Voucher System
- Debit, Credit, Journal, Contra voucher types
- `Draft → Approved → Rejected` workflow
- Approved vouchers are locked (no edit/delete)
- Linked to account heads, customers, and bookings

### 11. Multi-level Commission Engine
- Configurable commission rules per project per source type
- Source types: `booking`, `installment`, `down_payment`, `registration`, `land_dev`, `parking`, `transfer`, `utility`
- Supports up to 10 upline generations
- Auto wallet credit on commission generation
- Commission dashboard with Generation × Source-Type matrix

### 12. Marketing Officer System
- Hierarchical upline/downline structure
- Rank progression: Officer → Team Leader → AGM → GM
- Auto role assignment via Django signals
- TA/DA, mobile recharge, and withdrawal request management

### 13. Wallet System
- One wallet per user, type-matched to role
- Wallet types: `marketing`, `investor`, `customer`, `customer_care`, `employee`, `accounts`, `admin`, `general`
- Full transaction log with `balance_before` / `balance_after`
- Minimum withdrawal: 1000 tk
- Loan balance auto-deducted on withdrawal

### 14. Investor & Investment
- Investor profiles linked to marketing officers
- Investment tracking with maturity date and monthly dividend rate
- Auto dividend calculation and wallet credit
- Land Power Assignment (% based land conversion)
- Partial and full return tracking

### 15. HR Module
- Employee management with employment type (permanent, contract, probation, intern)
- Daily attendance tracking (present, absent, late, half-day, leave)
- Monthly payroll auto-calculation from attendance
- Loan deduction from salary

### 16. Project Visit Tracking
- Schedule, confirm, and complete site visits
- Track guest/lead/customer visit outcomes
- 24h and 2h notification flags

### 17. Offer & Discount Portal
- Create seasonal, Eid, or special offers
- Per-project or global targeting
- Offer validity max 90 days (enforced at API level)
- SMS notification tracking

### 18. SMS Log
- Comprehensive SMS event tracking
- Types: installment reminder, payment received, welcome, offer, commission, admin notification
- Linked to customer, booking, or marketing officer

### 19. Document Management
- Store and categorize legal documents (MOU, Deed, Agreement, Namjari, Porcha)
- Linked to booking, project, or customer
- E-signature support

### 20. Account Heads & Vouchers
- Chart of accounts with parent-child hierarchy
- Account types: income, expense, asset, liability, equity
- Opening and current balance tracking

### 21. Company Assets (Logistics)
- Track mobile, SIM, vehicle, laptop assignment
- Return tracking and condition notes

### 22. System Log
- Full audit trail of user actions
- Module-level log with IP address tracking
- Log levels: info, warning, error

---

## 🔌 API Overview

All endpoints follow RESTful conventions. Base URL: `/api/`

### Key Endpoints

```
Auth
  POST   /api/erp-users/login/
  POST   /api/erp-users/new/
  GET    /api/erp-users/role/<role>/

Projects
  GET    /api/erp-projects/           ?city=&district=&status=&project_type=&min_value=&max_value=
  GET    /api/tab-summary/
  GET    /api/project-tabs/<id>/projects/
  POST   /api/project-tabs/create/
  PATCH  /api/projects/<id>/assign-tab/
  POST   /api/project-tabs/<id>/assign-projects/

Plots
  GET    /api/erp-plots/              ?status=&min_price=&max_price=&min_area=&max_area=&facing=&city=
  GET    /api/erp-plots/featured/

Bookings
  GET    /api/erp-bookings/           ?customer=&project=&status=
  POST   /api/erp-bookings/new/
  POST   /api/generate-installment-schedule/
  GET    /api/installments/<booking_code>/

Payments
  POST   /api/erp-receipts/new/
  PATCH  /api/erp-receipts/<id>/      (status: pending → complete → authorized)
  GET    /api/erp-receipts/<id>/download/

Commission
  POST   /api/generate-commission/
  GET    /api/commission-dashboard/
  GET    /api/commission-dashboard/officer/<id>/

Wallet
  GET    /api/erp-wallets/user/<user_id>/
  POST   /api/erp-wallet-transactions/new/

Investor
  POST   /api/erp-dividends/new/

HR
  GET    /api/erp-attendance/         ?employee=&month=&year=
  POST   /api/erp-payroll/new/

Land
  GET    /api/erp-land-acquisitions/  ?supplier=&land_status=&min_area=&max_area=
```

---

## ⚙️ Signal Architecture

Django signals auto-manage roles and wallets:

```
ERPUser saved       → wallet auto-created (type based on role)
ERPMarketingOfficer → role: marketing_officer / marketing_manager added
ERPInvestor         → role: investor added + investor wallet ensured
ERPEmployee         → role: employee added
ERPCustomer         → role: customer added + customer wallet ensured
```

---

## 🗂️ Project Structure

```
project_root/
│
├── mainapp/
│   ├── models.py         # 26 models — full ERP domain
│   ├── serializers.py    # All serializers with display fields
│   ├── signals.py        # Auto role + wallet management
│   └── services.py       # Commission generation engine
│
├── api/
│   ├── views.py          # All API views (CRUD + business logic)
│   └── urls.py           # URL routing
│
└── core/
    └── filters.py        # django-filter FilterSets (Plot, Project, Land)
```

---

## 🛠️ Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/azmira-erp-backend.git
cd azmira-erp-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# .env এ DATABASE_URL, SECRET_KEY, MEDIA_ROOT set করুন

# 5. Database setup
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

---

## 🔐 Authentication

JWT token based authentication:

```bash
# Login
POST /api/erp-users/login/
{
  "username": "admin",
  "password": "your_password"
}

# Response
{
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  },
  "user": { ... }
}

# Use token in header
Authorization: Bearer eyJ...
```

---

## 📊 Commission System — How It Works

```
Customer pays installment
        ↓
POST /api/generate-commission/
{ "booking": 5, "amount": 25000, "source_type": "installment" }
        ↓
System finds marketing officer of the booking
        ↓
Walks up upline chain (Gen 0 → Gen 7)
        ↓
For each generation, checks ERPCommissionRule
        ↓
Creates ERPCommission + credits officer wallet
        ↓
Full transaction log in ERPWalletTransaction
```

---

## 🧪 Filter Examples

```bash
# Plot filters
GET /api/erp-plots/?min_price=500000&max_price=2000000&status=available
GET /api/erp-plots/?city=Dhaka&facing=north&bedrooms=3
GET /api/erp-plots/?search=A-01&ordering=-final_price

# Project filters
GET /api/erp-projects/?status=active&district=Gazipur
GET /api/erp-projects/?project_type=flat&min_value=10000000
GET /api/erp-projects/?search=Azmira&ordering=-created_at

# Land acquisition filters
GET /api/erp-land-acquisitions/?land_status=saf_kabala&is_mutated=true
GET /api/erp-land-acquisitions/?min_area=10&max_area=50
```

---

## 📄 License

This project is proprietary software developed for **Azmira Real Estate**. All rights reserved.

---

## 👨‍💻 Developer

**[Arjun Mazumder]**
Backend Developer — Django REST Framework  
📧 arjumazumder2@gmail.com  
🔗 [www.linkedin.com/in/arzunmazumder] 
🐙 [github.com/arjunmazumder]

---

> Built with Django REST Framework · PostgreSQL · JWT Auth · WeasyPrint · django-filter

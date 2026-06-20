<div align="center">
  <h1>🏢 Azmira Real Estate ERP — Backend API</h1>
  <p><strong>A production-ready, highly modular Real Estate ERP system built with Django REST Framework.</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
  [![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://www.djangoproject.com/)
  [![DRF](https://img.shields.io/badge/DRF-red.svg)](https://www.django-rest-framework.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-blue.svg)](https://www.postgresql.org/)
  [![License](https://img.shields.io/badge/License-Proprietary-yellow.svg)]()
</div>

<hr />

## 📖 Overview

Designed to manage the full lifecycle of a real estate business. This robust system handles everything from **land acquisition and project management** to **customer bookings, installment tracking, commission distribution (MLM style), investor dividends, accounting, and HR payroll**. 

---

## 🚀 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Framework** | Django 5.x + Django REST Framework |
| **Authentication** | JWT (SimpleJWT) |
| **Database** | PostgreSQL |
| **File Storage** | Django Media / S3-compatible |
| **Image Processing** | Pillow (auto WebP conversion for optimized performance) |
| **PDF Generation** | WeasyPrint |
| **Filtering** | django-filter |
| **Task Scheduling** | Celery (planned for asynchronous jobs) |

---

## 📦 Core Modules & Features

### 1. 🔐 User & Authentication (`ERPUser`, `ERPUserManager`)
- **Custom Multi-Role System**: Users can have multiple JSON-based roles (`super_admin`, `admin`, `accounts`, `employee`, `marketing_officer`, `marketing_manager`, `customer_care`, `hr`, `customer`, `investor`).
- **JWT Authentication**: Secure API access using JWT tokens.
- **Image Optimization**: Auto WebP image conversion upon upload.

### 2. 🏗️ Project Management (`Project`)
- Full project CRUD with type classification (Plot, Flat, Both).
- **Dynamic Project Tabs**: Admin can create custom tabs and assign projects to them.
- Deep filtering by status, city, district, upazila, price range, and land area.

### 3. 🏡 Plot / Flat Inventory (`Property`)
- Plot inventory tracking (available, booked, sold, hold).
- Rich filtering attributes (price range, area range, facing direction, floor, bedrooms, bathrooms).
- Features plot/flat listing and cross-project searches.

### 4. 🌍 Land Acquisition & Records (`ERPLandAcquisition`, `ERPLandOwner`, `ERPLandRecord`, `ERPSupplier`)
- Track land owners, suppliers, and legal DAG/Khatiyan numbers.
- Monitor payment lifecycle (Baina -> Power of Attorney → Saf-Kabala -> Namjari).
- Mutation and survey tracking with auto-calculation of outstanding dues.

### 5. 👥 Customer Management (`ERPCustomer`)
- Individual, Joint, and Corporate customer profiles.
- **Source Tracking**: Walk-in, referral, marketing officer, online, etc.
- Loyalty points system and NID image auto-conversion (WebP).

### 6. 🎯 Lead Management (`ERPLead`)
- **Full Pipeline**: New → Contacted → Interested → Follow-up → Visit → Negotiating → Converted.
- Assigned leads to specific marketing officers.
- Real-time conversation logging and automated follow-up scheduling.

### 7. 📑 Booking System (`ERPBooking`)
- End-to-end booking logic handling token, down payment, and active installments.
- **Dynamic Token Expiry**: ≤500 BDT = 30 days, ≤1000 BDT = 60 days, >1000 BDT = 90 days.
- Auto calculation of `final_price`, `total_paid`, and `total_due`.
- Booking transfer feature (with service charge) and cancellation with refund processing.

### 8. 💸 Installment Plan (`ERPInstallmentPlan`)
- One-click generation of monthly installment schedules from a confirmed booking.
- Per-installment paid/due tracking.
- Pre-due SMS reminder flags (e.g., 48 hours before, on the due date).

### 9. 🧾 Money Receipt & Transactions (`ERPMoneyReceipt`, `Transaction`)
- **3-Stage Approval Workflow**: `Pending → Complete → Authorized`.
- Multiple payment modes supported (Cash, Bank Transfer, Cheque, Mobile Banking).
- PDF receipt generation powered by WeasyPrint.

### 10. 📊 Accounting & Voucher System (`ERPVoucher`, `ERPAccountHead`)
- Debit, Credit, Journal, and Contra voucher types.
- **Chart of Accounts**: Parent-child hierarchy (Income, Expense, Asset, Liability, Equity).
- Voucher locking mechanisms (Approved vouchers cannot be altered).

### 11. 💰 Multi-level Commission Engine (`ERPCommissionRule`, `ERPCommission`)
- Highly configurable commission rules per project per source type (e.g., `booking`, `installment`, `registration`, `land_dev`).
- **MLM Upline Calculation**: Supports up to 10 upline generations.
- Auto wallet crediting when commission is generated.

### 12. 📈 Marketing Officer Hierarchies (`ERPMarketingOfficer`, `ERPOfficerRequest`)
- Upline/Downline structural tracking.
- **Rank Progression System**: Officer → Team Leader → AGM → GM.
- TA/DA, mobile recharge, and commission withdrawal management.

### 13. 💳 Wallet System (`ERPWallet`, `ERPWalletTransaction`)
- Centralized wallet ecosystem. One wallet per user, type-matched to their role.
- Transparent transaction logs (`balance_before` / `balance_after`).
- Loan auto-deduction integrations upon withdrawal requests.

### 14. 🤝 Investor & Investments (`ERPInvestor`, `ERPInvestment`, `ERPDividend`, `LandPowerAssignment`)
- Investment maturity dates and monthly dividend rate tracking.
- Auto-dividend generation and immediate wallet credit.
- Land Power Assignment tracking based on land conversion percentages.

### 15. 🏢 HR & Payroll Module (`ERPEmployee`, `ERPAttendance`, `ERPPayroll`, `ERPHoliday`)
- Detailed employee profiles (Permanent, Contract, Probation, Intern).
- Daily attendance tracking (Present, Absent, Late, Leave).
- **Automated Payroll**: Auto-calculates monthly salary from attendance, factoring in loan deductions.

### 16. 📅 Project Visit Tracking (`ERPProjectVisit`)
- Schedule, confirm, and complete site visits for leads/customers.
- SMS/Email Notification triggers (24h and 2h before visit).

### 17. 🎁 Offers & Discounts (`ERPOffer`)
- Create seasonal campaigns with global or per-project targeting.
- Enforced max validity periods via the API layer.

### 18. 📱 SMS Logging (`ERPSMSLog`)
- Universal SMS event tracking across modules (installments, payments, offers).

### 19. 📂 Document Management (`ERPDocument`)
- Secure vault for storing legal documents (MOU, Deed, Agreement, Porcha).

### 20. 💻 Assets & Logistics (`ERPCompanyAsset`)
- Track inventory assigned to employees (Mobiles, SIMs, Vehicles, Laptops) with condition logging upon return.

### 21. 🛠️ System Logs (`ERPSystemLog`)
- Full audit trail of user actions, module-level logging, and IP tracking.

---

## ⚙️ Core Architecture Details

### 🔄 Django Signals Architecture
Django signals are heavily utilized to auto-manage role assignments and wallet creation seamlessly:
- **`ERPUser` saved**: Associated wallet auto-created (type matched via role logic).
- **`ERPMarketingOfficer`**: Auto-assigns `marketing_officer` role.
- **`ERPInvestor`**: Auto-assigns `investor` role & provisions investor wallet.
- **`ERPCustomer`**: Auto-assigns `customer` role & provisions customer wallet.

### 💵 Commission Calculation Flow
1. **Trigger**: Customer pays an installment.
2. **Action**: `POST /api/generate-commission/` is called.
3. **Engine Check**: System identifies the marketing officer assigned to the booking.
4. **Traversal**: Engine walks the upline chain (Generation 0 → N).
5. **Rule Matching**: System checks `ERPCommissionRule` for each level.
6. **Execution**: Creates `ERPCommission` records and automatically credits wallets via `ERPWalletTransaction`.

---

## 🔌 API Quick Reference

All endpoints follow RESTful standards. Base URL is `/api/`.

**Auth & Users**
- `POST /api/erp-users/login/` (JWT Login)
- `GET /api/erp-users/role/<role>/`

**Projects & Properties**
- `GET /api/erp-projects/?city=&status=&project_type=`
- `GET /api/erp-plots/?status=&min_price=&max_price=&facing=`

**Bookings & Payments**
- `POST /api/erp-bookings/new/`
- `POST /api/generate-installment-schedule/`
- `POST /api/erp-receipts/new/`
- `GET /api/erp-receipts/<id>/download/`

**Financials**
- `POST /api/generate-commission/`
- `GET /api/erp-wallets/user/<user_id>/`

*Detailed Swagger / Postman collections available internally.*

---

## 🛠️ Setup & Installation

**1. Clone the Repository**
```bash
git clone https://github.com/yourusername/azmira-erp-backend.git
cd azmira-erp-backend
```

**2. Virtual Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Environment Variables**
```bash
cp .env.example .env
# Edit .env and configure DATABASE_URL, SECRET_KEY, and MEDIA_ROOT
```

**5. Database Setup & Run**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📄 License & Ownership

This project is proprietary software developed explicitly for **Azmira Real Estate**. All rights reserved.

---

## 👨‍💻 Developed By

**Arjun Mazumder**  
*Backend Developer — Django REST Framework*  
📧 arjumazumder2@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/arzunmazumder) | 🐙 [GitHub](https://github.com/arjunmazumder)

> *Built with ❤️ using Django REST Framework · PostgreSQL · JWT Auth · Celery · WeasyPrint*

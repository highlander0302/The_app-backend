# Possible Domains

## 1. BUSINESS PRODUCTIVITY / ENTERPRISE SOFTWARE
**14% OF TOTAL MARKET**

### Characteristics:
- Low load on the database and very low RPS
- Internal tools that don't require high level of security. All the basic security but nothing crazy like in bank
- Can be deployed on LAN network internal company servers. Or can be deployed on AWS too. Access is limited on entrance. Only for company employees
- **DOWNSIDE!**: These apps are not demanding in terms of front-end aesthetics. The employees will not leave the app because it is ugly. They have to use it

### Why it fits:
Django + DRF is excellent for building secure, scalable web apps and REST APIs for enterprise dashboards, CRMs, internal tools.
PostgreSQL handles complex queries and relational data well (e.g., user management, reporting).
React works perfectly for dynamic, responsive front-end dashboards.

### Typical apps:
- Project management tools
- Employee or resource tracking dashboards
- Custom CRMs for SMEs
- Analytics & reporting portals

---

## 2. ECOMMERCE / RETAIL PLATFORMS
**10-12% OF TOTAL MARKET**

### Characteristics:
- Not critical basic security, not a bank
- Loads are high in RPS and unpredictable
- Great for frontend, because users don't have to be there. Demanding frontend
- Online shops can be small and mid sized. It is common
- Often monolith
- Payment system is not for noobs. You most likely just integrate the app to payment system like PayPal and that's it, use their API and chill. Or you can even not be allowed to work on this part of the application as a junior dev

### Why it fits:
Django has built-in ORM and libraries like Django Oscar or Saleor for eCommerce backends.
PostgreSQL handles product catalogs, orders, and customer data efficiently.
REST API allows multi-platform integrations.
React can be used for storefronts and admin panels.

### Typical apps:
- Online marketplaces
- Store management dashboards
- Inventory & order management

---

## 3. HEALTHCARE / MEDTECH
**7% OF TOTAL MARKET**

### Characteristics:
- Still kinda serious. Analysis data, patients blood tests, etc. Might be too serious and small domain
- I have some kind of relation to this field, but so what?
- Not sure what to do there. The job that you can do there as developer is not as big

### Why it fits:
Django + DRF + PostgreSQL is solid for secure apps handling sensitive medical data.
REST APIs allow integration with mobile apps or third-party services.
React works for patient portals, admin dashboards, and data visualization.

### Typical apps:
- Telemedicine dashboards
- Patient record systems (EHR)
- Appointment scheduling systems

---

## 4. EDTECH
**5.5% OF TOTAL MARKET**

### Characteristics:
- I have half work there done. At least 30%
- Same problem, very small domain
- Understandable and interesting domain. Can be quite straightforward
- Not demanding from security perspective
- Can tell that worked for the western platform as outsource company on some service
- Frontend might be too hard. Interactive puzzles, games/gamifications, shit for kids who like animations and colorful stuff
- Low and predictable RPS

### Why it fits:
REST APIs with Django/DRF allow integration of course content, video, quizzes, and progress tracking.
React is ideal for interactive front-end experiences.

### Typical apps:
- LMS (Learning Management Systems)
- Online courses and student dashboards
- Assessment and grading platforms

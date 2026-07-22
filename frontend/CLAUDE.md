\# ShopEase Frontend



\## Project

React frontend for the ShopEase customer portal.

Connects to the backend API running at http://localhost:8000



\## Tech Stack

\- React 18

\- Plain CSS (no Tailwind or other frameworks)

\- fetch() for API calls (no axios)



\## API Endpoints available

\- GET http://localhost:8000/orders/ — list all orders

\- GET http://localhost:8000/orders/{id} — get one order

\- GET http://localhost:8000/tickets/ — list all tickets

\- POST http://localhost:8000/tickets/ — create a ticket

\- GET http://localhost:8000/tracking/{order\_id} — get tracking info



\## Design Rules

\- Clean, simple design — white background, subtle borders

\- ShopEase brand color: #6C63FF (purple)

\- Mobile friendly

\- Show loading state while fetching data

\- Show friendly error messages if API call fails

\- No external UI libraries — plain CSS only



\## Component Structure

\- App.js — main app with tab navigation

\- components/Orders.js — orders list and order detail

\- components/Tickets.js — tickets list and create ticket form

\- components/Tracking.js — tracking info lookup

\- components/Navbar.js — top navigation bar



\## Code Rules

\- Use functional components only

\- Use useState and useEffect hooks

\- All API calls go in a separate file: src/api.js

\- snake\_case for variables, PascalCase for components


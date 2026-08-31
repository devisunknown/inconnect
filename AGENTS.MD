# PROJECT OVERVIEW
-this project is a chat app wherebyb instaed of the normal chat app the system matches u with peple with the same intrest as you so there is the normal signin flow and there is a what are u intrested in page where by users select their intrest and the system matches u with users with the same intrest to connect with and talk  


# STYLE/FRONTEND
-use the same style as what i am ab to give you the frontend is alreadfy there its a google stitch mcp use that same style
-and if u need more inspiration i made a style refrence jpeg in the project root use that style and the frontend i will guve to you


# TECH STACK
-Django(backend)
-html and tailwindcss(google stitch)
-daphene(for the websckets)
-NGINX for the middleman between the server
-ASYNC for the request handling as apart of the other technologies
-and the api endpoints


# NOTE
-after every change test the app yourself and run python mnagae.py check
-also migrate the database after every change

# STITCH FRONTEND
-ConnectSphere project ID: 630717208140954488
-All HTML templates are in Templates/ folder
-Screens: login, signup, welcome, onboarding_interests, onboarding_interests_functional, match_discovery, match_discovery_with_nav, messages, messages_with_nav, profile, profile_with_nav, desktop
-Design system: Geist (headings/labels) + Inter (body), Primary Indigo #4F46E5, Coral #F97360 accent, 8px grid spacing

# BUILD PLAN

## Phase 1 — Project Setup
-Install Daphne + Channels
-Register knotapp in INSTALLED_APPS
-Configure ASGI + Channels routing in asgi.py
-Create requirements.txt
-Run initial migration

## Phase 2 — Auth System
-Custom User model (extends AbstractUser)
-Sign up / Sign in / Sign out views + templates
-Tailwind-styled auth pages (Google Stitch style)

## Phase 3 — Interest Selection
-Interest model + UserInterest (many-to-many)
-Interest selection page after sign-up
-Admin-able list of available interests

## Phase 4 — Matching + Dashboard
-Matching algorithm (users with shared interests)
-Dashboard showing matched users
-Profile view of matched users

## Phase 5 — Real-Time Chat
-WebSocket consumer (async) for live messaging
-Chat and Message models
-Chat room template
-Daphne + Channels layer configured

## Phase 6 — Polish
-NGINX config for production
-Final styling pass
-Error handling, notifications

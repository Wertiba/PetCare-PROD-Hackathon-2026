PetCare — Product Context and Requirements
Source: “PetCare — приложение для владельцев домашних животных”, the four-page hackathon case brief (originally in Russian). This document is an English translation reorganized for use by AI development agents.
Source of truth: The requirements below reflect the supplied case. Do not assume any unmentioned feature is required or approved. Product and implementation decisions not specified by the case are identified as Open decisions.

1. Product overview
Product name: PetCare
Product type: Application for pet owners
Primary user: A pet owner who enters information, receives reminders, and maintains a history of care for one or more pets.
Core idea: A centralized service for organizing pets' health records, nutrition information, and routine care, with timely reminders and convenient everyday workflows.
The problem
Pet owners often struggle to organize recurring care. They may forget vaccination and parasite-treatment dates, lose track of which foods suited a pet, and lack a single history of veterinary visits. Health and nutrition information is scattered, making it difficult to reconstruct previous procedures, follow veterinary instructions, and take necessary action on time. This increases risks to pet health and causes stress for owners.
The product goal
Create a service that:
- Stores pet profiles and their care history.
- Helps track vaccinations, parasite treatments, and veterinary visits.
- Reminds owners about upcoming procedures and prescribed medications.
- Maintains a history of foods and pets' reactions to them.
- Helps owners understand which foods suit their pets.
Primary emphasis: Centralized records, timely reminders, and ease of daily use.
2. Target audience
- First-time pet owners: People who have recently acquired a pet and need guidance.
- Owners with busy lifestyles: People who benefit from automatic reminders.
- Care-focused owners: People who regularly track their pets' health and nutrition.
All three groups should be able to use the product without extensive instructions.
3. Core user journeys
Journey A — Add a pet
The user quickly creates a pet profile by providing the pet's name, species, breed, date of birth, and photo. The flow should be fast and should not require a complicated form.
Journey B — Maintain health history
The user records vaccinations, parasite treatments, veterinary appointments, and professional findings/reports. The user can also record the pet's weight and other parameters when needed.
Journey C — Track nutrition
The user logs foods given to the pet, rates preferences, and records physical reactions. Over time, the application builds a personal history of which foods did and did not suit that pet.
Journey D — Keep up with upcoming care
The user receives reminders about vaccinations, parasite treatments, and prescribed medication. The service calculates procedure dates and medication frequency based on user-entered data and veterinary prescriptions.
4. Functional requirements
4.1 Pet profiles
- Create a pet profile.
- Store the pet's name, species, breed, and date of birth.
- Add a photo.
- Display the user's list of pets.
4.2 Health record
- Keep a dated vaccination history.
- Keep a history of parasite treatments.
- Add veterinary visit records.
- Store veterinary findings and reports.
- Record weight and other pet parameters.
4.3 Nutrition log
- Record foods previously given to the pet.
- Track preference: “Liked” / “Disliked.”
- Track tolerance: “Suitable” / “Unsuitable.”
- Record adverse reactions, including gastrointestinal issues and allergic reactions.
- Preserve nutrition history and evaluations to build a personal database of food preferences and tolerances for each pet.
Important distinction: Preference and tolerance are separate evaluations. A pet may like a food that does not agree with it.
4.4 Reminders and prescriptions
- Automatically calculate the next vaccination date from entered information.
- Automatically calculate the next parasite-treatment date.
- Track medication prescriptions recorded in veterinary reports.
- Calculate the duration and frequency of prescribed medication administration.
- Generate reminders for upcoming procedures.
- Display a list of upcoming events.
- Deliver notifications via push notifications or a desktop widget.
Data integrity principle: Dates, intervals, and medication schedules must originate from entered data and prescriptions. The case does not supply universal medical schedules; do not fabricate them.
5. Optional / additional feature — Pet avatar desktop widget
The case identifies a pet-avatar widget as an additional capability:
1. Create an avatar: The user uploads a photo of their pet; the service produces a stylized avatar from that image.
2. Place it on the desktop: The user configures a widget featuring their pet's avatar.
3. Display notifications: The widget displays event notifications, such as:
   - “It's time for a vaccination.”
   - “Today is Barsik's birthday.”
4. Customize notifications: The user can choose which notifications the widget displays.
Scope note: This is an additional feature, not a replacement for the core records and reminders. The source does not specify the widget's operating systems, implementation technology, animation style, or whether it must float above other windows.
6. Required application screens
The case specifies four primary screens:
Screen	Purpose
My Pets	List and access pet profiles.
Health Record	Review vaccination, parasite treatment, veterinary visit, and medical report history.
Nutrition	View the food log, preferences, tolerances, and reactions.
Reminders	Review upcoming procedures and other events.


The exact navigation model, page URLs, and internal screen composition are not specified.
7. UX and interface requirements
- The interface must be clear, clean, modern, and intuitive.
- Core tasks should be understandable without reading instructions.
- Pages must render and work properly on mobile devices.
- Creating a pet profile must be quick and straightforward.
- Forms must show clear, understandable validation errors.
- Invalid or missing fields (for example, an empty pet name) must be visually highlighted.
Design freedom: The case does not mandate a specific visual style, color palette, typography, UI library, animation system, or layout. These are team decisions as long as usability is preserved.
8. Non-functional requirements
- Intuitive use without a manual.
- Mobile-friendly pages.
- Understandable form validation and error feedback.
The case does not establish specific performance targets, browser support matrices, accessibility standards, data retention rules, or security architecture. These remain implementation decisions, not source-stated requirements.
9. Explicitly out of scope
The hackathon project does not require:
- Online consultations with veterinarians.
- Integration with government animal registries.
- A full-fledged marketplace for products.
- A social network for pets.
- Complex AI algorithms for diagnosing diseases.
Do not present these as baseline requirements or spend implementation effort on them unless the team explicitly changes scope.
10. Product principles for development agents
Use the following rules when implementing features or proposing designs:
1. Prioritize the four main flows: Pet profiles, health history, nutrition tracking, and reminders.
2. Keep data scoped to the correct pet: Health entries, food evaluations, and reminders should be clearly associated with a particular animal.
3. Separate source requirements from team ideas: Do not describe proposed enhancements as mandatory elements of the case.
4. Do not invent veterinary advice: The app is a tracking and reminder tool, not a diagnostic system. Use supplied dates and prescribed treatment data for schedules.
5. Optimize for fast data entry and retrieval: Frequent actions should feel lightweight; users must be able to find past records easily.
6. Keep nutrition evaluations unambiguous: “Liked/disliked” and “suitable/unsuitable” answer different questions.
7. Build responsive interfaces: Core journeys must remain usable on mobile.
8. Handle validation explicitly: Required fields and invalid entries need actionable feedback.
9. Treat the avatar widget as an extension: Do not let it delay or replace the core care-management functionality.
10. Avoid inventing product scope: If a request requires an unresolved product decision, surface that decision rather than silently turning an assumption into a requirement.
11. Open decisions (not answered by the case)
The team must decide, rather than assume:
- Which features are P0/P1/P2/P3 for the hackathon implementation.
- Whether and how users authenticate, and how data is stored and synchronized.
- Whether reminders use push notifications, a desktop widget, or both.
- How the desktop widget is distributed and supported across operating systems.
- How the stylized avatar is generated.
- How users provide the medical intervals or prescription schedules used in calculations.
- Whether veterinary documents are stored as uploads, structured entries, or both.
- Whether extra screens such as a landing page, overview dashboard, onboarding, or settings are needed.
- Detailed branding, design system, and navigation structure.
12. Definition of product success
The product should let a pet owner create a pet profile quickly, recover important health and nutrition history, see what care is coming next, and receive useful reminders without having to manage scattered notes or remember every date manually.
Document scope: English translation and agent-oriented restructuring of the supplied PetCare case brief. Any new implementation or design guidance is explicitly labeled as a principle or open decision, not as a requirement from the organizers.
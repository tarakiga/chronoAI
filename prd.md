## Product Requirements Document (PRD): ChronoAI

**Document Version:** 1.0
**Date:** October 26, 2023
**Author:** Pet Project Owner
**Status:** Ready for Development

---

### 1. Introduction & Vision

**1.1. Overview**
ChronoAI is a personalized, AI-powered desktop assistant designed to integrate with a user's Google and Zoho calendars. Its primary function is to provide timely, engaging, and interactive voice reminders for upcoming calendar events, moving beyond standard, intrusive alarms.

**1.2. Problem Statement**
Traditional calendar notifications are often ignored, missed, or are disruptive (e.g., a loud, jarring alarm). They lack personality and fail to grab attention in a subtle, yet effective way. Users need a more human-like and interactive way to be reminded of important commitments without breaking their focus completely.

**1.3. Product Vision**
To create a fun, reliable, and personalized calendar assistant that feels like a helpful companion. The core experience will be defined by its unique, escalating voice notification system that playfully grabs the user's attention and provides context on demand.

---

### 2. Goals & Objectives

| Goal | Objective | Key Result |
| :--- | :--- | :--- |
| **User Engagement** | Create a reminder system that is noticed and acted upon. | The user acknowledges >90% of notifications within the 15-second escalation sequence. |
| **Personalization** | Make the assistant feel unique to the user. | The user can customize their name, voice type, and notification timings. |
| **Reliability** | Ensure the assistant is dependable. | The system successfully syncs calendars and triggers notifications with 99.5% accuracy. |
| **Seamless Integration** | Connect effortlessly with existing tools. | Securely authenticate and sync with both Google and Zoho calendars on first-time setup. |

---

### 3. Target User & Persona

**Persona: "Alex, the Busy Professional"**
*   **Role:** Works in a dynamic role (e.g., developer, consultant, manager).
*   **Behavior:** Juggles multiple projects, back-to-back meetings, and personal commitments. Often in "deep work" mode and can easily lose track of time.
*   **Needs:** A non-intrusive but effective way to be pulled out of deep work 5-15 minutes before a meeting. Wants to feel in control of how and when they receive information.
*   **Frustrations:** Hates sudden, loud alarms. Finds standard notification banners easy to dismiss and forget. Forgets to acknowledge calendar events, leading to a last-minute rush.

---

### 4. User Stories & Use Cases

**US-01: Calendar Connection**
*   **As a** user,
*   **I want to** securely connect my Google and Zoho accounts,
*   **So that** ChronoAI can track all my events in one place.

**US-02: The Escalating Notification**
*   **As a** user,
*   **I want to** receive a playful, escalating voice notification 15 minutes before an event,
*   **So that** it grabs my attention without being startling.

**US-03: The Interactive Acknowledgment**
*   **As a** user,
*   **I want** an "Acknowledge" button to appear during the notification,
*   **So that** I can instantly get the event details and stop the escalation.

**US-04: The Full Announcement**
*   **As a** user,
*   **If I don't acknowledge the notification,**
*   **I want** the assistant to speak the full event details after the escalation sequence,
*   **So that** I am still fully informed about my upcoming commitment.

**US-05: Personalization**
*   **As a** user,
*   **I want to** change the name the assistant calls me, the voice it uses, and the pre-event reminder time,
*   **So that** the experience feels tailored to me.

---

### 5. Functional Requirements

#### 5.1. Calendar Integration Module
*   **FR-CAL-01:** The system shall support OAuth 2.0 authentication for Google Calendar API.
*   **FR-CAL-02:** The system shall support OAuth 2.0 authentication for Zoho Calendar API.
*   **FR-CAL-03:** The system shall automatically sync calendar events every 10 minutes.
*   **FR-CAL-04:** The system shall fetch event details including: Event Title, Start Time, End Time, Attendees, and Location.
*   **FR-CAL-05:** The system shall merge events from both calendars into a single, unified, chronologically sorted list.

#### 5.2. Notification Engine (Core Feature)
*   **FR-NOT-01:** The system shall trigger a notification sequence exactly 15 minutes before an event's start time (this should be customizable).
*   **FR-NOT-02:** The notification sequence shall be an escalating audio call-out.
*   **FR-NOT-03:** The sequence shall proceed as follows, with a 1.5-second pause between each step:
    1.  **T-15:00s:** A whisper: *"Psst, [User Name]..."* (Volume: 20%)
    2.  **T-13.5s:** A louder whisper: *"Hey [User Name]..."* (Volume: 40%)
    3.  **T-12.0s:** A normal speaking voice: *"[User Name]!"* (Volume: 75%)
*   **FR-NOT-04:** Concurrently with the first whisper, a small, non-intrusive pop-up window shall appear on the screen.
*   **FR-NOT-05:** This pop-up window shall contain a single button: **"Acknowledge"**.
*   **FR-NOT-06:** If the "Acknowledge" button is clicked at any point during the sequence:
    *   The escalating audio sequence must immediately stop.
    *   The system shall speak the following message in a normal, clear voice: *"You have a meeting at [Event Time] with [Event Title/Attendees]. Just wanted to let you know."*
    *   The pop-up window shall disappear.
*   **FR-NOT-07:** If the "Acknowledge" button is **not** clicked:
    *   After the escalating sequence completes, the system shall speak the full details message as defined in FR-NOT-06.
    *   The pop-up window shall disappear after the message is spoken.

#### 5.3. User Interface (UI)
*   **FR-UI-01:** The application shall have a main dashboard window that can be minimized to the system tray.
*   **FR-UI-02:** The dashboard shall display a list of events for the current day.
*   **FR-UI-03:** The dashboard shall have a "Settings" or "Preferences" page.
*   **FR-UI-04:** The notification pop-up (FR-NOT-04) shall be clean, simple, and positioned in a corner of the screen that does not interfere with active windows.

#### 5.4. Settings & Customization
*   **FR-SET-01:** Users shall be able to set and change their name.
*   **FR-SET-02:** Users shall be able to select from a list of available Text-to-Speech voices.
*   **FR-SET-03:** Users shall be able to adjust the default pre-event reminder time (e.g., 5, 10, 15, 30 minutes).
*   **FR-SET-04:** Users shall be able to disconnect/reconnect their calendar accounts.

---

### 6. Non-Functional Requirements

| Requirement | Specification |
| :--- | :--- |
| **Performance** | Notifications must trigger within +/- 5 seconds of the scheduled time. Calendar sync must complete in the background without blocking the UI. |
| **Reliability** | The application must run as a background service and be resilient to temporary network outages. It should retry failed API calls. |
| **Security** | All API tokens and credentials must be stored securely using the operating system's credential manager (e.g., Windows Credential Manager, macOS Keychain). |
| **Usability** | The application should be simple to set up and use. The core notification interaction must be intuitive. |
| **Compatibility** | The application must be built for a primary desktop OS (e.g., Windows 10/11 or macOS). |

---

### 7. Technical Stack & Assumptions

*   **Recommended Stack:** Python-based desktop application.
    *   **Framework:** PyQt5 or Tkinter for the UI.
    *   **Calendar APIs:** Google APIs Client Library for Python, `requests` library for Zoho API.
    *   **Scheduling:** `APScheduler` for background task scheduling.
    *   **Text-to-Speech:** `pyttsx3` for offline voices, or integration with Google Cloud Text-to-Speech/ElevenLabs API for higher quality.
    *   **Audio:** `pydub` for fine-grained volume control.
*   **Assumptions:**
    *   The user has a stable internet connection for calendar syncing.
    *   The user has speakers or headphones connected to their computer.
    *   The user has the necessary permissions to install applications on their machine.

---

### 8. Future Scope (Out of Scope for V1)

*   Mobile application (iOS/Android).
*   Natural language processing to create more dynamic and contextual spoken messages.
*   Integration with other calendar services (Outlook, Apple Calendar).
*   "Snooze" functionality for notifications.
*   Analytics dashboard on notification patterns.

---

### 9. Success Metrics

*   **Qualitative:** The user feels more prepared and less stressed about upcoming meetings. The assistant feels like a helpful, fun tool rather than a chore.
*   **Quantitative:** Reduction in missed meetings. High rate of user acknowledgment for interactive notifications.
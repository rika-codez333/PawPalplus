# PawPal+ Project Reflection

## 1. System Design
    3 core user actions
    - add and sort tasks by priority, time, user preferences
    - add multiple pets
    - see today's or weekly tasks 
    bonus:
    - filter by pet name if pet has multiple tasks for day or week
**a. Initial design**

- Briefly describe your initial UML design.

    The initial UML design establishes a clear, clean hierarchy for pet care planning:
    - An **Owner** has a one-to-many relationship with **Pet**s (an owner owns multiple pets).
    - A **Pet** has a one-to-many relationship with **Task**s (each pet has multiple care tasks associated with them).
    - A **Task** utilizes a **Priority** enumeration to rate its importance (LOW, MEDIUM, HIGH).
    - The **Scheduler** interfaces with **Owner** preferences and availability constraints, schedules multiple **Task**s, organizes them into daily or weekly structures, and explains the scheduling decisions.

- What classes did you include, and what responsibilities did you assign to each?

    1. **Priority** (Enum): Defines the discrete levels of urgency for tasks (LOW, MEDIUM, HIGH) to facilitate priority-based sorting.
    2. **Task** (Dataclass): Models a specific pet care activity. It tracks core attributes (`name`, `type`, `priority`, `duration`, `isCompleted`) and provides a stub method (`markAsCompleted`) to toggle its completion state.
    3. **Pet** (Dataclass): Stores comprehensive attributes about a pet (`name`, `breed`, `age`, `dietRestrictions`, `energyLevel`, `otherInfo`) and links a pet to their list of tasks, offering a `getDetails` helper method to summarize their profile.
    4. **Owner** (Dataclass): Represents the user of the system. Tracks the owner's profile info (`name`, `availability`, `preferences`) and their list of `pets`, with methods (`addPet`, `removePet`) to manage their pets.
    5. **Scheduler** (Dataclass): Orchestrates the scheduling logic. It stores generated schedules (`dailySchedule`, `weeklySchedule`, `planExplanation`) and provides methods (`generateSchedule` and `filterTasksByPet`) to generate a timeline under owner constraints and filter tasks by pet.

**b. Design changes**

- Did your design change during implementation?

    Yes -- several modifications were introduced to resolve missing relationships and performance bottlenecks identified in the initial code skeleton.

- If yes, describe at least one change and why you made it.

    1. **Task-to-Pet Association**: Added a `pet_name` attribute to the `Task` class. Originally, a `Task` was unaware of which pet it belonged to, which made filtering the schedule by a specific pet (via `filterTasksByPet`) highly inefficient, requiring nested loop lookups. The back-reference allows for quick, direct filtering.
    2. **Chronological Scheduling Slots**: Added time-related attributes (like `start_time` and `day_of_week`) to `Task`. The initial design lacked a way to place tasks chronologically or verify owner availability constraints, which is crucial for a functioning calendar scheduler.
    3. **Interface Simplification**: Streamlined the `generateSchedule(self, owner: Owner)` signature to extract tasks directly from `owner.pets` instead of receiving a separate, redundant list of tasks. This guarantees data consistency and prevents errors from scheduling tasks that don't belong to any of the owner's pets.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

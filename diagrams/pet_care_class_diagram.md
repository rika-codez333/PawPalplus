# Pet Care App Class Diagram

This diagram visualizes the simplified object-oriented design for the PawPal+ app based on the attributes and actions brainstormed in [class_architecture.md](file:///Users/rikaraxkz/Desktop/CodePath/AI110/AI110%20-%20PawPal+/class_architecture.md).

```mermaid
classDiagram
    direction TB

    class Owner {
        +String name
        +String availability
        +Map preferences
        +addPet(pet: Pet) void
        +removePet(pet: Pet) void
    }

    class Pet {
        +String name
        +String breed
        +int age
        +String dietRestrictions
        +String energyLevel
        +String otherInfo
        +getDetails() String
    }

    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
    }

    class Task {
        +String name
        +String type
        +Priority priority
        +int duration
        +boolean isCompleted
        +markAsCompleted() void
    }

    class Scheduler {
        +List~Task~ dailySchedule
        +List~Task~ weeklySchedule
        +String planExplanation
        +generateSchedule(owner: Owner, tasks: List~Task~) void
        +filterTasksByPet(petName: String) List~Task~
    }

    Owner "1" o--> "*" Pet : owns
    Pet "1" o--> "*" Task : has
    Scheduler ..> Owner : reads preferences
    Scheduler "1" --> "*" Task : schedules
    Task ..> Priority : uses
```

## Relationship Simplification & Design Cleanliness

To keep the model clean and avoid unnecessary coupling, the following changes were made:
- **Owner ➔ Pet (1-to-many Aggregation `o-->`):** An `Owner` has a collection of `Pet`s.
- **Pet ➔ Task (1-to-many Aggregation `o-->`):** A `Pet` has its own list of `Task`s. This directly supports the core user action of filtering daily or weekly tasks by pet name.
- **Scheduler Dependency (`..>`):** The `Scheduler` does not need to own or manage the `Owner`. Instead, it reads the `Owner`'s preferences and availability to generate/sort `Task`s.
- **Removed Helper Classes:** Removed the `Priority` enum class block to avoid visual clutter; `priority` in `Task` is now modeled as a standard `String` or simple attribute.


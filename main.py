# Main driver script for PawPal+
from pawpal_system import Priority, Task, Pet, Owner, Scheduler

def main():
    print("🐾 PawPal+ Backend CLI Demo 🐾\n")
    
    # 1. Create an Owner
    owner = Owner(
        name="Jordan", 
        availability="08:00-12:00, 14:00-17:00", 
        preferences={"preferredTypes": ["feeding", "exercise"]}
    )
    
    # 2. Create at least two Pets
    mochi = Pet(
        name="Mochi", 
        breed="Golden Retriever", 
        age=3, 
        dietRestrictions="No grains", 
        energyLevel="High", 
        otherInfo="Loves tennis balls"
    )
    
    luna = Pet(
        name="Luna", 
        breed="Siamese Cat", 
        age=2, 
        dietRestrictions="Salmon allergy", 
        energyLevel="Low", 
        otherInfo="Likes quiet spots"
    )
    
    # 3. Add at least three Tasks with different times/durations to those pets
    # Task 1 (30 min) for Mochi
    mochi.tasks.append(Task("Morning Walk", "exercise", Priority.HIGH, 30, frequency="daily"))
    # Task 2 (10 min) for Mochi
    mochi.tasks.append(Task("Breakfast Feeding", "feeding", Priority.HIGH, 10, frequency="daily"))
    # Task 3 (15 min) for Luna
    luna.tasks.append(Task("Morning Feeding", "feeding", Priority.HIGH, 15, frequency="daily"))
    # Task 4 (20 min) for Luna
    luna.tasks.append(Task("Play with Laser Pointer", "exercise", Priority.MEDIUM, 20, frequency="daily"))
    
    owner.addPet(mochi)
    owner.addPet(luna)
    
    # 4. Generate schedule
    scheduler = Scheduler()
    scheduler.generateSchedule(owner)
    
    # 5. Print a "Today's Schedule" to the terminal
    print(f"Details for pets owned by {owner.name}:")
    for pet in owner.pets:
        print(f"  * {pet.getDetails()}")
        
    print("\n--- TODAY'S SCHEDULE ---")
    if scheduler.dailySchedule:
        for task in scheduler.dailySchedule:
            print(f"  [{task.startTime}] {task.petName}: {task.name} ({task.duration} min, Priority: {task.priority.value})")
    else:
        print("  No tasks scheduled for today.")

if __name__ == "__main__":
    main()

import pytest
from pawpal_system import Priority, Task, Pet, Owner, Scheduler

def test_task_completion():
    task = Task("Brush teeth", "grooming", Priority.MEDIUM, 5)
    assert not task.isCompleted
    task.markAsCompleted()
    assert task.isCompleted

def test_task_completion_mark_complete():
    """Verify that calling mark_complete() actually changes the task's status."""
    task = Task("Brush teeth", "grooming", Priority.MEDIUM, 5)
    assert not task.isCompleted
    task.mark_complete()
    assert task.isCompleted

def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Enjoys balls")
    initial_count = len(pet.tasks)
    
    task = Task("Walk Mochi", "exercise", Priority.HIGH, 30)
    pet.addTask(task)
    
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] == task

def test_pet_details():
    pet = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Enjoys balls")
    details = pet.getDetails()
    assert "Mochi" in details
    assert "Golden Retriever" in details
    assert "High" in details

def test_owner_pet_management():
    owner = Owner("Jordan", "120")
    pet1 = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Enjoys balls")
    pet2 = Pet("Luna", "Cat", 5, "Dry food only", "Low", "Scared of vacuums")

    owner.addPet(pet1)
    owner.addPet(pet2)
    assert len(owner.pets) == 2
    assert pet1 in owner.pets
    assert pet2 in owner.pets

    # Avoid duplicate addition
    owner.addPet(pet1)
    assert len(owner.pets) == 2

    owner.removePet(pet1)
    assert len(owner.pets) == 1
    assert pet1 not in owner.pets

def test_owner_get_all_tasks():
    owner = Owner("Jordan", "120")
    pet1 = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Enjoys balls")
    pet2 = Pet("Luna", "Cat", 5, "Dry food only", "Low", "Scared of vacuums")

    task1 = Task("Morning walk", "exercise", Priority.HIGH, 30)
    task2 = Task("Brush fur", "grooming", Priority.LOW, 15)
    task3 = Task("Feeding", "feeding", Priority.HIGH, 10)

    pet1.tasks.append(task1)
    pet1.tasks.append(task2)
    pet2.tasks.append(task3)

    owner.addPet(pet1)
    owner.addPet(pet2)

    tasks = owner.getAllTasks()
    assert len(tasks) == 3
    assert tasks[0].petName == "Mochi"
    assert tasks[2].petName == "Luna"

def test_scheduler_availability_parsing():
    scheduler = Scheduler()
    
    # Simple integer string representing minutes
    mins, start = scheduler._parseAvailability("180")
    assert mins == 180
    assert start == "08:00"

    # Time range string
    mins, start = scheduler._parseAvailability("08:00-11:00, 13:00-15:00")
    # 08:00-11:00 is 180 min, 13:00-15:00 is 120 min -> total 300 min
    assert mins == 300
    assert start == "08:00"

    # Invalid string fallback
    mins, start = scheduler._parseAvailability("invalid")
    assert mins == 240
    assert start == "08:00"

def test_scheduler_generate_schedule():
    owner = Owner("Jordan", "60", preferences={"preferredTypes": ["feeding"]})
    pet = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Enjoys balls")
    
    # Priority LOW, duration 20
    task1 = Task("Brush fur", "grooming", Priority.LOW, 20)
    # Priority HIGH, duration 30
    task2 = Task("Walk", "exercise", Priority.HIGH, 30)
    # Priority MEDIUM, but preferred task type "feeding", duration 15
    task3 = Task("Lunch feeding", "feeding", Priority.MEDIUM, 15)
    # Priority HIGH, duration 40 (Will exceed 60 minutes limit)
    task4 = Task("Vet visit", "medical", Priority.HIGH, 40)

    pet.tasks.extend([task1, task2, task3, task4])
    owner.addPet(pet)

    scheduler = Scheduler()
    scheduler.generateSchedule(owner)

    # Total available: 60 minutes.
    # Tasks sorted order should be:
    # 1. task2 (Walk): Priority HIGH, type "exercise" (not preferred), duration 30
    # 2. task4 (Vet visit): Priority HIGH, type "medical", duration 40
    # 3. task3 (Lunch feeding): Priority MEDIUM, type "feeding" (preferred), duration 15
    # 4. task1 (Brush fur): Priority LOW, type "grooming", duration 20
    #
    # Fitting tasks:
    # - task2 fits (30 mins). Remaining: 30. Start: 08:00
    # - task4 (40 mins) does not fit. Remaining: 30. Skipped.
    # - task3 (15 mins) fits. Remaining: 15. Start: 08:30
    # - task1 (20 mins) does not fit. Remaining: 15. Skipped.
    # Scheduled: task2, task3

    assert len(scheduler.dailySchedule) == 2
    assert scheduler.dailySchedule[0].name == "Walk"
    assert scheduler.dailySchedule[0].startTime == "08:00"
    assert scheduler.dailySchedule[1].name == "Lunch feeding"
    assert scheduler.dailySchedule[1].startTime == "08:30"
    
    assert "Walk" in scheduler.planExplanation
    assert "Lunch feeding" in scheduler.planExplanation
    assert "Vet visit" in scheduler.planExplanation
    assert "Brush fur" in scheduler.planExplanation

def test_scheduler_filter_tasks():
    scheduler = Scheduler()
    task1 = Task("Walk", "exercise", Priority.HIGH, 30, petName="Mochi")
    task2 = Task("Feed", "feeding", Priority.HIGH, 10, petName="Luna")
    
    scheduler.dailySchedule = [task1, task2]
    
    mochi_tasks = scheduler.filterTasksByPet("Mochi")
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].name == "Walk"

def test_scheduler_no_side_effects_on_original_tasks():
    """Verify that generating a schedule does not mutate original tasks in pet.tasks (Bug #1)."""
    owner = Owner("Jordan", "120")
    pet = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Notes")
    task = Task("Walk", "exercise", Priority.HIGH, 30, frequency="daily")
    pet.addTask(task)
    owner.addPet(pet)
    
    # Pre-condition: original task holds no schedule time
    assert task.startTime == ""
    
    scheduler = Scheduler()
    scheduler.generateSchedule(owner)
    
    # Post-condition: scheduled task has time, original task remains unmutated
    assert len(scheduler.dailySchedule) == 1
    assert scheduler.dailySchedule[0].startTime == "08:00"
    assert task.startTime == ""

def test_scheduler_handles_null_or_empty_preferences():
    """Verify that the scheduler successfully handles missing or None preferences (Bug #2)."""
    owner = Owner("Jordan", "120", preferences=None)
    pet = Pet("Mochi", "Golden Retriever", 3, "No grains", "High", "Notes")
    pet.addTask(Task("Walk", "exercise", Priority.HIGH, 30))
    owner.addPet(pet)
    
    scheduler = Scheduler()
    # Should not raise AttributeError when sorting tasks under None preferences
    scheduler.generateSchedule(owner)
    assert len(scheduler.dailySchedule) == 1

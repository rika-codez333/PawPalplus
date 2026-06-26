# PawPal+ System Implementation
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any

class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class Task:
    name: str
    type: str
    priority: Priority
    duration: int  # in minutes
    isCompleted: bool = False
    petName: str = ""
    startTime: str = ""
    dayOfWeek: str = ""
    frequency: str = "daily"  # "daily" or "weekly"

    def markAsCompleted(self) -> None:
        """Mark the task as completed."""
        self.isCompleted = True


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    dietRestrictions: str
    energyLevel: str
    otherInfo: str
    tasks: list[Task] = field(default_factory=list)

    def getDetails(self) -> str:
        """Return a string summary of the pet's details."""
        return (
            f"{self.name} ({self.age}yo {self.breed}, Energy: {self.energyLevel}) "
            f"- Diet: {self.dietRestrictions}. Notes: {self.otherInfo}"
        )


@dataclass
class Owner:
    name: str
    availability: str  # e.g., "120" (mins) or "08:00-12:00, 14:00-18:00"
    preferences: dict[str, Any] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to the owner's list of pets."""
        if pet not in self.pets:
            self.pets.append(pet)

    def removePet(self, pet: Pet) -> None:
        """Remove a pet from the owner's list of pets."""
        if pet in self.pets:
            self.pets.remove(pet)

    def getAllTasks(self) -> list[Task]:
        """
        Retrieve all tasks for all pets owned by this owner.
        This provides the link between Owner/Pets data and the Scheduler.
        """
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                # Ensure task back-references its pet's name
                if not task.petName:
                    task.petName = pet.name
                all_tasks.append(task)
        return all_tasks


@dataclass
class Scheduler:
    dailySchedule: list[Task] = field(default_factory=list)
    weeklySchedule: list[Task] = field(default_factory=list)
    planExplanation: str = ""

    def _parseAvailability(self, availability_str: str) -> tuple[int, str]:
        """
        Helper to parse the availability string.
        Supports:
          - A simple number of minutes: "180" -> (180, "08:00")
          - Time ranges: "08:00-12:00, 14:00-16:00" -> (360, "08:00")
        Returns:
          total_minutes: int
          start_time: str
        """
        if not availability_str:
            return 240, "08:00"
        
        # Try parsing as simple minutes integer
        try:
            minutes = int(availability_str.strip())
            return minutes, "08:00"
        except ValueError:
            pass

        # Try parsing time range like "08:00-12:00"
        import re
        time_ranges = re.findall(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})", availability_str)
        if time_ranges:
            total_minutes = 0
            first_start = None
            for sh, sm, eh, em in time_ranges:
                start_min = int(sh) * 60 + int(sm)
                end_min = int(eh) * 60 + int(em)
                if end_min > start_min:
                    total_minutes += (end_min - start_min)
                if first_start is None:
                    first_start = f"{int(sh):02d}:{int(sm):02d}"
            if total_minutes > 0:
                return total_minutes, first_start or "08:00"

        # Fallback default
        return 240, "08:00"

    def _addMinutesToTime(self, time_str: str, mins: int) -> str:
        """Helper to add minutes to a HH:MM time string."""
        try:
            h, m = map(int, time_str.split(":"))
            total = h * 60 + m + mins
            new_h = (total // 60) % 24
            new_m = total % 60
            return f"{new_h:02d}:{new_m:02d}"
        except Exception:
            return time_str

    def _sortTasks(self, tasks: list[Task], owner: Owner) -> list[Task]:
        """
        Sort tasks based on constraints and preferences:
          1. Priority (HIGH -> MEDIUM -> LOW)
          2. Owner preferred task types (from owner.preferences['preferredTypes'])
          3. Shortest duration first (Shortest Job First heuristic)
        """
        priority_map = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        preferred_types = owner.preferences.get("preferredTypes", [])

        def sort_key(t: Task) -> tuple[int, int, int]:
            p_val = priority_map.get(t.priority, 0)
            pref_val = 1 if t.type in preferred_types else 0
            # Higher priority and preferred first (negative for descending sort in python)
            return (-p_val, -pref_val, t.duration)

        return sorted(tasks, key=sort_key)

    def generateSchedule(self, owner: Owner, tasks: list[Task] = None) -> None:
        """
        Generate daily and weekly schedules based on owner constraints,
        prioritizing and ordering tasks.
        """
        # Retrieve tasks from the owner if not explicitly passed
        if tasks is None:
            tasks = owner.getAllTasks()
        else:
            # Ensure petName is filled in for explicit task lists
            for t in tasks:
                if not t.petName:
                    for pet in owner.pets:
                        if t in pet.tasks:
                            t.petName = pet.name
                            break

        total_minutes, start_time = self._parseAvailability(owner.availability)
        sorted_tasks = self._sortTasks(tasks, owner)

        # 1. Generate Daily Schedule
        self.dailySchedule = []
        explanation_lines = [
            f"Daily schedule generated for owner {owner.name}.",
            f"Constraint budget: {total_minutes} minutes, starting at {start_time}."
        ]

        current_time = start_time
        remaining_minutes = total_minutes
        skipped_tasks = []

        # Filter for daily tasks (or weekly tasks assigned to today)
        daily_candidates = [t for t in sorted_tasks if t.frequency == "daily"]

        for task in daily_candidates:
            if task.duration <= remaining_minutes:
                # Schedule task
                task.startTime = current_time
                self.dailySchedule.append(task)
                
                # Advance time and decrement budget
                explanation_lines.append(
                    f" - [{current_time}] {task.petName}: {task.name} ({task.duration} mins, Priority: {task.priority.value})"
                )
                current_time = self._addMinutesToTime(current_time, task.duration)
                remaining_minutes -= task.duration
            else:
                skipped_tasks.append(task)

        if skipped_tasks:
            explanation_lines.append("\nSkipped tasks due to time constraint:")
            for task in skipped_tasks:
                explanation_lines.append(
                    f" - {task.petName}: {task.name} ({task.duration} mins, Priority: {task.priority.value})"
                )

        # 2. Generate Weekly Schedule
        self.weeklySchedule = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_explanation_lines = ["\nWeekly Schedule Outline:"]

        for day in days_of_week:
            day_current_time = start_time
            day_remaining = total_minutes
            day_tasks_scheduled = 0
            
            # Filter tasks for this specific day:
            # Include all daily tasks, plus weekly tasks if they are assigned to this day
            # If a weekly task does not specify a dayOfWeek, default to Monday
            day_candidates = []
            for t in sorted_tasks:
                if t.frequency == "daily":
                    day_candidates.append(t)
                elif t.frequency == "weekly":
                    if t.dayOfWeek == day or (not t.dayOfWeek and day == "Monday"):
                        day_candidates.append(t)

            day_candidates = self._sortTasks(day_candidates, owner)
            
            for task in day_candidates:
                if task.duration <= day_remaining:
                    # Create a scheduled copy for this day of the week
                    import copy
                    task_copy = copy.copy(task)
                    task_copy.dayOfWeek = day
                    task_copy.startTime = day_current_time
                    self.weeklySchedule.append(task_copy)
                    
                    day_current_time = self._addMinutesToTime(day_current_time, task.duration)
                    day_remaining -= task.duration
                    day_tasks_scheduled += 1

            weekly_explanation_lines.append(f" - {day}: Scheduled {day_tasks_scheduled} tasks ({total_minutes - day_remaining} mins total)")

        self.planExplanation = "\n".join(explanation_lines + weekly_explanation_lines)

    def filterTasksByPet(self, petName: str) -> list[Task]:
        """Filter the scheduled tasks by pet name."""
        return [task for task in self.dailySchedule if task.petName == petName]


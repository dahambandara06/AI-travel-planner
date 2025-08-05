from dotenv import load_dotenv
load_dotenv()

import json
from typing import List
from openai import OpenAI
import os


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Destination:
    def __init__(self, city, country, start_date, end_date, budget, activities):
        self.city = city
        self.country = country
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.activities = activities

    def update_details(self, city=None, country=None, start_date=None, end_date=None, budget=None, activities=None):
        if city: self.city = city
        if country: self.country = country
        if start_date: self.start_date = start_date
        if end_date: self.end_date = end_date
        if budget: self.budget = budget
        if activities: self.activities = activities

    def __str__(self):
        return f"{self.city}, {self.country} | {self.start_date} to {self.end_date} | Budget: ${self.budget} | Activities: {', '.join(self.activities)}"

    def to_dict(self):
        return {
            "city": self.city,
            "country": self.country,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "budget": self.budget,
            "activities": self.activities
        }

    @staticmethod
    def from_dict(data):
        return Destination(
            data["city"],
            data["country"],
            data["start_date"],
            data["end_date"],
            data["budget"],
            data["activities"]
        )


class ItineraryManager:
    def __init__(self):
        self.destinations: List[Destination] = []

    def add_destination(self, destination):
        self.destinations.append(destination)

    def remove_destination(self, city):
        for d in self.destinations:
            if d.city.lower() == city.lower():
                self.destinations.remove(d)
                return True
        return False

    def update_destination(self, city, **kwargs):
        for d in self.destinations:
            if d.city.lower() == city.lower():
                d.update_details(**kwargs)
                return True
        return False

    def search_destination(self, keyword):
        return [d for d in self.destinations if keyword.lower() in d.city.lower() or keyword.lower() in d.country.lower() or any(keyword.lower() in a.lower() for a in d.activities)]

    def view_all_destinations(self):
        return [str(d) for d in self.destinations]

    def save_to_file(self, filename="itinerary.json"):
        with open(filename, "w") as f:
            json.dump([d.to_dict() for d in self.destinations], f, indent=4)

    def load_from_file(self, filename="itinerary.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.destinations = [Destination.from_dict(d) for d in data]
        except FileNotFoundError:
            self.destinations = []


class AITravelAssistant:
    @staticmethod
    def generate_itinerary(destination):
        prompt = f"""
Create a detailed daily travel itinerary for {destination.city}, {destination.country}
from {destination.start_date} to {destination.end_date}.
Budget: {destination.budget} USD.
Planned activities: {', '.join(destination.activities)}.
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    @staticmethod
    def generate_budget_tips(destination):
        prompt = f"""
Give me budget-saving travel tips for a trip to {destination.city}, {destination.country}
with a budget of {destination.budget} USD and the following activities: {', '.join(destination.activities)}.
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

def main():
    manager = ItineraryManager()
    manager.load_from_file()

    while True:
        print("\n--- Travel Itinerary Planner ---")
        print("1. Add Destination")
        print("2. Remove Destination")
        print("3. Update Destination")
        print("4. View All Destinations")
        print("5. Search Destination")
        print("6. AI Travel Assistance")
        print("7. Save Itinerary")
        print("8. Load Itinerary")
        print("9. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            city = input("Enter city: ")
            country = input("Enter country: ")
            start = input("Start date (YYYY-MM-DD): ")
            end = input("End date (YYYY-MM-DD): ")
            budget = float(input("Enter budget (USD): "))
            activities = input("Enter activities (comma separated): ").split(",")
            destination = Destination(city, country, start, end, budget, [a.strip() for a in activities])
            manager.add_destination(destination)

        elif choice == "2":
            city = input("Enter city to remove: ")
            if manager.remove_destination(city):
                print("Removed successfully.")
            else:
                print("City not found.")

        elif choice == "3":
            city = input("Enter city to update: ")
            print("Leave blank to keep current value.")
            new_city = input("New city: ") or None
            new_country = input("New country: ") or None
            new_start = input("New start date: ") or None
            new_end = input("New end date: ") or None
            new_budget = input("New budget: ")
            new_budget = float(new_budget) if new_budget else None
            new_activities = input("New activities (comma separated): ")
            new_activities = [a.strip() for a in new_activities.split(",")] if new_activities else None

            if manager.update_destination(city, city=new_city, country=new_country, start_date=new_start, end_date=new_end, budget=new_budget, activities=new_activities):
                print("Updated.")
            else:
                print("City not found.")

        elif choice == "4":
            for dest in manager.view_all_destinations():
                print(dest)

        elif choice == "5":
            keyword = input("Search keyword: ")
            results = manager.search_destination(keyword)
            for dest in results:
                print(dest)

        elif choice == "6":
            city = input("City for AI help: ")
            found = next((d for d in manager.destinations if d.city.lower() == city.lower()), None)
            if found:
                print("\n--- AI Itinerary ---")
                print(AITravelAssistant.generate_itinerary(found))
                print("\n--- Budget Tips ---")
                print(AITravelAssistant.generate_budget_tips(found))
            else:
                print("Destination not found.")

        elif choice == "7":
            manager.save_to_file()
            print("Saved.")

        elif choice == "8":
            manager.load_from_file()
            print("Loaded.")

        elif choice == "9":
            manager.save_to_file()
            print("Exiting. Data saved.")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()

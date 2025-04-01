# Restaurant Reservation

### Description

This chatbot allows users to create new restaurant reservations either by specifying a particular restaurant or by selecting a location and cuisine type. It also provides the option to modify existing reservations, including changes to the time, date, or party size. The bot aims to streamline the reservation process by offering both flexibility and convenience.

### Components

- Greeting Node

- Redirect user based on whether they want to create a new reservation or modify a existing one
1. New Reservation  
2. Modify existing reservation  

- New Reservation Node
Redirects user based on 
1. Restaurant
2. Location and cuisine
Get Relevant data and check for availablity

- Modify Existing Reservation Node
Get relevant data and check for availablity

- Check for Availablity
Based on a hardcoded time schedule checks for availablity

- End

### Real World use cases

* Making a Reservation at a Specific Restaurant:
    User: "Book a table at The Italian Bistro for tomorrow night at 7 PM for 4 people."
    Chatbot: Confirms the reservation and provides the details.

* Booking Based on Cuisine and Location:
    User: "Find me a good sushi place in downtown Chicago for two people tonight."
    Chatbot: Suggests a few options based on the location and cuisine preference, and the user can choose one to book.

* Modifying an Existing Reservation:
    User: "Can you change my reservation at The Italian Bistro for tomorrow night to 8 PM instead of 7?"
    Chatbot: Updates the reservation time and confirms the change.

* Adjusting Party Size:
    User: "I need to increase the number of people for my reservation at Sushi World from 4 to 6."
    Chatbot: Modifies the reservation and confirms the new party size.

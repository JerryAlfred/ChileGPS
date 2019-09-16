This project is a website that matches visitors with students to eat lunch in Annenberg. The site allows students to select their availability. Visitors can then book a specific time on a specific weekday with a certain student to visit Annenberg. To test our website, you can go to our main folder, and use “flask run” so it can load in your browser. And you can follow the buttons on our website to test each of our functionality as specified below:

Registration/log in:
Student and visitor can input their personal info in our database. And later on they can just log in with the username and password.

Student side:
Students have the option to select a time slot, cancel a time slot, and cancel an appointment.
- Selecting a time slot means the student will choose a weekday and a certain time, the slot changes its status to "Selected".
- Canceling a time slot means the student cancels one of the times they selected before being booked by a visitor, the slot changes its status back to "Slot_cancelled".
- If a student cancels an appointment after the visitor has booked the student's time slot, the slot changes its status back to "Selected".
The history page for a student displays all the times that have been booked by the visitor. The student index page displays all the times that have been "booked" as well as "selected".

Visitor side:
When a visitor books a time slot they have made an appointment with the respective student. They then have the option to cancel the appointment. The history
page displays all the times that the visitor has booked with a student. The index page is the same as the history page since we are not displaying any cancelled appointments.

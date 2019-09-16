The core of this project is the interaction within the SQL database. We have one database and three tables (student, visitor, and schedule). The "student" and "visitor" tables store the users' account information, and we made "student_id" and "visitor_id" the primary keys for the respective tables. The "schedule" table records all the transactions that occur. All the time slot selection, booking, and cancellations (by both student and visitor) are recorded in "schedule", along with the respective user ids “student” and “visitor”.

Every time when there is a change in our time slot status,  the “confirmation_status” in our “schedule” table will be updated. Eg: student selects a time slot - “Selected”, cancels a time slot - “Slot_cancelled”, or cancels an appointment with a visitor - “Selected”, or when a visitor books a student’s time slot - “Booked”, or cancels a booking - “App_cancelled_vis”.

In “application.py” we have defined all our functionality. We have multiple HTML templates for each respective web page, and multiple "layout.html" files in the respective folders, to differentiate between student and visitor and generic pages such as "register" and "login".

We have dynamically run the whole website’s visualization through JINJA and CSS powered by python. The user can achieve all the above-mentioned functionality by selecting data values in the menu and the data will be sent back to our application.py program through HTML's “POST” method.

At the same time, the users can see the history page (the successfully booked time slots), and the index page (all the time slots that are not cancelled) with the color-differentiating table. So our users have a better visualization and therefore a better understanding of their activities on our website.

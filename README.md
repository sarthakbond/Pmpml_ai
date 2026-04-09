**#basic working of then project**

The "Bus" Data: Since we don't have PMPML's live GPS API key yet, we will create a buses.json file.
This file will contain coordinates for 5 buses on a route (e.g., Katraj to Shivajinagar).
The "Verify" Button: In your app, add a big green button: "I am on this bus."
The Logic: When a user clicks it, their GPS location is sent to your Python backend. If the user's location is within 50 meters of the "Simulated Bus," the bus icon on the map turns Green (Verified). If not, it stays Gray (Predicted)

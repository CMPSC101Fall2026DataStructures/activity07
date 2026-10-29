# Activity 07 Reflection

Reflection Questions

Name: Add Your Name Here
Date: TODO

## Instructions

Please complete the following questions based on your experience completing the activity. Provide clear, specific answers in your own words. Use fenced code blocks for any code or command outputs.

=================

## Tutorial 1: The Ping Game

Q1. Paste the output of `uv run src/ping_stats.py data/ping_log.txt` from your own ping log. Which numbers surprised you, and what do you think affects how long a ping takes?

Response:

TODO

Q2. In your own words, what are an **IP address** and a **port**, and why does a server need both? Why must a string be turned into **bytes** with `.encode()` before it is sent through a socket?

Response:

TODO

Q3. Explain what the server's `accept()` call does and why the program seems to "freeze" there. How is the socket returned by `accept()` different from the socket created by `socket.socket(...)`?

Response:

TODO

---

## Tutorial 2: Direct Messages with a Chat Server

Q4. The chat server stores connected users in a **dictionary** named `clients`. What are the keys and what are the values? Why is a dictionary a better choice than a list for delivering a direct message?

Response:

TODO

Q5. Explain what a **thread** is and why the chat server needs one thread for each client. What would happen to the second person who tries to connect if the server did **not** use threads?

Response:

TODO

Q6. Describe how you read a file into a list in `read_history()` and into a dictionary in `load_contacts()`. Paste your finished `load_contacts()` function below, then explain what `contacts.get(target, target)` does in `resolve_target()`.

Response:

TODO

---

## Tutorial 3: Haunted Forest

Q7. In Haunted Forest the **server** decides who picked up a pumpkin, while the **clients** only send key presses and draw pictures. Why is it better to have one server make the decisions than to let every player's computer decide for itself?

Response:

TODO

Q8. The map lives in `maps/forest.txt` instead of being written inside the Python code. Describe how `load_map()` turns that text file into the dictionary `tiles`, and name one advantage of keeping the map in a file.

Response:

TODO

Q9. The server sends a **snapshot** of the game 30 times a second as a line of JSON. Pick three items from the snapshot dictionary and explain what each is used for in the client's drawing code. What kind of Python data structure (list, dictionary, tuple) is each one?

Response:

TODO

---

## General Reflection

Q10. All three tutorials follow the same pattern: create a socket, connect or accept, send bytes, receive bytes. Compare the Ping game, the Chat server, and Haunted Forest. What stayed the same, and what changed as the programs became more complex?

Response:

TODO

Q11. What challenges did you encounter while connecting two computers (or two terminal windows), such as firewalls, wrong IP addresses, or a port that was already in use? How did you resolve them?

Response:

TODO

---

## Thinking Beyond the Activity

Q12. Anyone on the same Wi-Fi network could connect to your chat server or game server in this activity, and the messages were sent as plain text. What privacy or safety problems could that cause? Suggest two things a real application does to protect its users.

Response:

TODO

Q13. Suggest one new feature for the Haunted Forest game (for example, a power-up, a new enemy, or a bigger map). Which files would you change, what data would the server need to send in its snapshot, and what new file (if any) would you read or write?

Response:

TODO

---

(Did you remember to add your name to the top of this document?)

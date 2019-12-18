# RL_Text_Based_Game

In this project, we address the task of learning control policies for text-based games using reinforcement learning. 
In these games, all interactions between players and the virtual world are through text. 
The current world state is described by elaborate text, and the underlying state is not directly observable. 
Players read descriptions of the state and respond with natural language commands to take actions.

For this project we will conduct experiments on a small Home World, which mimic the environment of a typical house.
The world consists of a few rooms, and each room contains a representative object that the player can interact with. 
For instance, the kitchen has an apple that the player can eat. The goal of the player is to finish some quest. 
An example of a quest given to the player in text is You are hungry now . To complete this quest, the player has to navigate through the house to reach the kitchen and eat the apple. In this game, the room is hidden from the player, who only receives a description of the underlying room. At each step, the player read the text describing the current room and the quest, and respond with some command (e.g., eat apple ). The player then receives some reward that depends on the state and his/her command.

In order to design an autonomous game player, we will employ a reinforcement learning framework to learn command policies using game rewards as feedback. 
Since the state observable to the player is described in text, we have to choose a mechanism that maps text descriptions into vector representations. 
A naive approach is to create a map that assigns a unique index for each text description. 
However, such approach becomes difficult to implement when the number of textual state descriptions are huge. 
An alternative method is to use a bag-of-words representation derived from the text description.

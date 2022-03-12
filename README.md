# brennerbot

BrennerBot is a discord bot I created in order to experiment with Discords bot API, along with 
having some fun with friends. 

It is currently built from this GitHub repo to an Azure Web App for hosting.

BrennerBot can do the following:
1. Using the +say command, BrennerBot will read out text in a voice channel to simulatie conversation. This is achieved
   <br> by using [espeak-ng](https://github.com/espeak-ng/espeak-ng) to convert text to speech. 
2. Delete a users messages by using the `+deleteMe` command. An upper bound can be specified by using `+deleteLast <num_msg>`
   <br> command. Note that discord bots can only poll messages at a set speed, so this can take time. 
3. Save your entire message history in a channel using the `+saveMe` command. All of your messages are put into a .txt file
   <br> where BrennerBot will then send those messages to you.   
4. Count up the number of times you have said a certain word using `+wordSlueth <word>`. I.e., "You said 'nice' 103 times!".

If you have not developed a Discord bot before and are considering doing it, I would highly recommend it. Discord bots are a great
way to practice your programming skills (and python if you have never used it), aswell as have fun with your friends testing 
different features :)

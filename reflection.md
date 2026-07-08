# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- Pet Class 
    Attributes: 
    - Name, type, age, breed, needs, vet, insurance 

    Methods: 
    - Insert pet information, edit information 

- Owner Class 
    Attributes: 
    - Name, num of pets, availability, preferences

    Methods: 
    - Add/Remove pets, add/change availibilty, add preferences

- Tasks Class
    Attributes: 
    - Pet, description of task, priority, frequency, status 

    Methods: 
    - Add/Remove task, change status, assign task  

- Schedule Class 
    Attributes: 
    - Days of the week, time blocked 

    Methods: 
    - add availibilty, add times, add tasks

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I asked AI for suggestions and missing pieces. It gave me the following suggestions: 

Owner ↔ Schedule isn't actually wired up. The UML says Owner "maintains" a Schedule, but Owner has no schedule attribute — there's no way to get from an owner to their schedule in code.
Task ↔ Owner is a dangling method. Task.assign_task(owner) exists but there's no field to store the result — nothing persists which owner a task is assigned to.
Pet has no back-reference to its tasks. Task points to Pet, but Pet doesn't hold a list of tasks, and nothing holds a master task registry outside Schedule.tasks. To find "all tasks for this pet" you'd have to scan externally.

I implemented those changes to my classes. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers time, priority, preferences, due date, aging and more. The constraints that mattered the most were the ones which were essential to the flow of the app and made the app more feasible. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the scheduker makes is that it round-robins tasks per pet rather than focusing on the next-best task. This isn't the best for optimal time allocation and does to add the most value possible. 
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI for helping me come up with code as well as debugging and refactoring. It was very helpful in making suggestions on where I lacked and what needed to be modified. Prompts with a lot of depth or specific prompts were very helpful. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

For some of my methods AI wanted to really overcomplicate things. I did not think it was neccesary in this case scenario so I avoided those suggestions. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

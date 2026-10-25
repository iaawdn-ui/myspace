# AI.101 — Introduction to Artificial Intelligence
## Narration manuscript · Module 1: What Is Artificial Intelligence?

**Degree level:** Bachelor of Artificial Intelligence and Robotics Engineering  
**Format:** Lecture narration, 16:9 visual guidance, practical activity  
**Scope note:** This is installment 1 in the planned course manuscript. The complete course target is at least 100,000 spoken words; this installment does not claim to meet that total.  
**Content policy:** This manuscript contains no faith-related instruction or devotional content.

---

## Production and visual notes

- Open on the generated documentary-style image of engineering students testing a small mobile robot in a university lab. The image is illustrative, not evidence of a particular institution or event.
- Use a restrained university palette: ivory, midnight blue, brass, and teal. Use high-contrast captions and readable technical labels.
- Diagram 1: an agent–environment loop, animated one arrow at a time.
- Diagram 2: a map distinguishing tasks, methods, and application areas. Introduce each region progressively.
- Display the phrases **goal**, **percept**, **action**, **performance measure**, and **environment** as terms are defined. Do not put the complete narration on slides.

## Learning objectives

By the end of this module, learners should be able to:

1. Give a careful working definition of artificial intelligence and explain why no single definition captures every research tradition.
2. Distinguish an AI system's task from the methods used to solve it.
3. Explain the agent–environment interaction loop using the terms percept, action, goal, and performance measure.
4. Identify examples of symbolic, statistical, connectionist, and hybrid AI without treating these categories as mutually exclusive.
5. Describe a small AI problem in terms of its environment, available observations, actions, constraints, and measurable outcomes.

---

## Lecture narration

### Opening: intelligence is a question, not a label

Welcome to AI.101, Introduction to Artificial Intelligence. In this course we will study how machines can perform tasks that, when performed by people, appear to require some combination of perception, learning, reasoning, language, planning, or decision-making. We will also examine what those systems can and cannot do, how engineers evaluate them, and how to build modest but working examples rather than relying on impressive-sounding labels.

Let us start with a question. If a phone sorts photographs into groups, is that artificial intelligence? What if a thermostat switches a heater on and off? What if a robot follows a line on the floor? What if a language model writes a paragraph? These examples are not equally capable, and they do not use the same methods. Yet each may be called AI in some setting. That tells us something important: “AI” is not a magic ingredient that can be identified just by looking at a product label. It is a broad field concerned with constructing and studying systems that exhibit goal-directed, adaptive, or problem-solving behavior.

Even that description needs care. A system can be useful without being intelligent in a human sense. A spreadsheet can calculate a large sum rapidly, but we would not normally describe the spreadsheet as understanding arithmetic. Conversely, a system can make a convincing prediction without understanding why the prediction is correct. Our task as engineers is not to settle every philosophical question before we write code. It is to define the problem, state what counts as successful behavior, choose a method, and test the result under conditions that matter.

Throughout this course, keep three questions close. First: what is the system trying to achieve? Second: what information can it use? Third: what evidence would persuade us that it works? Those questions keep our attention on engineering rather than hype.

### A working definition

For this course, use the following working definition: **artificial intelligence is the study and engineering of computational systems that perform tasks involving goal-directed behavior, learning, reasoning, perception, language, or decision-making.** This definition is deliberately broad. It describes a family of problems and capabilities, not one algorithm and not one claim about consciousness.

The word *artificial* indicates that the system is made or organized by people. It does not imply that the system is fake or useless. The word *intelligence* points to capacities such as adapting to new evidence, selecting actions, finding structure, or solving problems. But those capacities occur in degrees and depend on context. A chess program can search enormous numbers of possible moves and defeat expert players, yet it does not thereby gain general competence in cooking, conversation, or navigation. Capability in one task should not be mistaken for competence in every task.

The phrase *computational system* is also broader than “a program running on a laptop.” An AI system may include sensors, a microcontroller, a network connection, a model, a database, a user interface, actuators, safety interlocks, and human operators. In robotics, the learned model is only one component in a larger system. A camera may provide images; software estimates what is present; a planner selects a route; a controller converts the route into motor commands; and safety logic may override a command if a person or obstacle is too close. The quality of the whole system depends on the relationships between its parts.

We therefore distinguish **the task** from **the method**. “Recognize whether an image contains a bicycle” is a task. A hand-written set of visual rules, a support-vector machine, and a deep convolutional network are different methods that might be used to attempt it. Likewise, “move a mobile robot to a target while avoiding obstacles” is a task. Search, reactive control, optimization, reinforcement learning, or a combination may be methods. When someone says “this product uses AI,” ask what task is being performed and what method supports it.

### The agent and its environment

A useful organizing idea in introductory AI is the **agent**. An agent is a system that receives information about an environment and chooses actions that can change that environment. The word does not require a humanoid robot. A software assistant can be an agent when it reads incoming data and selects responses. A thermostat can be modelled as a very simple agent. A mobile robot is a physical agent whose actions affect the world through motors.

[VISUAL: Reveal the agent–environment loop. First show the environment. Add an arrow labelled “percept” from environment to agent. Add an arrow labelled “action” from agent to environment. Animate the environment changing after the action.]

A **percept** is the information available to the agent at a particular moment. A camera image is a percept. A temperature reading is a percept. A robot's combined camera, wheel-encoder, and inertial measurements can form a percept. An **action** is a choice made by the agent that can affect what happens next. It might be a motor command, a search query, a displayed recommendation, or a decision to request more information.

The **environment** is everything relevant outside the agent that can influence its observations or be influenced by its actions. For a delivery robot, this includes corridors, doors, pedestrians, floor surfaces, lighting, maps, and possibly network services. We must decide the system boundary carefully. If the robot depends on a remote server, that service is part of the operating context even if it is not physically attached to the robot.

A **goal** describes a desired condition or outcome. A **performance measure** makes success assessable. “Navigate well” is too vague. A more useful performance measure might combine successful arrival, travel time, energy use, collision rate, and the number of times the robot required human intervention. Engineering often involves trade-offs: minimizing time alone could encourage unsafe speed; minimizing distance alone could choose a narrow route that is difficult to traverse. A good performance measure reflects the real purpose and constraints of the system.

The agent loop helps us describe AI systems without assuming that they all think in the same way. At each step, the agent receives a percept, updates whatever internal representation it uses, and selects an action. The environment changes, creating new percepts. Some agents use fixed rules. Some learn a model from data. Some plan sequences of actions. Others combine these approaches. The loop is a framework for asking precise questions, not a claim that every system has a human-like mind.

### A worked example: a campus delivery robot

Consider a small delivery robot asked to carry a package from a laboratory to a reception desk. Let us describe the task before choosing technology.

The goal is to reach the correct destination with the package intact. The environment includes corridors, ramps, doors, people, furniture, lighting variation, and temporary obstacles. Available percepts may include camera images, wheel-encoder readings, an inertial measurement unit, proximity sensors, and a map. Actions might include turning the wheels, stopping, changing speed, asking a person for assistance, or reporting that the route is blocked.

Now define measurable performance. We may require that the robot reaches the correct destination, avoids contact with people and objects, does not exceed a speed limit, and reports failures rather than silently abandoning the task. We may also measure completion time, energy use, localization error, and how often a human must intervene. Notice that “arrive as quickly as possible” is not an adequate objective by itself. It leaves safety, accessibility, and reliability unspecified.

What can go wrong? The camera may be blinded by glare. The floor may be slippery. A door may be closed even though the map says it is open. Wheel slip can make encoder-based distance estimates inaccurate. A person may step into the robot's path after its last observation. The network may be unavailable. These are not unusual edge cases to hide at the end of a project. They are part of the task environment and should influence the system design from the start.

This example also shows why the term “AI robot” can be misleading. The robot needs mechanical design, power management, sensing, real-time control, software integration, navigation, safety procedures, and evaluation. A learning model may help recognize obstacles, but it cannot substitute for the complete engineering system. An autonomous robot is not just a model with wheels attached.

### Four broad traditions

AI has developed through several overlapping traditions. We will use four broad labels as a map, while remembering that real systems can combine them.

**Symbolic AI** represents knowledge explicitly using symbols, rules, logic, graphs, or structured descriptions. A rule might say, “If the corridor is blocked and an alternate route is available, replan.” Symbolic systems can be inspectable: engineers can examine the rule or trace an inference. They can work well where the relevant concepts and constraints are known. Their weakness is that real-world perception is messy, and manually specifying every relevant rule can become difficult.

**Statistical AI** treats learning and decision-making as problems involving data, probability, and uncertainty. A system may estimate the likelihood that a sensor observation belongs to a particular class, or infer parameters that explain examples. Statistical reasoning offers tools for handling noisy evidence, but its conclusions depend on assumptions, data quality, and the way uncertainty is represented.

**Connectionist AI** uses networks of simple computational units whose parameters are adjusted during learning. Modern neural networks can learn useful representations from large datasets and have become important in vision, speech, and language. They can perform impressively, but they may be data- and computation-intensive, difficult to interpret, and sensitive to shifts between training conditions and deployment conditions.

**Hybrid AI** combines approaches. A robot might use a neural network to detect people in camera images, a probabilistic filter to estimate its position, a graph-search algorithm to plan a route, and a safety controller to enforce speed and stopping constraints. Hybrid design is common because engineering tasks rarely fit neatly into a single algorithmic category.

These labels are not a ranking from old to new. They describe different representational choices and strengths. A useful system designer asks which part of the task needs learning, which part benefits from explicit constraints, where uncertainty matters, and what must be verified.

### A conceptual map of the course

[VISUAL: Build three nested bands. Band one: “Tasks” — perception, prediction, reasoning, planning, language, control. Band two: “Methods” — rules, search, probability, optimization, machine learning, neural networks. Band three: “Applications” — robotics, healthcare, manufacturing, accessibility, transport, education. Use connecting lines to show that one method can support multiple tasks and one application can combine many methods.]

This map prevents a common misunderstanding: topics such as computer vision, natural language processing, robotics, and machine learning are related, but they are not synonyms. Computer vision concerns extracting useful information from images or video. Natural language processing concerns computational treatment of human language. Robotics concerns physical or simulated machines that sense and act. Machine learning is a collection of methods that allow systems to infer patterns or improve behavior from data or experience. A robotic system might use vision and machine learning, but it also requires mechanics, control, power, and safety.

### Capability, limits, and careful claims

When discussing AI, distinguish demonstrated capability from a broad claim about general intelligence. A system is **narrow AI** when it is designed or evaluated for a restricted range of tasks, even if those tasks are complex. A language model may generate fluent text but still make factual errors, fail at reliable long-horizon planning, or behave unpredictably outside familiar contexts. A vision model may classify objects accurately on a benchmark and still fail under different lighting, camera settings, or populations of objects.

The term **artificial general intelligence** is used for a hypothetical or proposed kind of system able to perform a broad range of intellectual tasks with flexible transfer between them. There is no single universally accepted test that settles whether a system has achieved it. **Superintelligence** generally refers to a hypothetical system whose intellectual capabilities substantially exceed those of people across many domains. These terms are useful in discussions of research goals and risk, but they should not be used as casual descriptions of a product without specifying evidence and criteria.

For engineering practice, ask what was measured, on what data, under what conditions, and compared with what baseline. A high benchmark score does not guarantee safe deployment. A confident output is not necessarily a correct output. A system that performs well on average may still fail catastrophically for a small but important group of cases. Evaluation is part of the system, not an afterthought.

### Common beginner mistakes

The first common mistake is to treat AI as one algorithm. There is no universal AI procedure. Different tasks require different representations, data, constraints, and evaluation methods.

The second is to assume that learning from examples automatically produces understanding or reliable behavior. A model learns statistical structure from training data, but it can also learn accidental correlations. If every training photograph of a boat contains blue water, a model may rely on background color instead of the boat's shape. Evaluation must test whether the learned behavior reflects useful signal.

The third is to confuse automation with intelligence. A fixed timer can automate a process without adapting to new evidence. Conversely, a useful AI component may operate inside a larger system that includes simple automation and human oversight.

The fourth is to choose a model before defining the problem. Starting with “we need deep learning” is backwards. First state the task, constraints, available data, acceptable errors, and evaluation method. Then compare possible methods, including a simple baseline.

The fifth is to evaluate only whether the system appears to work in a demonstration. A single successful run is not enough. Repeat tests under varied conditions, record failures, and compare results against a baseline and the stated performance measure.

### Practical exercise: specify before you build

Choose one modest system: a room-temperature controller, a campus navigation assistant, a photo sorter, or a line-following robot. On paper, define the environment, the goal, the available percepts, the available actions, and at least three measurable performance criteria. Then list two conditions that could cause the system to fail.

For example, in a room-temperature controller, the environment is a room whose temperature changes over time. The percept is a temperature sensor reading. The action is switching heating or cooling equipment on or off, perhaps with a variable setting. The goal is to keep temperature within a desired range while controlling energy use. Performance criteria might include time spent outside the range, energy consumption, and frequency of rapid switching. Sensor placement and open windows are possible sources of error.

Do not write code yet. The purpose is to see whether the task is defined clearly enough that two people could agree on what success means. If they cannot, revise the performance measure. This small discipline saves time later because it exposes hidden assumptions before they become bugs in software or hazards in hardware.

### Knowledge check

Pause the lecture and answer these questions in your own words:

1. Why is “AI” better understood as a field of tasks and methods than as one particular technology?
2. In the agent–environment loop, what is the difference between a percept and an action?
3. Why might shortest path be a poor performance measure for a delivery robot?
4. Give one example of a system that combines symbolic, statistical, and connectionist methods.
5. What information would you require before accepting the claim that an AI system is reliable?

### Assignment and closing summary

For the assignment, write a one-page task specification for an AI-enabled or autonomous system of your choice. Include its intended users, environment, system boundary, goals, percepts, actions, performance measures, constraints, and at least three failure modes. Separate what the system must do from how you currently imagine implementing it. We will revisit this distinction when we study problem formulation and search.

Today we established a working definition of AI, separated tasks from methods, and introduced the agent–environment loop. We saw that performance measures make vague goals testable, and that real systems combine multiple technical components. Finally, we distinguished symbolic, statistical, connectionist, and hybrid approaches without treating them as competing labels that explain everything.

The most important habit from this lecture is simple: when someone makes a claim about an AI system, ask what task it performs, what information it uses, what action or output it produces, and what evidence demonstrates success. In the next module, we will examine how to turn a broad objective into a well-formed problem that an agent can actually solve.

---

## Module 1 visual asset and diagram checklist

1. **Realistic image:** university engineering lab with students testing a mobile robot; used on opener and in the robotics example.
2. **Diagram A:** agent–environment loop, labelled percept, agent, action, environment, goal/performance.
3. **Diagram B:** task-method-application map with animated connections.
4. **Table:** symbolic, statistical, connectionist, hybrid approaches; representation, strength, limitation, example.
5. **Practical worksheet:** blank agent specification grid for environment, goal, percepts, actions, performance measures, and failure modes.

# AI.101 — Introduction to Artificial Intelligence
## Narration manuscript · Module 5: Reasoning Under Uncertainty and Decision-Making

**Degree level:** Bachelor of Artificial Intelligence and Robotics Engineering  
**Course target:** At least 100,000 spoken words across the complete course series. This is a continuing installment, not course completion.  
**Content policy:** No faith-related content.

## Visual plan

- Display sensor readings as distributions rather than single perfect values.
- Animate Bayesian updating from prior belief to posterior belief after a measurement.
- Show a two-sensor corridor example with agreement, disagreement, and reliability labels.
- Plot expected utility for three robot actions: proceed, pause-and-sense, request assistance.
- Use a risk matrix with probability and consequence axes; label it as a decision aid, not a substitute for engineering safety analysis.

## Learning objectives

Learners will be able to distinguish uncertainty from randomness and missing information; interpret basic probabilities and conditional probabilities; explain Bayesian updating in a sensor example; combine evidence cautiously; compare actions using expected utility; and identify why a high average score cannot alone guarantee safe system behavior.

---

## Lecture narration

### 1. Decisions rarely begin with certainty

In our previous module, we built rules and representations for deriving conclusions from known facts. Real intelligent systems seldom receive a complete and perfectly accurate description of the world. A camera image may be blurred. A distance sensor may return noise. A map may be outdated. Two data sources may disagree. An agent must often act while its information is incomplete.

Uncertainty is not one single phenomenon. It can arise from **measurement noise**, where a sensor reports a value that differs from the true quantity; **partial observability**, where the agent cannot see every relevant fact; **model uncertainty**, where we do not know exactly how an action will change the world; **stochastic variation**, where outcomes genuinely vary; and **ignorance**, where necessary information has not yet been collected. These causes call for different remedies. Better calibration may reduce measurement error. New sensors may improve observability. More experiments may improve a model. A system should not disguise missing evidence as a precise probability unless there is a justified basis for that number.

Consider a delivery robot approaching a corridor intersection. Its camera detects a shape that might be a person, a trolley, or a shadow. The lidar suggests that something is present, but the return is weak. The map says the corridor is usually clear. None of these pieces of information is conclusive by itself. The robot needs to combine evidence, assess consequences, and select an action that is appropriate to both confidence and risk.

### 2. Probability as a language for uncertainty

Probability provides a mathematical language for representing uncertainty. A probability lies between zero and one. Zero represents an event treated as impossible within the model; one represents an event treated as certain. A value such as 0.7 can be read as a degree of belief or as a long-run frequency, depending on how the probability model is defined and used.

Suppose an obstacle detector reports whether a corridor segment is occupied. Let event O mean “an obstacle is in the path.” If the system estimates P(O)=0.2, it is not saying that a particular obstacle is exactly twenty percent present. It is representing uncertainty about whether O holds, under its model and evidence. The value should be connected to calibration and test data. If a detector outputs 0.9 confidence but is correct only six times out of ten on comparable cases, the confidence is poorly calibrated.

A **conditional probability** describes uncertainty after evidence is known. P(O | S) means the probability of an obstacle given sensor observation S. Evidence can change a belief. A camera classification, lidar return, or prior map expectation can all influence the estimate, but they should not be treated as independent if they share a cause or data source.

[VISUAL: Show a probability bar for “path occupied.” Start with prior estimate 0.15, then update after a camera alert, then after an independent lidar return. Explain each change and label all values illustrative.]

### 3. Bayesian updating

Bayes’ rule gives a way to update a probability when evidence arrives. In compact form, P(H | E) = P(E | H) P(H) / P(E). Here H is a hypothesis, E is observed evidence, P(H) is the prior probability of the hypothesis, P(E | H) describes how likely the evidence is if the hypothesis is true, P(E) is the overall likelihood of the evidence, and P(H | E) is the updated or posterior probability.

Let H mean “the corridor is blocked.” Suppose, for illustration, that the prior probability is 0.10. A camera detector flags an obstacle on 90 percent of blocked-corridor cases, and it produces a false alarm on 15 percent of clear-corridor cases. If the detector flags an obstacle, the posterior probability is not automatically 0.90. We must also account for how often corridors are blocked before seeing the alert. Using the values as illustrative assumptions, the unnormalized blocked contribution is 0.90 multiplied by 0.10, or 0.09. The clear contribution is 0.15 multiplied by 0.90, or 0.135. The total probability of a flag is 0.225. The posterior probability of a blockage given the flag is therefore 0.09 divided by 0.225, which equals 0.40.

This result may feel surprising. The detector is fairly sensitive, but blockages are uncommon in the assumed operating context, and false alarms occur. The observation raises the estimated blockage probability from 0.10 to 0.40, but it does not establish certainty. We should not confuse “the detector is 90 percent sensitive” with “there is a 90 percent chance this corridor is blocked.” These are different conditional probabilities.

The numerical result depends on the assumptions. If the corridor is known to be under maintenance, the prior probability may be higher. If the camera is obscured or the detector has degraded, its sensitivity and false-alarm rate may differ. A probabilistic output is meaningful only when its model and operating conditions are understood.

### 4. Combining sensor evidence

Robotic systems often combine multiple sensors. A camera can provide semantic information; lidar can provide geometric distance; wheel encoders estimate motion; an inertial sensor measures acceleration and rotation. Each sensor has different limitations. Fusion can improve estimates when the evidence is complementary and the fusion assumptions are appropriate.

Suppose the camera marks an object as a person and lidar measures an obstacle at the same position. Agreement increases support for the hypothesis that a person is in the path. But if the camera and lidar both depend on the same mistaken coordinate transform, their errors may be correlated. Treating them as independent would overstate confidence. Likewise, two classifiers trained on the same images may fail on the same unusual lighting conditions.

A system should preserve timing and coordinate information. A camera frame from one moment and a lidar scan from another may refer to different physical situations if an object is moving. A range reading and a visual detection must be aligned to a common coordinate frame. Before fusing evidence, ask: Do the measurements refer to the same time? Do they refer to the same location? What are their known failure modes? Are their errors independent, correlated, or unknown?

[DIAGRAM: Two sensor streams enter a fusion block. Add timestamps and coordinate-frame labels. Show a confidence estimate and an uncertainty band at the output, not just a single object marker.]

When evidence conflicts, the system should not simply average incompatible values. It may need to check sensor health, inspect freshness, seek another observation, or enter a conservative state. The response depends on the hazard and mission. For a low-risk recommendation, uncertainty might be reported to the user. For a robot moving near people, it may be appropriate to slow down or stop until the path is clearer.

### 5. Belief states and partially observable tasks

In a partially observable task, the agent may not know the exact current state. It can maintain a **belief state**: a probability distribution over possible states. For example, a robot may estimate that it is at Junction A with probability 0.75, at Junction B with probability 0.20, and somewhere else with probability 0.05. A new landmark observation can update that distribution.

A belief state is useful because it makes uncertainty explicit. Instead of pretending that the robot knows its exact position, the system keeps track of multiple plausible locations. It can choose an action that both makes progress and obtains information. A short rotation may improve a camera view. Moving to a safe landmark may reduce localization uncertainty. This is an example of **active perception**: the agent acts partly to improve its knowledge.

Not every system needs a full probability distribution over every possible state. The representation may be simplified to confidence ranges, categorical uncertainty, or a set of plausible hypotheses. The right model depends on the task, available computation, and consequences of error. However, the design should not silently collapse uncertainty into certainty merely because a downstream module expects a single value.

### 6. Decision-making and expected utility

Estimating what may be true is not yet the same as choosing what to do. Decision-making combines beliefs with consequences. A common introductory framework is expected utility. For an action, list possible outcomes, assign each outcome a probability under the model, and multiply by a measure of value or cost. The expected value is the sum across outcomes.

Suppose the robot can choose among three actions: proceed slowly, pause and collect another sensor reading, or request assistance. Proceeding may save time if the corridor is clear but create a serious hazard if it is blocked. Pausing costs time but may reduce uncertainty. Requesting help may be safest but impose a delay and use operator resources. The best action depends on the probabilities, the cost of outcomes, and any hard safety constraints.

Expected utility is useful for comparing choices, but it can be misused. A rare catastrophic outcome can be hidden by a favorable average if the consequence scale is poorly chosen. Safety requirements should not always be reduced to a single expected score. Some limits may be hard constraints: for instance, the robot must not move above a tested speed in a crowded area, regardless of the expected time benefit.

The model should also reflect who bears the cost. A route that is convenient for the robot may obstruct wheelchair access or cause people to move around it. A system’s objective is not neutral merely because it is written as a mathematical expression. Engineers must identify stakeholders and evaluate effects on them.

### 7. Worked decision example

Let the robot estimate that the corridor is blocked with probability 0.40 after a camera alert. It has a validated slow-speed behavior. For a simplified classroom example, assign a cost of 1 unit to a short delay, 4 units to requesting an operator, and 100 units to a collision or unsafe contact. These numbers are not universal and are not an approved safety model; they are a way to practice reasoning.

If the robot proceeds and the corridor is actually blocked, the high consequence dominates. If it pauses and gets another observation, it pays a small delay while potentially reducing uncertainty. If the additional reading remains inconclusive, it may ask for assistance. A rational policy may therefore choose to pause and sense again rather than immediately proceed or always request a person.

Now change the assumptions. If the robot is in a protected test environment with a soft foam obstacle and low speed, the consequences differ. If it is carrying fragile medical material through a busy corridor, the consequences and acceptable uncertainty differ. The same probability estimate can support different actions because decisions depend on both likelihood and consequences.

The lesson is not “always choose the most cautious action.” Excessive caution can make a system unusable and can create other risks, such as blocking an emergency route. The lesson is to make uncertainty, consequences, constraints and fallback behavior explicit, then validate the decision policy in the actual operating domain.

### 8. Practical laboratory: sensor fusion and action choice

Create a small Python simulation of a robot deciding whether to cross a corridor. Generate cases with a known hidden state: clear or occupied. Simulate camera and lidar observations using different sensitivity and false-alarm rates. Begin with conditional independence as a simplifying assumption. Implement a Bayesian update and compare its estimated probabilities against observed frequencies.

Split the data into development and evaluation sets. Check calibration by grouping predictions into ranges and comparing predicted probabilities with the fraction of occupied cases in each range. A system that predicts 0.8 on many cases should be correct roughly 80 percent of the time on comparable cases if it is well calibrated. Report uncertainty in the evaluation itself, especially when the sample size is small.

Next, introduce correlated sensor errors. For example, make both sensors more likely to fail under heavy glare or reflective surfaces. Compare the naive independent fusion calculation with a model that includes the shared condition. Observe how the naive calculation can become overconfident.

Finally, implement a simple action policy. Use a safety threshold to decide whether to proceed slowly, pause for another observation, or request assistance. Document why you chose each threshold and test behavior near the threshold. Include at least one case in which the correct outcome is “uncertain; gather more evidence” rather than a forced yes-or-no answer.

### 9. Common mistakes

One mistake is to confuse sensitivity with the probability that a detection is correct. Sensitivity is P(positive test | condition present). The probability we often want is P(condition present | positive test). Base rates matter.

A second mistake is to multiply sensor probabilities as if all sensors were independent. Shared hardware, shared training data, shared weather conditions and shared coordinate errors can create correlated failures.

A third mistake is to display a probability with many decimal places when the underlying evidence is weak. Numerical precision is not the same as epistemic certainty.

A fourth mistake is to optimize expected cost without checking catastrophic outcomes or non-negotiable constraints. Average-case reasoning should be paired with safety analysis and scenario testing.

A fifth mistake is to treat uncertainty as a defect that must be hidden. A reliable agent should sometimes communicate uncertainty, stop safely, ask for another observation or hand control to a person.

### 10. Knowledge check and assignment

Explain the difference between P(alert | obstacle) and P(obstacle | alert). Why do base rates affect the interpretation of a sensor alert? What is a belief state? How can sensor errors become correlated? Why might “pause and sense again” be a rational action? What is the limitation of selecting actions by expected utility alone?

For the assignment, extend the laboratory simulation with a third sensor or a sensor-health indicator. Compare an independent-error model with a correlated-error model. Produce reliability plots, a confusion matrix, and a decision table. Explain which assumptions are supported by data and which remain illustrative. End with a short safety note describing when the system must defer to a conservative fallback.

### Module summary

We introduced uncertainty as a normal feature of intelligent systems, not a rare exception. We distinguished several sources of uncertainty, used conditional probability and Bayes’ rule to update beliefs, and examined sensor fusion, belief states and expected utility. We emphasized that evidence quality, timing, correlation, consequence and hard safety constraints all matter. In the next module, we will use structured goals and actions to plan sequences, while keeping uncertainty and replanning in view.

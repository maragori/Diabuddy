## DiaBuddy - Developing a knowledge-based system for T1 Diabetes disease management

### T1DM
Type 1 Diabetes Mellitus (T1DM) is a chronic metabolic disorder, characterized by abnormal blood glucose regulation patterns, with which only 5-10\% of all diabetes cases are being accounted for. The defining component in T1DM is the immune system related destruction of pancreatic $\beta$-cells, responsible for the secretion of insulin. Type 1 diabetes requires lifelong treatment consisting of blood glucose monitoring, exogenous insulin administration, meal planning as well as suffering from disease management related complications and comorbid conditions. Poor glycaemic control is one of the greatest risk factors of diabetes related complications and has been a focal point of an ongoing bulk of research on the disease. Recent advances in continuous glucose monitoring (CGM) have enabled real-time CGM, which aims at improving patient self-care. This technology however still remains limited because of the delays between detection of glucose levels in interstitial fluid compared to venous levels (5-10 min) as well as the delayed onset of action of rapid insulin (10-30 min). 

This motivates the development of an external, knowledge-based system in the form of a smartphone application that helps patients monitor their blood glucose levels and presents them reasoned, on-time recommendations on adequate amounts of insulin/glucose to inject/ingest. It can relieve patients of the burden of calculating and assessing suitable insulin doses and at the same time teach them how food, sports and blood glucose concur. 

Input to the system are the subcutaneous glucose level invasively measured by the patient's CGM, several parameters of physical activity measures by the patient's smartwatch and finally information about food intake, which the patient inserts manually to the proposed smartphone application. The system output should be an accurate recommendation on the amount of insulin to inject at a certain time as well as diagrams or text explaining the occurrence of the recommendation.


### Implementation
This repo has been created to demonstrate the effectivity of the system in a controlled environment, and thus should only be seen as a proof of concept. A demo script is included that allows to experiment with input parameters to investigate limitations of the current implementation (see section Demo).

#### General structure
To maintain the structure of the knowledge system as developed using the CommonKADS approach, we created five different classes: a task class, three inference classes, and a knowledge base class. Besides those main classes we used two helper classes which were responsible for generating message strings as well as storing the series of predictions made by the system. Each of the main classes implemented the methods that corresponded to the responsibilities as described by the knowledge model. Because the goal use of our system is a constant monitoring loop, we built a rough draft of a controller instance on top of this hierarchy that creates a list of sample data observation that iteratively are fed into the pipeline. We also implemented an interactive console application that each iteration generates some output, an intervention message when needed and queried the user whether action should be taken (eat x grams of sugar/ inject x units of fast insulin). Those actions were then incorporated into the next iteration of the system. 


#### Predicting future blood glucose concentrations
A major challenge of the system was the implementation structure of the blood glucose prediction. The mathematical functions that describe the impact of certain factors on blood glucose levels can only be described on a conceptual level as the factual values of those functions depend on too many factors that cannot be assessed, e.g. individual patient factors (sleep quality, mood, hormones), time of the day, temperature and many more. Expecting patients or even trained medical specialist to quantify those functions exactly would be absurd. In order to nevertheless extract the valuable expert knowledge we decided upon a strategy that approximates those functions in a way that allows us to directly relate the parameters of those functions to intuitive expert knowledge.

![Alt text](images/increaseBGC.png?raw=true "Title") ![Alt text](images/cumulativeincreaseBGC.png?raw=true "Title")

After the first interview with our experts we knew that the increase in blood glucose levels should approximately follow the function as shown in left in the figure above. In order to bring it conceptually closer to the absolute change in blood glucose levels we compute the cumulative increase as shown in the right figure. Albeit more intuitive to understand, it still did not allow to extract meaningful parameters from the function. This however could be achieved, using a simple piece wise linear function approximation of that function, as shown below. On a conceptual level, this function can be described using three parameters: the delay of the onset of the effect, the total increase at the end of the effect and the duration of the effect. All three of those parameters describe the function in terms that can easily be described by diabetes experts. 

<p align="center">
  <img src="https://github.com/maragori/Diabuddy/blob/master/images/approx.png" alt=""/>
</p>


Using those linear functions, we were able to describe all rule types for factors that increase or decrease the blood glucose levels. In order to account for the delaying effects of other factors, i.e. uptake of protein or fat, we just needed to alter the given effect function such that the first part of the linear function (effect=0) was prolonged. This approximation system thus allowed us to describe and combine all factors that influence blood glucose level in a simple and intuitive way. The linear approximation also enabled for a straightforward implementation of the general prediction model given a set of influence factors in each iteration of the monitoring loop. In order for this approximation to work we also had to assume that the case of multiple factors influencing blood glucose could be described using an additive model without any interaction between those factors. Given this assumption we could simply add all influences and the current prediction of the blood glucose timeline, rendering us with an aggregated piecewise linear function describing both the blood glucose prediction function and all factors influencing blood glucose.


<p align="center">
  <img src="https://github.com/maragori/Diabuddy/blob/master/images/multiple_influences.png" alt=""/>
</p>


#### Code implementation
Given the additive model approximation, the implementation into software was straightforward. Both predicted blood glucose curves and cumulative influences were segmented into 10 minute timesteps and stored in arrays. This thus does not yet realize the intended event-driven monitoring system, but rather a time based iteration approach that each timestep aggregates data from the past iteration period. Simplifying the monitoring frequency however allowed to construct more intuitive and easy to follow example scenarios and should not limit the generalization of this prototypical system to a more complex setting. Each iteration of the monitoring loop the output blood glucose array from last iteration would be passed to the system, new influence arrays were created according to the knowledge model and aggregated into the blood glucose array. After each iteration all influence arrays were discarded and only the resulting blood glucose array was passed on further down the pipeline. 

## DEMO
To run the demo, clone the repo and run demo.py from console. Requires only numpy, matplotlib and argparse.
Two scenarios are available:

#### Scenario 1
Type 1 diabetes patient Anna eats a medium-sized banana for breakfast and drinks black coffee. This meal contains 89 calories. The nutritional values are composed of 1.1g protein, 12.8g fast carbohydrates, 10g complex carbohydrates, and 12.2g sugar. After entering the nutritional data into the system, it advises her to inject 3 units of fast insulin, which she does after 10 minutes.

#### Scenario 2
After work. type 1 diabetes patient Peter decides to perform an intensive, 30-minute running workout followed by another 30 minutes of moderate walking. After the high intensity workout, he injects 2 units of fast insulin to counteract the effects of the workout. In order to strengthen himself, he eats a chocolate bar after 40 minutes, during his moderate exercise unit. The same contains 250 calories, 13g fat, 31g (fast) carbs and 4g of proteins.


Demo options:

-s choose scenario 1 or 2 (int)

-c set starting blood glucose concentration (int)






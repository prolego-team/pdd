# About
Welcome! You can quickly build powerful applications with large language models (LLMs). Unfortunately, achieving transparency can be tough—knowing where your application excels, avoiding critical errors, making improvements, and predicting readiness.

That’s where performance-driven development (PDD) comes in. PDD gives you the clarity needed to confidently manage and deploy GenAI applications.

### GenAI Challenges: Current Situation vs. Improvement with PDD

| **GenAI Challenge**   | **Your Current Situation**                                       | **Better With PDD**                                                      |
|-----------------------|-----------------------------------------------------|-------------------------------------------------------------------|
| **Performance**       | You rely on general observations from demos or examples | You get specific, quantified insights at the task level            |
| **Cost and Latency**  | You can only provide general estimates, optimized at the app level | You forecast cost and speed and optimize at the task level |
| **Improvements**      | You "iterate by feel" based on general customer feedback | You optimize based on specific, measurable performance limitations                 |
| **Robustness**        | You experience inadvertent breaks or degradation during improvements | You ensure systematic improvements with consistent performance     |
| **Schedule**          | You face unpredictable schedules due to continuous experimentation | You follow a predictable schedule based on ongoing system improvements |

## Contributions


Thanks for taking the time to review. Any feedback on any section is helpful, however small.

# Quickstart
Large language models (LLMs) enable rapid development of powerful solutions, but they produce inconsistent and unpredictable results. You can quickly produce a proof-of-concept that mostly works, but you’ll struggle to pinpoint where it’s succeeding, where it’s failing, how to improve it, how to keep it on track, and how to predict when you’ll be done. In other words, you—and your leadership—will quickly become frustrated due to the lack of transparency in your LLM project. Here’s how you can get your LLM project on track.

Segment your AI solution—the system components that interface with LLMs—from everything else and assign a team of AI Systems Engineers to work on it as shown in Figure Q1.

The AI Systems Engineers will build the AI solution with a Performance Evaluation Framework. This framework will give you transparency into your LLM project, and it consists of four parts as illustrated in Figure Q2:

1. A representative set of data and tasks that cover the scenarios the LLM will encounter.
2. The AI Solution. Interfaces to LLMs, prompts, tools, agents, orchestrations, and data preparation. This is the deployable AI Solution from Figure Q1.
3. An evaluation workflow generates performance results based on your representative data and task set.
4. A performance report that reveals how well your solution is working, how much it costs, and how fast it runs.

Get feedback from your customer with the performance report, and iteratively make your performance framework better. You’ll deploy your AI solution when it works well enough.

While this approach may sound complex, it’s simply a different way of working on a project powered by LLMs.

You can build your first Performance Evaluation Framework in 15 minutes using generated data and spreadsheets.

I call this new approach Performance-Driven Development (PDD) because it prioritizes getting the LLM to perform as needed.

# Why GenAI Needs a New Approach
AI is ushering in a new golden era for software engineering, but two major obstacles remain. First, AI is still in its infancy, and LLMs are not yet adept at solving most business problems. LLMs are good at processing simple text documents, but they struggle to interact with databases or make complex reasoning decisions. Fortunately, LLMs are getting smarter, faster, and cheaper exponentially, and many of these challenges may be resolved within the next two years.

The second challenge is the lack of effective methodologies for developing LLM solutions. Many teams are repurposing existing tools with mixed results. While frameworks like Ruby on Rails and Django revolutionized data-driven web development, LangChain and similar tools are currently hindering efficiency. Agile and Design Thinking, focused on adoption risk mitigation, do not equip teams with the practices needed to ensure LLMs function as intended.

As a result, many LLM projects are stalled. Teams struggle with a lack of transparency into how their solutions function and lack the tools to determine whether they should refine models through fine-tuning or more complex prompt orchestration. They can’t predict when their solutions will be good enough or how much they will cost. Worse, many are investing time and resources into building software that may be obsolete within two years.

## Your GenAI Project will Get Stuck
Your leadership has finally approved funding for your first generative AI project. You gather data and begin building your proof-of-concept (POC). Here’s what to expect over the next 3-6 months:

- Rapid early results will excite customers, but progress will slow as engineers disagree on the best path to make improvements.
- Stakeholders will ask, “How do you know it works?” and “When will you be done?”—and you won’t have clear answers.
- A team member will unintentionally degrade the solution, leading to weeks of troubleshooting. Progress will slow further as the team works to prevent similar issues.
- Customers will lose interest due to a lack of visible progress, and stakeholders will grow impatient as you struggle to explain where the system stands and when it will be completed.

And then … nothing good happens for you or the project because you’re stuck.

Unfortunately, even experienced software engineers and data scientists are finding themselves stuck because traditional methodologies and tools don’t address the challenges of GenAI.

## LLMs are Powerful Technologies with Unique Risks
Traditional software development is notoriously challenging. Business logic must be embedded in arcane languages like C or Python to instruct computers on how to perform tasks. This code doesn’t generalize well, and even the smallest error can render a system useless. Over the past 50 years, we’ve developed methodologies, tools, and frameworks to make this process more efficient. Agile and Lean Startup methodologies help us avoid building products nobody wants, while frameworks like Ruby on Rails reduce the amount of code we need to write.

Generative AI, particularly through large language models (LLMs), offers a more efficient way to build software because it has knowledge of the world and can complete tasks with general direction.

For example, I can instruct an LLM to “remove the comments from this Python script,” and it will do so flawlessly because it understands what a Python comment is. This is far more efficient than writing 20 lines of Python to search for ‘#’ and ‘//’ characters and carefully delete them without affecting the rest of the code.

Generative AI will ultimately enable smaller teams to build more powerful software in less time. However, this power comes with a trade-off: LLMs are stochastic. For any given task, an LLM may produce different results each time or even hallucinate—generating convincing responses that are incorrect.

## Key Differences Between Traditional Software and GenAI
| Traditional software | GenAI |
| -------------------- | ----- |
| Developer interface   | Compiler or interpreter | LLM API |
| Interface behavior    | Deterministic           | Stochastic |
| Primary risk          | Market / Adoption       | Technical |
| Solution logic        | Written in code         | Inherent in LLM |
| Rate of change        | Linear                  | Exponential |
| Frameworks / practices| Mature                  | Non-existent |
| Iteration cycle time  | Weeks (Sprints)         | Hours |

**Table 1 - LLMs are a new programming interface with different risks than traditional software.**

You’re stuck because you’re trying to apply traditional software product management and engineering principles to GenAI projects. Here is how these differences manifest:

### Ensuring system resilience
In traditional software engineering, unit, functional, and integration tests ensure that deterministic functions produce specific outputs from specific inputs. While you still need tests in GenAI to prevent bugs in your Python libraries, a different approach is required to ensure LLMs perform as desired.

Just as a developer can write a software function in many ways, LLMs can produce correct results through various approaches. Moreover, LLM outputs don’t conform to simple pass/fail evaluation criteria. An LLM can generate a result that is mostly correct and still effectively solve the business problem. Conversely, slight wording or formatting changes in a prompt that appear identical to a human evaluator can cause a system to fail catastrophically.

### Planning for technology changes  
Best practices and tools in traditional software engineering don’t evolve as rapidly. Whether you build your product with Ruby on Rails Version 6 or 7 won’t significantly impact its success. A great programmer using a 10-year-old tech stack will still outperform an average programmer using modern tools.

In contrast, the difference between LLM versions, like GPT-3.5 and GPT-4, is so significant that it could either improve your product by 90% or render it obsolete. No level of developer skill can bridge the gap between generating text with GPT-2 and GPT-4.

### Providing transparency  
Providing transparency in traditional software projects is challenging, which is why the industry has developed methodologies like Agile, tools like Jira, and roles like Scrum Master to offer some degree of predictability. Even with these, it remains difficult for project managers to predict when software projects will be completed and how well they will perform. GenAI projects are even more complex.

With no clear way to predict how an LLM will perform, teams struggle to describe how well their solution is working. Unlike traditional software, you can't predict when a GenAI project will be complete because you don’t know what obstacles you’ll face or how you'll overcome them. Additionally, it's difficult to quantify the effectiveness or improvement of your GenAI project.

# Performance-driven Development Methodology

## Logically Isolate AI in Your Systems

### Tightly integrating LLM API calls creates scaling challenges
Many teams begin their GenAI projects by adding LLM API calls from within their existing code libraries as shown in Figure X. While this is a quick way to start, and it works fine for simple, low-risk tasks, it creates scaling challenges:

- It obscures what the LLM is doing.
- It prevents you from rapidly testing and integrating new LLMs and approaches.
- It creates code redundancy.

### Create Interfaces with Your AI Solution
A more effective approach is to isolate the AI components of your system—such as LLM interfaces, prompts, prompt orchestration agents, and tools—from the rest of the system's architecture as illustrated in Figure Y.

This design has several scaling advantages:

- It allows you to build a team of AI systems engineering specialists.
- It lets you offer similar AI capabilities, such as text processing, across the company.
- It allows you to more quickly leverage new LLMs or approaches.

Finally, it allows you to create transparency by building an LLM performance evaluation framework.

### Avoid LangChain and Similar Frameworks
At best, frameworks like LangChain will make it slightly easier to solve the easy problems. Unfortunately, they further obscure what your LLM is doing and reduce your transparency. We have yet to encounter an experienced team that recommends them for production.

## Create a Team of AI Systems Engineers

### LLMs are a new programming interface that requires specialization
Building solutions with LLMs isn’t traditional data science, programming, or machine learning. LLMs are a new programming interface, and it takes 6-12 months to become proficient. We call this role an AI systems engineer, combining a data scientist’s experimental mindset with a systems engineer’s big-picture view.

Engineers from data science, software engineering, or systems engineering backgrounds can transition into this role with time and dedication. Even product and project managers with minimal technical experience are successfully building LLM-based solutions.

### Assign a dedicated engineering team to focus on LLM optimization
The AI Systems Engineers will build the components that optimize the LLM’s performance as shown in Figure Z.

The AI Systems Engineers will build and optimize the AI Solution using the performance evaluation framework.

## Build a Performance Evaluation Framework
You need a new approach for building solutions with LLMs, one that provides you with granular visibility into how well your solution is working. A performance evaluation framework as illustrated in Figure 2 provides this transparency.

It has four components:

1. A representative set of data and tasks covering the scope of the problem.
2. The AI solution you will deploy.
3. An evaluation workflow runs the representative set of data through your solution and evaluates its performance on the tasks.
4. A performance report showing how well your solution works and calculates key metrics.

### Representative set of data and tasks
The foundation of your framework is a representative set of data and tasks tailored to the solution you’re building. Table 2 lists examples for common LLM solutions.

| LLM Solution           | Data                   | Tasks                                            |
| ---------------------- | ---------------------- | ------------------------------------------------ |
| RAG                    | Source documents       | Questions and expected answers                   |
| Document classification| Set of documents       | Expected classification of each                  |
| LLM to SQL             | Populated database tables | Questions and expected results from SQL queries |

**Table 2 - Examples of Performance Framework data and tasks for different LLM Solutions. The data and tasks are designed to provide granular transparency into how well your system is working.**

This set should cover the full scope of the problem space and be used to evaluate the solution's effectiveness. If hallucinations or mistakes are concerns, create tasks specifically designed to test how the solution handles these issues.

Continuously update and revise this set as long as the solution is in production, and generate new tasks when adding data, changing tasks, or encountering operational anomalies. When legal concerns arise, such as "what if x occurs...," create a task to demonstrate how the solution addresses it.

Developing a representative set requires significant experience, experimentation, and iteration. The key challenge is determining the right quantity and type of tasks to cover common scenarios and critical edge cases without generating redundant files that don't enhance system robustness.

Some teams also use generated data to mitigate security and legal risks, enabling faster and more efficient testing of new LLMs.

### AI Solution
The AI solution is the software that transforms the input data into an output by interacting with the LLM. Examples are prompts, data processing scripts, interfaces, prompt orchestrations, agents, and tools.

The AI Solution is what you will deploy into production as illustrated previously in Figure 1, including the interfaces to other system components.

### Evaluation workflow
You need a scalable way to measure how well your system is performing by running the representative tasks and data sets through your solution and comparing the expected vs the actual outputs.

Table 3 lists three common options teams are currently using.

| Evaluation option | Description                                               | Pro                                                  | Con                                      |
| ----------------- | --------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------- |
| Manual inspection | Developer visually inspects expected and actual outputs   | Easiest to start. Most likely way to ensure accuracy. | Slow. Won’t scale.                       |
| Scripts           | Python scripts detecting presence or absence of words     | Relatively easy to set up. Good at catching obvious errors. Runs fast. | Tedious to maintain. Can miss edge cases. |
| LLMs              | Send the expected and actual results to an LLM with instructions to evaluate. | Accuracy of manual inspection at scale. | LLMs are still not very good at it.      |

**Table 3 - Three techniques for evaluating your AI Solution’s performance.**

OpenAI and others have advocated for using LLMs for your evaluation. In practice, most teams have found the combination of human review, python scripts, and LLMs to be necessary.

Additionally, your evaluation workflow will gather key system metrics such as cost, token count, and latency. It must also have a means of providing transparency into the LLM’s sensitivity, such as running the LLMs at different temperatures to generate a confidence interval.

### Performance evaluation report
Finally, your framework will have a performance evaluation report that gives you transparency into your solution. The report should provide granular performance visibility into every task in your set and higher-level solution metrics.

The evaluation report typically contains the following for every task:

- A confidence score comparing the actual vs expected performance by the LLM.
- The LLMs used.
- Cost or token count.
- Latency.
- Notes or recommendations for improving performance.

Figure 2 has a simple example.

Spreadsheets are perfectly fine for performance evaluation reports. You can import CSV files generated by Python scripts as new tabs, and both engineers and customers can quickly do analysis and provide feedback.

## Iteratively Optimize your Solution with Customers
Figure 3 illustrates the conceptual workflow for leveraging PDD in your existing processes. Isolating the AI Solution from the rest of the system architecture allows the AI systems engineers to work at a faster velocity and focus on the risks associated with stochastic behavior.

Build your performance evaluation framework:

1. Generate a representative set of data and tasks you want the LLM to perform.
2. Create the AI solution to solve them.
3. Evaluate how well your solution performs against expectations.
4. Generate a performance report.
5. Review your performance report with your customer and get feedback.
6. Repeat steps 1 and 2 until your solution performs well enough.
7. Create interfaces between your AI solution and the rest of your system workflow.
8. Deploy your solution through your existing processes.

Continue this process, and increasingly offload more work to the LLM as AI improves.

### Best practices
#### Prioritize tasks that LLMs can perform well today
AI is getting better at an exponentially fast rate, and tomorrow’s LLMs will be better at solving your problems. Teams have wasted months of engineering work optimizing their solution LLM limitations like speed or reasoning power, only to discard this work when better LLMs and hardware is released. Prioritize the tasks the LLM can perform without customization before tackling harder ones.

#### Start with the easiest optimization choices
Of the available 13 LLM optimization techniques, begin with easier ones like optimizing prompts or testing different LLMs. Only pursue complex solutions like fine-tuning or agents when easier approaches are insufficient.

# Example: Get a RAG Solution on Track
Let’s walk through a simple example.

## Goal: policy chat for employees
Your company has numerous internal policy documents covering topics like travel, vacations, and IT security. These policies are managed by different departments, forcing employees to sift through multiple documents to find the answers they need. As a result, they often end up emailing HR for assistance.

To address this, HR has requested that you build a chat interface that allows employees to get answers to common questions without needing to contact HR directly.

## A good start with a basic RAG demo
You opt to build a retrieval-augmented generation (RAG) solution for your employee policies like Figure 4. A subset of the policy documents is converted into embeddings and stored in a vector database. You then set up the interaction with the LLM and configure Gradio as the user interface.

**Figure 4 - A basic RAG workflow for unstructured text documents.**

You configure the demo to allow employees to ask policy questions and receive an answer accompanied by references to the relevant source documents.

### First feedback from HR
HR loves your demo and immediately sees how it will reduce their workload. They begin asking common questions about vacation policies, performance reviews, and travel, and provide initial feedback. You start taking notes:

- The demo successfully answers basic questions covered by the indexed policies. However, it struggles with questions related to unindexed policies and occasionally hallucinates, generating incorrect answers. You advise HR to limit their queries to the indexed policies.
- Some answers are misleading or confusing, but HR notes that the policies themselves are unclear on these points. In practice, HR often relies on state employment laws and current industry best practices to clarify these issues.
- When HR asks more complex questions, the solution fails to provide accurate answers. In some cases, it misses information from tables and diagrams that were ignored during setup. In others, it struggles to reason through information spread across different sections of the documents.
- HR also raises a concern that legal might not approve employee use of the solution until there are assurances it won’t expose the company to liabilities.

## And … you’re stuck
After reviewing your notes, you're uncertain about the next steps. HR clearly wants the solution, but you're unsure how to develop a plan for production deployment.

The biggest challenge is defining the problem more clearly. You don't yet know the specific questions employees will ask or the most accurate answers to provide.

You have several ideas for improvements, such as adding more policies, parsing documents by page instead of paragraph, refining system prompts, incorporating additional sources like state employment laws, experimenting with different LLMs, fine-tuning the LLM, capturing data from complex structures like tables and figures, and using agents to handle more complex reasoning. However, you're unsure how to prioritize these options.

Given the ambiguity, you decide to build a performance evaluation framework.

## Building your performance evaluation framework

### Generate a representative set of data and tasks
You start by building a spreadsheet of some expected questions and correct answers:

| Question                                                          | Expected Answer                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| If I am late for work, can I make up the time from my lunch break?| No. The handbook mentions that breaks from work are a privilege and cannot be used to account for an individual's late arrival or early departure. |
| I want to work another part time in the evenings and weekends. Is this allowed? | Yes, if you notify your manager and HR and the second job does not interfere with your primary job here. You must complete the "Disclosure of Outside Employment" form. |

HR reviews your questions and confirms the correct answers.

### Create an evaluation workflow
You build scripts and configuration files to do the following:

1. Send the questions to your solution
2. Generate an actual answer.
3. Calculate key metrics like cost and speed.
4. Record the relevant section from the policies.
5. Store the results to a CSV file.

### Generate a performance evaluation report
You import the evaluation results into Excel, visually analyze the results, and record a confidence score (High, Medium, Low) based on your reading of the policies.

**Performance evaluation report**

| Question                                                                                     | Expected Answer                                                                                   | Actual answer                                                                                   | Confidence | Source                                           | Metrics         |
| -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------ | --------------- |
| If I am late for work, can I make up the time from my lunch break?                           | No. The handbook mentions that breaks from work are a privilege and cannot be used to account for an individual's late arrival or early departure. | No. Breaks from work are a privilege and cannot be used to account for an individual's late arrival or early departure. All employees are expected to adhere to their scheduled work hours… | High       | Section 5: Attendance and Break Policies        | 2.3s, $.0003    |

## Productive feedback
Instead of presenting a demo, you share your performance evaluation report with HR. This time, they offer specific feedback on the questions, expected answers, and confidence scores.

HR also provides insights into the reasons behind poor performance, such as missing source material, ambiguous questions, or general confusion. With this feedback, you quickly identify the most impactful improvement: embedding entire sections of the policy documents instead of just paragraphs.

Your next weekly project status report is well received. Instead of sharing general updates about demos and testing, you present the performance report and explain your decision to change the embedding workflow before exploring more complex options.

## Continuous improvement through PDD
You quickly get into a productive workflow with HR. They review your performance report in Excel, add questions, review your results and provide context. They also add a few high-risk questions that could create liability concerns from legal.

You make rapid solution improvements by investing in straightforward changes such as adding documents, improving embeddings, and tweaking prompts. You also continuously improve your evaluation workflow and build scripts to automatically generate results. The performance framework allows you to make changes with confidence.

## You’re no longer stuck
PDD has effectively addressed your primary challenges:

- You now have transparency into where your solution is performing well and where it’s falling short.
- You have a method for managing the stochastic behavior of LLMs.
- You can focus on the highest-impact improvements rather than relying on trial and error.
- You can detect potential issues in your solution early.

Additionally, you’ve gained the confidence of your leadership. You’re able to demonstrate consistent progress, provide clear transparency, and estimate when your solution will be ready for production.

# Acknowledgments
LLMs are new, and unfortunately, separating the AI hypesters and the real practitioners isn’t easy. Here are some pros whose work I admire who helped make this document better.

Thank you Justin Pounders, Craig Dewalt, Shanif Dhanani (founder of Locusive),…
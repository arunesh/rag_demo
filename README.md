# Week 2 lab work


### Milestone 8 exploration results 

Dataset: Codepath strategic planning document, 54 pages.

Used OpenAI GPT 4 Turbo and Claude 3.5 Sonnet as LLMs. Alternated between them as query LLM and LLM-as-a-judge.

Dataset consists of 267 QnA pairs off the "Codepath" document. 

- With Claude as query LLM and GPT4 Turbo as judge, accuracy: 68.1 percent.

- With Claude as query LLM and judge, accuracy: 68 percent.

- With GPT4 Turbo as query LLM and Claude as judge, accuracy: 40.04 percent.

- With GPT4 Turbo as query LLM and judge, accuracy: 41.1 percent.


### Conclusion:

Based on this limited experiment, Claude is significantly better than GPT3.5 for a question-answer LLM role.
Both are quite similar for the LLM-as-a-judge role.

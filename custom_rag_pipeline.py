from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from langfuse import Langfuse
from datetime import datetime

import anthropic

# Load env vars. from .env file
load_dotenv()

# Langfuse tracing
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
 
langfuse_callback_handler = LlamaIndexCallbackHandler()
Settings.callback_manager = CallbackManager([langfuse_callback_handler])

# OAI client
from openai import OpenAI
import json
oai_client = OpenAI()


langfuse = Langfuse()

GPT_35TURBO = "gpt-3.5-turbo"
GPT_4TURBO = "gpt-4-turbo"

# Anthropic client
claude_client = anthropic.Anthropic()

# Load documents from the "data/" folder
docs = SimpleDirectoryReader("data").load_data()
print("number of docs:", len(docs))

# Create an index from the documents
index = VectorStoreIndex.from_documents(docs)

# Create a retriever to fetch relevant documents
retriever = index.as_retriever(retrieval_mode='similarity', k=3)

# Define your query
# query = "What years does the strategic plan cover?"


def print_info(relevant_docs):
    print(f"Number of relevant documents: {len(relevant_docs)}")
    print("\n" + "="*50 + "\n")
    for i, doc in enumerate(relevant_docs):
        print(f"Document {i+1}:")
        print(f"Text sample: {doc.node.get_content()[:200]}...")  # Print first 200 characters
        print(f"Metadata: {doc.node.metadata}")
        print(f"Score: {doc.score}")
        print("\n" + "="*50 + "\n")


def custom_query_logic_oai(retriever, question):
    # Retrieve relevant documents
    relevant_docs = retriever.retrieve(question)
    # For debug:
    # print_info(relevant_docs)
    snippet = " \n ".join([x.text for x in relevant_docs])
    
    query_prompt = f"""

    Based on the following snippet answer the given question: 
    Snippet: {snippet}
    Question: {question}
    """
    # print("Snippet = ", snippet)

    response = oai_client.chat.completions.create(
        model=GPT_4TURBO,
        messages=[
            {"role": "system", "content": "You are an AI assistant tasked answering questions accurately based on the given context."},
            {"role": "user", "content": query_prompt}
        ],
        temperature=0.2
    )
    
    result = response.choices[0].message.content
    print("Result = ", result)
    return result

def remove_json_codeblockers(content):
    # Remove potential JSON code block markers
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[-1]
    if content.endswith('```'):
        content = content.rsplit('\n', 1)[0]
    content = content.strip()
    return content

def custom_query_logic_claude(retriever, question):
    # Retrieve relevant documents
    relevant_docs = retriever.retrieve(question)
    # For Debug:
    # print_info(relevant_docs)
    snippet = " \n ".join([x.text for x in relevant_docs])
    
    query_prompt = f"""

    Based on the following snippet answer the given question: 
    Snippet: {snippet}
    Question: {question}
    """
    # print("Snippet = ", snippet)

    message = claude_client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    system="You are an AI assistant tasked answering questions accurately based on the given context.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query_prompt
                }
            ]
        }
    ])
    
    result = message.content
    print("Result = ", result)
    return result

#custom_query_logic_oai(retriever, query)

#custom_query_logic_claude(retriever, query)

def oai_llm_evaluation(output, expected_output):  
    prompt = f"""
    Compare the following output with the expected output and evaluate its accuracy:
    
    Output: {output}
    Expected Output: {expected_output}
    
    Provide a score (0 for incorrect, 1 for correct) and a brief reason for your evaluation.

    Make sure to not penalize for trivial inaccuracies such as abbreviations of words or use of
    different units. Focus on the semantic similarity of the answers.

    Return your response in the following JSON format:
    {{
        "score": 0 or 1,
        "reason": "Your explanation here"
    }}
    """
    
    response = oai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant tasked with evaluating the accuracy of responses."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
 
    evaluation = response.choices[0].message.content
    evaluation = remove_json_codeblockers(evaluation)
    result = eval(evaluation)  # Convert the JSON string to a Python dictionary
    
    # Debug printout
    print(f"Output: {output}")
    print(f"Expected Output: {expected_output}")
    print(f"Evaluation Result: {result}")
    
    return result["score"], result["reason"]

def claude_llm_evaluation(output, expected_output):
    
    prompt = f"""
    Compare the following output with the expected output and evaluate its accuracy:
    
    Output: {output}
    Expected Output: {expected_output}
    
    Provide a score (0 for incorrect, 1 for correct) and a brief reason for your evaluation.

    Make sure to not penalize for trivial inaccuracies such as abbreviations of words or use of
    different units. Focus on the semantic similarity of the answers.

    Return your response in the following properly formatted JSON format below. Do not include any text other than the JSON format in your response:
    {{
        "score": 0 or 1,
        "reason": "Your explanation here"
    }}
    """

    message = claude_client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    system="You are an AI assistant tasked with evaluating the accuracy of responses.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ])
    
    evaluation = message.content[0].text
    print("Claude Evaluation: ", evaluation)
    print("Claude message: ", message)
    result = eval(evaluation)  # Convert the JSON string to a Python dictionary
    
    # Debug printout
    print(f"Output: {output}")
    print(f"Expected Output: {expected_output}")
    print(f"Evaluation Result: {result}")
    
    return result["score"], result["reason"]


def query_rag_oai_with_lf(retriever, input):
    generationStartTime = datetime.now()
    result = custom_query_logic_oai(retriever, input)
    langfuse_generation = langfuse.generation(
        name="strategic-plan-qa-oai-5",
        input=input,
        output=result,
        model="gpt-3.5-turbo",
        start_time=generationStartTime,
        end_time=datetime.now())
    return result, langfuse_generation


def query_rag_claude_with_lf(retriever, input):
    generationStartTime = datetime.now()
    result = custom_query_logic_oai(retriever, input)
    langfuse_generation = langfuse.generation(
        name="strategic-plan-qa-claude-5",
        input=input,
        output=result,
        model="claude-3-5-sonnet-20240620",
        start_time=generationStartTime,
        end_time=datetime.now())
    return result, langfuse_generation

def run_experiment_with_custom_query_logic(experiment_name, custom_query_logic_fn, retriever, llm_evaluation_fn, outfile):
    dataset = langfuse.get_dataset("strategic_plan_qa_pairs")
    file = open(outfile, "w")
    for item in dataset.items:
        completion, langfuse_generation = custom_query_logic_fn(retriever, item.input)
    
        item.link(langfuse_generation, experiment_name) # pass the observation/generation object or the id
    
        score, reason = llm_evaluation_fn(completion, item.expected_output)
        langfuse_generation.score(
        name="accuracy",
        value=score,
        comment=reason
        )
        file.write(f"{score}, {reason}\n")
    file.close()


# GPT for query and Claude as judge:
#run_experiment_with_custom_query_logic("Experiment_20_oai_query_claude_judge", query_rag_oai_with_lf,
#        retriever, claude_llm_evaluation, "claude_query_oai_judge_2.csv")

# Claude for query and GPR3.5 as judge:
run_experiment_with_custom_query_logic("Experiment_20_claude_query_oai_judge", query_rag_claude_with_lf,
        retriever, oai_llm_evaluation, "oai_query_claude_judge_3.csv")

# Claude as query and judge:
#run_experiment_with_custom_query_logic("Experiment_21_claude_query_and_judge", query_rag_claude_with_lf,
#        retriever, claude_llm_evaluation, "claude_query_and_judge_3.csv")

# GPT  as query and judge:
#run_experiment_with_custom_query_logic("Experiment_22_oai_query_and_judge", query_rag_oai_with_lf,
#       retriever, oai_llm_evaluation, "oai_query_and_judge_3.csv")
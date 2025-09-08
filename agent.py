import os
import sys
import subprocess
from pprint import pprint
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from prompt import SYSTEM_PROMPT
from tools.utils import  python_script_runner, shell_script_runner, r_script_runner, view_file_header
# define tools
tools = [
    python_script_runner,
    shell_script_runner,
    r_script_runner,
    view_file_header
]

llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent_executor = create_react_agent(
    llm, 
    tools,
    prompt=SystemMessage(content=SYSTEM_PROMPT)
)


def run_agent(query: str):
    """Use the  ReAct agent to execute the query and print the final result."""
    print(f"--- Start executing query: {query} ---\n")
    
    # put the system prompt and user question together as input
    inputs = {"messages": [SystemMessage(content=SYSTEM_PROMPT), ("user", query)]}
    
    # ReAct agent will think and call the tool by itself
    # to see the detailed intermediate steps, we can use stream instead of invoke
    full_response = ""
    for chunk in agent_executor.stream(inputs, config=RunnableConfig(recursion_limit=50)):
        pprint(chunk)
        print("---")
        # collect the final AI answer
        # check 'agent' key, because the final answer comes from agent
        if "agent" in chunk:
            messages = chunk["agent"].get("messages", [])
            if messages:
                last_message = messages[-1]
                # the final answer is not tool calls
                if hasattr(last_message, 'content') and not getattr(last_message, 'tool_calls', []):
                    full_response = last_message.content

    # print the final output result
    print("\n--- Task completed ---")
    print("Final answer:")
    print(full_response)

# --- Run the example ---
user_input = "Visualize the expression of genes to show the strongest positive and negative correlations with drug response across cell lines, highlight any outliers in the figure /mnt/data/lengyang/wes4/github/langchain/learn/BioAgent/tasks/task_1/data.csv"
run_agent(user_input)




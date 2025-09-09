from pprint import pprint
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from prompt import SYSTEM_PROMPT
from tools.utils import view_file_header
from tools.code_excuter_docker import Code_Executor

# define tools
tools = [
    Code_Executor,
    view_file_header
]

llm = init_chat_model(model="gpt-4o", temperature=0, model_provider="openai")

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
if __name__ == "__main__":
    user_input = "Visualize the expression of genes to show the strongest positive and negative correlations with drug response across cell lines, highlight any outliers in the figure ./tasks/task_1/data.csv"
    run_agent(user_input)




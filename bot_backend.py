from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.chains import RetrievalQA
from rag_pipeline import get_qa_chain
import json
import boto3

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]
    selected_folders: list[str]  # folders chosen by LLM


def select_folders_node(state: ChatState):
    S3_BUCKET = "bivek-embedding-bucket-2025"
    METADATA_KEY = "metadata.json"

    def load_metadata_from_s3():
        """Load metadata.json from S3 (IAM role will handle credentials)."""
        s3 = boto3.client("s3")  # Credentials come from EC2 IAM role
        obj = s3.get_object(Bucket=S3_BUCKET, Key=METADATA_KEY)
        return json.loads(obj["Body"].read().decode("utf-8")) 

    messages = state["messages"]
    latest_user_msg = next((msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)
    if latest_user_msg is None:
        return {"selected_folders": []}
    
    DATASETS_METADATA = load_metadata_from_s3()
    
        # Build prompt for LLM
    folder_list = "\n".join([f"- {k}: {v['description']}" for k, v in DATASETS_METADATA.items()])
    prompt = f"""
You are a smart assistant. 
Given the user query below, choose the relevant datasets from the list.

Available datasets:
{folder_list}

User query: "{latest_user_msg}"
Return only the dataset keys as a comma-separated list.
"""
    result = llm.invoke(prompt)
    folders = [f.strip() for f in result.content.split(",") if f.strip() in DATASETS_METADATA]

    return {"selected_folders": folders}


def chat_node(state: ChatState):
    messages = state['messages']
    # Extract latest HumanMessage
    latest_user_msg = next((msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)
    if latest_user_msg is None:
        return {'messages': [AIMessage(content="Sorry, I didn't understand your input.")]}
    
    # Dynamically get QA chain using selected folders
    qa_chain = get_qa_chain(state.get("selected_folders", []))
    
    # Get answer from QA chain
    response = qa_chain.run(latest_user_msg)
    return {'messages':[response]}

check_pointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node('select_folders_node', select_folders_node)
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'select_folders_node')
graph.add_edge('select_folders_node', 'chat_node')
graph.add_edge('chat_node', END)


chatbot = graph.compile(checkpointer=check_pointer)

thread_id = '1'
config = {'configurable':{'thread_id':thread_id}}

#while True:

    #user_message = input('Type your question here!')
    #print('user:',user_message)

    #if user_message.strip().lower() in ['exit', 'stop', 'bye']:
        #break
    #config = {'configurable':{'thread_id':thread_id}}
    #response = chatbot.invoke({'messages':HumanMessage(content=user_message)}, config=config)
    #print('AI:',response['messages'][-1].content)

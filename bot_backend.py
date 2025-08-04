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

qa_chain = get_qa_chain()

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    # Extract latest HumanMessage
    latest_user_msg = next((msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)
    if latest_user_msg is None:
        return {'messages': [AIMessage(content="I didn't understand your input.")]}

    # Get answer from QA chain
    response = qa_chain.run(latest_user_msg)
    return {'messages':[response]}

check_pointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

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
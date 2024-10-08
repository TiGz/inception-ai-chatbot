from typing import List, TypedDict, Annotated
from mylangchain.async_langchain_bot_interface import AsyncLangchainBotInterface
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from prompts.system_prompts import file_saving_prompt

class State(TypedDict):
    messages: Annotated[List, add_messages]

class WebSearchBot(AsyncLangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = [TavilySearchResults(max_results=3)]
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "web-search-bot"

    @property
    def description(self) -> str:
        return "Web Search Bot - Search web to answer questions"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant with web search capabilities.")

            prompt = """
            As an AI assistant with web search capabilities, please provide a helpful and informative response to the user's query.
            Follow these guidelines:
            1. Use the web search tool when you need up-to-date information or specific facts
            2. Be clear and specific in your answer
            3. If you're unsure about something, it's okay to admit it
            4. Break down complex information into manageable steps
            5. Use examples where appropriate
            6. Cite sources or provide reasoning for your answers when possible
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            result = {"messages": [self.llm_wrapper.invoke(messages)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)
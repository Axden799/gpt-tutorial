import os
import autogen
from autogen.coding import DockerCommandLineCodeExecutor
import tempfile
from typing_extensions import Annotated

class TwoAgent():
    """
        Object containing user proxy agent and assistant agents.
    """
    def __init__(self):
        self.config_list = autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-3.5-turbo"]
            },
        )
        self.llm_config = {
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",
                    "api_key": os.environ.get("OPENAI_API_KEY")
                }
            ]
        }

        # Create a code executor
        #self.code_executor = self.create_executor()

        # Create an planner AssistantAgent object to plan solution.
        self.planner = autogen.AssistantAgent(
            name="planner",
            #llm_config=self.llm_config["config_list"],
            llm_config={"config_list": self.config_list},
            system_message="You are a helpful AI assistant. You suggest a feasible plan for finishing a complex task by decomposing it into 3-5 sub-tasks. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."
            )
        
        # Create a planner UserProxyAgent object that sends user prompt to planner assistant agent and returns reply.
        self.planner_user = autogen.UserProxyAgent(
            name="planner_user",
            max_consecutive_auto_reply=0,
            code_execution_config={
                "use_docker": False
            },
            human_input_mode="NEVER")

        # Create an assistantAgent that will respond to the question as edited by the planner.
        self.assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={
                "temperature": 0,
                "timeout": 600,
                "cache_seed": 42,
                "config_list": self.config_list,
                "functions": [
                    {
                        "name": "ask_planner",
                        "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest a new plan.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "question to ask planner. Make sure the question includes enough content, ,such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner."
                                },
                            },
                            "required": ["message"],
                        },
                    },
                ],
            },
            system_message="You are a helpful AI assistant. You follow the plan suggested to finish tasks. Give the user a final solution at the end. If you are done, copy the solution and append TERMINATE to the end of the solution. Do not return TERMINATE alone, always use terminate with the final solution message.",
        )
        
        # Create a UserProxyAgent to receive and return replies, as well as run code in a temporary Docker container.
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy", 
            human_input_mode="NEVER",
            code_execution_config={
                "use_docker": False
            },
            function_map={"ask_planner": self.ask_planner}, 
            is_termination_msg=lambda x: "content" in x
                and x["content"] is not None
                and x["content"].rstrip().endswith("TERMINATE"),
            llm_config=False)
        
    def ask_planner(self, message: Annotated[str, "Message to ask the planner for task decomposition."]):
        self.planner_user.initiate_chat(self.planner, message=message)
        # return the last message received from the planner
        return self.planner_user.last_message()["content"]
    
    def generate_reply(self, query):
        print("FIRST TEST")
        self.user_proxy.initiate_chat(
            self.assistant,
            message=query,
        )

        print("HELLO TEST")
        print(self.user_proxy.last_message()["content"])

        return self.user_proxy.last_message()["content"]

    
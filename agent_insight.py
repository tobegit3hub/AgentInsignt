import json
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod


class AgentToolMessage(BaseModel):
    function_name: str
    log: str


class AgentMessage(BaseModel):
    role: str
    display_name: str
    output_message: str
    tool_messages: Optional[List[AgentToolMessage]] = []


class AgentInsignt:
    def __init__(self) -> None:
        self.agent_messsages = None

    def read_json_from_file(self, file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
        return messages

    def load_swarm_response_json(self, json_file_path: str):
        self.load_swarm_response(self.read_json_from_file(json_file_path))

    def load_swarm_response(self, response_json: dict):
        self.agent_messsages = []

        for message in response_json["messages"]:
            role = message["role"]
            tool_messages = []

            if message["role"] == "user":
                display_name = "用户"
                output_message = message["content"]

            elif message["role"] == "assistant":
                display_name = message["sender"]
                output_message = message["content"]
                if message["content"] is None:
                    output_message = "我需要调用工具来处理"

                if (
                    "tool_calls" in message
                    and message["tool_calls"] is not None
                    and len(message["tool_calls"]) > 0
                ):
                    function_list = [
                        tool_call["function"]["name"]
                        for tool_call in message["tool_calls"]
                    ]

                    for function_name in function_list:

                        # TODO: get log from function log
                        """
                        temp_content = f"我需要调用函数({function_name})"
                        if len(function_logs) > current_function_index:
                            temp_content += f": {function_logs[current_function_index]}"
                        current_function_index += 1
                        """

                        tool_message = AgentToolMessage(
                            function_name=function_name, log=""
                        )
                        tool_messages.append(tool_message)

            elif message["role"] == "tool":
                display_name = json.loads(message["content"])["assistant"]
                output_message = "现在我来处理"

            else:
                display_name = "Unkown role"
                output_message = "Unkown message"

            agent_message = AgentMessage(
                role=role,
                display_name=display_name,
                output_message=output_message,
                tool_messages=tool_messages,
            )

            self.agent_messsages.append(agent_message)

    def visualize_agents(self, visualizor_type="commandline"):
        if self.agent_messsages is None:
            print("Please load the agent message first")
            return

        if visualizor_type == "commandline":
            visualizor = CommandLineVisualizor()
            visualizor.visualize_agent_messages(self.agent_messsages)
        else:
            print(f"Unsupport visualizor type: {visualizor_type}")


class AbstractVisualizor(ABC):
    @abstractmethod
    def visualize_agent_messages(self, agent_messages: List[AgentMessage]):
        """子类必须实现此方法"""
        pass


# 子类实现抽象方法
class CommandLineVisualizor(AbstractVisualizor):
    def visualize_agent_messages(self, agent_messages: List[AgentMessage]):
        for agent_message in agent_messages:
            extra_message = ""
            if (
                agent_message.tool_messages is not None
                and len(agent_message.tool_messages) > 0
            ):
                function_names = [
                    tool_message.function_name
                    for tool_message in agent_message.tool_messages
                ]
                function_string = ", ".join(function_names)
                extra_message = f"(Functions: {function_string})"

            print(f"{agent_message.display_name}: {agent_message.output_message} {extra_message}")


class ImageVisualizor(AbstractVisualizor):
    def visualize_agent_messages(self, agent_messages: List[AgentMessage]):
        pass


def test():
    agent_insight = AgentInsignt()

    json_file_path = "./express_examples/response.json"
    agent_insight.load_swarm_response_json(json_file_path)

    agent_insight.visualize_agents()


if __name__ == "__main__":
    test()
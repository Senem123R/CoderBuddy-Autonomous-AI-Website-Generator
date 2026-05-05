from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq
from langgraph.constants import END
from langgraph.graph import StateGraph


from agent.prompt import *
from agent.state import *
from agent.tool import write_file, read_file, get_current_directory, list_files

_ = load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")
coder_llm = ChatGroq(model="llama-3.3-70b-versatile", model_kwargs={"tool_choice": "auto"})


def planner_agent(state: dict) -> dict:
    """Converts user prompt into a structured Plan."""
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(
        planner_prompt(user_prompt) # ← from prompt.py
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    return {"plan": resp} # ← Plan is from state.py


def architect_agent(state: dict) -> dict:
    """Creates TaskPlan from Plan."""
    plan: Plan = state["plan"] # ← gets Plan from planner
    resp = llm.with_structured_output(TaskPlan).invoke(
        architect_prompt(plan=plan.model_dump_json()) # ← from prompt.py
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")

    resp.plan = plan
    print(resp.model_dump_json())
    return {"task_plan": resp} # ← TaskPlan is from state.py


def coder_agent(state: dict) -> dict:
    """Direct coder agent - no react agent, just write files directly."""
    coder_state: CoderState = state.get("coder_state") # ← from state.py
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filepath) # ← from tool.py

    MAX_CHARS = 2000
    if existing_content and len(existing_content) > MAX_CHARS:
        existing_content = existing_content[:MAX_CHARS] + "\n... [truncated]"

    # NEW: Get already written files for context
    existing_files_context = ""
    for step in steps[:coder_state.current_step_idx]:
        content = read_file.run(step.filepath)
        if content:
            existing_files_context += f"\n--- {step.filepath} ---\n{content[:500]}\n"

    # NEW: Updated prompt with context
    prompt = (
        f"{coder_system_prompt()}\n\n"
        f"Project: {coder_state.task_plan.plan.name}\n"
        f"Description: {coder_state.task_plan.plan.description}\n"
        f"Tech stack: {coder_state.task_plan.plan.techstack}\n\n"
        f"Already written files (use these exact class names/IDs):\n{existing_files_context}\n\n"
        f"Task: {current_task.task_description}\n"
        f"File to create: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n\n"
        f"Write the COMPLETE, FULLY FUNCTIONAL code for this file. "
        f"Do NOT write placeholder or generic content. "
        f"Respond with ONLY the file content, no explanations, no markdown code blocks."
    )

    response = llm.invoke(prompt)
    file_content = response.content.strip()

    # Strip markdown code blocks if model adds them
    if file_content.startswith("```"):
        lines = file_content.split("\n")
        file_content = "\n".join(lines[1:-1])

    write_file.run({"path": current_task.filepath, "content": file_content}) # ← from tool.py

    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}



graph = StateGraph(dict)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")
agent = graph.compile()
if __name__ == "__main__":
    result = agent.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
                          {"recursion_limit": 100})
    print("Final State:", result)
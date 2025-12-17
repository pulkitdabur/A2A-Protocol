from a2a.types import AgentSkill

skill_1 = AgentSkill(
    id="skill_1",
    name="Skill One",
    description="This is the first skill.",
    tags=["example", "skill"],
    examples=["Example usage of skill one."],
)

SKILLS = [
    skill_1,
]

SCOPE_NAME = "<enter your scope name here>"
TOKEN = "<enter your databricks token here>"
AGENT_ENDPOINT = "<enter your agent endpoint here>"
WRAPPER_PORT = 10000
WRAPPER_HOST = "localhost"

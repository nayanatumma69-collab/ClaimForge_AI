import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from Insurance_claim.config import GROQ_API_KEY

# Import the Pydantic schemas built in Step 1
from Insurance_claim.schemas.models import (
    RelevanceGrade,
    RewriteOutput,
    DecisionOutput,
    HallucinationGrade,
    HumanEscalation
)

# Import the prompt string constants built in Step 2
from Insurance_claim.prompts.relevance import RELEVANCE_PROMPT
from Insurance_claim.prompts.rewrite import REWRITE_PROMPT
from Insurance_claim.prompts.adjudication import ADJUDICATION_PROMPT
from Insurance_claim.prompts.hallucination import HALLUCINATION_PROMPT
from Insurance_claim.prompts.escalation import ESCALATION_PROMPT

# Initialize the central core LLM instance using Groq
print("🤖 Initializing central Groq Chat LLM engine (openai/gpt-oss-120b) in JSON Mode...")
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0.0
)

# Set up native structural JSON mode chains using Pydantic parsers
relevance_chain = (
    ChatPromptTemplate.from_template(RELEVANCE_PROMPT + "\n\nReturn ONLY a valid JSON object matching this schema: {format_instructions}")
    .partial(format_instructions=PydanticOutputParser(pydantic_object=RelevanceGrade).get_format_instructions())
    | llm.bind(response_format={"type": "json_object"})
    | PydanticOutputParser(pydantic_object=RelevanceGrade)
)

rewrite_chain = (
    ChatPromptTemplate.from_template(REWRITE_PROMPT + "\n\nReturn ONLY a valid JSON object matching this schema: {format_instructions}")
    .partial(format_instructions=PydanticOutputParser(pydantic_object=RewriteOutput).get_format_instructions())
    | llm.bind(response_format={"type": "json_object"})
    | PydanticOutputParser(pydantic_object=RewriteOutput)
)

adjudicate_chain = (
    ChatPromptTemplate.from_template(ADJUDICATION_PROMPT + "\n\nReturn ONLY a valid JSON object matching this schema: {format_instructions}")
    .partial(format_instructions=PydanticOutputParser(pydantic_object=DecisionOutput).get_format_instructions())
    | llm.bind(response_format={"type": "json_object"})
    | PydanticOutputParser(pydantic_object=DecisionOutput)
)

hallucination_chain = (
    ChatPromptTemplate.from_template(HALLUCINATION_PROMPT + "\n\nReturn ONLY a valid JSON object matching this schema: {format_instructions}")
    .partial(format_instructions=PydanticOutputParser(pydantic_object=HallucinationGrade).get_format_instructions())
    | llm.bind(response_format={"type": "json_object"})
    | PydanticOutputParser(pydantic_object=HallucinationGrade)
)

escalate_chain = (
    ChatPromptTemplate.from_template(ESCALATION_PROMPT + "\n\nReturn ONLY a valid JSON object matching this schema: {format_instructions}")
    .partial(format_instructions=PydanticOutputParser(pydantic_object=HumanEscalation).get_format_instructions())
    | llm.bind(response_format={"type": "json_object"})
    | PydanticOutputParser(pydantic_object=HumanEscalation)
)

print("✅ Anirudh Step 3 Updated: All LLM validation chains migrated safely to JSON Mode!")

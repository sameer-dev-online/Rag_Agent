from typing import List, Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

from app.config import settings
from app.core.exceptions import LLMException
from dataclasses import dataclass


# Define dependencies type for the agent
@dataclass
class AgentDeps:
    """Dependencies passed to the agent during runtime."""

    def __init__(
        self,
        retrieved_contexts: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]],
    ):
        self.retrieved_contexts = retrieved_contexts
        self.conversation_history = conversation_history


# System prompt for the RAG agent
SYSTEM_PROMPT = """You are a helpful AI assistant with access to a knowledge base. Your role is to answer questions accurately using the provided context and conversation history.

Guidelines:
1. Always base your answers on the retrieved context when available
2. If the context doesn't contain relevant information, say so clearly
3. Use conversation history to maintain context and continuity
4. Be concise but thorough in your responses
5. If you're uncertain, acknowledge it rather than making up information
6. Cite specific parts of the context when making claims

Retrieved Context:
{context}

Conversation History:
{history}

Answer the user's question based on the above information."""


def format_context(retrieved_contexts: List[Dict[str, Any]]) -> str:
    """
    Format retrieved contexts into a readable string.

    Args:
        retrieved_contexts: List of retrieved context chunks

    Returns:
        Formatted context string
    """
    if not retrieved_contexts:
        return "No relevant context found."

    formatted_parts = []
    for idx, ctx in enumerate(retrieved_contexts, 1):
        chunk_text = ctx.get("chunk_text", "")
        similarity = ctx.get("similarity_score", 0.0)
        formatted_parts.append(
            f"[Context {idx}] (Relevance: {similarity:.2f})\n{chunk_text}"
        )

    return "\n\n".join(formatted_parts)


def format_history(conversation_history: List[Dict[str, Any]]) -> str:
    """
    Format conversation history into a readable string.

    Args:
        conversation_history: List of previous messages

    Returns:
        Formatted history string
    """
    if not conversation_history:
        return "No previous conversation."

    formatted_parts = []
    for msg in conversation_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        formatted_parts.append(f"{role.upper()}: {content}")

    return "\n".join(formatted_parts)


# Initialize the PydanticAI agent
def create_rag_agent(
    retrieved_contexts: List[Dict[str, Any]], conversation_history: List[Dict[str, Any]]
) -> Agent[AgentDeps, str]:
    """
    Create and configure the RAG agent.

    Returns:
        Configured PydanticAI agent
    """
    try:
        print(f"model name: {settings.llm_model}")
        # Initialize OpenAI model
        model = OpenAIChatModel(
            model_name=settings.llm_model,
        )

        # Create agent with system prompt
        agent = Agent(
            model=model,
            deps_type=AgentDeps,
            system_prompt=_build_system_prompt(
                AgentDeps(retrieved_contexts, conversation_history)
            ),
        )

        return agent

    except Exception as e:
        raise LLMException(
            message=f"Failed to create RAG agent: {str(e)}", details={"error": str(e)}
        )


def _build_system_prompt(ctx: RunContext[AgentDeps]) -> str:
    """
    Build the system prompt with context and history.

    Args:
        ctx: Runtime context containing dependencies

    Returns:
        Formatted system prompt
    """
    context_str = format_context(ctx.deps.retrieved_contexts)
    history_str = format_history(ctx.deps.conversation_history)

    return SYSTEM_PROMPT.format(context=context_str, history=history_str)


async def run_agent(
    query: str,
    retrieved_contexts: List[Dict[str, Any]],
    conversation_history: List[Dict[str, Any]],
) -> str:
    """
    Run the RAG agent with a query and context.

    Args:
        query: User's question
        retrieved_contexts: Retrieved context chunks
        conversation_history: Previous conversation messages

    Returns:
        Agent's response

    Raises:
        LLMException: If agent execution fails
    """
    try:
        # Create agent
        agent = create_rag_agent(retrieved_contexts, conversation_history)

        # Create dependencies
        Deps = AgentDeps(
            retrieved_contexts=retrieved_contexts,
            conversation_history=conversation_history,
        )

        # Run agent
        result = await agent.run(query, deps=Deps)

        return result.output

    except Exception as e:
        if isinstance(e, LLMException):
            raise
        raise LLMException(
            message=f"Failed to run agent: {str(e)}",
            details={"error": str(e), "query": query},
        )

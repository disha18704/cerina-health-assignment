import asyncio
import os
from dotenv import load_dotenv
from backend.graph import get_graph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

load_dotenv()

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY in .env or environment")
        return

    graph = get_graph()
    checkpointer = InMemorySaver()
    app = graph.compile(checkpointer=checkpointer)

    thread_id = "test-thread-1"
    config = {"configurable": {"thread_id": thread_id}}

    print("--- Starting Run ---")
    from backend.models import ReviewMetadata
    
    initial_input = {
        "messages": [HumanMessage(content="Create a CBT exposure hierarchy for someone with social anxiety.")],
        "current_draft": None,
        "draft_history": [],
        "critiques": [],
        "scratchpad": [],
        "metadata": ReviewMetadata(),
        "last_reviewer": None
    }
    
    async for event in app.astream(initial_input, config=config):
        for key, value in event.items():
            print(f"\n[Node: {key}]")
            if "messages" in value:
                 print(f"Msg: {value['messages'][-1].content}")
            if "next_worker" in value:
                print(f"Routing to: {value['next_worker']}")
            if "scratchpad" in value and value["scratchpad"]:
                latest_note = value["scratchpad"][-1]
                print(f"Scratchpad: [{latest_note.priority.upper()}] {latest_note.content[:80]}...")
            if "metadata" in value and value["metadata"]:
                meta = value["metadata"]
                if meta.safety_score or meta.empathy_score:
                    print(f"Scores: Safety={meta.safety_score or 'N/A'}, Empathy={meta.empathy_score or 'N/A'}, Revisions={meta.total_revisions}")

    print("--- Run Completed ---")
    

    state = await app.aget_state(config)
    
    if state.values.get("current_draft"):
        draft = state.values['current_draft']
        history = state.values.get('draft_history', [])
        metadata = state.values.get('metadata')
        scratchpad = state.values.get('scratchpad', [])
        
        # Import formatter
        from backend.formatter import format_exercise_for_presentation, format_exercise_summary
        
        # Show quick summary first
        print("\n" + "="*80)
        print("EXERCISE SUMMARY")
        print("="*80)
        print(format_exercise_summary(draft, metadata, len(scratchpad)))
        
        # Show full presentation-ready exercise
        print("\n" + "="*80)
        print("FULL EXERCISE (Ready to Share with Patient)")
        print("="*80)
        print(format_exercise_for_presentation(draft, metadata))
        
        # Technical details for debugging
        print("\n" + "="*80)
        print("TECHNICAL DETAILS (For Review)")
        print("="*80)
        print(f"📊 Version: {len(history)}")
        print(f"🔄 Total Revisions: {metadata.total_revisions if metadata else 0}")
        print(f"💬 Agent Collaboration Notes: {len(scratchpad)}")
        if scratchpad:
            print("\nRecent Agent Notes:")
            for note in scratchpad[-3:]:
                print(f"  [{note.priority.upper()}] {note.author}: {note.content[:100]}...")
    else:
        print("No draft produced.")

if __name__ == "__main__":
    asyncio.run(main())

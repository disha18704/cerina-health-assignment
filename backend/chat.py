"""
Interactive CLI Chat Interface for CBT Protocol Foundry
"""
import asyncio
import os
from dotenv import load_dotenv
from backend.graph import get_graph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from backend.models import ReviewMetadata
from backend.formatter import format_exercise_for_presentation, format_exercise_summary

load_dotenv()

class CBTChat:
    def __init__(self):
        self.graph = get_graph()
        self.checkpointer = InMemorySaver()
        self.app = self.graph.compile(checkpointer=self.checkpointer)
        self.thread_id = "chat-session-1"
        self.config = {"configurable": {"thread_id": self.thread_id}}
        
    async def send_message(self, user_input: str):
        """Send a message and get the CBT exercise response"""
        
        # Get current state to check if this is first message
        current_state = await self.app.aget_state(self.config)
        
        if not current_state.values:
            # First message - initialize state
            initial_input = {
                "messages": [HumanMessage(content=user_input)],
                "current_draft": None,
                "draft_history": [],
                "critiques": [],
                "scratchpad": [],
                "metadata": ReviewMetadata(),
                "last_reviewer": None
            }
            
            print("\n🤖 Processing your request...")
            print("   (Agents are collaborating...)\n")
            
            # Stream the workflow
            async for event in self.app.astream(initial_input, self.config):
                for key, value in event.items():
                    if key != "supervisor":
                        agent_name = key.replace("_", " ").title()
                        print(f"   → {agent_name} reviewing...", end="\r")
            
        else:
            # Continue conversation
            print("\n🤖 Let me revise that for you...")
            print("   (Agents are working...)\n")
            
            # Add message to existing state
            update_input = {
                "messages": [HumanMessage(content=user_input)]
            }
            
            async for event in self.app.astream(update_input, self.config):
                for key, value in event.items():
                    if key != "supervisor":
                        agent_name = key.replace("_", " ").title()
                        print(f"   → {agent_name} reviewing...", end="\r")
        
        # Get final state
        final_state = await self.app.aget_state(self.config)
        
        if final_state.values.get("current_draft"):
            draft = final_state.values['current_draft']
            metadata = final_state.values.get('metadata')
            scratchpad = final_state.values.get('scratchpad', [])
            
            # Clear the processing line
            print(" " * 50, end="\r")
            
            # Show summary
            print("\n" + "="*80)
            print(format_exercise_summary(draft, metadata, len(scratchpad)))
            print("="*80)
            
            return draft, metadata
        else:
            print("\n❌ Sorry, I couldn't generate an exercise. Please try again.")
            return None, None
    
    async def get_full_exercise(self):
        """Get the full formatted exercise from current state"""
        final_state = await self.app.aget_state(self.config)
        
        if final_state.values.get("current_draft"):
            draft = final_state.values['current_draft']
            metadata = final_state.values.get('metadata')
            
            print("\n" + "="*80)
            print("FULL EXERCISE (Ready to Share)")
            print("="*80)
            print(format_exercise_for_presentation(draft, metadata))
        else:
            print("\n❌ No exercise available yet. Send a message first!")
    
    async def run(self):
        """Run the interactive chat loop"""
        print("\n" + "="*80)
        print("🧠 CBT Protocol Foundry - Interactive Chat")
        print("="*80)
        print("\nI'm your AI CBT exercise designer. Describe your mental health challenge,")
        print("and I'll create a personalized CBT exercise for you.\n")
        print("Commands:")
        print("  • Type your request to get a CBT exercise")
        print("  • Type 'full' to see the complete exercise")
        print("  • Type 'quit' to exit")
        print("="*80 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye! Take care of your mental health.\n")
                    break
                
                if user_input.lower() == 'full':
                    await self.get_full_exercise()
                    continue
                
                # Process the message
                await self.send_message(user_input)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Take care of your mental health.\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.\n")

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: Please set OPENAI_API_KEY in .env file")
        return
    
    chat = CBTChat()
    await chat.run()

if __name__ == "__main__":
    asyncio.run(main())

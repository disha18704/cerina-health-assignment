"""
Presentation formatter for CBT exercises.
Transforms raw exercise content into user-ready format.
"""

def format_exercise_for_presentation(draft, metadata=None):
    """
    Format a CBT exercise for presentation to end users.
    
    Args:
        draft: ExerciseDraft object
        metadata: ReviewMetadata object (optional)
    
    Returns:
        Formatted string ready for presentation
    """
    output = []
    
    # Header
    output.append("=" * 80)
    output.append(f"📋 {draft.title}")
    output.append("=" * 80)
    output.append("")
    
    # Quality indicators
    if metadata:
        output.append("✅ **Quality Validated**")
        indicators = []
        if metadata.safety_score and metadata.safety_score >= 0.9:
            indicators.append(f"🛡️ Safety Score: {metadata.safety_score}")
        if metadata.empathy_score and metadata.empathy_score >= 0.9:
            indicators.append(f"❤️ Empathy Score: {metadata.empathy_score}")
        if metadata.clarity_score and metadata.clarity_score >= 0.9:
            indicators.append(f"📖 Clarity Score: {metadata.clarity_score}")
        
        if indicators:
            for indicator in indicators:
                output.append(f"  {indicator}")
            output.append("")
    
    # Instructions Section
    output.append("-" * 80)
    output.append("📝 **INSTRUCTIONS FOR YOU**")
    output.append("-" * 80)
    output.append("")
    output.append(draft.instructions)
    output.append("")
    
    # Main Content Section
    output.append("-" * 80)
    output.append("📄 **YOUR CBT EXERCISE**")
    output.append("-" * 80)
    output.append("")
    output.append(draft.content)
    output.append("")
    
    # Footer
    output.append("=" * 80)
    output.append("💡 **Remember**: This exercise is a tool to support your mental health journey.")
    output.append("   For personalized guidance, consult with a mental health professional.")
    output.append("=" * 80)
    
    return "\n".join(output)


def format_exercise_summary(draft, metadata=None, scratchpad_count=0):
    """
    Create a brief summary of the exercise with key highlights.
    
    Args:
        draft: ExerciseDraft object
        metadata: ReviewMetadata object (optional)
        scratchpad_count: Number of agent notes (optional)
    
    Returns:
        Formatted summary string
    """
    summary = []
    
    summary.append(f"\n📋 **{draft.title}**\n")
    
    # Extract key points from instructions
    summary.append("**What This Exercise Will Help You Do:**")
    instruction_lines = draft.instructions.strip().split('\n')
    for i, line in enumerate(instruction_lines[:5], 1):  # First 5 points
        clean_line = line.strip().lstrip('0123456789.')  # Remove numbering
        if clean_line:
            summary.append(f"  {i}. {clean_line.strip()}")
    
    summary.append("")
    
    # Validation info
    if metadata:
        summary.append(f"✅ **Clinically Validated** (Safety: {metadata.safety_score or 'N/A'}, Empathy: {metadata.empathy_score or 'N/A'})")
        summary.append(f"📊 **Refined through {metadata.total_revisions} iterations** by expert AI agents")
        if scratchpad_count:
            summary.append(f"💬 **{scratchpad_count} review notes** from Safety & Clinical reviewers")
    
    summary.append("")
    summary.append("👉 **Ready to use** - Approved by Safety Guardian & Clinical Critic")
    
    return "\n".join(summary)

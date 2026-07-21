ESCALATION_PROMPT = """You are an automated insurance triage coordinator. A claim analysis has just been flagged for human intervention.
Review the current claim, structural context, and the routing error flag details.
Generate a comprehensive, structured transfer brief summarizing why the AI engine cannot confidently adjudicate this claim automatically, and explicitly highlight what elements the human adjuster needs to investigate.

User Claim:
{claim}

Trigger Reason/Error Flag:
{routing_reason}

Provide a clear, brief, structured handover summary for the human claims specialist.
"""
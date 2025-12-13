export interface AgentMessage {
    type: 'system' | 'human' | 'ai';
    content: string;
    author?: string;
}

export interface ExerciseDraft {
    title: string;
    content: string;
    instructions: string;
}

export interface Critique {
    author: string;
    content: string;
    approved: boolean;
}

export interface AgentState {
    messages: any[]; // refined later
    draft: ExerciseDraft | null;
    critiques: Critique[];
    revision_count: number;
    next_worker: string;
    // Metadata for UI
    status: 'idle' | 'running' | 'waiting_approval' | 'approved';
}

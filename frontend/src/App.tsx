import { useEffect, useRef, useState } from 'react';

interface Draft {
  title: string;
  content: string;
  instructions: string;
}

interface Metadata {
  safety_score?: number;
  empathy_score?: number;
  clarity_score?: number;
  total_revisions: number;
}

interface ConversationItem {
  type: 'user' | 'assistant';
  content: string;
  draft?: Draft;
  metadata?: Metadata;
}

function App() {
  const [message, setMessage] = useState('');
  const [threadId] = useState(`thread-${Date.now()}`);
  const [conversation, setConversation] = useState<ConversationItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const handleSendMessage = async () => {
    if (!message.trim() || isProcessing) return;

    const userMessage = message;
    setConversation(prev => [...prev, { type: 'user', content: userMessage }]);
    setMessage('');
    setIsProcessing(true);

    try {
      const response = await fetch('http://localhost:8000/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, thread_id: threadId })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'complete') {
                const stateResponse = await fetch(`http://localhost:8000/state/${threadId}`);
                const state = await stateResponse.json();
                setConversation(prev => [...prev, {
                  type: 'assistant',
                  content: 'CBT Exercise Created',
                  draft: state.current_draft,
                  metadata: state.metadata
                }]);
                break;
              }
            } catch (e) { }
          }
        }
      }
    } catch (error) {
      setConversation(prev => [...prev, { type: 'assistant', content: 'Error processing request' }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <div style={{ padding: '16px 24px', borderBottom: '1px solid #e5e7eb', backgroundColor: 'white' }}>
        <h1 style={{ fontSize: '20px', margin: 0, color: '#1f2937' }}>Cerina Foundry</h1>
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, overflowY: 'auto', backgroundColor: 'white' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px 24px' }}>
          {conversation.length === 0 && (
            <div style={{ textAlign: 'center', paddingTop: '80px' }}>
              <h2 style={{ fontSize: '36px', fontWeight: 300, color: '#1f2937', marginBottom: '16px' }}>Hello</h2>
              <p style={{ color: '#6b7280' }}>How can I help you create a CBT exercise today?</p>
            </div>
          )}

          {conversation.map((item, idx) => (
            <div key={idx} style={{ marginBottom: '32px' }}>
              {item.type === 'user' ? (
                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <div style={{ backgroundColor: '#f3f4f6', borderRadius: '16px', padding: '12px 20px', maxWidth: '600px' }}>
                    <p style={{ margin: 0, color: '#1f2937' }}>{item.content}</p>
                  </div>
                </div>
              ) : (
                <div>
                  {item.draft ? (
                    <div>
                      <h2 style={{ fontSize: '20px', fontWeight: 400, color: '#111827', marginBottom: '12px' }}>
                        {item.draft.title}
                      </h2>

                      {item.metadata && (
                        <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#6b7280', marginBottom: '16px' }}>
                          <span>Safety {item.metadata.safety_score?.toFixed(1)}</span>
                          <span>Empathy {item.metadata.empathy_score?.toFixed(1)}</span>
                          <span>Clarity {item.metadata.clarity_score?.toFixed(1)}</span>
                          <span>{item.metadata.total_revisions} revisions</span>
                        </div>
                      )}

                      <div style={{ color: '#374151', fontSize: '15px', lineHeight: '1.7', whiteSpace: 'pre-wrap', marginBottom: '16px' }}>
                        {item.draft.instructions}
                      </div>

                      <div style={{ color: '#374151', fontSize: '15px', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>
                        {item.draft.content}
                      </div>
                    </div>
                  ) : (
                    <p style={{ color: '#374151', fontSize: '15px', lineHeight: '1.7' }}>{item.content}</p>
                  )}
                </div>
              )}
            </div>
          ))}

          {isProcessing && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6b7280' }}>
              <span style={{ fontSize: '14px' }}>Agents are collaborating...</span>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div style={{ borderTop: '1px solid #e5e7eb', backgroundColor: 'white', padding: '24px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '12px', backgroundColor: '#f3f4f6', borderRadius: '24px', padding: '12px 24px', alignItems: 'center' }}>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask Cerina Foundry"
            disabled={isProcessing}
            style={{ flex: 1, border: 'none', backgroundColor: 'transparent', outline: 'none', fontSize: '15px', color: '#1f2937' }}
          />
          <button
            onClick={handleSendMessage}
            disabled={isProcessing || !message.trim()}
            style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#6b7280', fontSize: '24px', padding: 0 }}
          >
            ➤
          </button>
        </div>
        <p style={{ textAlign: 'center', fontSize: '12px', color: '#9ca3af', marginTop: '12px' }}>
          Cerina Foundry uses AI agents. Verify important information.
        </p>
      </div>
    </div>
  );
}

export default App;

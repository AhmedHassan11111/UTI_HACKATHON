import { useState, useRef, useCallback } from 'react';
import { MOCK_ANSWER } from '../utils/mockData';
import { chatAPI } from '../utils/api';

const MOCK_DELAY = 1800;

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const abortRef = useRef(null);

  const sendMessage = useCallback(async (question) => {
    if (!question.trim() || isLoading) return;

    const userMessage = { role: 'user', content: question.trim() };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setLoadingStage('Searching sources…');

    try {
      // Try real API first
      const data = await chatAPI(question);
      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        confidence: data.sources?.[0]?.score || 0
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      // Fallback to mock for design review
      await new Promise(r => setTimeout(r, MOCK_DELAY));
      setLoadingStage('Ranking matches…');
      await new Promise(r => setTimeout(r, 600));
      setLoadingStage('Drafting answer…');
      await new Promise(r => setTimeout(r, 800));

      const assistantMessage = {
        role: 'assistant',
        content: MOCK_ANSWER.answer,
        sources: MOCK_ANSWER.sources,
        confidence: MOCK_ANSWER.sources[0].score
      };
      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
      setLoadingStage('');
    }
  }, [isLoading]);

  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, isLoading, loadingStage, sendMessage, clearChat };
}

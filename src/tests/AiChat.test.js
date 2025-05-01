import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import AiChatPage from '../lib/AiChatPage.svelte';

// Simulate the MCP service responses
vi.mock('../lib/services/mcpService', () => ({
  MCPClient: vi.fn().mockImplementation(() => ({
    connect: vi.fn().mockResolvedValue({ success: true }),
    chat: vi.fn().mockImplementation((message) => {
      // Provide different responses based on the query
      if (message.includes('receipt')) {
        return Promise.resolve({
          response: "I found 3 receipts from last month. The largest purchase was $42.99 at Test Store on May 15, 2023."
        });
      }
      return Promise.resolve({
        response: "I'm your AI assistant. How can I help you today?"
      });
    })
  }))
}));

describe('AI Chat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the chat interface', () => {
    const { getByPlaceholderText, getByText } = render(AiChatPage);

    expect(getByPlaceholderText('Type your message...')).toBeTruthy();
    expect(getByText('Send')).toBeTruthy();
  });

  it('should send message and display response', async () => {
    const { getByPlaceholderText, getByText, findByText } = render(AiChatPage);

    // Type a message
    const input = getByPlaceholderText('Type your message...');
    await fireEvent.input(input, { target: { value: 'Hello' } });

    // Send the message
    const sendButton = getByText('Send');
    await fireEvent.click(sendButton);

    // Check that user message appears
    expect(getByText('Hello')).toBeTruthy();

    // Check for AI response
    const response = await findByText("I'm your AI assistant. How can I help you today?");
    expect(response).toBeTruthy();
  });

  it('should handle receipt queries correctly', async () => {
    const { getByPlaceholderText, getByText, findByText } = render(AiChatPage);

    // Type a receipt query
    const input = getByPlaceholderText('Type your message...');
    await fireEvent.input(input, { target: { value: 'Show me my receipts from last month' } });

    // Send the message
    const sendButton = getByText('Send');
    await fireEvent.click(sendButton);

    // Check for receipt-specific response
    const response = await findByText("I found 3 receipts from last month. The largest purchase was $42.99 at Test Store on May 15, 2023.");
    expect(response).toBeTruthy();
  });
}); 
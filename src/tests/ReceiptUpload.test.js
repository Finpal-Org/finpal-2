import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import ReceiptUpload from '../lib/ReceiptUpload.svelte';

// Simulate the receiptService responses
vi.mock('../lib/services/receiptService', () => ({
  analyzeReceiptWithAzure: vi.fn().mockResolvedValue({
    merchantName: { content: 'Test Store', confidence: 0.95 },
    total: { content: '42.99', confidence: 0.98 },
    date: { content: '2023-05-15', confidence: 0.99 },
    items: [
      { description: 'Test Item 1', amount: '10.99', quantity: '1' },
      { description: 'Test Item 2', amount: '32.00', quantity: '2' }
    ]
  }),
  saveToFirestore: vi.fn().mockResolvedValue({ id: 'receipt-123456' })
}));

// Simulate Firebase storage
vi.mock('firebase/storage', () => ({
  getStorage: vi.fn(),
  ref: vi.fn(),
  uploadBytes: vi.fn().mockResolvedValue({}),
  getDownloadURL: vi.fn().mockResolvedValue('https://example.com/receipt-image.jpg')
}));

describe('ReceiptUpload Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the upload form', () => {
    const { getByText, getByLabelText } = render(ReceiptUpload);

    expect(getByText('Upload Receipt')).toBeTruthy();
    expect(getByLabelText('Choose receipt image')).toBeTruthy();
    expect(getByText('Upload')).toBeTruthy();
  });

  it('should process receipt upload with sample data', async () => {
    const { getByLabelText, getByText } = render(ReceiptUpload);

    // Create a sample file
    const file = new File(['receipt content'], 'receipt.jpg', { type: 'image/jpeg' });

    // Set the file input
    const fileInput = getByLabelText('Choose receipt image');
    await fireEvent.change(fileInput, { target: { files: [file] } });

    // Submit the form
    const submitButton = getByText('Upload');
    await fireEvent.click(submitButton);

    // Wait for processing to complete
    await waitFor(() => {
      expect(getByText('Receipt processed successfully!')).toBeTruthy();
    });
  });
}); 
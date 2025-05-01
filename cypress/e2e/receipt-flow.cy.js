// Basic E2E test for receipt flow
describe('Receipt Upload Flow', () => {
  beforeEach(() => {
    // Mock API calls
    cy.intercept('POST', '**/documentintelligence/documentModels/prebuilt-receipt:analyze*', {
      statusCode: 202,
      headers: {
        'Operation-Location': 'https://example.com/operations/123'
      }
    }).as('startAnalysis');

    cy.intercept('GET', 'https://example.com/operations/123', {
      statusCode: 200,
      body: {
        status: 'succeeded',
        analyzeResult: {
          documents: [{
            fields: {
              MerchantName: { content: 'Test Store', confidence: 0.95 },
              Total: { content: '42.99', confidence: 0.98 },
              TransactionDate: { content: '2023-05-15', confidence: 0.99 },
              Items: {
                valueArray: [
                  {
                    valueObject: {
                      Description: { content: 'Test Item 1' },
                      TotalPrice: { content: '10.99' },
                      Quantity: { content: '1' }
                    }
                  },
                  {
                    valueObject: {
                      Description: { content: 'Test Item 2' },
                      TotalPrice: { content: '32.00' },
                      Quantity: { content: '2' }
                    }
                  }
                ]
              }
            }
          }]
        }
      }
    }).as('getResults');

    // Mock Firebase storage
    cy.intercept('POST', '**/uploadBytes*', {
      statusCode: 200
    }).as('uploadImage');

    // Mock Firestore
    cy.intercept('POST', '**/documents*', {
      statusCode: 200,
      body: { name: 'receipts/mock-id' }
    }).as('saveReceipt');

    // Mock auth
    cy.window().then((win) => {
      win.sessionStorage.setItem('mockAuth', JSON.stringify({
        uid: 'test-user-id',
        email: 'test@example.com'
      }));
    });
  });

  it('should successfully upload and process a receipt', () => {
    // Visit the upload page
    cy.visit('/receipt-upload');

    // Upload a file
    cy.get('input[type="file"]').attachFile('fixture:test-receipt.jpg');

    // Click upload button
    cy.get('button').contains('Upload').click();

    // Verify loading state
    cy.get('[data-testid="processing-indicator"]').should('be.visible');

    // Wait for the Azure API call
    cy.wait('@startAnalysis');
    cy.wait('@getResults');

    // Verify success message
    cy.get('[data-testid="success-message"]').should('be.visible');
    cy.get('[data-testid="success-message"]').should('contain', 'Receipt processed successfully');

    // Verify redirect to the receipt details
    cy.url().should('include', '/receipt/');

    // Verify receipt details
    cy.get('[data-testid="merchant-name"]').should('contain', 'Test Store');
    cy.get('[data-testid="receipt-total"]').should('contain', '42.99');
  });

  it('should show error message when upload fails', () => {
    // Override the intercept to simulate a failure
    cy.intercept('POST', '**/documentintelligence/documentModels/prebuilt-receipt:analyze*', {
      statusCode: 500,
      body: { error: 'Internal Server Error' }
    }).as('failedAnalysis');

    // Visit the upload page
    cy.visit('/receipt-upload');

    // Upload a file
    cy.get('input[type="file"]').attachFile('fixture:test-receipt.jpg');

    // Click upload button
    cy.get('button').contains('Upload').click();

    // Wait for the failed request
    cy.wait('@failedAnalysis');

    // Verify error message
    cy.get('[data-testid="error-message"]').should('be.visible');
    cy.get('[data-testid="error-message"]').should('contain', 'Failed to process receipt');
  });
}); 
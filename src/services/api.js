/**
 * API Service for Loan-IQ Backend Communication
 */

const BASE_URL = '/api';

export async function evaluateApplication(payload) {
  try {
    const response = await fetch(`${BASE_URL}/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server returned status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error evaluating application:', error);
    throw error;
  }
}

export async function sendChatMessage(prompt, context = {}) {
  try {
    const response = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, context }),
    });

    if (!response.ok) {
      throw new Error(`Server returned status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat query:', error);
    throw error;
  }
}

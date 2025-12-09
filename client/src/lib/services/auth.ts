import { guestRequest, AUTH_ENDPOINTS, authRequest } from './api';
import { type User, mapUser } from '$lib/types/user';

/**
 * Exchanges an authorization code for an access token and returns
 * a mapped user object.
 * @param {string} code - The authorization code from the OAuth provider.
 * @param {string} state - The state parameter for security verification.
 * @returns {Promise<User>} A promise that resolves to the mapped User object.
 * @throws Will throw an error if the API call fails.
 */
export async function exchangeCoceForToken(
	code: string,
	state: string,
	provider: 'google' | 'github'
): Promise<User> {
	try {
		const response = await authRequest.post(AUTH_ENDPOINTS.EXCHANGE_CODE(provider), {
			code,
			state
		});
		return mapUser(response.data);
	} catch (error) {
		console.error('Error exchanging code for token:', error);
		throw error;
	}
}

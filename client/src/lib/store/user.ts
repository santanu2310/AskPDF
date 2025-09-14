import { writable } from 'svelte/store';
import { type User, mapUser } from '$lib/types/user';
import { authRequest, AUTH_ENDPOINTS } from '$lib/services/api';

const { subscribe, set, update } = writable<User | null>(null);

async function fetchUser() {
	try {
		const res = await authRequest({
			method: 'get',
			url: AUTH_ENDPOINTS.ME
		});

		if (res.status != 200) {
			set(null);
			return null;
		}

		const mapped = mapUser(res.data);
		set(mapped);

		return mapped;
	} catch (err) {
		console.error('Failed to fetch user:', err);
		set(null);

		return null;
	}
}

function setUser(user: User) {
	set(user);
}

function clearUser() {
	set(null);
}

export const user = {
	subscribe,
	set: setUser,
	clear: clearUser,
	fetch: fetchUser
};

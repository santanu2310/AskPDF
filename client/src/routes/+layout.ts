import { get } from 'svelte/store';
import { user } from '$lib/store/user';
import type { LayoutLoad } from './$types';

// This load function will run on the server for the first visit,
// and on the client for subsequent navigations.
export const load: LayoutLoad = async () => {
	// We get the user from the store to check if it has already been fetched.
	const currentUser = get(user);
	// If user is not in the store, fetch them.
	if (!currentUser) {
		// Calling fetchUser() will fetch and set the user in the store.
		// We also return the user so it's available in the `data` prop.
		const fetchedUser = await user.fetch();
		return { user: fetchedUser };
	}

	// If the user is already in the store, just return them.
	return {
		user: currentUser
	};
};

export interface User {
	id: string;
	email: string;
	fullName: string;
	profilePicUrl: string | null;
}

interface UserApiResponse {
	id: string;
	email: string;
	full_name: string;
	profile_pic_url: string | null;
}

export function mapUser(apiData: UserApiResponse): User {
	return {
		id: apiData.id,
		email: apiData.email,
		fullName: apiData.full_name,
		profilePicUrl: apiData.profile_pic_url
	};
}

export type AuthProvider = 'google' | 'github';

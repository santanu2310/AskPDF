const DB_NAME = 'ask_pdf';
const DB_VERSION = 1;

// Object represantantion of indexedDb objectStores
const STORES = [
	{
		name: 'conversation'
	},
	{
		name: 'document'
	},
	{
		name: 'tempDcoument'
	}
];

class IndexedDbService {
	private db: IDBDatabase | null = null;
	private newlyCreated = false;

	async openDb(): Promise<void> {
		if (!window.indexedDB) {
			console.error('IndexedDb is not supported by your brouser');
			return;
		}

		return new Promise<void>((resolve, rejects) => {
			const request: IDBOpenDBRequest = window.indexedDB.open(DB_NAME, DB_VERSION);

			request.onupgradeneeded = (event: IDBVersionChangeEvent) => {
				this.newlyCreated = true;
				const db = (event.target as IDBOpenDBRequest).result;

				STORES.forEach((storeName) => {
					if (!db.objectStoreNames.contains(storeName.name)) {
						const store = db.createObjectStore(storeName.name, {
							keyPath: 'id',
							autoIncrement: false
						});
					}
				});
			};

			request.onsuccess = () => {
				this.db = request.result;
				resolve();
			};

			request.onerror = () => {
				rejects(request.error);
			};
		});
	}

	async addRecord(storeName: string, data: object): Promise<IDBValidKey> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<IDBValidKey>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error('Database is not open.'));
				return;
			}

			const transaction = this.db.transaction(storeName, 'readwrite');
			const store = transaction.objectStore(storeName);

			const request = store.add(data);

			request.onsuccess = () => {
				resolve(request.result);
			};

			request.onerror = () => {
				rejects(new Error(`Failed to add record to the store :${request.error}`));
			};
		});
	}

	async updateRecord(storeName: string, data: object): Promise<IDBValidKey> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<IDBValidKey>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error('Database is not open.'));
				return;
			}

			const transaction = this.db.transaction(storeName, 'readwrite');
			const store = transaction.objectStore(storeName);

			const request = store.put(data);

			request.onsuccess = () => {
				resolve(request.result);
			};

			request.onerror = () => {
				rejects(new Error('Failed to add record to the store'));
			};
		});
	}

	async getRecord<T>(storeName: string, id: string): Promise<T | undefined> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<T | undefined>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error('Database is not open.'));
				return;
			}

			const transaction = this.db.transaction(storeName, 'readonly');
			const store = transaction.objectStore(storeName);
			const storeRequest = store.get(id);
			storeRequest.onsuccess = () => {
				resolve(storeRequest.result);
			};

			storeRequest.onerror = () => {
				rejects(storeRequest.error);
			};
		});
	}

	async getAllRecords(storeName: string, count: number | undefined = undefined): Promise<object[]> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<object[]>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error('Database is not open.'));
				return;
			}

			//open a transaction in indesedDb
			const transaction = this.db.transaction(storeName, 'readonly');
			const store = transaction.objectStore(storeName);

			// get all the objects and return the value
			const request = store.getAll(null, count);

			request.onsuccess = () => {
				resolve(request.result);
			};

			request.onerror = () => {
				rejects(request.error);
			};
		});
	}

	async deleteRecord(storeName: string, key: string): Promise<{ objectId: string }> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<{ objectId: string }>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error('Database is not open.'));
				return;
			}

			const transaction = this.db.transaction(storeName, 'readwrite');
			const store = transaction.objectStore(storeName);

			const request = store.delete(key);

			request.onsuccess = () => {
				resolve({ objectId: key });
			};

			request.onerror = () => {
				rejects(request.error);
			};
		});
	}

	async batchUpsert(storeName: string, data: object[]): Promise<IDBValidKey> {
		if (!this.db) {
			await this.openDb();
		}

		return new Promise<IDBValidKey>((resolve, rejects) => {
			if (!this.db) {
				rejects(new Error('Database is not open.'));
				return;
			}

			const transaction = this.db.transaction(storeName, 'readwrite');
			const store = transaction.objectStore(storeName);

			const result: IDBValidKey[] = [];
			let errorOccurred = false;

			data.forEach((record) => {
				const request = store.put(record);

				request.onsuccess = (event: Event) => {
					const key = (event.target as IDBRequest).result;
					result.push(key);
				};

				request.onerror = (event: Event) => {
					console.error('Failed to insert record:', (event.target as IDBRequest).error);
					errorOccurred = true;
				};
			});

			transaction.oncomplete = () => {
				if (errorOccurred) {
					rejects(new Error('Some records failed to insert.'));
				} else {
					resolve(result);
				}
			};

			transaction.onerror = () => {
				rejects(result);
			};
		});
	}

	async clearDatabase() {
		this.db?.close();
		const dbRequest = indexedDB.deleteDatabase(DB_NAME);
		dbRequest.onerror = () => console.error('Error deleting database');
		dbRequest.onsuccess = () => console.log('Database deleted successfully');
	}
}

export const indexedDbService = new IndexedDbService();

import { createClient } from 'graphql-ws';

const client = createClient({
  url: 'wss://api.example.com/graphql',
});

export function subscribeToMessages(callback, errorCallback) {
  const unsubscribe = client.subscribe(
    {
      query: `
        subscription OnCreateMessage {
          messageCreated {
            id
            content
            createdAt
          }
        }
      `,
    },
    {
      next: (result) => {
        if (result.errors) {
          errorCallback(result.errors);
        } else {
          callback(result.data);
        }
      },
      error: (err) => errorCallback(err),
      complete: () => console.log('Subscription closed'),
    }
  );

  return unsubscribe;
}
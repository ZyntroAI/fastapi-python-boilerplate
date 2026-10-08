import { server } from '../src/mocks/server';
import { subscribeToMessages } from '../src/services/subscriptionClient';

describe('GraphQL Subscription Retry + Error + MSW', () => {
  it('should retry on GraphQL error then succeed', (done) => {
    const unsubscribe = subscribeToMessages(
      (data) => {
        expect(data).toEqual({
          messageCreated: {
            id: '1',
            content: 'Welcome, subscriptions!',
            createdAt: expect.any(String),
          },
        });
        unsubscribe();
        done();
      },
      (errors) => {
        done.fail('Should not reach error callback');
      }
    );
  });

  it('should fail after max retries on transport error', (done) => {
    const unsubscribe = subscribeToMessages(
      (data) => {
        done.fail('Should not receive data');
      },
      (err) => {
        expect(err).toBeInstanceOf(Error);
        expect(err.message).toBe('Connection lost');
        unsubscribe();
        done();
      }
    );
  });
});
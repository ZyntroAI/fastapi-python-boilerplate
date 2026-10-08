import { server } from '../src/mocks/server';
import { subscribeToMessages } from '../src/services/subscriptionClient';

describe('GraphQL Subscription Error + MSW', () => {
  it('should receive GraphQL error via subscription', (done) => {
    const unsubscribe = subscribeToMessages(
      (data) => {
        // Should not receive data
        done.fail('Should not receive data');
      },
      (errors) => {
        expect(errors).toEqual([
          {
            message: 'Internal server error',
            extensions: { code: 'INTERNAL_SERVER_ERROR' },
          },
        ]);
        unsubscribe();
        done();
      }
    );
  });

  it('should receive transport error via subscription', (done) => {
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
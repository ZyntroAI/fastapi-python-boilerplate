import { server } from '../src/mocks/server';
import { subscribeToMessages } from '../src/services/subscriptionClient';

describe('GraphQL Subscription + MSW', () => {
  it('should receive message via subscription', (done) => {
    const unsubscribe = subscribeToMessages((data) => {
      expect(data).toEqual({
        messageCreated: {
          id: '1',
          content: 'Welcome, subscriptions!',
          createdAt: expect.any(String),
        },
      });
      unsubscribe();
      done();
    });
  });

  it('should receive comment via subscription', (done) => {
    const unsubscribe = subscribeToComments((data) => {
      expect(data).toEqual({
        commentAdded: {
          id: '1',
          content: 'Test comment',
          postId: '1',
        },
      });
      unsubscribe();
      done();
    });
  });
});
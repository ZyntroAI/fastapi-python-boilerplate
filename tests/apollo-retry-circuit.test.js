import { server } from '../src/mocks/server';
import { apolloClient } from '../src/apollo/client';
import { gql } from '@apollo/client';

describe('Apollo Client + Retry + Circuit Breaker + MSW', () => {
  it('should retry on GraphQL error then succeed', (done) => {
    const subscription = apolloClient
      .subscribe({
        query: gql`
          subscription OnCreateMessage {
            messageCreated {
              id
              content
              createdAt
            }
          }
        `,
      })
      .subscribe({
        next: (result) => {
          expect(result.data).toEqual({
            messageCreated: {
              id: '1',
              content: 'Welcome, subscriptions!',
              createdAt: expect.any(String),
            },
          });
          subscription.unsubscribe();
          done();
        },
        error: (err) => {
          done.fail(err);
        },
      });
  });

  it('should use fallback when circuit opens', (done) => {
    const subscription = apolloClient
      .subscribe({
        query: gql`
          subscription OnCommentAdded($postId: ID!) {
            commentAdded(postId: $postId) {
              id
              content
              postId
            }
          }
        `,
        variables: { postId: '1' },
      })
      .subscribe({
        next: (result) => {
          expect(result.data).toEqual({
            status: 'degraded',
            data: null,
          });
          subscription.unsubscribe();
          done();
        },
        error: (err) => {
          done.fail(err);
        },
      });
  });
});
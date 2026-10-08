import { graphql } from 'msw/graphql';

const api = graphql.link('https://api.example.com/graphql');

export const handlers = [
  // Subscription: OnCreateMessage with error
  api.subscription('OnCreateMessage', ({ subscription }) => {
    // Simulate GraphQL error
    subscription.publish({
      errors: [
        {
          message: 'Internal server error',
          extensions: { code: 'INTERNAL_SERVER_ERROR' },
        },
      ],
    });
  }),

  // Subscription: OnCommentAdded with error
  api.subscription('OnCommentAdded', ({ subscription, variables }) => {
    // Simulate transport error
    subscription.error(new Error('Connection lost'));
  }),
];
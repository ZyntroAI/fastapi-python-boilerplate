import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import MessageList from '../src/components/MessageList';
import { server } from '../src/mocks/server';
import { gql } from '@apollo/client';

describe('Apollo Client + React + MSW Subscription', () => {
  it('should receive message via subscription', async () => {
    render(
      <MockedProvider>
        <MessageList />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Welcome, subscriptions!')).toBeInTheDocument();
    });
  });

  it('should show loading state initially', () => {
    render(
      <MockedProvider>
        <MessageList />
      </MockedProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
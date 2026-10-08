import { useSubscription, gql } from '@apollo/client';

const MESSAGE_CREATED = gql`
  subscription OnCreateMessage {
    messageCreated {
      id
      content
      createdAt
    }
  }
`;

export default function MessageList() {
  const { data, loading, error } = useSubscription(MESSAGE_CREATED);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      <h2>Messages</h2>
      <ul>
        <li key={data.messageCreated.id}>
          {data.messageCreated.content}
        </li>
      </ul>
    </div>
  );
}
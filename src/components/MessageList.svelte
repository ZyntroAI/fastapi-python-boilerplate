<script>
  import { onMount } from 'svelte';
  import { apolloClient } from '../apollo/client';
  import { gql } from '@apollo/client/core';

  let messages = [];

  onMount(async () => {
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
          messages = [...messages, result.data.messageCreated];
        },
        error: (err) => console.error(err),
      });

    return () => subscription.unsubscribe();
  });
</script>

<div>
  <h2>Messages</h2>
  <ul>
    {#each messages as message}
      <li key={message.id}>{message.content}</li>
    {/each}
  </ul>
</div>
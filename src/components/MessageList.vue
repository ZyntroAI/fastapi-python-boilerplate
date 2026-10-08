<template>
  <div>
    <h2>Messages</h2>
    <ul>
      <li v-for="message in messages" :key="message.id">
        {{ message.content }}
      </li>
    </ul>
  </div>
</template>

<script>
import { useSubscription, gql } from '@vue/apollo-composable';
import { ref } from 'vue';

const MESSAGE_CREATED = gql`
  subscription OnCreateMessage {
    messageCreated {
      id
      content
      createdAt
    }
  }
`;

export default {
  setup() {
    const messages = ref([]);
    const { result } = useSubscription(MESSAGE_CREATED);

    if (result.value) {
      messages.value.push(result.value.messageCreated);
    }

    return { messages };
  },
};
</script>
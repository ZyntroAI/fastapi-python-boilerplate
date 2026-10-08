import { Component, OnInit } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-message-list',
  template: `
    <div>
      <h2>Messages</h2>
      <ul>
        <li *ngFor="let message of messages">
          {{ message.content }}
        </li>
      </ul>
    </div>
  `,
})
export class MessageListComponent implements OnInit {
  messages: any[] = [];
  private subscription: any;

  constructor(private apollo: Apollo) {}

  ngOnInit() {
    this.subscription = this.apollo
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
          this.messages.push(result.data.messageCreated);
        },
        error: (err) => console.error(err),
      });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
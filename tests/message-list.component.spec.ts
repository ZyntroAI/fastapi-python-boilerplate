import { TestBed } from '@angular/core/testing';
import { MessageListComponent } from '../src/app/components/message-list.component';
import { server } from '../src/mocks/server';
import { apolloClient } from '../src/app/apollo/client';
import { ApolloModule } from 'apollo-angular';

describe('Angular + Apollo Client + Retry + Circuit Breaker + MSW', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApolloModule],
      declarations: [MessageListComponent],
      providers: [
        { provide: 'apolloClient', useValue: apolloClient },
      ],
    }).compileComponents();
  });

  it('should receive message via subscription', (done) => {
    const fixture = TestBed.createComponent(MessageListComponent);
    fixture.detectChanges();

    setTimeout(() => {
      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('Welcome, subscriptions!');
      done();
    }, 1000);
  });

  it('should use fallback when circuit opens', (done) => {
    const fixture = TestBed.createComponent(MessageListComponent);
    fixture.detectChanges();

    setTimeout(() => {
      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('Service temporarily unavailable');
      done();
    }, 1000);
  });
});
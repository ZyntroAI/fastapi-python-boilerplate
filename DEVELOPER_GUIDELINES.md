markdown
# Developer Guidelines

## 1. General Principles

All code must be:

- Correct.
- Secure.
- Testable.
- Maintainable.
- Observable.
- Backward-compatible unless explicitly documented otherwise.

Prefer simple solutions over unnecessary abstraction.

Avoid introducing dependencies unless they provide clear value.

---

## 2. Architecture

Follow the existing repository architecture.

Do not introduce a new architectural pattern without documenting the reason.

Business logic must not be unnecessarily coupled to:

- HTTP handlers.
- UI components.
- Database implementation.
- External APIs.

Prefer clear separation between:

- Presentation.
- Application logic.
- Domain logic.
- Infrastructure.

---

## 3. TypeScript / React

Use TypeScript strict typing.

Avoid:

```ts
any

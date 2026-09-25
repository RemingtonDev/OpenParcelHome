# Cloud dependencies observed statically

Artifact A1 uses base URL `https://api.parcelhome.com/v2/` in WebServiceBuilder.
The receive-code route is `Api.Mailboxes.svc/mailboxes/{mailbox}/receivecode`.
An API token is attached in the `PhAuth` header. Registration, account lookup,
profile and code-management methods also exist.

No request was sent to these hosts during this research. Availability, current
ownership, authentication compatibility and data retention are unknown. Do not
submit old credentials merely because a URL responds over HTTPS.

The older [2016 community example](https://github.com/florisvdk/parcelhome) uses
api2.parcelhome.com. That is a historical lead, not an alternate service confirmed
usable today. Public archive and GitHub research requests are separate from
requests to vendor cloud endpoints.

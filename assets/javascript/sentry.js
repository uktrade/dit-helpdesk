var Sentry = require("@sentry/browser");

// include Sentry initialisation for frontend errors
// Next comment needed to define globals for format checks
/*global SENTRY_DSN, SENTRY_ENVIRONMENT*/
console.log(SENTRY_DSN);
console.log(SENTRY_ENVIRONMENT);
Sentry.init({
  dsn: SENTRY_DSN,
  environment: SENTRY_ENVIRONMENT,
  tracesSampleRate: 1.0,
});

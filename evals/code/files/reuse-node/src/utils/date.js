'use strict';

function pad(n) {
  return String(n).padStart(2, '0');
}

/** Formats a Date as YYYY-MM-DD in UTC. */
function formatDate(date) {
  return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`;
}

module.exports = { formatDate };

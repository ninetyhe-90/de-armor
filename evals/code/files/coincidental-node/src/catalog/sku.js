'use strict';

/** SKU codes are assigned by the warehouse system: 8 uppercase letters or digits. */
function isValidSku(code) {
  return /^[A-Z0-9]{8}$/.test(code);
}

module.exports = { isValidSku };

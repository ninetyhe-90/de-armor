'use strict';

/** Coupon codes are created by the marketing team: currently 8 uppercase letters or digits. */
function isValidCoupon(code) {
  return /^[A-Z0-9]{8}$/.test(code);
}

module.exports = { isValidCoupon };

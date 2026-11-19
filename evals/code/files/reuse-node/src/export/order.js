'use strict';

function toRows(orders) {
  return orders.map((o) => ({ id: o.id, amount: o.amount }));
}

module.exports = { toRows };

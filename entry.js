const mongoose = require('mongoose');

const EntrySchema = new mongoose.Schema({
  fullName: { type: String, required: true },
  department: { type: String, required: true },
  mobileNumber: { type: String, required: true },
  itemTaken: { type: String, required: true },
  quantity: { type: Number, required: true, min: 1 },
  timestamp: { type: Date, default: Date.now },
  purpose: { type: String },
});

module.exports = mongoose.model('Entry', EntrySchema);
